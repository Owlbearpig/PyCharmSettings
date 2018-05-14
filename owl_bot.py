import discord
import asyncio
import csv
from files import variables
from bot_extensions.extension_class import BotExtensionFunctions
from bot_extensions.discord_utils import BotUtilities
import update_all_members_db_table as update
import character_groups as char_groups


#
# Owlbot, a Discord bot by Owlbearpig and Inarius, based on discord.py and its command
#                             extension
#
#
#

vars = variables.Variables()
client = discord.Client()
loop = asyncio.get_event_loop()

token = vars._disc_login_token

async def print_channels():
    await client.wait_until_ready()
    channels = client.get_all_channels()
    print([(str(channel),str(channel.id)) for channel in list(channels)])

async def send_msg():
    await client.wait_until_ready()
    #await client.send_message(discord.Object(id="410942179952033794"), content="#hello : )")

@client.event
async def on_ready():
    await send_msg()
    print('Logged in. Reading chat')

def destination(channel):
    id = str(channel.id)
    return discord.Object(id=id)

@client.event
async def on_message(message):
    extensions = BotExtensionFunctions(loop=loop)
    utils = BotUtilities(loop=loop)

    if message.author == client.user: # don't wanna read our own messages
        return

    if message.content.startswith('%%sheet'):
        await client.send_message(destination(message.channel), "generating spreadsheet")
        await extensions.dungeonator_main()
        await client.send_message(destination(message.channel), "done. Attaching file...")
        await client.send_file(destination(message.channel), "out.csv")

    elif message.content.startswith("%%m++"):
        disc_id = await utils.get_user_id(message=message)
        is_present_in_db = await extensions.altinator_main(disc_id=disc_id)
        await client.send_file(message.author, extensions.altinator_png_path)

        if not is_present_in_db:
            await client.send_message(message.author, "User not in the db :(")
            await client.send_message(message.author, "But you can add yourself by replying with \"%%add:\"one of your chars\" :D ")
            await client.send_message(message.author, "(case-insensitive, doesn't matter which of your chars and you only have to do it once. Takes a few mins to add+update) Example:")
            await client.send_message(message.author, "\"%%add owlbearpig\"")

    elif message.content.startswith("%%add"):
        disc_id = await utils.get_user_id(message=message)
        new_user_char = await utils.format_msg(message)
        add_result = await extensions.add_disc_user(new_char=new_user_char, disc_id=disc_id)
        if add_result == 1:
            await client.send_message(message.author, "char not found in the guild db try again or ask owl for halp")
        elif add_result == 2:
            await client.send_message(message.author, "already in db just do %%m++ =) Or this is not your char ? :O")
        elif add_result == None:
            char_groups.create_member_links() # updating db member links table, after successfully adding the user
            await client.send_message(message.author, "{} added to db poggers. Doing spreadsheet now".format(new_user_char))
            await extensions.altinator_main(disc_id=disc_id)
            await client.send_file(message.author, extensions.altinator_png_path)

    elif message.content.startswith("%%lu"):
        disc_id = await utils.format_msg_ul(message)
        await extensions.altinator_main(disc_id=disc_id)
        await client.send_file(message.author, extensions.altinator_png_path)


async def _run():
    await client.login(token)
    await client.connect()

async def logout():
    await client.logout()


try:
    loop.run_until_complete(_run())
except Exception as e:
    print(e)
    loop.run_until_complete(logout())
finally:
    loop.close()



