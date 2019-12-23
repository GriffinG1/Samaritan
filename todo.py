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
        try:
            self.bot.todo_dict[str(ctx.author.id)]
        except KeyError:
            self.bot.todo_dict[str(ctx.author.id)] = []
        self.bot.todo_dict[str(ctx.author.id)].append(item)
        await ctx.send(f"{ctx.author.mention} I added `{item}` to your list. There are now {len(self.bot.todo_dict[str(ctx.author.id)])} item(s) on your list.")
        with open('todo.json', 'w') as f:
            json.dump(self.bot.todo_dict[str(ctx.author.id)], f, indent=4)

    @commands.command(name='remove')
    async def remove_item(self, ctx, index: int):
        """Removes an item from the author's to-do list"""
        try:
            item = self.bot.todo_dict[str(ctx.author.id)].pop(index - 1)
        except IndexError:
            return await ctx.send(f"{ctx.author.mention} I couldn't find an item at that index.")
        await ctx.send(f"{ctx.author.mention} I removed the item at index {index} from your list. Item is below, in case this was an accident.\n\n`{item}`")
        with open('todo.json', 'w') as f:
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
        await ctx.send(f"{ctx.author.mention} Your to-do list has been completely cleared.")


def setup(bot):
    bot.add_cog(Todo(bot))
