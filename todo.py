import discord
import json
import random
from discord.ext import commands


class Todo(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        print("Addon \"{}\" loaded".format(self.__class__.__name__))

    @commands.command(name='add')
    async def add_item(self, ctx, *, item):
        """Adds an item to the author's to-do list"""
        if ctx.message.attachments:
            for atch in ctx.message.attachments:
                item += "\n" + atch.url
        try:
            self.bot.todo_dict[str(ctx.author.id)]
        except KeyError:
            self.bot.todo_dict[str(ctx.author.id)] = []
        self.bot.todo_dict[str(ctx.author.id)].append(item)
        await ctx.send(f">>> {ctx.author.mention} I added ```{item}``` to your list. There are now {len(self.bot.todo_dict[str(ctx.author.id)])} item(s) on your list.")
        with open('saves/{}.json'.format(str(ctx.guild.id)), 'w') as f:
            json.dump(self.bot.todo_dict, f, indent=4)

    @commands.command(name='remove')
    async def remove_item(self, ctx, *, index):
        """Removes an item from the author's to-do list"""
        is_multi = False
        if " " in index or "," in index:
            index = index.replace(', ', ' ').replace(',', ' ')
            multi_index = index.split(' ')
            try:
                multi_index = sorted(multi_index, key=int, reverse=True)
            except ValueError:
                for x in multi_index:
                    if not x.isdigit():
                        multi_index.remove(x)
                multi_index = sorted(multi_index, key=int, reverse=True)
            is_multi = True
        if is_multi:
            items = []
            failed_indexes = []
            successful_indexes = []
            msg = ""
            for i in multi_index:
                if int(i) < 1:
                    msg += f"{i} is an invalid value, and was skipped."
                    continue
                try:
                    items.insert(0, self.bot.todo_dict[str(ctx.author.id)].pop(int(i) - 1))
                    successful_indexes.insert(0, i)
                except IndexError:
                    failed_indexes.append(i)
                except KeyError:
                    return await ctx.send(f"{ctx.author.mention} You have no items on your list!")
            items_str = ""
            for i in range(len(items)):
                items_str += f"{successful_indexes[i]}: {items[i]}\n"
            if len(items_str) > 0:
                msg += f">>> {ctx.author.mention} I removed the item(s) at indexes `{', '.join(successful_indexes)}` from your list. Item is below, in case this was an accident.\n\n```{items_str}```"
            if len(failed_indexes) > 0:
                msg += f"\n I couldn't find an item at indexes `{' '.join(failed_indexes)}`."
            await ctx.send(msg)
        else:
            if not index.isdigit() or int(index) < 1:
                return await ctx.send(f"{ctx.author.mention} `{index}` isn't a valid integer!")
            try:
                item = self.bot.todo_dict[str(ctx.author.id)].pop(int(index) - 1)
            except IndexError:
                return await ctx.send(f"{ctx.author.mention} I couldn't find an item at that index.")
            except KeyError:
                return await ctx.send(f"{ctx.author.mention} You have no items on your list!")
            await ctx.send(f">>> {ctx.author.mention} I removed the item at index {index} from your list. Item is below, in case this was an accident.\n\n```{item}```")
        with open('saves/{}.json'.format(str(ctx.guild.id)), 'w') as f:
            json.dump(self.bot.todo_dict, f, indent=4)

    @commands.command(name='list')
    async def list_items(self, ctx):
        """Returns author's to-do list"""
        try:
            items = self.bot.todo_dict[str(ctx.author.id)]
            if len(items) == 0:
                raise(IndexError)
        except (KeyError, IndexError):
            return await ctx.send(f"{ctx.author.mention} You currently have no items on your to-do list. 🎉")
        embed = discord.Embed(title=f"{ctx.author.name}'s To-Do List", description="")
        count = 1
        for item in items:
            embed.description += f"**{count}**: {item}\n"
            count += 1
        await ctx.send(f"{ctx.author.mention}", embed=embed)

    @commands.command(name='clear')
    async def clear_list(self, ctx):
        """Completely clears the author's to-do list"""
        try:
            user_list = self.bot.todo_dict[str(ctx.author.id)]
            if len(user_list) == 0:
                raise(IndexError)
        except (KeyError, IndexError):
            return await ctx.send(f"{ctx.author.mention} You have no items in your list, so there's nothing to clear.")
        yes_val = random.randint(100, 10000)

        def check_author(m):
            return m.author == ctx.author

        await ctx.send(f"{ctx.author.mention} This will completely clear your to-do list. Reply with {yes_val} to confirm. Reply with anything else to cancel. This will time out in 60 seconds.")
        message = await self.bot.wait_for('message', check=check_author, timeout=60.0)
        choice = message.content == str(yes_val)
        if not choice:
            return await ctx.send(f"{ctx.author.mention} You have chosen not to clear your to-do list.")
        self.bot.todo_dict[str(ctx.author.id)] = []
        with open('saves/{}.json'.format(str(ctx.guild.id)), 'w') as f:
            json.dump(self.bot.todo_dict, f, indent=4)
        await ctx.send(f"{ctx.author.mention} Your to-do list has been completely cleared.")


def setup(bot):
    bot.add_cog(Todo(bot))
