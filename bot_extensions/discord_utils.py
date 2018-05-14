import asyncio

class BotUtilities():

    def __init__(self, loop=None):
        self.loop = loop

    async def get_user_id(self, message):
        return message.author.id

    async def format_msg(self, message):
        dirt = ["%%add", " ", ":", "!"]
        msg = str(message.content)
        for piece in dirt:
            msg = msg.replace(piece, "")
        return msg