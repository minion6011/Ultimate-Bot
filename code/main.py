import discord
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions, CheckFailure, NoPrivateMessage
from discord.utils import get
import random #random exractor - captcha-image-text - giveaway bot
from random import choice #random exractor
import asyncio #time - music-bot #giveaway
import os #botinfo - music-bot
import aiohttp #https
import requests #https
from requests import get #https
import json #htpps #giveaway
import psutil, datetime #system-info
from deep_translator import GoogleTranslator #traduttore
import pytubefix #music-bot
from pytubefix import YouTube #music-bot
from pytubefix import Search #music-bot
from pytubefix.cli import on_progress
import base64 #generate image
from io import BytesIO #generate image
import io #captcha-image - generate image
from PIL import Image, ImageDraw, ImageFont #captcha-image
from typing import Literal #slash preset-option - automod
from datetime import timedelta #timeout time - automod
from discord import ui #discord-ui
from discord import app_commands #discord-slash - discord-ui
import typing #suggestion
import string #suggestion
import time #errorlog #giveaway bot
import datetime as dtm #giveaway Bot
from datetime import datetime as dt #giveaway Bot


with open("config.json") as f:
	try:
		data = json.load(f)
	except json.decoder.JSONDecodeError as e:
		print("Errore in config.json")
		print(e)
		exit(1)


# - Mini Config

# Basic Info
prefix = data["command_prefix"]
footer_testo = data["footer_embed"]
token_json = data["discord_token"]

# Id List
my_id = [0, 0]

# Channel List
stalkid = 0
errorchannel = 0
statuschannel = 0
reportbugchannel = 0

# Database
giveaway_database = "giveaway_data.json"
database_ticket = "ticket_channels.json"
database_verify = "verify_channels.json"
database_suggestion = "suggestion_data.json"
error_log_file = "log.txt"

# Timeout (Anti-Ratelimit)
timeout_time_ticket = 5
timeout_time_suggestion = 5
timeout_time_automod = 2
generic_error_delete_after_time = 4
command_error_delete_after_time = 4

# Slash Command ID
# 1* sezione
slash_suggestionsetupadd_id = "0"
slash_suggestionsetupremove_id = "0"
slash_suggest_id = "0"
slash_approve_id = "0"
slash_deny_id = "0"
# 2* sezione
slash_automodcreate_id = "0"
slash_automoddelete_id = "0"
# 3* sezione
slash_verifysetup_id = "0"
# 4* sezione
slash_ticketsetup_id = "0"
# 5* sezione
slash_play_id = "0"
slash_stop_id = "0"
slash_volume_id = "0"
# 7* sezione
slash_help_id = "0"
slash_reportbug_id = "0"
slash_giveaway_id = "0"

#-----------Client--------------#

class PersistentViewBot(commands.Bot): 
	def __init__(self):
		intents = discord.Intents.all()

		super().__init__(command_prefix=prefix, intents=intents, case_insensitive=True)
	async def setup_hook(self) -> None:
		slash_sync = await self.tree.sync() # - slash 
		print(f"Synced app command (tree) {len(slash_sync)}.") # - slash 

		# - Ticket Button
		view_ticket_open = discord.ui.View(timeout=None)
		view_ticket_open.add_item(Open_Ticket_Button(label=None))
		self.add_view(view_ticket_open) # Open Ticket Button
		self.add_view(Close_Ticket_Button()) # Close Ticket Button

		# - Verify Button
		view_verify_open = discord.ui.View(timeout=None)
		view_verify_open.add_item(Open_Verify(label=None))
		self.add_view(view_verify_open)
		self.add_view(Captcha_Button(None))

		# - Suggestion Button
		self.add_view(Suggestion_Button())

		# - Giveaway System
		#database
		with open(giveaway_database, 'r') as f:
			c_dati = json.load(f)
		if not "dati" in str(c_dati):
			c_dati["dati"] = []
			with open(giveaway_database, 'w') as f:
				json.dump(c_dati, f)
		#view
		self.add_view(Partecipate_Giveaway_Button())
		#task loop
		giveaway_check.start()

client = PersistentViewBot() 

is_me = commands.check(lambda ctx: ctx.author.id in my_id)

client.remove_command('help')

# - global setup

global captcha_text
captcha_text = None


#-----------Events--------------#


@client.event
async def on_ready():
	try:
		change_status.cancel()
	except:
		pass
	print(f"Bot logged into {client.user}.")
	channel = client.get_channel(statuschannel)
	embed = discord.Embed(title=f"**Bot Online 🟢**", color=discord.Color.green())
	await channel.send(embed=embed)
	await asyncio.sleep(10)
	change_status.start()



@client.event
async def on_voice_state_update(member, before, after): # Music Bot Event
	voice_client = member.guild.voice_client
	if member.display_name == client.user:
		if voice_client.is_playing():
			voice_client.stop()   	


@client.event
async def on_message_edit(before, after): # Command Event
	if after.author.bot:
		return
	elif before.author.bot:
		return
	else:
		await client.process_commands(after)



# - database removing
		
@client.event
async def on_guild_remove(guild):
	channel_id_list = []
	for channel in guild.text_channels:
		channel_id_list.append(channel.id)
	for channel in guild.voice_channels:
		channel_id_list.append(channel.id)
	
	with open(database_ticket, 'r') as f: # Database Ticket Remove
		dati_ticket = json.load(f)
	for channel in channel_id_list:
		if str(channel) in dati_ticket:
			del dati_ticket[str(channel)]
			with open(database_ticket, 'w') as f: 
				json.dump(dati_ticket, f)

	with open(database_verify, 'r') as f: # Database Verify Remove
		dati_verify = json.load(f)
	if str(guild.id) in dati_verify:
		for channel in channel_id_list:
			if str(channel) in dati_verify[str(guild.id)]["v_channel"]:
				del dati_verify[str(guild.id)]
				with open(database_verify, 'w') as f:
					json.dump(dati_verify, f)




@client.event
async def on_guild_channel_delete(channel):
		channel_id = channel.id

		# Dati Ticket
		with open(database_ticket, 'r') as f:
			dati_ticket = json.load(f)

		if channel_id in dati_ticket: #Check Ticket
			del dati_ticket[str(channel_id)]
			with open(database_ticket, 'w') as f:
				json.dump(dati_ticket, f)

		# Dati Verify
		with open(database_verify, 'r') as f:
			dati_verify = json.load(f)
		if str(channel.guild.id) in dati_verify: 
			if str(channel_id) in dati_verify[str(channel.guild.id)]["v_channel"]:
				del dati_verify[str(channel.guild.id)]
				with open(database_verify, 'w') as f:
					json.dump(dati_verify, f)
				try:
					r_id = int(dati_verify[str(channel_id)]["r_id"])
					if discord.utils.get(channel.guild.roles, id=r_id):
						try:
							role_id = discord.utils.get(channel.guild.roles, id=r_id)

							#channel - restore
							for channel in channel.guild.channels:

								role_ver = discord.utils.get(channel.guild.roles, id=role_id)

								overwrite_role = channel.overwrites_for(role_ver)
								if overwrite_role.view_channel == True:
									await channel.set_permissions(channel.guild.default_role, view_channel=True)

							role = discord.utils.get(channel.guild.roles, name="verify")
							await role.delete()
						except:
							pass
				except:
					pass



#----------Commands--------#


@commands.cooldown(1, 5, commands.BucketType.user)
@client.command()
@commands.guild_only()
async def help(ctx):
	embed = discord.Embed(title=f"`?help` has been disabled\nTry using </help:{slash_help_id}>", color=discord.Color.greyple())
	embed.set_footer(text=footer_testo)
	await ctx.send(embed=embed, delete_after=10)


#--Mod command

@client.command()
@commands.guild_only()
@commands.has_permissions(manage_messages=True)
@commands.cooldown(1, 20, commands.BucketType.user)
async def nuke(ctx, amount: int = 50):
	if amount == 0:
		embed = discord.Embed(title=f"Unable to delete messages, you must select a number between 1 and 400", color=discord.Color.red())
		embed.set_footer(text=footer_testo)  
		await ctx.send(embed=embed, delete_after=command_error_delete_after_time)
		return
	if amount < 400:
		embed = discord.Embed(title=f"{amount} messages deleted", color=discord.Color.red())
		embed.set_image(url="https://www.19fortyfive.com/wp-content/uploads/2021/10/Nuclear-Weapons-Test.jpg")
		await ctx.channel.purge(limit=amount)
		embed.set_footer(text=footer_testo)  
		await ctx.send(embed=embed, delete_after=6)
	else:
		embed = discord.Embed(title=f"Unable to delete messages, the maximum is 400", color=discord.Color.red())
		embed.set_footer(text=footer_testo)  
		await ctx.send(embed=embed, delete_after=command_error_delete_after_time)




@client.command()
@commands.guild_only()
@has_permissions(kick_members=True)
async def kick(ctx, member : discord.Member, *, reason = None):
	try:
		if member == None:
			embed = discord.Embed(title=":warning: Please write the member's ID :warning:", color=discord.Color.red())
			embed.set_footer(text=footer_testo)  
			await ctx.send(embed=embed)
		elif reason == None:
			if member == None:
				embed = discord.Embed(title=":warning: Please write the member's ID :warning:", color=discord.Color.red())
				embed.set_footer(text=footer_testo)  
				await ctx.send(embed=embed)
			else:
				embed = discord.Embed(title=":warning: Member was kicked :warning:", color=discord.Color.red())
				embed.set_footer(text=footer_testo)  
				await ctx.send(embed=embed)
				await member.kick(reason=f"You have been banned from the server: {ctx.guild.name}")
		else:
			embed = discord.Embed(title=":warning: Member was kicked :warning:", color=discord.Color.red())
			embed.set_footer(text=footer_testo)  
			await ctx.send(embed=embed)
			await member.kick(reason=f"You have been kicked from the server: {ctx.guild.name}, For: '{reason}'")
	except Exception as e:
		if 'error code: 50013' in str(e):
			embed = discord.Embed(title="Error: I don't have permission to kick this user", color=discord.Color.red())
			embed.set_footer(text=footer_testo)
			await ctx.send(embed=embed, delete_after=command_error_delete_after_time)
		else:
			channel = client.get_channel(errorchannel)
			await channel.send(f"**[Errore]** \nisinstance: ```{e}```\nerror: ```{str(e)}```")
			errror_log(e,str(e),"kick command")





@client.command()
@commands.guild_only()
@has_permissions(ban_members=True)
async def ban(ctx, member : discord.Member, *, reason = None):
	try:
		if member == None:
			embed = discord.Embed(title=":warning: Please write the member's ID :warning:", color=discord.Color.red())
			embed.set_footer(text=footer_testo)  
			await ctx.send(embed=embed)
		elif reason == None:
			if member == None:
				embed = discord.Embed(title=":warning: Please write the member's ID :warning:", color=discord.Color.red())
				embed.set_footer(text=footer_testo)  
				await ctx.send(embed=embed)
			else:
				await member.ban(reason=f"You have been banned from the server: {ctx.guild.name}")
				embed = discord.Embed(title=":warning: Member was banned :warning:", color=discord.Color.red())
				embed.set_footer(text=footer_testo)  
				await ctx.send(embed=embed,delete_after=10)
		else:
			await member.ban(reason=f"You have been banned from the server: {ctx.guild.name}, For: '{reason}'")
			embed = discord.Embed(title=":warning: Member was banned :warning:", color=discord.Color.red())
			embed.set_footer(text=footer_testo)  
			await ctx.send(embed=embed,delete_after=10)
	except Exception as e:
		if 'error code: 50013' in str(e):
			embed = discord.Embed(title="Error: I don't have permission to ban this user", color=discord.Color.red())
			embed.set_footer(text=footer_testo)
			await ctx.send(embed=embed, delete_after=command_error_delete_after_time)
		else:
			channel = client.get_channel(errorchannel)
			await channel.send(f"**[Errore]** \nisinstance: ```{e}```\nerror: ```{str(e)}```")
			errror_log(e,str(e),"ban command")





@client.command()
@commands.guild_only()
@has_permissions(ban_members=True)
async def unban(ctx, user: discord.User):
	try:
		if user == None:
			embed = discord.Embed(title=":warning: Please write the member's ID :warning:", color=discord.Color.red())
			embed.set_footer(text=footer_testo)  
			await ctx.send(embed=embed)
		else:
			await ctx.guild.unban(user)
			embed = discord.Embed(title=f":warning: `{user}` has been unbanned :warning:", color=discord.Color.red())
			embed.set_footer(text=footer_testo)  
			await ctx.send(embed=embed)
	except Exception as e:
		if 'error code: 50013' in str(e):
			embed = discord.Embed(title="Error: I don't have permission to ban this user", color=discord.Color.red())
			embed.set_footer(text=footer_testo)
			await ctx.send(embed=embed, delete_after=command_error_delete_after_time)
		else:
			channel = client.get_channel(errorchannel)
			await channel.send(f"**[Errore]** \nisinstance: ```{e}```\nerror: ```{str(e)}```")
			errror_log(e,str(e),"unban command")



@client.command()
@commands.guild_only()
@has_permissions(administrator = True)
@commands.cooldown(1, 60, commands.BucketType.user)
async def delchannel(ctx):
	for c in ctx.guild.channels: # iterating through each guild channel
		await c.delete()



@client.command()
@commands.guild_only()
@commands.cooldown(1, 5, commands.BucketType.user)
@commands.has_permissions(manage_channels = True)
async def lockdown(ctx):
	await ctx.message.delete()
	for role in ctx.guild.roles:
		if role.permissions.manage_channels:
			await ctx.channel.set_permissions(role, attach_files=True, send_messages=True, read_messages=True, read_message_history=True, add_reactions=True)
	await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False, view_channel=False)
	embed = discord.Embed(title=f"***{ctx.channel.mention} is now in lockdown.*** :lock:", color=discord.Color.yellow())
	await ctx.send(embed=embed, delete_after=5)

@client.command()
@commands.guild_only()
@commands.cooldown(1, 5, commands.BucketType.user)
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
	await ctx.message.delete()
	await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True, view_channel=True)
	embed = discord.Embed(title=f"***{ctx.channel.mention} has been unlocked.*** :unlock:", color=discord.Color.yellow())
	await ctx.send(embed=embed, delete_after=5)



@client.command()
@commands.guild_only()
@commands.cooldown(1, 5, commands.BucketType.user)
@commands.has_permissions(moderate_members=True)
async def mute(ctx, user: discord.Member = None, reason = None):
		try:
			if user == None:
				embed = discord.Embed(title="Please send the user id", color=discord.Color.red())
				embed.set_footer(text=footer_testo)
				await ctx.send(embed=embed, delete_after=command_error_delete_after_time)
			else:
				guild = ctx.guild
				if discord.utils.get(ctx.guild.roles, name="mute"):
					if reason == None:
						role = discord.utils.get(ctx.guild.roles, name="mute")
						guild = ctx.guild
						for channel in ctx.guild.channels:
							permissions = discord.PermissionOverwrite(send_messages=False, read_messages=True, speak=False)
							await channel.set_permissions(role, overwrite=permissions)
						await user.add_roles(role)
						embed = discord.Embed(title = 'I muted', description = f'{user}', color=discord.Color.blue())
						embed.set_footer(text=footer_testo)
						await ctx.send(embed=embed, delete_after=7)
						name = str(ctx.guild.name)
						check_voice_member = ctx.guild.get_member(int(user.id))
						if check_voice_member and check_voice_member.voice:
							await check_voice_member.move_to(None)
						try:
							await user.send(f"You have been muted in the server: **{name}**")
						except:
							return
					else:
						role = discord.utils.get(ctx.guild.roles, name="mute")
						guild = ctx.guild
						for channel in ctx.guild.channels:
							permissions = discord.PermissionOverwrite(send_messages=False, read_messages=True, speak=False)
							await channel.set_permissions(role, overwrite=permissions)
						await user.add_roles(role)
						embed = discord.Embed(title = f'I muted {user}', description = f'For reason: {reason}', color=discord.Color.blue())
						embed.set_footer(text=footer_testo)
						await ctx.send(embed=embed, delete_after=7)
						name = str(ctx.guild.name)
						check_voice_member = ctx.guild.get_member(int(user.id))
						if check_voice_member and check_voice_member.voice:
							await check_voice_member.move_to(None)
						try:
							await user.send(f"You have been muted in the server: **{name}** because:\n{reason}")
						except:
							return
				else:
					if reason == None:
						role = discord.utils.get(ctx.guild.roles, name="mute")
						permissions = discord.Permissions(send_messages=False, read_messages=True, speak=False)
						await guild.create_role(name="mute", colour=discord.Colour(0x444949), permissions=permissions)
						guild = ctx.guild
						for channel in ctx.guild.channels:
							permissions = discord.PermissionOverwrite(send_messages=False, read_messages=True, speak=False)
							await channel.set_permissions(role, overwrite=permissions)
						await user.add_roles(role)
						embed = discord.Embed(title = 'I muted', description = f'{user}', color=discord.Color.blue())
						embed.set_footer(text=footer_testo)
						await ctx.send(embed=embed, delete_after=7)
						name = str(ctx.guild.name)
						check_voice_member = ctx.guild.get_member(int(user.id))
						if check_voice_member and check_voice_member.voice:
							await check_voice_member.move_to(None)
						else:
							return
						try:
							await user.send(f"You have been muted in the server: **{name}**")
						except:
							pass
					else:
						role = discord.utils.get(ctx.guild.roles, name="mute")
						permissions = discord.Permissions(send_messages=False, read_messages=True, speak=False)
						await guild.create_role(name="mute", colour=discord.Colour(0x444949), permissions=permissions)
						for channel in ctx.guild.channels:
							permissions = discord.PermissionOverwrite(send_messages=False, read_messages=True, speak=False)
							await channel.set_permissions(role, overwrite=permissions)
						await user.add_roles(role)
						embed = discord.Embed(title = f'I muted {user}', description = f'For reason: {reason}', color=discord.Color.blue())	
						embed.set_footer(text=footer_testo)
						await ctx.send(embed=embed, delete_after=7)
						name = str(ctx.guild.name)
						check_voice_member = ctx.guild.get_member(int(user.id))
						if check_voice_member and check_voice_member.voice:
							await check_voice_member.move_to(None)
						else:
							return
						try:
							await user.send(f"You have been muted in the server: **{name}** because:\n{reason}")
						except:
							pass
		except Exception as e:
			if "target parameter must be either Member or Role" in str(e):
				embed = discord.Embed(title="Error: You need to ping the user to mute it", color=discord.Color.red())
				embed.set_footer(text=footer_testo)
				await ctx.send(embed=embed, delete_after=command_error_delete_after_time)
			else:
				channel = client.get_channel(errorchannel)
				await channel.send(f"**[Errore]** \nisinstance: ```{isinstance}```\nerror: ```{str(e)}```")
				errror_log(e,str(e),"mute command")

@client.command()
@commands.guild_only()
@commands.cooldown(1, 5, commands.BucketType.user)
@commands.has_permissions(moderate_members=True)
async def unmute(ctx, user: discord.Member = None):
	try:
			if user == None:
				embed = discord.Embed(title="Please send the user id", color=discord.Color.red())
				embed.set_footer(text=footer_testo)
				await ctx.send(embed=embed)
			else:
				role = discord.utils.get(ctx.guild.roles, name="mute")
				await user.remove_roles(role)
				check_voice_member = ctx.guild.get_member(int(user.id))
				if check_voice_member and check_voice_member.voice:
					await check_voice_member.move_to(None)
				else:
					return
				embed = discord.Embed(title = 'I unmuted', description = f'{user}', color=discord.Color.blue())
				embed.set_footer(text=footer_testo)
				await ctx.send(embed=embed)
	except Exception as e:
			if "target parameter must be either Member or Role" in str(e):
				embed = discord.Embed(title="Error: You need to ping the user to mute it", color=discord.Color.red())
				embed.set_footer(text=footer_testo)
				await ctx.send(embed=embed, delete_after=command_error_delete_after_time)
			else:
				channel = client.get_channel(errorchannel)
				await channel.send(f"**[Errore]** \nisinstance: ```{isinstance}```\nerror: ```{str(e)}```")
				errror_log(e,str(e),"unmute command")




@client.command()
@commands.guild_only()
@commands.has_permissions(manage_channels=True)
@commands.cooldown(1, 5, commands.BucketType.user)
async def slowmode(ctx, seconds: int):
	await ctx.channel.edit(slowmode_delay=seconds)
	slowmode_embed = discord.Embed(title="Slowmode", description="A slowmode was set for this channel", colour=discord.Colour.green())
	slowmode_embed.set_footer(text=footer_testo)
	await ctx.send(embed=slowmode_embed, delete_after=10)




#--Utilty


@client.command()
@commands.guild_only()
@commands.cooldown(1, 5, commands.BucketType.user)
async def infobot(ctx):
	time_boot = datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("**Date: `%Y-%m-%d`  Time: `%H:%M:%S`**")
	embed = discord.Embed(title = 'System Resource Usage', description = 'See CPU and memory usage of the system.', color=discord.Color.blue())
	embed.add_field(name = ':computer: **CPU Usage**', value = f'{psutil.cpu_percent()}%', inline = False)
	embed.add_field(name = ':floppy_disk: **Memory Usage**', value = f'{psutil.virtual_memory().percent}%', inline = False)
	embed.add_field(name = ':floppy_disk: **Available Memory**', value = f'{psutil.virtual_memory().available * 100 / psutil.virtual_memory().total}%', inline = False)
	embed.add_field(name = ':globe_with_meridians: **Ping**', value = f'{round(client.latency * 1000)}ms')
	embed.add_field(name = ':timer: **Last Boot**', value =time_boot)
	embed.set_footer(text=footer_testo)
	await ctx.send(embed = embed)



@client.command()
@commands.guild_only()
@commands.cooldown(1, 5, commands.BucketType.user)
async def serverinfo(ctx):
	guild_create = ctx.guild.created_at.strftime("%d-%m-%Y")
	check_text = discord.utils.get(ctx.guild.text_channels)
	check_voice = discord.utils.get(ctx.guild.voice_channels)
	check_category = discord.utils.get(ctx.guild.categories)
	embed = discord.Embed(title=f"***{ctx.guild.name}*** - Info", color=discord.Colour.blue())
	embed.add_field(name=':page_facing_up: - Nome del Server', value=f'**`{str(ctx.guild.name)}`**', inline=True)
	embed.add_field(name=':bookmark_tabs: -  Descrizione del Server', value=f'**`{str(ctx.guild.description)}`**', inline=True)
	embed.add_field(name=':id: - ID del Server', value=f"`{ctx.guild.id}`", inline=True)
	embed.add_field(name=':busts_in_silhouette: - Membri', value=f'**`{ctx.guild.member_count}` Membri**', inline=True)
	embed.add_field(name=':crown: - Creatore del Server', value=f"<@{ctx.guild.owner_id}>", inline=True)
	embed.add_field(name=':bust_in_silhouette: - Numero Ruoli', value=f'**`{len(ctx.guild.roles)}` Ruoli**', inline=True)
	#if check_forum is not None:
	#	embed.add_field(name=f':speech_left: - Forum {len(ctx.guild.forum_channels)}', inline=False)
	if check_text is not None:
		embed.add_field(name=f':speech_balloon: - Canali Testuali ', value=f'**`{len(ctx.guild.text_channels)}`**', inline=True)
	if check_voice is not None:
		embed.add_field(name=f':speaker: - Canali Vocali ', value=f'**`{len(ctx.guild.voice_channels)}`**', inline=True)
	if check_category is not None:
		embed.add_field(name=':open_file_folder: - Categorie ', value=f'**`{len(ctx.guild.categories)}`**', inline=True)
	embed.add_field(name=':calendar: - Server creato il:', value=f"**`{guild_create}`**", inline=False)
	embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
	embed.set_footer(text=footer_testo)
	await ctx.send(embed=embed)



@client.command()
@commands.guild_only()
@commands.cooldown(1, 5, commands.BucketType.user)
async def userinfo(ctx, *, member: discord.Member = None):
	user = member
	voice_state = None if not user.voice else user.voice.channel
	role = user.top_role.name
	acc_created = user.created_at.__format__('Date: %A, %d. %B %Y Time: %H:%M:%S')
	server_join = user.joined_at.__format__('Date: %A, %d. %B %Y Time: %H:%M:%S')
	if role == "@everyone":
		role = None
	embed = discord.Embed(title=f"**User Info**", color=discord.Colour.blue())
	embed.add_field(name=":bust_in_silhouette: - Displayed Server Name", value=member.mention, inline=True)
	embed.add_field(name=':bust_in_silhouette: - User Name', value=f"`{member.name}`", inline=True)
	embed.add_field(name=':id: - User ID', value=f"`{member.id}`", inline=False)
	embed.add_field(name=':robot: - Robot?', value=f"`{member.bot}`", inline=True)
	embed.add_field(name=':loud_sound:  - Is in voice', value=f"**In:** `{voice_state}`", inline=True)
	embed.add_field(name=':radio_button:  - Highest Role', value=f"`{role}`", inline=True)
	embed.add_field(name=':calendar: - Account Created', value=f"`{acc_created}`", inline=False)
	embed.add_field(name=':calendar: - Join Server Date', value=f"`{server_join}`", inline=False)
	embed.set_thumbnail(url=user.avatar)
	embed.set_footer(text=footer_testo)
	await ctx.send(embed=embed)


@client.command()
@commands.guild_only()
@commands.cooldown(1, 5, commands.BucketType.user)
async def translate(ctx, language, *, request):
	text = request
	lang = language
	try:
		if len(text) > 1998:
			embed = discord.Embed(title="Error: The text is too long must not exceed 1998 characters", color=discord.Color.red())
			embed.set_footer(text=footer_testo)
			await ctx.send(embed=embed, delete_after=command_error_delete_after_time)
		else:
			if len(text) > 1024:
				traduttore = GoogleTranslator(source='auto', target=lang)
				risultato = traduttore.translate(text)
				await ctx.send(f"```{risultato}```")
			else:
				traduttore = GoogleTranslator(source='auto', target=lang)
				risultato = traduttore.translate(text)
				embed=discord.Embed(color=discord.Color.green())
				embed.add_field(name=":earth_americas: Request:", value=f"{request}")
				embed.set_footer(text=footer_testo)
				await ctx.send(embed=embed, content=f"```{risultato}```")
	except Exception as e:
		embed=discord.Embed(title=f"The language {lang} is not supported.\nTo see the supported languages press the button.", color=discord.Color.green())
		embed.set_footer(text=footer_testo)
		await ctx.send(embed=embed, view=TraslateButton())


@client.command()
@commands.guild_only()
@commands.cooldown(1, 5, commands.BucketType.user)
async def custom_emoji_info(ctx, emoji: discord.Emoji = None):
	try:
		if not emoji:
			embed = discord.Embed(title="Error\nPlease send a valid emoji", colour=discord.Colour.red())
			embed.set_footer(text=footer_testo)
			await ctx.send(embed=embed)
		else:
			response_emoji = await emoji.guild.fetch_emoji(emoji.id)
			
			is_managed = "Yes" if response_emoji.managed else "No" 
			is_animated = "Yes" if response_emoji.animated else "No"
			requires_colons = "Yes" if response_emoji.require_colons else "No"
			creation_time = response_emoji.created_at.strftime("%b %d %Y")
			can_use_emoji = "Everyone" if not response_emoji.roles else "".join(role.name for role in response_emoji.roles)
			name = response_emoji.name
			id_emoji = response_emoji.id
	
			embed = discord.Embed(title="Emoji - Info", colour=discord.Colour.blue())
			embed.add_field(name=":scroll: Name", value=f"`{name}`", inline=True)
			embed.add_field(name=":id: Id", value=f"`{id_emoji}`", inline=True)
			embed.add_field(name=":camera: Url", value=f"[Emoji Url]({response_emoji.url})", inline=True)
	
			embed.add_field(name=":page_facing_up: Guild name", value=f"`{response_emoji.guild.name}`", inline=True)
			embed.add_field(name=":busts_in_silhouette: Author", value=f"`{response_emoji.user.name}`", inline=True)
			embed.add_field(name=":calendar: Time Created", value=f"`{creation_time}`", inline=True)
	
			embed.add_field(name="Animated", value=f"`{is_animated}`", inline=True)
			embed.add_field(name="Managed", value=f"`{is_managed}`", inline=True)
			embed.add_field(name="Requires colons", value=f"`{requires_colons}`", inline=True)
	
			embed.add_field(name=":busts_in_silhouette: Usable by", value=f"`{can_use_emoji}`", inline=False)
	
			embed.set_footer(text=footer_testo)
			embed.set_thumbnail(url=response_emoji.url)
			await ctx.send(embed=embed)
	except Exception as e:
		if 'not found.' in str(e):
			embed = discord.Embed(title="Error: Emoji not found", color=discord.Color.red())
			embed.set_footer(text=footer_testo)
			await ctx.send(embed=embed, delete_after=command_error_delete_after_time)
		else:
			embed = discord.Embed(title="Error: Unknown", color=discord.Color.red())
			embed.set_footer(text=footer_testo)
			await ctx.send(embed=embed, delete_after=command_error_delete_after_time)
			#error-chat
			channel = client.get_channel(errorchannel)
			await channel.send(f"**[Errore]** \nisinstance: ```{isinstance}```\nerror: ```{str(e)}```")   
			errror_log(e,str(e),"custom_emoji_info command")      


@client.command()
@commands.guild_only()
@commands.cooldown(1, 5, commands.BucketType.user)
async def dictionary(ctx, term):
	url = f"https://api.urbandictionary.com/v0/define?term={term}"
	response = requests.get(url).json()
	if "list" in response:
		if response["list"]:
			definition = response["list"][0]["definition"]
			example = response["list"][0]["example"]
			
			#await ctx.send(f"**{term}**:\n\n{definition}\n\n*Esempio:* {example}")
			embed = discord.Embed(title=" :notebook_with_decorative_cover: Dictionary :notebook_with_decorative_cover: ", colour=discord.Colour.green())
			embed.add_field(name="Definition", value=f"{definition}", inline=False)
			embed.add_field(name="Example", value=f"{example}", inline=False)
			embed.set_footer(text=footer_testo)
			await ctx.send(embed=embed)
		else:
			embed = discord.Embed(title="Error: No definitions found for the specified word or phrase", color=discord.Color.red())
			embed.set_footer(text=footer_testo)
			await ctx.send(embed=embed)
	else:
		embed = discord.Embed(title="Error: An error occurred while searching for the definition", color=discord.Color.red())
		embed.add_field(name="Please report the bug using:", value=f"</reportbug:{slash_reportbug_id}>", inline=True)
		embed.set_footer(text=footer_testo)
		await ctx.send(embed=embed)




#--Fun

@client.command()
@commands.guild_only()
@commands.cooldown(1, 5, commands.BucketType.user)
async def meme(ctx):
		link_list = [
			"https://www.reddit.com/r/memes/new.json",
			"https://www.reddit.com/r/dankmemes/new.json",
			"https://www.reddit.com/r/meme/new.json",
		]
		link = random.choice(link_list)
		embed = discord.Embed(title="Meme", color=discord.Colour.green())
		async with aiohttp.ClientSession() as cs:
			async with cs.get(link) as r:
				res = await r.json()
				n = int(len(res['data']['children']))
				embed.set_image(url=res['data']['children'][random.randint(0, n)]['data']['url'])
				embed.set_footer(text=footer_testo)  
				await ctx.send(embed=embed)




@client.command()
@commands.guild_only()
@commands.cooldown(1, 5, commands.BucketType.user)
async def casual(ctx):
	list1 = ["yes", "no"]
	r = random.choice(list1)
	embed = discord.Embed(title=f"{r}", color=discord.Color.blue())
	embed.set_footer(text=footer_testo)  
	await ctx.send(embed=embed)

@client.command()
@commands.guild_only()
@commands.cooldown(1, 5, commands.BucketType.user)
async def coinflip(ctx):
	coin = ['heads  :coin:','tails  :coin:']
	r = random.choice(coin)
	link = 'https://i.pinimg.com/originals/d7/49/06/d74906d39a1964e7d07555e7601b06ad.gif'
	#link = 'https://cdn-icons-png.flaticon.com/512/1540/1540515.png'
	embed = discord.Embed(title=f"It came up {r}", color=discord.Color.gold())
	embed.set_image(url=link)
	embed.set_footer(text=footer_testo)  
	await ctx.send(embed=embed)



@client.command()
@commands.guild_only()
@commands.cooldown(1, 5, commands.BucketType.user)
async def num_extractor(ctx):
	number = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
	r = random.choice(number)
	embed = discord.Embed(title=f"Is out", color=discord.Color.blue())
	embed.add_field(name = 'Number', value = f'{r}')
	embed.set_footer(text=footer_testo)  
	await ctx.send(embed=embed)


@commands.cooldown(1, 20, commands.BucketType.user)
@commands.guild_only()
@client.command()
async def generate_image(ctx, *, request: str):
	#ETA = int(time.time() + 60)
	embed = discord.Embed(title=f"Loading the image...", colour=discord.Color.blue())
	embed.set_footer(text=footer_testo)
	msg = await ctx.send(embed=embed)
	async with ctx.typing():
		try:
			seed = random.randint(1, 1000)
			image_url = f"https://image.pollinations.ai/prompt/{request}?seed={seed}"
			async with aiohttp.ClientSession() as session:
				async with session.get(image_url) as response:
					if response.status == 200:
						image_data = await response.read()
						image_io = io.BytesIO(image_data)
						await msg.delete()
						file = discord.File(image_io, "generatedImage.png")
						#file = discord.File(resp, "generatedImage.png")
						image_embed = discord.Embed(title=f"Request: ```{request}```", colour=discord.Color.green())
						image_embed.set_image(url="attachment://generatedImage.png")
						image_embed.set_footer(text=footer_testo)
						await ctx.send(file=file, embed=image_embed)
						#await ctx.send("Here's the generated image:", file=discord.File(image, "generatedImage.png"))
					else:
						response_text = await response.text()
						embed = discord.Embed(title="Error: Unknow", color=discord.Color.red())
						embed.set_footer(text=footer_testo)
						await ctx.send(embed=embed, delete_after=command_error_delete_after_time)
						#error-chat
						channel = client.get_channel(errorchannel)
						response_text = await response.text()
						embed = discord.Embed(title=f"**[Errore]** \nisinstance:\nText: {response_text}", color=discord.Color.red())
						await channel.send(embed=embed)
		except aiohttp.ContentTypeError as e:
				embed = discord.Embed(title="Error: Unknown", color=discord.Color.red())
				embed.set_footer(text=footer_testo)
				await ctx.send(embed=embed, delete_after=command_error_delete_after_time)
				#error-chat
				channel = client.get_channel(errorchannel)
				response_text = await response.text()
				embed = discord.Embed(title=f"**[Errore]** \nisinstance: ```{e}```\nerror: ```{str(e)}```\nText: {response_text}", color=discord.Color.red())
				await channel.send(embed=embed)
				errror_log(e,str(e),"generate_image command")


#--Slash

#------------Suggestion-------#
				

def random_txt(length):
	letters = string.ascii_letters
	result_str = ''.join(random.choice(letters) for i in range(length))
	return result_str





@client.tree.command(name="deny", description = "Deny a suggestion")
async def deny(interaction: discord.Interaction, id:str,response:str):
	if interaction.user.guild_permissions.manage_channels:
		await asyncio.sleep(0.5)
		with open(database_suggestion, 'r') as f:
			c_dati = json.load(f)
		id_c = str(interaction.channel.id)
		id_c_s_i = str(id)
		if id_c in c_dati:
			id_c_s = str(c_dati[id_c])
			if id_c_s_i in id_c_s:
				id_c_s_n = len(c_dati[id_c]["dati"])
				for i in range(id_c_s_n):
					if id_c_s_i in c_dati[id_c]["dati"][i]["id_c"]:
	
							vote_p = c_dati[id_c]["dati"][i]["pos"]
							vote_n = c_dati[id_c]["dati"][i]["neg"]
							title = c_dati[id_c]["dati"][i]["title"]
							sugg_user_id = c_dati[id_c]["dati"][i]["id_u"]
							id_m = c_dati[id_c]["dati"][i]["id_m"]
							ris_id = c_dati[id_c]["ris_channel"]
							channel_ris = client.get_channel(int(ris_id))
							user = await client.fetch_user(sugg_user_id)
							
							channel = client.get_channel(int(id_c))
							await channel.delete_messages([discord.Object(id=int(id_m))])
							
							embed_a = discord.Embed(title="**I denied that suggestion ❌**", color=discord.Color.red())
							await interaction.response.send_message(embed=embed_a, ephemeral=True)
				
							
							embed = discord.Embed(title=None, description=f"**Results:**\n**✅ = `{vote_p}`**\n**❌ = `{vote_n}`**\n\n**Submitter:**\n{user.mention}\n\n**Approved by:**\n{interaction.user.mention}\n\n**Title:**\n`{title}`\n\n**Response:**\n`{response}`", color=discord.Color.red())
							if not interaction.guild.icon == None:
								embed.set_author(name=interaction.guild.name, icon_url=interaction.guild.icon.url)
							embed.set_thumbnail(url=user.avatar)
							await channel_ris.send(embed=embed)
							del c_dati[id_c]["dati"][i]
							with open(database_suggestion, 'w') as f:
								json.dump(c_dati, f)
			else:
				embed_e2 = discord.Embed(title="Error: The selected suggestion does not exist", color=discord.Color.red())
				await interaction.response.send_message(embed=embed_e2,ephemeral=True)            
		else:
			embed_e1 = discord.Embed(title="Error: This channel does not have a recommendation system set up \n(try using the command in the channel where recommendations can be made)", color=discord.Color.red())
			await interaction.response.send_message(embed=embed_e1,ephemeral=True)
	else:
		embed = discord.Embed(title='Error: You need the permission to use this command `"manage channels"`', color=discord.Color.red())
		await interaction.response.send_message(embed=embed, ephemeral=True)
				 
	
	
@deny.autocomplete("id")
async def deny_autocomplete(interaction: discord.Interaction, current:str) -> typing.List[app_commands.Choice[str]]:
	with open(database_suggestion, 'r') as f:
		c_dati = json.load(f)
		
	id_c = str(interaction.channel.id)
	
	if id_c in c_dati:
		id_s = []
		id_c_s_n = len(c_dati[id_c]["dati"])
		for i in range(id_c_s_n):
			id_s_i = str(c_dati[id_c]["dati"][i]["id_c"])
			id_s.append(app_commands.Choice(name=id_s_i, value=id_s_i))
		return id_s
	else:
		id_s_i = None
		id_s.append(app_commands.Choice(name=id_s_i, value=id_s_i))
		return id_s_i
				
				
				
				


@client.tree.command(name="approve", description = "Approve a suggestion")
async def approve(interaction: discord.Interaction, id:str,response:str):
	if interaction.user.guild_permissions.manage_channels:
		with open(database_suggestion, 'r') as f:
			c_dati = json.load(f)
		id_c = str(interaction.channel.id)
		id_c_s_i = str(id)
		if id_c in c_dati:
			id_c_s = str(c_dati[id_c])
			if id_c_s_i in id_c_s:
				id_c_s_n = len(c_dati[id_c]["dati"])
				for i in range(id_c_s_n):
					if id_c_s_i in c_dati[id_c]["dati"][i]["id_c"]:
	
							vote_p = c_dati[id_c]["dati"][i]["pos"]
							vote_n = c_dati[id_c]["dati"][i]["neg"]
							title = c_dati[id_c]["dati"][i]["title"]
							sugg_user_id = c_dati[id_c]["dati"][i]["id_u"]
							id_m = c_dati[id_c]["dati"][i]["id_m"]
							ris_id = c_dati[id_c]["ris_channel"]
							channel_ris = client.get_channel(int(ris_id))
							user = await client.fetch_user(sugg_user_id)
							
							channel = client.get_channel(int(id_c))
							await channel.delete_messages([discord.Object(id=int(id_m))])
							
							embed_a = discord.Embed(title="**I approved that suggestion ✅**", color=discord.Color.green())
							await interaction.response.send_message(embed=embed_a, ephemeral=True)
				
							
							embed = discord.Embed(title=None, description=f"**Results:**\n**✅ = `{vote_p}`**\n**❌ = `{vote_n}`**\n\n**Submitter:**\n{user.mention}\n\n**Approved by:**\n{interaction.user.mention}\n\n**Title:**\n`{title}`\n\n**Response:**\n`{response}`", color=discord.Color.green())
							if not interaction.guild.icon == None:
								embed.set_author(name=interaction.guild.name, icon_url=interaction.guild.icon.url)
							embed.set_thumbnail(url=user.avatar)
							await channel_ris.send(embed=embed)
							del c_dati[id_c]["dati"][i]
							with open(database_suggestion, 'w') as f:
								json.dump(c_dati, f)
			else:
				embed_e2 = discord.Embed(title="Error: The selected suggestion does not exist", color=discord.Color.red())
				await interaction.response.send_message(embed=embed_e2,ephemeral=True)            
		else:
			embed_e1 = discord.Embed(title="Error: This channel does not have a recommendation system set up \n(try using the command in the channel where recommendations can be made)", color=discord.Color.red())
			await interaction.response.send_message(embed=embed_e1,ephemeral=True)
	else:
		embed = discord.Embed(title='Error: You need the permission to use this command `"manage channels"`', color=discord.Color.red())
		await interaction.response.send_message(embed=embed, ephemeral=True)
				 
	
	
@approve.autocomplete("id")
async def approve_autocomplete(interaction: discord.Interaction, current:str) -> typing.List[app_commands.Choice[str]]:
	with open(database_suggestion, 'r') as f:
		c_dati = json.load(f)
		
	id_c = str(interaction.channel.id)
	
	if id_c in c_dati:
		id_s = []
		id_c_s_n = len(c_dati[id_c]["dati"])
		for i in range(id_c_s_n):
			id_s_i = str(c_dati[id_c]["dati"][i]["id_c"])
			id_s.append(app_commands.Choice(name=id_s_i, value=id_s_i))
		return id_s
	else:
		id_s_i = None
		id_s.append(app_commands.Choice(name=id_s_i, value=id_s_i))
		return id_s_i
				
					


@client.tree.command(name="suggest", description = "Create a suggestion in this channel")
async def suggest(interaction: discord.Interaction, suggestion:str):
	with open(database_suggestion, 'r') as f:
		c_dati = json.load(f)
	if str(interaction.channel.id) in c_dati: 
		title=suggestion
		id_suggestion = random_txt(10)
		channel_id = interaction.channel.id
		user_id = interaction.user.id

		embed = discord.Embed(title=f"**Submitter:**\n`{interaction.user.name}`\n\n**Suggestion:**\n`{title}`\n\n**Suggestion votes:**\n**✅ = `0`**\n**❌ = `0`**", color=discord.Color.dark_gold())
		embed.set_thumbnail(url=interaction.user.avatar)
		embed.set_footer(text=f"Suggestion id: {id_suggestion}")
		message = await interaction.channel.send(embed=embed, view=Suggestion_Button())
		await message.create_thread(name=f"{interaction.user.display_name} Suggestion",reason=f"Opening of {interaction.user.display_name} Suggestion thread")
		id_message = message.id
		
		embed = discord.Embed(title="**I created your suggestion**", color=discord.Color.green())
		await interaction.response.send_message(embed=embed, ephemeral=True)
		

		new_data = {
			"id_c": f"{id_suggestion}",
			"id_m": f"{id_message}",
			"id_u": f"{user_id}",
			"title": f"{title}",
			"p_pos": [],
			"p_neg": [],
			"pos": 0,
			"neg": 0
			}
		
		c_dati[str(channel_id)]["dati"].append(new_data)

		with open(database_suggestion, 'w') as f:
			json.dump(c_dati, f)
	else:
		embed_r = discord.Embed(title="Error: This channel does not have a Suggestion System", color=discord.Color.red())
		await interaction.response.send_message(embed=embed_r,ephemeral=True)




class Suggestion_Button(discord.ui.View):
	def __init__(self):
		super().__init__(timeout=None)

	@discord.ui.button(label=None, emoji="✅", style=discord.ButtonStyle.green, custom_id='persistant_button:suggestion_up')
	async def suggestion_up(self, interaction: discord.Interaction, button: discord.ui.Button):
		with open(database_suggestion, 'r') as f:
			c_dati = json.load(f)

		id_c = str(interaction.channel.id)
		id_m = str(interaction.message.id) 
		if id_c in c_dati:
			id_c_s_n = len(c_dati[id_c]["dati"])
			id_c_s = str(c_dati[id_c])
			if id_m in id_c_s:
				for i in range(id_c_s_n):
					if id_m in c_dati[id_c]["dati"][i]["id_m"]:
						id_s = c_dati[id_c]["dati"][i]


						user = str(interaction.user.id)
						if str(interaction.user.id) in id_s["p_pos"]:
							embed = discord.Embed(title="**You have already voted**", color=discord.Color.red())
							await interaction.response.send_message(embed=embed, ephemeral=True)
							return
						if str(interaction.user.id) in id_s["p_neg"]:
							id_s["p_neg"].remove(user)
							id_s["p_pos"].append(user)

							embed = discord.Embed(title="**I changed your vote to positive for the suggestion ✅**", color=discord.Color.green())
							await interaction.response.send_message(embed=embed, ephemeral=True)
							await asyncio.sleep(timeout_time_suggestion)
							id_m = id_s["id_m"]
							id_c = id_s["id_c"]
							id_u = id_s["id_u"]

							titolo = id_s["title"]

							pos = id_s["pos"]
							neg = id_s["neg"]

							pos_int = int(pos) + 1
							id_s["pos"] = pos_int
							pos_str = str(pos_int)

							neg_int = int(neg) - 1
							id_s["neg"] = neg_int  
							neg_str = str(neg_int)

							id_suggestion = str(id_c)
							title = str(titolo)
							user = await client.fetch_user(id_u)
							embed = discord.Embed(title=f"**Submitter:**\n`{user.name}`\n\n**Suggestion:**\n`{title}`\n\n**Suggestion votes:**\n**✅ = `{pos_str}`**\n**❌ = `{neg_str}`**", color=discord.Color.dark_gold())
							embed.set_thumbnail(url=user.avatar)
							embed.set_footer(text=f"Suggestion id: {id_suggestion}")
							await interaction.message.edit(embed=embed)
							with open(database_suggestion, 'w') as f:
								json.dump(c_dati, f)    
						else:
							id_s["p_pos"].append(user)
							embed = discord.Embed(title="**I upvoted the suggestion ✅**", color=discord.Color.green())
							await interaction.response.send_message(embed=embed, ephemeral=True)
							await asyncio.sleep(timeout_time_suggestion)
							id_m = id_s["id_m"]
							id_c = id_s["id_c"]
							id_u = id_s["id_u"]
							titolo = id_s["title"]
							pos = id_s["pos"]
							neg = id_s["neg"]
							pos_int = int(pos) + 1
							id_s["pos"] = pos_int
							pos_str = str(pos_int)
							neg_str = str(neg)

							id_suggestion = str(id_c)
							title = str(titolo)
							user = await client.fetch_user(id_u)
							embed = discord.Embed(title=f"**Submitter:**\n`{user.name}`\n\n**Suggestion:**\n`{title}`\n\n**Suggestion votes:**\n**✅ = `{pos_str}`**\n**❌ = `{neg_str}`**", color=discord.Color.dark_gold())
							embed.set_thumbnail(url=user.avatar)
							embed.set_footer(text=f"Suggestion id: {id_suggestion}")
							await interaction.message.edit(embed=embed)
							with open(database_suggestion, 'w') as f:
								json.dump(c_dati, f)
			else:
				embed = discord.Embed(title="Error: The id of this suggestion is missing from the database\n`deleting the suggestion...`", color=discord.Color.red())
				await interaction.response.send_message(embed=embed, ephemeral=True)
				await interaction.message.delete()
				print("Error: Missing the id of the suggestion in the database")
			
		else:
			embed = discord.Embed(title="Error: The channel is not in the database\n`deleting the suggestion...`", color=discord.Color.red())
			await interaction.response.send_message(embed=embed, ephemeral=True)
			await interaction.message.delete()
			print("Error: The channel is not in the database")


	@discord.ui.button(label=None, emoji="✖️", style=discord.ButtonStyle.red, custom_id='persistant_button:suggestion_down')
	async def suggestion_down(self, interaction: discord.Interaction, button: discord.ui.Button):
		with open(database_suggestion, 'r') as f:
			c_dati = json.load(f)

		id_c = str(interaction.channel.id)
		id_m = str(interaction.message.id)
		if id_c in c_dati:
			id_c_s_n = len(c_dati[id_c]["dati"])
			id_c_s = str(c_dati[id_c])
			if id_m in id_c_s:
				for i in range(id_c_s_n):
					if id_m in c_dati[id_c]["dati"][i]["id_m"]:
						id_s = c_dati[id_c]["dati"][i]

						user = str(interaction.user.id)
						if str(interaction.user.id) in id_s["p_neg"]:
							embed = discord.Embed(title="**You have already voted**", color=discord.Color.red())
							await interaction.response.send_message(embed=embed, ephemeral=True)
							return
						if str(interaction.user.id) in id_s["p_pos"]:
							id_s["p_pos"].remove(user)
							id_s["p_neg"].append(user)
							embed = discord.Embed(title="**I changed your vote to negative for the suggestion ❌**", color=discord.Color.red())
							await interaction.response.send_message(embed=embed, ephemeral=True)
							await asyncio.sleep(timeout_time_suggestion)
							id_m = id_s["id_m"]
							id_c = id_s["id_c"]
							id_u = id_s["id_u"]

							titolo = id_s["title"]

							pos = id_s["pos"]
							neg = id_s["neg"]

							pos_int = int(pos) - 1
							id_s["pos"] = pos_int
							pos_str = str(pos_int)

							neg_int = int(neg) + 1
							id_s["neg"] = neg_int  
							neg_str = str(neg_int)

							id_suggestion = str(id_c)
							title = str(titolo)
							user = await client.fetch_user(id_u)
							embed = discord.Embed(title=f"**Submitter:**\n`{user.name}`\n\n**Suggestion:**\n`{title}`\n\n**Suggestion votes:**\n**✅ = `{pos_str}`**\n**❌ = `{neg_str}`**", color=discord.Color.dark_gold())
							embed.set_thumbnail(url=user.avatar)
							embed.set_footer(text=f"Suggestion id: {id_suggestion}")
							await interaction.message.edit(embed=embed)
							with open(database_suggestion, 'w') as f:
								json.dump(c_dati, f)    
						else:
							id_s["p_neg"].append(user)
							embed = discord.Embed(title="**I downvoted the suggestion ❌**", color=discord.Color.red())
							await interaction.response.send_message(embed=embed, ephemeral=True)
							await asyncio.sleep(timeout_time_suggestion)
							id_m = id_s["id_m"]
							id_c = id_s["id_c"]
							id_u = id_s["id_u"]

							titolo = id_s["title"]

							pos = id_s["pos"]
							neg = id_s["neg"]

							neg_int = int(neg) + 1
							id_s["neg"] = neg_int
							neg_str = str(neg_int)
							pos_str = str(pos)

							id_suggestion = str(id_c)
							title = str(titolo)
							user = await client.fetch_user(id_u)
							embed = discord.Embed(title=f"**Submitter:**\n`{user.name}`\n\n**Suggestion:**\n`{title}`\n\n**Suggestion votes:**\n**✅ = `{pos_str}`**\n**❌ = `{neg_str}`**", color=discord.Color.dark_gold())
							embed.set_thumbnail(url=user.avatar)
							embed.set_footer(text=f"Suggestion id: {id_suggestion}")
							await interaction.message.edit(embed=embed)
							with open(database_suggestion, 'w') as f:
								json.dump(c_dati, f)
			else:
				embed = discord.Embed(title="Error: The id of this suggestion is missing from the database\n`deleting the suggestion...`", color=discord.Color.red())
				await interaction.response.send_message(embed=embed, ephemeral=True)
				await interaction.message.delete()
				print("Error: Missing the id of the suggestion in the database")
		else:
			embed = discord.Embed(title="Error: The channel is not in the database\n`deleting the suggestion...`", color=discord.Color.red())
			await interaction.response.send_message(embed=embed, ephemeral=True)
			await interaction.message.delete()
			print("Error: The channel is not in the database")


@client.tree.command(name="suggestion_setup_add", description = "Add the Suggestion System to this server")
async def suggestion_setup_add(interaction: discord.Interaction, suggestion_channel:discord.TextChannel,result_channel: discord.TextChannel):
	if interaction.user.guild_permissions.manage_channels:
		with open(database_suggestion, 'r') as f:
			c_dati = json.load(f)
			
		channel_id = str(suggestion_channel.id)
		
		if channel_id in c_dati:
			embed_r = discord.Embed(title="Error: This channel has already been set up to propose suggestions/surveys", color=discord.Color.red())
			await interaction.response.send_message(embed=embed_r,ephemeral=True)
		else:
			new_data = {
				"ris_channel": f"{result_channel.id}",
				"dati": []
				}
			c_dati[channel_id] = new_data
			
			with open(database_suggestion, 'w') as f:
				json.dump(c_dati, f)
				
			embed_r = discord.Embed(title=f"**I have set up this channel: {suggestion_channel.mention} to propose suggestions/surveys and this channel: {result_channel.mention} to get the result of the suggestions/surveys**", color=discord.Color.green())
			await interaction.response.send_message(embed=embed_r,ephemeral=True)
			
			if result_channel.id == suggestion_channel.id:
				embed = discord.Embed(title="**This channel has been set up to propose suggestions/surveys and receive their results**", color=discord.Color.blurple())
				await suggestion_channel.send(embed=embed)
			else:
				embed = discord.Embed(title="**This channel has been set up to propose suggestions/surveys**", color=discord.Color.blurple())
				await suggestion_channel.send(embed=embed)
				embed_p = discord.Embed(title="**This channel has been set up to receive suggestions/surveys results**", color=discord.Color.blurple())
				await result_channel.send(embed=embed_p)
	else:
		embed = discord.Embed(title='Error: You need the permission to use this command `"manage channels"`', color=discord.Color.red())
		await interaction.response.send_message(embed=embed, ephemeral=True)



@client.tree.command(name="suggestion_setup_remove", description = "Remove the Suggestion System from this channel")
async def suggestion_setup_remove(interaction: discord.Interaction):
	if interaction.user.guild_permissions.manage_channels:

		with open(database_suggestion, 'r') as f:
			c_dati = json.load(f)
			
		channel_id = str(interaction.channel.id)
		if channel_id in c_dati:
			
			res_id = c_dati[channel_id]["ris_channel"] #res id data
			res_id_i = int(res_id)
			if channel_id == res_id_i:
				
				del c_dati[channel_id] #delete data

				with open(database_suggestion, 'w') as f:
					json.dump(c_dati, f) #load data
					
				def check_sug(msg):
					return msg.author == client.user
				await interaction.channel.purge(limit=100, check=check_sug)

				embed = discord.Embed(title="I deleted the Suggestion System from this channel", color=discord.Color.green())
				await interaction.response.send_message(embed=embed,ephemeral=True)   
			else:
				res_id_c = client.get_channel(res_id_i)
				
				del c_dati[channel_id] #delete data

				with open(database_suggestion, 'w') as f:
					json.dump(c_dati, f) #load data
					
				def check_sug(msg):
					return msg.author == client.user
				await interaction.channel.purge(limit=100, check=check_sug)

				def check_res(msg):
					return msg.author == client.user
				await res_id_c.purge(limit=100, check=check_res)


				embed = discord.Embed(title="I deleted the Suggestion System from this channel", color=discord.Color.green())
				await interaction.response.send_message(embed=embed,ephemeral=True)

		else:
			embed_r = discord.Embed(title="Error: This channel does not have a Suggestion System", color=discord.Color.red())
			await interaction.response.send_message(embed=embed_r,ephemeral=True)

	else:  
		embed = discord.Embed(title='Error: You need the permission to use this command `"manage channels"`', color=discord.Color.red())
		await interaction.response.send_message(embed=embed, ephemeral=True)



#------------Verify-------#


class CaptchaModal(ui.Modal, title='Captcha'):
	captcha_t = ui.TextInput(label='Captcha',required=True, max_length=6)

	async def on_submit(self, interaction: discord.Interaction):

		with open(database_verify, 'r') as f:
			dati = json.load(f)

		ser_id = str(interaction.guild.id)
		ro_id = int(dati[ser_id]["r_id"])

		global captcha_text
		text = captcha_text

		response_min = str(self.children[0].value)
		response = str(response_min.upper())
	
		captcha_text = None
		if response == text:
			c_embed = discord.Embed(title=" :white_check_mark: Correct CAPTCHA :white_check_mark: ", colour=discord.Color.green())
			await interaction.response.send_message(embed=c_embed, ephemeral=True)
			await asyncio.sleep(1)
			if discord.utils.get(interaction.guild.roles, id=ro_id):
				if not discord.utils.get(interaction.guild.roles, id=ro_id) in interaction.user.roles:
					role = discord.utils.get(interaction.guild.roles, id=ro_id)
					await interaction.user.add_roles(role)
				else:
					error1_embed = discord.Embed(title="Error: Unknown", color=discord.Color.red())
					error1_embed.add_field(name="Please report the bug using:", value=f"</reportbug:{slash_reportbug_id}>", inline=True)
					await interaction.edit_original_response(embed=error1_embed)
			else:
				error1_embed = discord.Embed(title="Error: Unknown", color=discord.Color.red())
				error1_embed.add_field(name="Please report the bug using:", value=f"</reportbug:{slash_reportbug_id}>", inline=True)
				await interaction.edit_original_response(embed=error1_embed)
		else:
			w_embed = discord.Embed(title=" :x: Wrong CAPTCHA :x: ", colour=discord.Color.red())
			await interaction.response.send_message(embed=w_embed, ephemeral=True)




class Captcha_Button(discord.ui.View):
	def __init__(self,data):
		self.data = data
		super().__init__(timeout=None)

	@discord.ui.button(label=None, emoji="🖋️", style=discord.ButtonStyle.blurple, custom_id="persistant_button:captcha_open")
	async def Captcha(self, interaction: discord.Interaction, button: discord.ui.Button):
		data = self.data
		global captcha_text
		if not captcha_text == data or captcha_text == None:
			#button.disabled = True
			embed=discord.Embed(title=":x: You have already answered the captcha :x:", color=discord.Color.red())
			#await interaction.message.edit(embed=embed,view=self)
			await interaction.response.edit_message(embed=embed, view=None,attachments=[])
		else:
			await interaction.response.send_modal(CaptchaModal())
	

		



class Open_Verify(discord.ui.Button):
	def __init__(self,label):
		super().__init__(label=label, emoji="✅", style=discord.ButtonStyle.green, custom_id="persistant_button:verify_open")
		
	async def callback(self, interaction: discord.Interaction):
		
		with open(database_verify, 'r') as f:
			dati = json.load(f)

		ser_id = str(interaction.guild.id)
		ch_id = str(interaction.channel.id)

		if not ser_id in dati:
			embed=discord.Embed(title="Error: The server has not been set up to have a verification system\n`deleting the message...`", color=discord.Color.red())
			await interaction.response.send_message(embed=embed, ephemeral=True)
			print("Error: Database Verify error")
			await asyncio.sleep(5)
			await interaction.message.delete()
		else:
			if not ch_id in str(dati):
				embed=discord.Embed(title="Error: The channel has not been set up to have a verification system\n`deleting the message...`", color=discord.Color.red())
				await interaction.response.send_message(embed=embed, ephemeral=True)
				print("Error: Database Verify error")
				await asyncio.sleep(5)
				await interaction.message.delete()
			else:
				if not discord.utils.get(interaction.guild.roles, name="verify"):
					if interaction.user.guild_permissions.manage_roles or interaction.user.guild_permissions.administrator:
						embed=discord.Embed(title="Error: This server does not have the role to perform the verification, to solve the problem remove the verification system and then put it back\n`deleting the message...`", color=discord.Color.red())
						await interaction.response.send_message(embed=embed, ephemeral=True)
						print("Error: Missing role")
						await asyncio.sleep(5)
						await interaction.message.delete()
					else:
						embed=discord.Embed(title="Error: This server does not have the role to perform the verification\n`deleting the message...`", color=discord.Color.red())
						await interaction.response.send_message(embed=embed, ephemeral=True)
						print("Error: Missing role")
						await asyncio.sleep(5)
						await interaction.message.delete()

				if discord.utils.get(interaction.guild.roles, name="verify") in interaction.user.roles:
					v_e_embed = discord.Embed(title=" :x: You have already been verified :x: ", colour=discord.Color.red())
					await interaction.response.send_message(embed=v_e_embed, ephemeral=True)
					return
				else:
					image = Image.new('RGB', (350, 100), (255, 255, 255))
					draw = ImageDraw.Draw(image)
					text = random.choice(["J3PKL2", "8QGT2V", "T3FWR6", "VF7NY2", "UPA2XZ", "I5CYWJ", "BVT6NC"])
					font = ImageFont.truetype("captcha.ttf", 60)
					draw.text((80, 25), text, font=font, fill=(0, 0, 0))
					buffer = io.BytesIO()
					image.save(buffer, format='PNG')
					buffer.seek(0)
					file = discord.File(buffer, filename='captcha.png')
					#file = discord.File(resp, "generatedImage.png")
					image_embed = discord.Embed(title=" :robot: Captcha :white_check_mark: ", colour=discord.Color.green())
					image_embed.add_field(name=" :warning: Warning :warning: ", value="Write the characters in the image\nPress the button to reply", inline=True)
					image_embed.set_image(url="attachment://captcha.png")
					global captcha_text
					captcha_text = text

					await interaction.response.send_message(file=file, embed=image_embed,view=Captcha_Button(text),ephemeral=True)



			




class VerifyModal(ui.Modal, title='Verify Setup'):
	title_name = ui.TextInput(label='Message Title',required=True,placeholder='Message title...', max_length=50)
	description_name = ui.TextInput(label='Message Description',required=True, style=discord.TextStyle.paragraph, max_length=300,placeholder='Message Description...')
	button_name = ui.TextInput(label='Captcha Button Text',required=True, placeholder='Button Text...', max_length=50)

	async def on_submit(self, interaction: discord.Interaction):

		ch_id = str(interaction.channel.id)
		ser_id = str(interaction.guild.id)

		with open(database_verify, 'r') as f:
			dati = json.load(f)

		if ser_id in dati:
			embed = discord.Embed(title="Error: You have already set up the verification system on this server",color=discord.Color.red())
			interaction.response.send_message(embed=embed, ephemeral=True)
		else:
			if not ch_id in str(dati):
				if discord.utils.get(interaction.guild.roles, name="verify"):
					permissions = discord.Permissions(send_messages=True, read_messages=True) #da-cambiare
					role = discord.utils.get(interaction.guild.roles, name="verify")
					try:
						await role.edit(reason=None,permissions=permissions)
					except:
						pass

					#database
					data = {
						"v_channel":f"{ch_id}",
						"r_id":f"{role.id}"
						}
				
					dati[str(ser_id)] = data

					with open(database_verify, 'w') as f:
						json.dump(dati, f)

					
					embed_m_f=discord.Embed(title="I have set up the Verify System in this server", color=discord.Color.green())
					await interaction.response.send_message(embed=embed_m_f, ephemeral=True)

					await asyncio.sleep(0.5)

					try:
						await interaction.channel.set_permissions(client.user,overwrite=discord.PermissionOverwrite(view_channel=True))
					except:
						pass

					#set role
					for category in interaction.guild.categories:
						overwrites = category.overwrites_for(interaction.guild.default_role)
						if overwrites.is_empty() or overwrites.view_channel is None or overwrites.view_channel:
							role_overwrites = category.overwrites_for(role)
							role_overwrites.view_channel = True
							await category.set_permissions(role, overwrite=role_overwrites)
							everyone_overwrites = category.overwrites_for(interaction.guild.default_role)
							everyone_overwrites.view_channel = False
							await category.set_permissions(interaction.guild.default_role, overwrite=everyone_overwrites)
							
					for channel in interaction.guild.channels:
						overwrites = channel.overwrites_for(interaction.guild.default_role)
						if overwrites.is_empty() or overwrites.view_channel is None or overwrites.view_channel:
							role_overwrites = channel.overwrites_for(role)
							role_overwrites.view_channel = True
							await channel.set_permissions(role, overwrite=role_overwrites)
							everyone_overwrites = channel.overwrites_for(interaction.guild.default_role)
							everyone_overwrites.view_channel = False
							await channel.set_permissions(interaction.guild.default_role, overwrite=everyone_overwrites)
							#verify_channel can be seen
							channel_v = interaction.channel
							role_v_e = discord.utils.get(interaction.guild.roles, name="@everyone")
							role_v_v = discord.utils.get(interaction.guild.roles, name="verify")
							permissions_v_e = discord.PermissionOverwrite(view_channel=True)
							permissions_v_v = discord.PermissionOverwrite(view_channel=False)
							await channel_v.set_permissions(role_v_e, overwrite=permissions_v_e)
							await channel_v.set_permissions(role_v_v, overwrite=permissions_v_v)
					

					#message visible
					channel = interaction.channel
					embed_ex = discord.Embed(title=f"{self.children[0].value}",description=f"{self.children[1].value}", color=discord.Color.green())
					
					label = str(self.children[2].value)
					view = discord.ui.View(timeout=None)

					view.add_item(Open_Verify(label))
		
					await channel.send(embed=embed_ex,view=view)

				else:
					permissions = discord.Permissions(send_messages=True, read_messages=True) #da-cambiare
					guild = interaction.guild
					await guild.create_role(name="verify", colour=discord.Colour(0x00ff00), permissions=permissions)
					role = discord.utils.get(interaction.guild.roles, name="verify")

					#database
					data = {
						"v_channel":f"{ch_id}",
						"r_id":f"{role.id}"
						}
				
					dati[str(ser_id)] = data

					with open(database_verify, 'w') as f:
						json.dump(dati, f)


					embed_m_f=discord.Embed(title="I have set up the Verify System in this server", color=discord.Color.green())
					await interaction.response.send_message(embed=embed_m_f, ephemeral=True)

					await asyncio.sleep(0.5)


					try:
						await interaction.channel.set_permissions(client.user,overwrite=discord.PermissionOverwrite(view_channel=True))
					except:
						pass

					#set role
					for category in interaction.guild.categories:
						overwrites = category.overwrites_for(interaction.guild.default_role)
						if overwrites.is_empty() or overwrites.view_channel is None or overwrites.view_channel:
							role_overwrites = category.overwrites_for(role)
							role_overwrites.view_channel = True
							await category.set_permissions(role, overwrite=role_overwrites)
							everyone_overwrites = category.overwrites_for(interaction.guild.default_role)
							everyone_overwrites.view_channel = False
							await category.set_permissions(interaction.guild.default_role, overwrite=everyone_overwrites)
							
					for channel in interaction.guild.channels:
						overwrites = channel.overwrites_for(interaction.guild.default_role)
						if overwrites.is_empty() or overwrites.view_channel is None or overwrites.view_channel:
							role_overwrites = channel.overwrites_for(role)
							role_overwrites.view_channel = True
							await channel.set_permissions(role, overwrite=role_overwrites)
							everyone_overwrites = channel.overwrites_for(interaction.guild.default_role)
							everyone_overwrites.view_channel = False
							await channel.set_permissions(interaction.guild.default_role, overwrite=everyone_overwrites)
							#verify_channel can be seen
							channel_v = interaction.channel
							role_v_e = discord.utils.get(interaction.guild.roles, name="@everyone")
							role_v_v = discord.utils.get(interaction.guild.roles, name="verify")
							permissions_v_e = discord.PermissionOverwrite(view_channel=True)
							permissions_v_v = discord.PermissionOverwrite(view_channel=False)
							await channel_v.set_permissions(role_v_e, overwrite=permissions_v_e)
							await channel_v.set_permissions(role_v_v, overwrite=permissions_v_v)


					#message visible
					channel = interaction.channel
					embed_ex = discord.Embed(title=f"{self.children[0].value}",description=f"{self.children[1].value}", color=discord.Color.green())
					
					label = str(self.children[2].value)
					view = discord.ui.View(timeout=None)

					view.add_item(Open_Verify(label))
		
					await channel.send(embed=embed_ex,view=view)





class Verify_Button(discord.ui.View):
	def __init__(self):
		super().__init__()
		self.value = None

	@discord.ui.button(label="Add", emoji="➕", style=discord.ButtonStyle.green)
	async def Ticket_add(self, interaction: discord.Interaction, button: discord.ui.Button):
		s_id = interaction.guild.id
		with open(database_verify, 'r') as f:
			servers = json.load(f)
		if not str(s_id) in servers:
			await interaction.response.send_modal(VerifyModal())
		else:
			embed = discord.Embed(title=f'The ticket system has already been set up in this channel', color=discord.Color.red())
			await interaction.response.send_message(embed=embed, ephemeral=True)

	@discord.ui.button(label="Remove",emoji="➖", style=discord.ButtonStyle.red)
	async def Ticket_remove(self, interaction: discord.Interaction, button: discord.ui.Button):


		s_id = interaction.guild.id
		with open(database_verify, 'r') as f:
			servers = json.load(f)
		if str(s_id) in servers:
			role_id = int(servers[str(s_id)]["r_id"])


			if discord.utils.get(interaction.guild.roles, id=role_id):


				embed = discord.Embed(title='The ticket system has been removed from this channel', color=discord.Color.red())
				await interaction.response.send_message(embed=embed, ephemeral=True)
				#channel - restore
				try:
					for channel in interaction.guild.channels:

						role_ver = discord.utils.get(interaction.guild.roles, id=role_id)

						overwrite_role = channel.overwrites_for(role_ver)
						if overwrite_role.view_channel == True:
							await channel.set_permissions(interaction.guild.default_role, view_channel=True)

					role = discord.utils.get(interaction.guild.roles, id=role_id)
					await role.delete()
				except:
					pass

			channel_id = servers[str(s_id)]["v_channel"]
			channel = client.get_channel(int(channel_id))

			del servers[str(s_id)]

			with open(database_verify, 'w') as f:
				json.dump(servers, f)

			def check(msg):
				return msg.author == client.user
	
			await channel.purge(limit=30, check=check)
		else:
			embed = discord.Embed(title=f'The ticket system has not been set up in this channel', color=discord.Color.red())
			await interaction.response.send_message(embed=embed, ephemeral=True)



@client.tree.command(name="verifysetup", description = "Set up the system for verification on the server") #slash command
async def verifysetup(interaction: discord.Interaction):
	if interaction.user.guild_permissions.manage_roles or interaction.user.guild_permissions.administrator:
		embed = discord.Embed(title="Setup Verify", color=discord.Color.blue())
		embed.add_field(name="Press the green button to add the verification system from this channel", value=":green_circle:",inline=True)
		embed.add_field(name="Press the red button to remove the verification system from this server", value=":red_circle:",inline=False)
		await interaction.response.send_message(embed=embed, ephemeral=True, view=Verify_Button())
	else:
		embed = discord.Embed(title='Error: You need the permission to use this command `"manage roles"`', color=discord.Color.red())
		await interaction.response.send_message(embed=embed, ephemeral=True)

#-------------Ui----------#


#-ReportBug

class BugModal(ui.Modal, title='Report Bug'):
	bug_name = ui.TextInput(label='Bugged Command name',required=True,placeholder='Bugged command name...', max_length=50)
	#options = [discord.SelectOption(label='Option 1', value='1'), discord.SelectOption(label='Option 2', value='2')]
	#type_of_bug = ui.Select(placeholder="Bug Type", min_values=1, max_values=1, options=options)
	answer = ui.TextInput(label='Description of the bug', style=discord.TextStyle.paragraph, max_length=300,placeholder='Bug description...')

	async def on_submit(self, interaction: discord.Interaction):
		channel = client.get_channel(reportbugchannel)
		embed = discord.Embed(title=":bug: Bug report :bug:")
		embed.add_field(name="Bugged Command name", value=self.children[0].value)
		#embed.add_field(name="Type of bug", value=self.children[1].value)
		embed.add_field(name="Description of the bug", value=self.children[1].value)
		embed.add_field(name="User:", value=f"`{interaction.user}`")
		await channel.send(embed=embed)
		embed1 = discord.Embed(title="Bug report sent", color=discord.Color.green())
		embed1.set_footer(text=footer_testo)
		await interaction.response.send_message(embed=embed1, ephemeral=True)




#----Help
		
class HelpDropdownView(discord.ui.View):
	def __init__(self):
		super().__init__()
		self.add_item(HelpDropdown())
		
class HelpDropdown(discord.ui.Select):
	def __init__(self):
		options = [
			discord.SelectOption(label='Mod Commands', emoji='🔐'),
			discord.SelectOption(label='Utilty Commands', emoji='📉'),
			discord.SelectOption(label='Fun Commands', emoji='🎉'),
			discord.SelectOption(label='Slash Commands', emoji='💻')
			]
		
		super().__init__(placeholder='Choose help section...', min_values=1, max_values=1, options=options)

	async def callback(self, interaction: discord.Interaction):
		if self.values[0] == "Mod Commands":
			embed = discord.Embed(title="Mod Commands :closed_lock_with_key:", color=discord.Color.gold())
			embed.add_field(name=f"{prefix}nuke", value=f"Delete messages in the chat where it is used", inline=True)
			embed.add_field(name=f"{prefix}kick `user_id` `reason`", value=f"Kick a member from the server", inline=True)
			embed.add_field(name=f"{prefix}ban `user_id` `reason`", value=f"Ban a member from the server", inline=True)
			embed.add_field(name=f"{prefix}unban `user_id`", value=f"Unban a member from the server", inline=True)
			embed.add_field(name=f"{prefix}delchannel", value=f"Delete all channel", inline=True)
			embed.add_field(name=f"{prefix}lockdown", value=f"Lockdown the channel", inline=True)
			embed.add_field(name=f"{prefix}unlock", value=f"Unlock the channel", inline=True)
			embed.add_field(name=f"{prefix}mute `user_id`", value=f"Mute a member", inline=True)
			embed.add_field(name=f"{prefix}unmute `user_id`", value=f"Unmute a member", inline=True)
			embed.add_field(name=f"{prefix}slowmode `seconds`", value=f"Set the slowmode of the channel", inline=True)
			embed.set_footer(text=footer_testo)
			await interaction.response.send_message(embed=embed, ephemeral=True)
		elif self.values[0] == "Utilty Commands":
			embed = discord.Embed(title="Utilty :chart_with_downwards_trend:", color=discord.Color.green())
			embed.add_field(name=f"{prefix}infobot", value="Send the bot stats (cpu, memory, ping)", inline=True)
			embed.add_field(name=f"{prefix}serverinfo", value="Send the Server info", inline=True)
			embed.add_field(name=f"{prefix}userinfo `user_id`", value="Send the User info", inline=True)
			embed.add_field(name=f"{prefix}translate `language` `text`", value="Translates text into any supported language", inline=True)
			embed.add_field(name=f"{prefix}custom_emoji_info `custom_emoji`", value="Tells you the information of a custom emoji", inline=True)
			embed.add_field(name=f"{prefix}dictionary `word`", value="Tells you the meaning of a word", inline=True)
			embed.set_footer(text=footer_testo)
			await interaction.response.send_message(embed=embed, ephemeral=True)
		elif self.values[0] == "Fun Commands":
			embed = discord.Embed(title="Fun Commands :tada:", color=discord.Color.blurple())
			embed.add_field(name=f"{prefix}meme", value="Send a random meme", inline=True)
			embed.add_field(name=f"{prefix}casual", value="Extracts Yes or No", inline=True)
			embed.add_field(name=f"{prefix}coinflip", value="Extracts heads or tails", inline=True)
			embed.add_field(name=f"{prefix}num_extractor", value="Extracts a number from 1 to 10", inline=True)
			embed.add_field(name=f"{prefix}generate_image `request`", value="Generate an image", inline=True)
			embed.set_footer(text=footer_testo)
			await interaction.response.send_message(embed=embed, ephemeral=True)
		elif self.values[0] == "Slash Commands":
			embed1 = discord.Embed(title="Slash Commands :computer:", color=discord.Color.light_grey())
			
			embed2 = discord.Embed(title="Suggestion System :page_with_curl:", color=discord.Color.dark_gold())
			embed2.add_field(name=f"</suggestion_setup_add:{slash_suggestionsetupadd_id}>", value="This command is used to create a suggestion system", inline=True)
			embed2.add_field(name=f"</suggestion_setup_remove:{slash_suggestionsetupremove_id}>", value="This command is used to remove a suggestion system", inline=True)
			embed2.add_field(name=f"</suggest:{slash_suggest_id}>", value="Makes a suggestion", inline=True)
			embed2.add_field(name=f"</approve:{slash_approve_id}>", value="Approve a suggestion", inline=True)
			embed2.add_field(name=f"</deny:{slash_deny_id}>", value="Reject a suggestion", inline=True)

			embed3 = discord.Embed(title="Automod Command :shield:", color=discord.Color.dark_blue())
			embed3.add_field(name=f"</automod_create:{slash_automodcreate_id}>", value="This command is used to create automod rules", inline=True)
			embed3.add_field(name=f"</automod_delete:{slash_automoddelete_id}>", value="This command is used to delete automod rules", inline=True)

			embed4 = discord.Embed(title="Verify System :white_check_mark:", color=discord.Color.green())
			embed4.add_field(name=f"</verifysetup:{slash_verifysetup_id}>", value="This command is used to create a verification system on the server", inline=True)

			embed5 = discord.Embed(title="Ticket System :envelope:", color=discord.Color.yellow())
			embed5.add_field(name=f"</ticketsetup:{slash_ticketsetup_id}>", value="This command is used to create a ticket system on the server", inline=True)

			embed6 = discord.Embed(title="Music Bot :musical_note:", color=discord.Color.blurple())
			embed6.add_field(name=f"</play:{slash_play_id}>", value="This command plays a song", inline=True)
			embed6.add_field(name=f"</stop:{slash_stop_id}>", value="This command stops a song", inline=True)
			embed6.add_field(name=f"</volume:{slash_volume_id}>", value="This command increases or decreases the volume of the song", inline=True)

			embed7 = discord.Embed(title="Other commands :computer:", color=discord.Color.blue())
			embed7.add_field(name=f"</help:{slash_help_id}>", value="This command", inline=True)
			embed7.add_field(name=f"</reportbug:{slash_reportbug_id}>", value="Report a Ultimate-Bot Bug", inline=True)
			embed7.add_field(name=f"</giveaway:{slash_giveaway_id}>", value="Make a giveaway for all member in a server", inline=True)
			embed7.set_footer(text=footer_testo)

			await interaction.response.send_message(embeds=[embed1,embed2,embed3,embed4,embed5,embed6,embed7], ephemeral=True)



#-Traslate	
		
class TraslateButton(discord.ui.View):
	def __init__(self):
		super().__init__()
		self.value = None

	@discord.ui.button(label="List of language", style=discord.ButtonStyle.red)
	async def TraslateButton(self, interaction: discord.Interaction, button: discord.ui.Button):
		lingue_supportate = GoogleTranslator().get_supported_languages()
		#embed_traslate=discord.Embed(title=f"***```{lingue_supportate}```***", color=discord.Color.green())
		#embed_traslate.set_footer(text=footer_testo)
		await interaction.response.send_message(f"***```{lingue_supportate}```***", ephemeral=True)
		
		

#------------Slash------------#

@client.tree.command(name="help", description = "Show the list of command for Ultimate-Bot")
async def help(interaction: discord.Interaction):
	if interaction.user.id in my_id:
		admin_embed = discord.Embed(title="Admin Command :money_with_wings:", color=discord.Color.dark_red())
		admin_embed.add_field(name=f"{prefix}manutenzione", value="Set or Remove maintence mode to the bot", inline=True)
		admin_embed.add_field(name=f"{prefix}update", value="Update Bot code", inline=True)
		admin_embed.add_field(name=f"{prefix}slash_sync", value="Sync tree command", inline=True)
		admin_embed.add_field(name=f"{prefix}system_c `comando`", value="Send a command to the bot hosting console", inline=True)
		admin_embed.add_field(name=f"{prefix}servers", value="The bot will send a copy of all the servers it is in", inline=True)
		admin_embed.add_field(name=f"{prefix}data_send", value="Send a copy of `log.txt` , `suggestion_data.json` , `ticket_channels.json` and `verify_channels.json`", inline=True)
		admin_embed.set_footer(text=footer_testo)
		await interaction.response.send_message(view=HelpDropdownView(), embed=admin_embed, ephemeral=True)
	else:
		await interaction.response.send_message(view=HelpDropdownView(), ephemeral=True)


#----Ticket---start

class TicketModal(ui.Modal, title='Ticket Setup'):
	title_name = ui.TextInput(label='Message Title',required=True,placeholder='Message title...', max_length=50)
	description_name = ui.TextInput(label='Message Description',required=True, style=discord.TextStyle.paragraph, max_length=300,placeholder='Message Description...')
	button_name = ui.TextInput(label='Ticket Button Text',required=True, placeholder='Button Text...', max_length=50)
	async def on_submit(self, interaction: discord.Interaction):
		channel = interaction.channel

		embed_r = discord.Embed(title='The ticket system has been set up', color=discord.Color.green())
		await interaction.response.send_message(embed=embed_r, ephemeral=True)

		embed = discord.Embed(title=f"{self.children[0].value}",description=f"{self.children[1].value}", color=discord.Color.green())
		label = str(self.children[2].value)
		view = discord.ui.View(timeout=None)
		view.add_item(Open_Ticket_Button(label))
		await channel.send(embed=embed, view=view)
		channel_id = interaction.channel.id
		with open(database_ticket, 'r') as f:
			channels = json.load(f)
		channels[str(channel_id)] = True
		with open(database_ticket, 'w') as f:
			json.dump(channels, f)



class Open_Ticket_Button(discord.ui.Button):
	def __init__(self,label):
		super().__init__(label=label, emoji="✉️", style=discord.ButtonStyle.green, custom_id="persistant_button:ticket_open")

	async def callback(self, interaction: discord.Interaction):
		with open(database_ticket, 'r') as f:
			channels = json.load(f)
		if str(interaction.channel.id) in channels:
			channel_name_list = []
			for channel_t in interaction.guild.text_channels:
				channel_name_list.append(channel_t.name)

			ticket_name = str(f'ticket-{interaction.user.name}')
			ticket_n = ticket_name.replace(".","")

			if ticket_n in channel_name_list: 
				embed_r = discord.Embed(title='You have already opened a ticket:',description=f"<#{channel_t.id}>", color=discord.Color.red())
				await interaction.response.send_message(embed=embed_r,ephemeral=True) 
				return


			embed_r = discord.Embed(title='The ticket was opened', color=discord.Color.green())
			await interaction.response.send_message(embed=embed_r,ephemeral=True)  
			guild = interaction.guild
			ticket_channel = await guild.create_text_channel(name=f'ticket-{interaction.user.name}')
			await asyncio.sleep(timeout_time_ticket)
			await ticket_channel.set_permissions(guild.get_role(guild.id), send_messages=False, read_messages=False)
			await ticket_channel.set_permissions(interaction.user, attach_files=True, send_messages=True, read_messages=True, read_message_history=True, add_reactions=True)
			for role in guild.roles:
				if role.permissions.manage_roles:
					await ticket_channel.set_permissions(role, attach_files=True, send_messages=True, read_messages=True, read_message_history=True, add_reactions=True)
			embed = discord.Embed(title=f'**`{interaction.user.name}` - Ticket**', color=discord.Color.blue())
			await ticket_channel.send(embed=embed, view=Close_Ticket_Button())
		else:
			embed = discord.Embed(title='Error: This channel has not been set to initiate tickets', color=discord.Color.red())
			await interaction.response.send_message(embed=embed,ephemeral=True)


class Close_Ticket_Button(discord.ui.View):
	def __init__(self):
		super().__init__(timeout=None)

	@discord.ui.button(label='Close Ticket', emoji="🔒", style=discord.ButtonStyle.red, custom_id='persistant_button:ticket_close')
	async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
		if interaction.user.guild_permissions.manage_roles or interaction.user.guild_permissions.administrator:
			if 'ticket-' in interaction.channel.name:
				embed = discord.Embed(title='The ticket will be closed in 5 seconds', color=discord.Color.dark_blue())
				await interaction.response.send_message(embed=embed,ephemeral=True)
				await asyncio.sleep(5)
				await interaction.channel.delete()
			else:
					embed = discord.Embed(title=f'Error: This channel is not a ticket', color=discord.Color.red())
					await interaction.response.send_message(embed=embed,ephemeral=True)
		else:
			embed = discord.Embed(title='Error: You need the permission to use this command `"manage roles"`', color=discord.Color.red())
			await interaction.response.send_message(embed=embed,ephemeral=True)    





class Ticket_Button(discord.ui.View):
	def __init__(self):
		super().__init__()
		self.value = None

	@discord.ui.button(label="Add", emoji="➕", style=discord.ButtonStyle.green)
	async def Ticket_add(self, interaction: discord.Interaction, button: discord.ui.Button):
		channel_id = interaction.channel.id
		with open(database_ticket, 'r') as f:
			channels = json.load(f)
		if not str(channel_id) in channels:
			await interaction.response.send_modal(TicketModal())
		else:
			embed = discord.Embed(title='Error: The ticket system has already been set up in this channel', color=discord.Color.red())
			await interaction.response.send_message(embed=embed, ephemeral=True)


	@discord.ui.button(label="Remove",emoji="➖", style=discord.ButtonStyle.red)
	async def Ticket_remove(self, interaction: discord.Interaction, button: discord.ui.Button):
		channel_id = interaction.channel.id
		with open(database_ticket, 'r') as f:
			channels = json.load(f)
		if str(channel_id) in channels:
			del channels[str(channel_id)]
			with open(database_ticket, 'w') as f:
				json.dump(channels, f)
			embed = discord.Embed(title=f'The ticket system in the channel: <#{channel_id}> as been removed', color=discord.Color.red())
			await interaction.response.send_message(embed=embed, ephemeral=True)
			def check(msg):
				return msg.author == client.user
			await interaction.channel.purge(limit=100, check=check)
		else:
			embed = discord.Embed(title='Error: The ticket system has not been set up in this channel', color=discord.Color.red())
			await interaction.response.send_message(embed=embed, ephemeral=True)


@client.tree.command(name="ticketsetup", description = "Set up the ticket system on the server") #slash command
async def ticketsetup(interaction: discord.Interaction):
	if interaction.user.guild_permissions.manage_roles or interaction.user.guild_permissions.administrator:
		embed = discord.Embed(title="Ticket System Setup", color=discord.Color.blue())
		embed.add_field(name="Press the green button to add the ticket system to this channel", value=":green_circle:",inline=True)
		embed.add_field(name="\nPress the red button to remove the ticket system from this channel", value=":red_circle:",inline=True)
		await interaction.response.send_message(embed=embed, ephemeral=True, view=Ticket_Button())
	else:
		embed = discord.Embed(title='Error: You need the permission to use this command `"manage roles"`', color=discord.Color.red())
		await interaction.response.send_message(embed=embed, ephemeral=True)

#----Ticket---stop



#----Automod---start


#automod d



@client.tree.command(name="automod_delete", description = "Delete an AutoMod rule from the server")
async def automod_delete(interaction: discord.Interaction):
	try:
		rules = await interaction.guild.fetch_automod_rules()
		rule_opf = []
		for rule in rules:
			rule_op = discord.SelectOption(label=str(rule.name))  # Convert rule.name to string
			rule_opf.append(rule_op)
		view = Automod_D_Dropdown_View(rule_opf)
		embed = discord.Embed(title='Choose the Automod rule to delete', color=discord.Color.red())
		await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
	except Exception as e:
		if "In data.components.0.components.0.options:" in str(e):
			embed = discord.Embed(title="Error: There are no automod rules in the server", color=discord.Color.red())
			embed.set_footer(text=footer_testo)
			await interaction.response.send_message(embed=embed, ephemeral=True)
		else:
			embed = discord.Embed(title="Error: Unknown", color=discord.Color.red())
			embed.add_field(name="Please report the bug using:", value=f"</reportbug:{slash_reportbug_id}>", inline=True)
			embed.set_footer(text=footer_testo)
			await interaction.response.send_message(embed=embed, ephemeral=True)
			#error-chat
			channel = client.get_channel(errorchannel)
			await channel.send(f"**[Errore]** \nisinstance: ```{isinstance}```\nerror: ```{str(e)}```")
			errror_log(e,str(e),"automod_delete command (slash)")



class Automod_D_Dropdown_View(discord.ui.View):
	def __init__(self, options):
		super().__init__()
		self.add_item(Automod_D_Dropdown(options))


class Automod_D_Dropdown(discord.ui.Select):
	def __init__(self, options):
		super().__init__(placeholder='Choose the Automod rule...', min_values=1, max_values=1, options=options)

	async def callback(self, interaction: discord.Interaction):
		await asyncio.sleep(timeout_time_automod)
		try:
			rules = await interaction.guild.fetch_automod_rules()
			for rule in rules:
				if self.values[0] == rule.name:
					await rule.delete()
					embed = discord.Embed(title=f'I deleted `{rule.name}`', color=discord.Color.red())
					await interaction.response.edit_message(embed=embed, view=None)
		except Exception as e:
			if "In data.components.0.components.0.options:" in str(e):
				embed = discord.Embed(title="Error: There are no automod rules in the server", color=discord.Color.red())
				embed.set_footer(text=footer_testo)
				await interaction.response.send_message(embed=embed, ephemeral=True)
			else:
				embed = discord.Embed(title="Error: Unknown", color=discord.Color.red())
				embed.add_field(name="Please report the bug using:", value=f"</reportbug:{slash_reportbug_id}>", inline=True)
				embed.set_footer(text=footer_testo)
				await interaction.response.send_message(embed=embed, ephemeral=True)
				#error-chat
				channel = client.get_channel(errorchannel)
				await channel.send(f"**[Errore]** \nisinstance: ```{isinstance}```\nerror: ```{str(e)}```")
				errror_log(e,str(e),"Automod_D_Dropdown (ui)")



#automod c

@client.tree.command(name="automod_create", description = "Adds AutoMod rules to the server")
@app_commands.describe(type='The type of rule you want', timeout_time='The time the person violating the rule will be put in timeout', log_channel="The channel where alerts will be sent when someone violates a rule")
async def automod_create(interaction: discord.Interaction, type: Literal['Spam', 'Mention Spam', 'Custom Keyword', 'Keyword Preset'], timeout_time: Literal['60 sec', '5 min.','10 min.', '1 hour', '1 day', '1 week'], log_channel: discord.TextChannel):
	if interaction.user.guild_permissions.manage_messages or interaction.user.guild_permissions.administrator:
		time_value = {
			"60 sec": timedelta(seconds=60),
			"5 min.": timedelta(minutes=5),
			"10 min.": timedelta(minutes=10),
			"1 hour": timedelta(hours=1),
			"1 day": timedelta(days=1),
			"1 week": timedelta(weeks=1)
		}
		embed = discord.Embed(title=f'I created a `{type}` rule in automod, the timeout time is `{timeout_time}` , the log channel is `#{log_channel}`', color=discord.Color.green())
		embed.set_footer(text=footer_testo)
		if timeout_time in time_value:
			time = time_value[timeout_time]
			try:
				if type == 'Custom Keyword':
					global timeout_time_f
					global time_f
					global log_channel_f
					timeout_time_f = timeout_time
					time_f = time
					log_channel_f = log_channel
					await interaction.response.send_modal(AutomodCustom_Keyword_Modal())
				elif type == 'Spam':
					actions = [
						discord.AutoModRuleAction(),
						discord.AutoModRuleAction(channel_id=log_channel.id),
						]
					await interaction.guild.create_automod_rule(
						name="Spam Rule",
						event_type=discord.AutoModRuleEventType.message_send,
						trigger=discord.AutoModTrigger(
						type=discord.AutoModRuleTriggerType.spam
						),
						enabled=True,
						actions=actions
					)
					await interaction.response.send_message(embed=embed, ephemeral=True)
				elif type == 'Mention Spam':
					actions = [
						discord.AutoModRuleAction(),
						discord.AutoModRuleAction(channel_id=log_channel.id),
						discord.AutoModRuleAction(duration=time),
						discord.AutoModRuleAction(custom_message=">>> **You are sending too many mentions**")
						]
					await interaction.guild.create_automod_rule(
						name="Mention Spam Rule",
						event_type=discord.AutoModRuleEventType.message_send,
						trigger=discord.AutoModTrigger(
						type=discord.AutoModRuleTriggerType.mention_spam, mention_limit=5
						),
						enabled=True,
						actions=actions
					)
					await interaction.response.send_message(embed=embed, ephemeral=True)
				elif type == 'Keyword Preset':
					global timeout_time_d
					global time_d
					global log_channel_d
					timeout_time_d = timeout_time
					time_d = time
					log_channel_d = log_channel
					embed_key = discord.Embed(title=f'Select a Keyword preset for the rule', color=discord.Color.blue())
					embed_key.set_footer(text="\nWarning:\nIn the Keyword preset the isn't a timeout time because the message will be blocked")
					await interaction.response.send_message(embed=embed_key, view=AutomodKeyword_Preset_Dropdown_View(), ephemeral=True)
			except Exception as e:
				if "AUTO_MODERATION_MAX_RULES_OF_TYPE_EXCEEDED" in str(e):
					embed = discord.Embed(title="Error: Auto-mod Max Rules of this type\n\nYou have reached the maximum number of rules of this type", color=discord.Color.red())
					embed.set_footer(text=footer_testo)
					await interaction.response.send_message(embed=embed, ephemeral=True)
				else:
					embed = discord.Embed(title="Error: Unknown", color=discord.Color.red())
					embed.add_field(name="Please report the bug using:", value=f"</reportbug:{slash_reportbug_id}>", inline=True)
					embed.set_footer(text=footer_testo)
					await interaction.response.send_message(embed=embed, ephemeral=True)
					#error-chat
					channel = client.get_channel(errorchannel)
					await channel.send(f"**[Errore]** \nisinstance: ```{isinstance}```\nerror: ```{str(e)}```")
					errror_log(e,str(e),"automod_create command (slash)")
	else:
		embed = discord.Embed(title="Error: You need the permission to use this command (`manage_messages`)", color=discord.Color.red())
		embed.set_footer(text=footer_testo)
		await interaction.response.send_message(embed=embed, ephemeral=True)
		



class AutomodCustom_Keyword_Modal(ui.Modal, title='AutoMod Customod Keyword'):
	w1 = ui.TextInput(label='First word',required=True,placeholder='A bad word...', max_length=50)
	w2 = ui.TextInput(label='Second word',required=False,placeholder='A bad word...', max_length=50)
	w3 = ui.TextInput(label='Third word',required=False,placeholder='A bad word...', max_length=50)
	w4 = ui.TextInput(label='Fourth word',required=False,placeholder='A bad word...', max_length=50)
	w5 = ui.TextInput(label='Fifth word',required=False,placeholder='A bad word...', max_length=50)

	async def on_submit(self, interaction: discord.Interaction):
		try:
			global timeout_time_f
			global time_f
			global log_channel_f
			timeout_time = timeout_time_f
			time = time_f
			log_channel = log_channel_f
			type = "Custom Keyword"

			w1_f = self.children[0].value
			w2_f = self.children[1].value
			w3_f = self.children[2].value
			w4_f = self.children[3].value
			w5_f = self.children[4].value
			w_c_d = [f"{w1_f}" if w1_f is not None else None,
				f"{w2_f}" if w2_f is not None else None,
				f"{w3_f}" if w3_f is not None else None,
				f"{w4_f}" if w4_f is not None else None,
				f"{w5_f}" if w5_f is not None else None]

			# Rimuovi gli elementi None da w_c
			w_c = [f"*{item}*" if item is not None else None for item in w_c_d]
			time_value = {
				w1_f: timedelta(seconds=60),
				w2_f: timedelta(minutes=5),
				w3_f: timedelta(minutes=10),
				w4_f: timedelta(hours=1),
				w5_f: timedelta(days=1)
			}
			actions = [
				discord.AutoModRuleAction(),
				discord.AutoModRuleAction(channel_id=log_channel.id),
				discord.AutoModRuleAction(duration=time),
				]
			await interaction.guild.create_automod_rule(
				name="Custom Keywords Rule",
				event_type=discord.AutoModRuleEventType.message_send,
				trigger=discord.AutoModTrigger(
				type=discord.AutoModRuleTriggerType.keyword, keyword_filter=w_c
				),
				enabled=True,
				actions=actions
			)

			embed = discord.Embed(title=f'I created a `{type}` rule in automod, the timeout time is `{timeout_time}` , the log channel is `#{log_channel}`', color=discord.Color.green())
			embed.set_footer(text=footer_testo)

			await interaction.response.send_message(embed=embed, ephemeral=True)
		except Exception as e:
			if "AUTO_MODERATION_MAX_RULES_OF_TYPE_EXCEEDED" in str(e):
				embed = discord.Embed(title="Error: Auto-mod Max Rules of this type\n\nYou have reached the maximum number of rules of this type", color=discord.Color.red())
				embed.set_footer(text=footer_testo)
				await interaction.response.send_message(embed=embed, ephemeral=True)
			else:
				embed = discord.Embed(title="Error: Unknown", color=discord.Color.red())
				embed.add_field(name="Please report the bug using:", value=f"</reportbug:{slash_reportbug_id}>", inline=True)
				embed.set_footer(text=footer_testo)
				await interaction.response.send_message(embed=embed, ephemeral=True)
				#error-chat
				channel = client.get_channel(errorchannel)
				await channel.send(f"**[Errore]** \nisinstance: ```{isinstance}```\nerror: ```{str(e)}```")
				errror_log(e,str(e),"AutomodCustom_Keyword_Modal (ui)")




class AutomodKeyword_Preset_Dropdown_View(discord.ui.View):
	def __init__(self):
		super().__init__()
		self.add_item(AutomodKeyword_Preset_Dropdown())


class AutomodKeyword_Preset_Dropdown(discord.ui.Select):
	def __init__(self):
		options = [discord.SelectOption(label='Profanity', emoji='🗣️'), discord.SelectOption(label='Sexual content', emoji='💋'), discord.SelectOption(label='Slurs', emoji='🗨️'), discord.SelectOption(label='All', emoji='📁')]
		super().__init__(placeholder='Choose the automod preset for the keyword...', min_values=1, max_values=1, options=options)

	async def callback(self, interaction: discord.Interaction):
		try:
			type = f"{self.values[0]} keyword preset rule"

			#global -- info
			global timeout_time_d
			global time_d
			global log_channel_d
			timeout_time = timeout_time_d
			time = time_d
			log_channel = log_channel_d

			embed = discord.Embed(title=f"I created a `{type}` rule in automod, there isn't a timeout time for this rule, the log channel is `#{log_channel}`", color=discord.Color.green())
			embed.set_footer(text=footer_testo)
			if self.values[0] == "Profanity":
				actions = [
					discord.AutoModRuleAction(),
					discord.AutoModRuleAction(channel_id=log_channel.id),
					discord.AutoModRuleAction(custom_message=">>> **Profanity messages are not allowed**")
					]
				await interaction.guild.create_automod_rule(
					name="Profanity Rule",
					event_type=discord.AutoModRuleEventType.message_send,
					trigger=discord.AutoModTrigger(
					type=discord.AutoModRuleTriggerType.keyword_preset, presets = discord.AutoModPresets(profanity=True)
					),
					enabled=True,
					actions=actions
				)
				await interaction.response.send_message(embed=embed, ephemeral=True)
			elif self.values[0] == "Sexual content":
				actions = [
					discord.AutoModRuleAction(),
					discord.AutoModRuleAction(channel_id=log_channel.id),
					discord.AutoModRuleAction(custom_message=">>> **Sexual content messages are not allowed**")
					]
				await interaction.guild.create_automod_rule(
					name="Sexual content Rule",
					event_type=discord.AutoModRuleEventType.message_send,
					trigger=discord.AutoModTrigger(
					type=discord.AutoModRuleTriggerType.keyword_preset, presets = discord.AutoModPresets(sexual_content=True)
					),
					enabled=True,
					actions=actions
				)
				await interaction.response.send_message(embed=embed, ephemeral=True)
			elif self.values[0] == "Slurs":
				actions = [
					discord.AutoModRuleAction(),
					discord.AutoModRuleAction(channel_id=log_channel.id),
					discord.AutoModRuleAction(custom_message=">>> **Slurs messages are not allowed**")
					]
				await interaction.guild.create_automod_rule(
					name="Slurs Rule",
					event_type=discord.AutoModRuleEventType.message_send,
					trigger=discord.AutoModTrigger(
					type=discord.AutoModRuleTriggerType.keyword_preset, presets = discord.AutoModPresets(slurs=True)
					),
					enabled=True,
					actions=actions
				)
				await interaction.response.send_message(embed=embed, ephemeral=True)
			elif self.values[0] == "All":
				actions = [
					discord.AutoModRuleAction(),
					discord.AutoModRuleAction(channel_id=log_channel.id),
					discord.AutoModRuleAction(custom_message=">>> **Slurs, Profanity and Sexual content messages are not allowed**")
					]
				await interaction.guild.create_automod_rule(
					name="All Keywords Presets Rule",
					event_type=discord.AutoModRuleEventType.message_send,
					trigger=discord.AutoModTrigger(
					type=discord.AutoModRuleTriggerType.keyword_preset, presets = discord.AutoModPresets.all()
					),
					enabled=True,
					actions=actions
				)
				embed_a = discord.Embed(title=f"I created a rule in automod with all of keywords presets, there isn't a timeout time for this rule, the log channel is `#{log_channel}`", color=discord.Color.green())
				embed_a.set_footer(text=footer_testo)
				await interaction.response.send_message(embed=embed_a, ephemeral=True)
		except Exception as e:
			if "AUTO_MODERATION_MAX_RULES_OF_TYPE_EXCEEDED" in str(e):
				embed = discord.Embed(title="Error: Auto-mod Max Rules of this type\n\nYou have reached the maximum number of rules of this type", color=discord.Color.red())
				embed.set_footer(text=footer_testo)
				await interaction.response.send_message(embed=embed, ephemeral=True)
			else:
				embed = discord.Embed(title="Error: Unknown", color=discord.Color.red())
				embed.add_field(name="Please report the bug using:", value=f"</reportbug:{slash_reportbug_id}>", inline=True)
				embed.set_footer(text=footer_testo)
				await interaction.response.send_message(embed=embed, ephemeral=True)
				#error-chat
				channel = client.get_channel(errorchannel)
				await channel.send(f"**[Errore]** \nisinstance: ```{isinstance}```\nerror: ```{str(e)}```")
				errror_log(e,str(e),"AutomodKeyword_Preset_Dropdown (ui)")



#----Automod---stop



#----Giveaway---start


@client.tree.command(name="giveaway", description = "Make a giveaway") #slash command
@app_commands.describe(prize='The prize that you wanna give in giveaway',year="The year in which the giveaway must take place",month="The month in which the giveaway must take place",day="The day in which the giveaway must take place",hour="The hour in which the giveaway must take place",minute="The minute in which the giveaway must take place")
async def giveaway(interaction: discord.Interaction, prize:str, year:int, month:int, day:int, hour:int, minute:int):
	if interaction.user.guild_permissions.administrator:
		if month > 12 or month <= 0:
			embed = discord.Embed(title="Error: Invalid time format", color=discord.Color.red())
			await interaction.response.send_message(embed=embed,ephemeral=True)
			return
		if month == 1 and day > 31 or month == 2 and day > 28 or month == 3 and day > 31 or month == 4 and day > 30 or month == 5 and day > 31 or month == 6 and day > 30 or month == 7 and day > 31 or month == 8 and day > 31 or month == 9 and day > 30 or month == 10 and day > 31 or month == 11 and day > 30 or month == 12 and day > 31:
			embed = discord.Embed(title="Error: Invalid time format", color=discord.Color.red())
			await interaction.response.send_message(embed=embed,ephemeral=True)
			return
		if hour > 24 or hour <= 0:
			embed = discord.Embed(title="Error: Invalid time format", color=discord.Color.red())
			await interaction.response.send_message(embed=embed,ephemeral=True)
			return
		if minute > 60 or minute <= 0:
			embed = discord.Embed(title="Error: Invalid time format", color=discord.Color.red())
			await interaction.response.send_message(embed=embed,ephemeral=True)
			return
		# - Timestamp
		dnow = dt.now()
		dtime = dt(year, month, day, hour, minute)
		n_stamp = dnow.timestamp()
		t_stamp = dtime.timestamp()
		tms = int(t_stamp)
		if int(t_stamp) < int(n_stamp): #ckeck if the time is passed
			embed = discord.Embed(title="Error: This time has already passed", color=discord.Color.red())
			await interaction.response.send_message(embed=embed,ephemeral=True)
			return
		# -- Normal Code
		start_embed = discord.Embed(title=f":tada: Giveaway starts at: <t:{int(t_stamp)}:R> :tada:\nThe prize is `{prize}` :moneybag:", color=0xe91e63)
		message = await interaction.channel.send(embed=start_embed,view=Partecipate_Giveaway_Button())
		# - Message
		embed = discord.Embed(title="The giveaway has been set", color=discord.Color.green())
		await interaction.response.send_message(embed=embed,ephemeral=True)
		# - Data
		#s_id = str(interaction.guild.id)
		ch_id = str(interaction.channel.id)
		m_id = str(message.id)
		# - Database
		with open(giveaway_database, 'r') as f:
			c_dati = json.load(f)
		dati = {
			"ch_id":f"{ch_id}",
			"m_id":f"{m_id}",
			"prize":f"{prize}",
			"tms":f"{tms}",
			"people":[]
			}				
		c_dati["dati"].append(dati)
		with open(giveaway_database, 'w') as f:
			json.dump(c_dati, f)
		# - Timestamp minimum check
		position = c_dati["dati"].index(dati)
		i_pos = int(position)
		time_tms = converter_timestamp_giveaway(tms)
		if time_tms < 5:
			await time_giveaway(time_tms*60, i_pos, client, giveaway_database)

	else:
		embed = discord.Embed(title="Error: You need the permission to use this command", color=discord.Color.red())
		await interaction.response.send_message(embed=embed, ephemeral=True)






class Exit_Giveaway_Button(discord.ui.View):
	def __init__(self,i_pos):
		self.i_pos = i_pos
		super().__init__(timeout=None)

	@discord.ui.button(label="Exit", emoji="❌", style=discord.ButtonStyle.red, custom_id="normal_button:giveaway_leave")
	async def giveaway_leave(self, interaction: discord.Interaction, button: discord.ui.Button):
		try:
			inter = str(self.i_pos)
			with open(giveaway_database, 'r') as f:
				c_dati = json.load(f)
			for x in range(int(len(c_dati["dati"]))):
				if inter in str(c_dati["dati"][x]):
					i = int(x)
							
					if converter_timestamp_giveaway(c_dati["dati"][i]["tms"]) < 0:
						embed = discord.Embed(title="❌ The giveaway has ended ❌",color=discord.Color.red())
						await interaction.response.send_message(embed=embed,ephemeral=True)		
						return
					c_dati["dati"][i]["people"].remove(int(interaction.user.id))
					with open(giveaway_database, 'w') as f:
						json.dump(c_dati, f)
					embed = discord.Embed(title="❌ You have been removed from the giveaway ❌",color=discord.Color.red())
					await interaction.response.send_message(embed=embed,ephemeral=True)
		except Exception as e:
			if "list.remove(x): x not in list" in str(e):
				embed = discord.Embed(title="Error: You are not a giveaway participant",color=discord.Color.red())
				await interaction.response.send_message(embed=embed,ephemeral=True)
			else:
				embed = discord.Embed(title="Error: Unknown",color=discord.Color.red())
				await interaction.response.send_message(embed=embed,ephemeral=True)
				errror_log(e,str(e),"Exit Button Giveaway")






class Partecipate_Giveaway_Button(discord.ui.View):
	def __init__(self):
		super().__init__(timeout=None)

	@discord.ui.button(label="Join", emoji="🎉", style=discord.ButtonStyle.blurple, custom_id="persistant_button:giveaway_join")
	async def giveaway_join(self, interaction: discord.Interaction, button: discord.ui.Button):
		try:
			
			with open(giveaway_database, 'r') as f:
				c_dati = json.load(f)
			for i in range(int(len(c_dati["dati"]))):
				if str(interaction.message.id) in c_dati["dati"][i]["m_id"]:
					if converter_timestamp_giveaway(c_dati["dati"][i]["tms"]) < 0:
						embed = discord.Embed(title="❌ The giveaway has ended ❌",color=discord.Color.red())
						await interaction.response.send_message(embed=embed,ephemeral=True)		
						return
					if not int(interaction.user.id) in c_dati["dati"][i]["people"]:
						c_dati["dati"][i]["people"].append(int(interaction.user.id))
						with open(giveaway_database, 'w') as f:
							json.dump(c_dati, f)
						embed = discord.Embed(title="🎉 You have been added to the giveaway 🎉",color=discord.Color.green())
						await interaction.response.send_message(embed=embed,ephemeral=True)
					elif int(interaction.user.id) in c_dati["dati"][i]["people"]:
						inter = interaction.message.id
						embed = discord.Embed(title="⚠️ If you want to exit the giveaway, press the exit button ⚠️",color=discord.Color.gold())
						await interaction.response.send_message(embed=embed,view=Exit_Giveaway_Button(inter),ephemeral=True)				
		except Exception as e:
			embed = discord.Embed(title="Error: Unknown",color=discord.Color.red())
			await interaction.response.send_message(embed=embed,ephemeral=True)
			errror_log(e,str(e),"Join Button Giveaway")


@tasks.loop(minutes=5)
async def giveaway_check():
	with open(giveaway_database, 'r') as f:
		c_dati = json.load(f)
	if len(c_dati["dati"]) == 0:
		return
	for i in range(int(len(c_dati["dati"]))):
		dato = c_dati["dati"][i]
		time_tms = converter_timestamp_giveaway(dato["tms"])
		if time_tms < 5:
			await time_giveaway(time_tms*60, i, client, giveaway_database)


def converter_timestamp_giveaway(t):
	try:
		ti = int(t)
		dt_object = dtm.datetime.utcfromtimestamp(ti)
		current_dt = dtm.datetime.utcnow()
		minutes_until = (dt_object - current_dt).total_seconds() / 60
		return minutes_until
	except Exception as e:
		print(e)
		errror_log(e,str(e),"converter_timestamp Giveaway")



async def time_giveaway(ti, i, client, giveaway_database):
	try:
		i = int(i)
		ti = float(ti)
		await asyncio.sleep(ti)
		with open(giveaway_database, 'r') as f:
			c_dati = json.load(f)
		dato = c_dati["dati"][i]
		list_people = dato["people"]
		ch_id = dato["ch_id"]
		ms_id = dato["m_id"]
		prize = dato["prize"]
		try:
			channel = client.get_channel(int(ch_id))
			fetched_message = await channel.fetch_message(int(ms_id))
		except Exception as e:
			if "'NoneType' object has no attribute 'fetch_message'" in str(e) or "404 Not Found (error code: 10008): Unknown Message" in str(e):
				del c_dati["dati"][i]
				with open(giveaway_database, 'w') as f:
					json.dump(c_dati, f)
				print("missing message id... deleting data...")
			else:
				try:
					del c_dati["dati"][i]
					with open(giveaway_database, 'w') as f:
						json.dump(c_dati, f)
				except:
					pass
				errror_log(e,str(e),"time giveaway function - 1")
		if len(list_people) == 0:
			embed = discord.Embed(title="🎉 Giveaway Finished 🎉",description="❌ No one participated in the giveaway ❌",color=0xe91e63)
			embed.add_field(name="Prize", value=f"💰 **`{prize}`** 💰")
			await fetched_message.edit(embed=embed,view=None)
			del c_dati["dati"][i]
			with open(giveaway_database, 'w') as f:
				json.dump(c_dati, f)
			return
		winner_id = random.choice(list_people)
		embed = discord.Embed(title="🎉 Giveaway Finished 🎉",color=0xe91e63)
		embed.add_field(name="Winner user:", value=f"🎁 **<@{int(winner_id)}>** 🎁")
		embed.add_field(name="Prize", value=f"💰 **`{prize}`** 💰")
		await fetched_message.edit(embed=embed,view=None)
		del c_dati["dati"][i]
		with open(giveaway_database, 'w') as f:
			json.dump(c_dati, f)
		return
	except Exception as e:
		errror_log(e,str(e),"time giveaway function - 2")

#----Giveaway---stop


@client.tree.command(name="reportbug", description="Report a bug of a Ultimate-Bot command") #slash command
async def report_bug(interaction: discord.Interaction):
	await interaction.response.send_modal(BugModal())




@client.tree.context_menu(name="Get User Info")
async def getuserinfo(interaction: discord.Interaction, member: discord.Member):
	voice_state = None if not member.voice else member.voice.channel
	role = member.top_role.name
	acc_created = member.created_at.__format__('Date: %A, %d. %B %Y Time: %H:%M:%S')
	server_join = member.joined_at.__format__('Date: %A, %d. %B %Y Time: %H:%M:%S')
	if role == "@everyone":
		role = None
	embed = discord.Embed(title=f"**User Info**", color=discord.Colour.blue())
	embed.add_field(name=":bust_in_silhouette: - Displayed Server Name", value=member.mention, inline=True)
	embed.add_field(name=':bust_in_silhouette: - User Name', value=f"`{member.name}`", inline=True)
	embed.add_field(name=':id: - User ID', value=f"`{member.id}`", inline=False)
	embed.add_field(name=':robot: - Robot?', value=f"`{member.bot}`", inline=True)
	embed.add_field(name=':loud_sound:  - Is in voice', value=f"**In:** `{voice_state}`", inline=True)
	embed.add_field(name=':radio_button:  - Highest Role', value=f"`{role}`", inline=True)
	embed.add_field(name=':calendar: - Account Created', value=f"`{acc_created}`", inline=False)
	embed.add_field(name=':calendar: - Join Server Date', value=f"`{server_join}`", inline=False)
	embed.set_thumbnail(url=member.avatar)
	embed.set_footer(text=footer_testo)
	await interaction.response.send_message(embed=embed, ephemeral=True)
	
@client.tree.context_menu(name="Get Message ID") #message contex command
async def getmessageid(interaction: discord.Interaction, message: discord.Message):
	await interaction.response.send_message(f"***Message ID: ***`{message.id}`", ephemeral=True)




@client.tree.context_menu(name="Ban User") #message contex command
async def ban(interaction: discord.Interaction, message: discord.Message):
	if interaction.user.guild_permissions.administrator:
		try:
			target = message.author
		
			# Banna l'utente
			await interaction.guild.ban(target)
		
			# Invia un messaggio di conferma
			embed = discord.Embed(title="The user has been banned!", color=discord.Color.red())
			embed.set_footer(text=footer_testo)
			await interaction.response.send_message(embed=embed, ephemeral=True)
			
		except Exception as e:
			if 'error code: 50013' in str(e):
				embed = discord.Embed(title="Error: I don't have permission to ban this user", color=discord.Color.red())
				embed.set_footer(text=footer_testo)
				await interaction.response.send_message(embed=embed, ephemeral=True)
			else:
				embed = discord.Embed(title="Error: Unknown", color=discord.Color.red())
				embed.add_field(name="Please report the bug using:", value=f"</reportbug:{slash_reportbug_id}>", inline=True)
				embed.set_footer(text=footer_testo)
				await interaction.response.send_message(embed=embed, ephemeral=True)
				channel = client.get_channel(errorchannel)
				await channel.send(f"**[Errore]** \nisinstance: ```{e}```\nerror: ```{str(e)}```")
				errror_log(e,str(e),"ban command (context menu)")
		except discord.ext.commands.errors.MissingPermissions as e:
			embed = discord.Embed(title="Error: I don't have permission to ban", color=discord.Color.red())
			embed.set_footer(text=footer_testo)
			await interaction.response.send_message(embed=embed, ephemeral=True)
	else:
		embed = discord.Embed(title="Error: You need the permission to use this command", color=discord.Color.red())
		embed.set_footer(text=footer_testo)
		await interaction.response.send_message(embed=embed, ephemeral=True)
		
		

@client.tree.context_menu(name="Traslate message") #message contex command
async def traslate(interaction: discord.Interaction, message: discord.Message):
	text = message.content
	lang = "en"
	try:
		if len(text) > 1998:
			embed = discord.Embed(title="Error: The text is too long must not exceed 1998 characters", color=discord.Color.red())
			embed.set_footer(text=footer_testo)
			await interaction.response.send_message(embed=embed, ephemeral=True)
			#await ctx.send(embed=embed, delete_after=4)
		else:
			if len(text) > 1024:
				traduttore = GoogleTranslator(source='auto', target=lang)
				risultato = traduttore.translate(text)
				await interaction.response.send_message(f"```{risultato}```", ephemeral=True)
				#await ctx.send(f"```{risultato}```")
			else:
				traduttore = GoogleTranslator(source='auto', target=lang)
				risultato = traduttore.translate(text)
				embed=discord.Embed(color=discord.Color.green())
				embed.set_footer(text=footer_testo)
				await interaction.response.send_message(embed=embed, content=f"```{risultato}```", ephemeral=True)
	except Exception as e:
		embed = discord.Embed(title="Error: Unknown", color=discord.Color.red())
		embed.set_footer(text=footer_testo)
		await interaction.response.send_message(embed=embed, ephemeral=True)
		#error-chat
		channel = client.get_channel(errorchannel)
		await channel.send(f"**[Errore]** \nisinstance: ```{e}```\nerror: ```{str(e)}```")
		errror_log(e,str(e),"translate command")




@client.tree.command(name="play", description = "Play a song") #slash command
async def play(interaction: discord.Interaction, name: str):
	url = name
	if interaction.user.voice is None:
		embed = discord.Embed(title="*** You are not currently in a voice channel. ***", color=discord.Colour.red())
		await interaction.response.send_message(embed=embed, ephemeral=True)
	else:
		if interaction.guild.voice_client is not None and interaction.guild.voice_client.is_playing():
			no_music_embed = discord.Embed(title="*** Please wait until the song is finished to start another one, If you want to stop the song you can use </stop:1114604126861525132> ***", color=discord.Colour.red())
			await interaction.response.send_message(embed=no_music_embed, ephemeral=True)
			await asyncio.sleep(0.5)
		else:
			loading_embed = discord.Embed(title=":arrows_clockwise: Downloading song :musical_note:", color=discord.Colour.blue())
			await interaction.response.send_message(embed=loading_embed, ephemeral=True)
			try:
				if "playlist?list=" in url:
					error_embed = discord.Embed(title="*** Playlists cannot be played ***", color=discord.Colour.red())
					await interaction.edit_original_response(embed=error_embed)
				else:
					if url.startswith("https://"):
						if url.startswith("https://youtu.be/"):
							share_video_url = url.replace("https://youtu.be/", "https://youtube.com/watch?v=")
						else:
							share_video_url = url	
					else:
						s = Search(url)
						searchResults = []
						for v in s.videos:
							searchResults.append(v.watch_url)
						share_video_url = searchResults[0]
					# Scarica l'audio da YouTube
					yt = YouTube(share_video_url, on_progress_callback = on_progress)
					stream = yt.streams.get_audio_only() #w
					stream_url = stream.url

					channel = interaction.user.voice.channel
					voice_channel = await channel.connect()

					#----FFMPEG_OPTION
			
					#permette la canzone di essere completata quando si ha un delay nell'app di ffmpeg
					FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
			

					#----source option
					#source = discord.FFmpegPCMAudio(stream_url) #-2 w
					#source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(stream_url)) #-1 w
					source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(stream_url, **FFMPEG_OPTIONS)) #w c
			
					#evita errori di rallentamento e velocizzamento nella canzone
					source.read()
			

					#----voice play
					voice_channel.play(source)
			

					#----voice option
					#voice_channel.source = discord.PCMVolumeTransformer(voice_channel.source)
					voice_channel.source.volume = 0.5
			

					#----info tittle_embed
			
					video_length = yt.length
					minutes, seconds = divmod(video_length, 60)
			
					artist = yt.author
			
					title_embed = discord.Embed(color=discord.Colour.red())
					title_embed.set_image(url=yt.thumbnail_url)
					title_embed.description = f"*** ## {yt.title}\n\n`{artist}` \n\n`{minutes}:{seconds}` :clock10:\n⇆ㅤ ◁◁ㅤ❚❚ㅤ▷▷ㅤ ↻***"
					await interaction.edit_original_response(embed=title_embed)
			

					# Wait for the video to finish playing
					while voice_channel.is_playing():
						await asyncio.sleep(1)
					
					await voice_channel.disconnect()
			
					end_embed = discord.Embed(title="***:cd: The song is ended***", color=discord.Colour.red())
					await interaction.edit_original_response(embed=end_embed)
			except Exception as e:
				if 'is age restricted' in str(e):
					error_embed = discord.Embed(title="Error: The video is `age-restricted`", color=discord.Colour.red())
					await interaction.edit_original_response(embed=error_embed)
				elif 'is unavailable' in str(e):
					error_embed = discord.Embed(title="Error: Youtube service is unavailable", color=discord.Colour.red())
					await interaction.edit_original_response(embed=error_embed)
				elif 'is streaming live' in str(e):
					error_embed = discord.Embed(title="Error: The video is a `live` or a `premiere`", color=discord.Colour.red())
					await interaction.edit_original_response(embed=error_embed)
				elif "HTTP Error 400: Bad Request" in str(e):
					error_embed = discord.Embed(title="Error: The song isn't supported", color=discord.Colour.red())
					await interaction.edit_original_response(embed=error_embed)
				elif str(e) == "Already connected to a voice channel.":
					pass
				elif "get_throttling_function_name" in str(e):
					error_embed = discord.Embed(title="***Error: Youtube service is unavailable***", color=discord.Colour.red())
					await interaction.edit_original_response(embed=error_embed)
					#err - channel
					channel = client.get_channel(errorchannel)
					await channel.send(f"**[Errore]** \nget_throttling_function_name: (discord.py) ```{e}```")
				else:
					print(e)
					error_embed = discord.Embed(title="***An error occurred while playing the video***", color=discord.Colour.red())
					embed.add_field(name="Please report the bug using:", value=f"</reportbug:{slash_reportbug_id}>", inline=True)
					await interaction.edit_original_response(embed=error_embed)
					#err - channel
					channel = client.get_channel(system_config["id_error_channel"])
					await channel.send(f"**[Errore]** \naudio isinstance: (discord.py) ```{e}```\n url: {url}")



@client.tree.command(name="stop", description = "Stop a song") #slash command
async def stop(interaction: discord.Interaction):				
	voice_client = interaction.guild.voice_client
	if voice_client and voice_client.is_connected():
		if voice_client.is_playing():
			embed = discord.Embed(title=':cd: The song has been stopped', color=discord.Colour.red())
			embed.set_footer(text=footer_testo)
			await interaction.response.send_message(embed=embed, ephemeral=True)
			voice_client.stop()
			await voice_client.disconnect()
			#await asyncio.sleep(2)
		else:
			embed = discord.Embed(title=':x: The bot has been disconnected', color=discord.Colour.red())
			embed.set_footer(text=footer_testo)
			await interaction.response.send_message(embed=embed, ephemeral=True)
			await voice_client.disconnect()
	else:
		embed = discord.Embed(title='Please enter the voice chat where the bot is or play a song and enter in the voice chat where the bot is', color=discord.Colour.red())
		embed.set_footer(text=footer_testo)
		await interaction.response.send_message(embed=embed, ephemeral=True)

		
		
		
@client.tree.command(name="volume", description = "Set the volume of the song") #slash command
async def volume(interaction: discord.Interaction, volume: float):				
	voice_client = interaction.guild.voice_client
	
	if not voice_client:
		embed = discord.Embed(title='Please enter the voice chat where the bot is', color=discord.Colour.red())
		embed.set_footer(text=footer_testo)
		await interaction.response.send_message(embed=embed, ephemeral=True)
		return
	if voice_client.is_playing():
		if volume < 0.0 or volume > 25.0:
			embed = discord.Embed(title=f'The max of volume is ```25.0```\nThe min ```0.0```', color=discord.Colour.red())
			embed.set_footer(text=footer_testo)
			await interaction.response.send_message(embed=embed, ephemeral=True)
		else:
			voice_client.source.volume = volume
			embed = discord.Embed(title=f':loud_sound: Volume set to ***```{volume}```***', color=discord.Colour.blue())
			embed.set_footer(text=footer_testo)
			await interaction.response.send_message(embed=embed, ephemeral=True)
	else:
		embed = discord.Embed(title='No songs playing at the moment', color=discord.Colour.red())
		embed.set_footer(text=footer_testo)
		await interaction.response.send_message(embed=embed, ephemeral=True)





#----------Admin---------------


@client.command()
@commands.guild_only()
@is_me #solo se è il mio id
async def slash_sync(ctx):
	slash = await client.tree.sync()
	#await client.tree.sync(guild=discord.Object(id=1031812528226967603))
	embed = discord.Embed(title=f"Reloading slash {len(slash)}", color=0x2c2f33)
	embed.set_footer(text=footer_testo)
	await ctx.send(embed=embed, delete_after=7)

@client.command()
@commands.guild_only()
@is_me #solo se è il mio id
async def data_send(ctx, f:str=None):
	file_log=discord.File("log.txt")
	file1=discord.File("suggestion_data.json")
	file2=discord.File("ticket_channels.json")
	file3=discord.File("verify_channels.json")
	file3=discord.File("giveaway_data.json")
	await ctx.send(files=[file_log,file1,file2,file3])

@client.command()
@commands.guild_only()
@is_me #solo se è il mio id
async def update(ctx):
	embed = discord.Embed(title="Reloading system...", color=0x2c2f33)
	embed.set_image(url="https://support.discord.com/hc/en-us/article_attachments/206303208/eJwVyksOwiAQANC7sJfp8Ke7Lt15A0MoUpJWGmZcGe-ubl_eW7zGLmaxMZ80A6yNch-rJO4j1SJr73Uv6Wwkcz8gMae8HeXJBOjC5NEap42dokUX_4SotI8GVfBaYYDldr3n3y_jomRtD_H5ArCeI9g.zGz1JSL-9DXgpkX_SkmMDM8NWGg.gif")
	embed.add_field(name = '**System info**', value = f':gear:', inline = False)
	embed.add_field(name = ':computer: **CPU Usage**', value = f'{psutil.cpu_percent()}%', inline = False)
	embed.add_field(name = ':floppy_disk: **Memory Usage**', value = f'{psutil.virtual_memory().percent}%', inline = False)
	embed.add_field(name = ':floppy_disk: **Available Memory**', value = f'{psutil.virtual_memory().available * 100 / psutil.virtual_memory().total}%', inline = False)
	embed.add_field(name = ':globe_with_meridians: **Ping**', value = f'{round(client.latency * 1000)}ms')
	embed.set_footer(text=footer_testo)
	await ctx.send(embed=embed, delete_after=4)
	await asyncio.sleep(5)
	channel = client.get_channel(statuschannel)
	embed = discord.Embed(title=f"**Bot Maintenance🟡**", color=discord.Color.gold())
	await channel.send(embed=embed)
	exit(1)

#return await ctx.invoke(client.bot_get_command("help"), entity="commandname")


#--------Task-Loop------------#

		

@tasks.loop(seconds=20)
async def change_status():
	stbot1 = data["status-1"]
	stbot2 = data["status-2"]
	#statuses = [f"{stbot1}",f"{stbot2}"]
	#status = random.choice(statuses)
	await client.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name=f"{stbot1}"))
	await asyncio.sleep(6)
	await client.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name=f"{stbot2}"))
	await asyncio.sleep(6)
	await client.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name=f"{len(client.guilds)} server"))


#----------Error--------#

def errror_log(error_title, error, info=None):
	file = open(error_log_file, "a")
	time = dt.now()
	log = f"\n\n\nError:\nTime: {time}\nTitle: \n{error_title}\nComplete Error: \n{error}\nInfo: \n{info}"
	file.write(log)
	file.close()


@client.event
async def on_command_error(ctx, error):
	if isinstance(error, discord.ext.commands.errors.CommandNotFound):
		embed = discord.Embed(title="Error: This command does not exist", color=discord.Color.red())
		embed.set_footer(text=footer_testo)
		await ctx.send(embed=embed, delete_after=generic_error_delete_after_time)
		#error-chat
		channel = client.get_channel(errorchannel)
		embed = discord.Embed(title=f"**[Errore]** \nisinstance: ```{isinstance}```\nerror: ```{str(error)}```", color=discord.Color.red())
		await channel.send(embed=embed)
		errror_log(str(isinstance),str(error),"Error Generic: discord.ext.commands.errors.CommandNotFound")
	elif isinstance(error, discord.ext.commands.errors.CommandInvokeError):
		await ctx.message.delete()
		embed = discord.Embed(title=f"Error: Command Invoke Error", color=discord.Color.red())
		embed.add_field(name="Please report the bug using:", value=f"</reportbug:{slash_reportbug_id}>", inline=True)
		embed.set_footer(text=footer_testo)
		await ctx.send(embed=embed, delete_after=generic_error_delete_after_time)
		#error-chat
		channel = client.get_channel(errorchannel)
		#embed = discord.Embed(title=f"**[Errore]** \nisinstance: ```{isinstance}```\nerror: ```{str(error)}```", color=discord.Color.red())
		await channel.send(f"**[Errore]** \nisinstance: ```{isinstance}```\nerror: ```{str(error)}```")
		errror_log(str(isinstance),str(error),"Error Generic: discord.ext.commands.errors.CommandInvokeError")
	elif isinstance(error, discord.ext.commands.errors.MissingPermissions):
		embed = discord.Embed(title="Error: You need the permission to use this command", color=discord.Color.red())
		embed.set_footer(text=footer_testo)
		await ctx.send(embed=embed, delete_after=generic_error_delete_after_time)
		#error-chat
		channel = client.get_channel(errorchannel)
		embed = discord.Embed(title=f"**[Errore]** \nisinstance: ```{isinstance}```\nerror: ```{str(error)}```", color=discord.Color.red())
		await channel.send(embed=embed)
		errror_log(str(isinstance),str(error),"Error Generic: discord.ext.commands.errors.MissingPermissions")
	elif isinstance(error, discord.ext.commands.errors.MemberNotFound):
		embed = discord.Embed(title="Error: Member not found", color=discord.Color.red())
		embed.set_footer(text=footer_testo)
		await ctx.send(embed=embed, delete_after=generic_error_delete_after_time)
		#error-chat
		channel = client.get_channel(errorchannel)
		embed = discord.Embed(title=f"**[Errore]** \nisinstance: ```{isinstance}```\nerror: ```{str(error)}```", color=discord.Color.red())
		await channel.send(embed=embed)
		errror_log(str(isinstance),str(error),"Error Generic: discord.ext.commands.errors.MemberNotFound")
	elif isinstance(error, discord.ext.commands.errors.UserNotFound):
		embed = discord.Embed(title="Error: User not found", color=discord.Color.red())
		embed.set_footer(text=footer_testo)
		await ctx.send(embed=embed, delete_after=generic_error_delete_after_time)
		#error-chat
		channel = client.get_channel(errorchannel)
		embed = discord.Embed(title=f"**[Errore]** \nisinstance: ```{isinstance}```\nerror: ```{str(error)}```", color=discord.Color.red())
		await channel.send(embed=embed)
		errror_log(str(isinstance),str(error),"Error Generic: discord.ext.commands.errors.UserNotFound")
	elif isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
		embed = discord.Embed(title="Error: Missing required argument", color=discord.Color.red())
		embed.set_footer(text=footer_testo)
		await ctx.send(embed=embed, delete_after=generic_error_delete_after_time)
		#error-chat
		channel = client.get_channel(errorchannel)
		embed = discord.Embed(title=f"**[Errore]** \nisinstance: ```{isinstance}```\nerror: ```{str(error)}```", color=discord.Color.red())
		await channel.send(embed=embed)
		errror_log(str(isinstance),str(error),"Error Generic: discord.ext.commands.errors.MissingRequiredArgument")
	elif isinstance(error, discord.ext.commands.errors.NoPrivateMessage):
		embed = discord.Embed(title="Error: This command can only be used in servers", color=discord.Color.red())
		embed.set_footer(text=footer_testo)
		await ctx.send(embed=embed, delete_after=generic_error_delete_after_time)
		#error-chat
		channel = client.get_channel(errorchannel)
		embed = discord.Embed(title=f"**[Errore]** \nisinstance: ```{isinstance}```\nerror: ```{str(error)}```", color=discord.Color.red())
		await channel.send(embed=embed)
		errror_log(str(isinstance),str(error),"Error Generic: discord.ext.commands.errors.NoPrivateMessage")
	elif isinstance(error, discord.errors.HTTPException):
		embed = discord.Embed(title="Error HTTP", color=discord.Color.red())
		embed.add_field(name="Please report the bug using:", value=f"</reportbug:{slash_reportbug_id}>", inline=True)
		embed.set_footer(text=footer_testo)
		await ctx.send(embed=embed, delete_after=generic_error_delete_after_time)
		#error-chat
		channel = client.get_channel(errorchannel)
		await channel.send(f"**[Errore]** \nisinstance: ```{isinstance}```\nerror: ```{str(error)}```")
		errror_log(str(isinstance),str(error),"Error Generic: discord.errors.HTTPException")
	elif isinstance(error, discord.NotFound):
		embed = discord.Embed(title="Error\nNot founded", color=discord.Color.red())
		embed.set_footer(text=footer_testo)
		await ctx.send(embed=embed, delete_after=generic_error_delete_after_time)
	elif isinstance(error, commands.CommandOnCooldown):
		await asyncio.sleep(random.randint(5, 15))
		embed = discord.Embed(title="Error", color=discord.Color.red())
		embed.add_field(name=f'You cannot use this command for', value=f'**{error.retry_after:.2f} seconds**', inline=False)
		await ctx.send(embed=embed, delete_after=generic_error_delete_after_time)
	else:
		if 'not found.' in str(error):
			embed = discord.Embed(title="Error: Not found", color=discord.Color.red())
			embed.set_footer(text=footer_testo)
			await ctx.send(embed=embed, delete_after=generic_error_delete_after_time)
			#error-chat
			channel = client.get_channel(errorchannel)
			await channel.send(f"**[Errore]** \nisinstance: ```{isinstance}```\nerror: ```{str(error)}```")
			errror_log(str(isinstance),str(error),"Error Generic: not found.")    
		else:
			embed = discord.Embed(title="Error: Unknown", color=discord.Color.red())
			embed.add_field(name="Please report the bug using:", value=f"</reportbug:{slash_reportbug_id}>", inline=True)
			embed.set_footer(text=footer_testo)
			await ctx.send(embed=embed, delete_after=generic_error_delete_after_time)
			#error-chat
			channel = client.get_channel(errorchannel)
			await channel.send(f"**[Errore]** \nisinstance: ```{isinstance}```\nerror: ```{str(error)}```")
			errror_log(str(isinstance),str(error),"Error Generic: Unknown")
			raise error
		
	  

client.run(token_json)
