import discord

# setup discord client
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


# setup on_ready listener
@client.event
async def on_ready():
    print(f'Logged in as {client.user}')


# setup on_message event listener
@client.event
async def on_message(message):
    print(f'{message.author}: {message.content}')