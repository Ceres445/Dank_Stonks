from discord.ext import commands


class BadListType(commands.CommandError):
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return self.text


class BadQueryType(commands.CommandError):
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return self.text
