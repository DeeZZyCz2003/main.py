import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

import discord
from discord.ext import commands

from flask import Flask
from threading import Thread

intents = discord.Intents.default()
intents.message_content = True  # Povolení přístupu k obsahu zpráv
intents.members = True

client = commands.Bot(command_prefix='!', intents=intents)  # when user inputs "!", it calls the bot.

faculties = ["Pedagogická fakulta", "Přírodovědecká fakulta", "Fakulta sociálních studií", "Fakulta umění", "Fakulta filozofická", "Lékařská fakulta"]

client.remove_command('help')
@client.event
async def on_ready():
    print("The bot is ready for use!")
    print("-------------------------")
@client.command()
async def hello(ctx):
    await ctx.send("Hi, I am OSU bot.")
@client.command()
async def goodbye(ctx):
    await ctx.send("Goodbye, hope you have a great day.")
@client.event
async def on_member_join(member):
    def check(m):
        return m.author == member and m.channel == member.dm_channel

    try:
        await member.send("Vítejte na serveru. Prosím zadejte svou fakultu jako roli:")

        # Vytvoření hezky formátovaného seznamu fakult
        formatted_faculties = "\n".join(f"- {faculty}" for faculty in faculties)
        await member.send(f"Zde je seznam fakult:\n{formatted_faculties}")

        faculty_msg = await client.wait_for('message', check=check)
        faculty = faculty_msg.content.strip().lower()

        role_name = None
        for fac in faculties:
            if fac.lower() == faculty:
                role_name = fac
                break

        # Debugging output
        print(f"User input: {faculty}")
        print(f"Matched faculty: {role_name}")

        if role_name:
            role = discord.utils.get(member.guild.roles, name=role_name)
            if role is None:
                role = await member.guild.create_role(name=role_name, hoist=True)
            await member.add_roles(role)
            await member.send(f'Byla vám přidělena role: {role_name}')
        else:
            await member.send('Nepodařilo se přiřadit roli. Kontaktujte administrátora.')
    except Exception as e:
        print(f'Error occurred: {e}')
@client.command()
@commands.has_permissions(administrator=True)
async def delete_role(ctx, *, role_name: str):
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if role:
        await role.delete()
        await ctx.send(f'Role {role_name} byla smazána.')
    else:
        await ctx.send(f'Role {role_name} nebyla nalezena.')
@delete_role.error
async def delete_role_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send('Nemáte povolení smazat role.')
@client.command()
@commands.has_permissions(administrator=True)
async def add_role(ctx, *, role_name: str):
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if role:
        await ctx.send(f'Role {role_name} již existuje.')
    else:
        role = await ctx.guild.create_role(name=role_name, hoist=True)
        await ctx.send(f'Role {role_name} byla vytvořena.')
@add_role.error
async def add_role_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send('Nemáte povolení přidat role.')
@client.command()
@commands.has_permissions(administrator=True)
async def set_role(ctx, member: discord.Member, *, role_name: str):
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if role:
        await member.add_roles(role)
        await ctx.send(f'Role {role_name} byla přidělena uživateli {member.mention}.')
    else:
        await ctx.send(f'Role {role_name} nebyla nalezena. Použij příkaz !add_role pro vytvoření nové role.')
@set_role.error
async def set_role_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send('Nemáte povolení přidělit roli.')
@client.command()
@commands.has_permissions(administrator=True)
async def remove_role(ctx, member: discord.Member, *, role_name: str):
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if role:
        await member.remove_roles(role)
        await ctx.send(f'Role {role_name} byla odebrána uživateli {member.mention}.')
    else:
        await ctx.send(f'Role {role_name} nebyla nalezena.')
@remove_role.error
async def remove_role_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send('Nemáte povolení odebrat roli.')
@client.command()
@commands.has_permissions(manage_messages=True)
async def clear_all(ctx):
    await ctx.send('Začínám mazat všechny zprávy...', delete_after=5)
    deleted = 0
    while True:
        deleted_messages = await ctx.channel.purge(limit=100)
        deleted += len(deleted_messages)
        if len(deleted_messages) < 100:
            break
    await ctx.send(f'Bylo vymazáno {deleted} zpráv.', delete_after=5)

@clear_all.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send('Nemáte povolení vymazat zprávy.')

@client.command(name='help')
async def custom_help(ctx):
    help_text = """
    ```
    Dostupné příkazy:
    !add_role <název role>          - Vytvoří novou roli (pouze pro administrátory).
    !set_role <uživatel> <název role>  - Přiřadí roli uživateli (pouze pro administrátory).
    !delete_role <název role>          - Odstraní roli (pouze pro administrátory).
    !hello                             - Pozdraví uživatele.
    !goodbye                           - Rozloučí se s uživatelem.
    !clear_all                         - Vymaže všechny zprávy (pouze pro administrátory).
    ```
    """
    await ctx.send(help_text)

app = Flask('')

@app.route('/')
def home():
    return "I am alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

t = Thread(target=run)
t.start()

client.run(TOKEN)
