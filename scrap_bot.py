import discord
import asyncio


client = discord.Client()

async def print_channels():
    await client.wait_until_ready()
    channels = client.get_all_channels()
    print([(str(channel),str(channel.id)) for channel in list(channels)])

async def send_msg():
    await client.wait_until_ready()
    await client.send_message(discord.Object(id="407911597017661450"), content="#wave")

@client.event
@asyncio.coroutine
def on_ready():
    print('\nLogged in. Reading chat\nctrl+c to logout')

def destination(channel):
    id = str(channel.id)
    return discord.Object(id=id)


async def get_members_with_role():
    await client.wait_until_ready()
    members = client.get_all_members()

    print([(str(member), str(member.id), [str(role) for role in member.roles]) for member in list(members)])



@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith('%%sheet'):
        await client.send_message(destination(message.channel), "generating spreadsheet...")
        await client.send_file(destination(message.channel), "out.csv")
    #elif message.content.startswith("%%m+"):
        #message.author

if __name__ == '__main__':

    #client.loop.create_task(print_channels())
    client.loop.create_task(send_msg())
    client.loop.create_task(get_members_with_role())

try:
    client.run('NDE4NTU1OTE5NjI2OTI4MTI4.DXjSTA.CKIQ75wdY9rB7JPa36DdlthVQUs')
except KeyboardInterrupt:
    client.logout()
finally:
    print("logged out")