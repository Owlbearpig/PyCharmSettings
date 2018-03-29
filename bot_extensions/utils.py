import asyncio

class BotUtilities():

    def __init__(self, loop=None):
        self.loop = loop

    async def get_user_id(self, message):
        return message.author.id