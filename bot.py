import os
import asyncio
import discord
import datetime
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='?')

servers = {}

confession_channel = {
	718886828891176997 : 771297583753855007,
	786247752635908116 : 786247752635908119,
	414279195821080597 : 782703953086775346,
	768834106611204096 : 770160051414892567,
	784002698588061727 : 785057888959332353
}

def is_int(s):
	try: 
		int(s)
		return True
	except ValueError:
		return False

def prepare_embed(msg):
	embedVar = discord.Embed(title='Anonymous Confession')
	utcnow = datetime.datetime.utcnow()
	istnow = utcnow + datetime.timedelta(hours = 5, minutes = 30)
	embedVar.set_footer(text = '{0:%b %d • %I:%M %p}'.format(istnow))

	if msg.content:
		embedVar.description = msg.content

	if msg.embeds:
		data = msg.embeds[0]
		if data.type == 'image':
			embedVar.set_image(url=data.url)

	if msg.attachments:
		file = msg.attachments[0]
		if file.url.lower().endswith(('png', 'jpeg', 'jpg', 'gif', 'webp')):
			embedVar.set_image(url=file.url)
		else:
			embedVar.add_field(name='Attachment', value=f'[{file.filename}]({file.url})', inline=False)

	return embedVar

@bot.event
async def on_ready():
	print(f'{bot.user} is connected to the following guild:\n')
	for guild in bot.guilds:
		print(f'{guild.name} (id: {guild.id})\n')
	for guild in bot.guilds:
		servers[guild.id] = {}
		async for member in guild.fetch_members(limit=None):
			servers[guild.id][member.id] = True


@bot.command()
@commands.dm_only()
async def confess(ctx):
	mutual_servers = []
	for guild in bot.guilds:
		if ctx.author.id in servers[guild.id]:
			mutual_servers.append(guild)
	
	embedVar = discord.Embed(title = 'Server Select')
	embedVar.description = '**'
	i = 0
	for guild in mutual_servers:
		i = i + 1
		embedVar.description += str(i) + ' - ' + guild.name + '\n\n'
	embedVar.description += '**'
	embedVar.set_footer(text='You have 1 minute to select a server - send "cancel" to cancel')
	await ctx.send(embed=embedVar)

	def server_select(msg):
		return msg.channel == ctx.channel and ((is_int(msg.content) and int(msg.content) <= i and int(msg.content) >= 1) or msg.content == 'cancel')

	try:
		msg = await bot.wait_for('message', timeout=60, check=server_select)
	except asyncio.TimeoutError:
		await ctx.send('⏳ Server selection timed out. Please start a new confession.')
		return

	if msg.content == 'cancel':
		await ctx.send('✅ Cancelled')
		return

	guild = mutual_servers[int(msg.content) - 1]
	confess_in = bot.get_channel(confession_channel[guild.id])
	embedVar = discord.Embed()
	embedVar.title = 'Confessions : ' + guild.name
	embedVar.description = f'Simply type your confession / send a image link / upload a file to post it anonymously in {confess_in.mention}.'
	embedVar.set_footer(text='You have 2 minutes to respond - type "cancel" to abort')
	await ctx.send(embed=embedVar)

	def check_confess(msg):
		return msg.channel == ctx.channel

	try:
		msg = await bot.wait_for('message', timeout=120, check=check_confess)
	except asyncio.TimeoutError:
		await ctx.send('⏳ Your confession timed out. Please start a new confession.')
		return

	if msg.content == 'cancel':
		await ctx.send('✅ Cancelled')
		return

	
	confession = await confess_in.send(embed = prepare_embed(msg))
	confirmation = await ctx.send(f'✅ Your confession has been added to {confess_in.mention}!')


bot.run(TOKEN)
