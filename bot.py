import os
import asyncio
import discord
import datetime
import requests
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
TENOR_API_KEY = os.getenv('TENOR_API_KEY')

bot = commands.Bot(command_prefix='?')

servers = {}

confession_channel = {
	# server_id : confession_channel_id
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

def get_tenor_url(view_url):
	if view_url.lower().endswith('gif'):
		return view_url
	gif_id = view_url.split('-')[-1]
	url = f'https://api.tenor.com/v1/gifs?ids={gif_id}&key={TENOR_API_KEY}'
	res = requests.get(url)
	if res.status_code == 200:
		return res.json()['results'][0]['media'][0]['gif']['url']
	else:
		return None

def get_giphy_url(view_url):
	if view_url.lower().endswith('gif'):
		return view_url
	else:
		gif_id = view_url.split('-')[-1]
		return f'https://media.giphy.com/media/{gif_id}/giphy.gif'

def prepare_embed(msg):
	embedVar = discord.Embed(title='Anonymous Confession')
	embedVar.timestamp = datetime.datetime.utcnow()

	if msg.content:
		embedVar.description = msg.content

	if msg.embeds:
		data = msg.embeds[0]
		if data.type == 'image':
			embedVar.set_image(url=data.url)
			if data.url == msg.content:
				embedVar.description = None
		if data.type == 'gifv' and data.provider.name == 'Tenor':
			embedVar.set_image(url=get_tenor_url(data.url))
			if data.url == msg.content:
				embedVar.description = None
		if data.type == 'gifv' and data.provider.name == 'Giphy':
			embedVar.set_image(url=get_giphy_url(data.url))
			if data.url == msg.content:
				embedVar.description = None

	if msg.attachments:
		file = msg.attachments[0]
		if file.url.lower().endswith(('png', 'jpeg', 'jpg', 'gif', 'webp')):
			embedVar.set_image(url=file.url)
		else:
			embedVar.add_field(name='Attachment', value=f'[{file.filename}]({file.url})')

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


async def check_if_delete(msg, confession, confirmation):
	def check(deleted_msg):
		return msg.id == deleted_msg.id 

	try:
		await bot.wait_for('message_delete', timeout=120, check=check)
		await confession.delete()
		await confirmation.edit(content=f'✅ Confession with message id `{confession.id}` in {confession.channel.mention} has been deleted.')
	except asyncio.TimeoutError:
		return


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
		return msg.channel == ctx.channel and msg.author == ctx.author and ((is_int(msg.content) and int(msg.content) <= i and int(msg.content) >= 1) or msg.content == 'cancel')

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
		return msg.channel == ctx.channel and msg.author == ctx.author

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

	asyncio.create_task(check_if_delete(msg, confession, confirmation))

	def check_edit(before, after):
		return msg.id == after.id
	
	edit_count = 0
	if msg.edited_at:
		await confession.edit(embed = prepare_embed(msg))
		edit_count += 1
		await confirmation.edit(content=f'✅ Confession with message id `{confession.id}` in {confess_in.mention} has been edited ({edit_count}).')
	
	
	while True:
		try:
			before, after = await bot.wait_for('message_edit', timeout=120, check=check_edit)
			await confession.edit(embed = prepare_embed(after))
			edit_count += 1
			await confirmation.edit(content=f'✅ Confession with message id `{confession.id}` in {confess_in.mention} has been edited ({edit_count}).')
		except asyncio.TimeoutError:
			return


bot.run(TOKEN)
