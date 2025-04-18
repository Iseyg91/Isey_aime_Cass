import discord
from discord.ext import commands, tasks
from discord import app_commands, Embed, ButtonStyle, ui
from discord.ui import Button, View, Select, Modal, TextInput, button
from discord.ui import Modal, TextInput, Button, View
from discord.utils import get
from discord import TextStyle
from functools import wraps
import os
from discord import app_commands, Interaction, TextChannel, Role
import io
import random
import asyncio
import time
import re
import subprocess
import sys
import math
import traceback
from keep_alive import keep_alive
from datetime import datetime, timedelta
from collections import defaultdict, deque
import pymongo
from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient
import psutil
import pytz
import platform
from discord.ui import Select, View
import random
import discord
from discord.ext import commands
from datetime import datetime, timedelta


token = os.environ['ETHERYA']
intents = discord.Intents.all()
start_time = time.time()
bot = commands.Bot(command_prefix="!!", intents=intents, help_command=None)

# Connexion MongoDB
mongo_uri = os.getenv("MONGO_DB")  # URI de connexion à MongoDB
print("Mongo URI :", mongo_uri)  # Cela affichera l'URI de connexion (assure-toi de ne pas laisser cela en prod)
client = MongoClient(mongo_uri)
db = client['Cass-Eco2']

# Collections
collection = db['ether_eco']  #Stock les Bal
collection2 = db['ether_daily']  #Stock les cd de daily
collection3 = db['ether_slut']  #Stock les cd de slut
collection4 = db['ether_crime']  #Stock les cd de slut
collection5 = db['ether_collect'] #Stock les cd de collect
collection6 = db['ether_work'] #Stock les cd de Work
collection7 = db['ether_inventory'] #Stock les inventaires
collection8 = db['info_cf'] #Stock les Info du cf
collection9 = db['info_logs'] #Stock le Salon logs
collection10 = db['info_bj'] #Stock les Info du Bj
collection11 = db['info_rr'] #Stock les Info de RR
collection12 = db['info_roulette'] #Stock les Info de SM
collection13 = db['info_sm'] #Stock les Info de SM
collection14 = db['ether_rob'] #Stock les cd de Rob

def get_cf_config(guild_id):
    config = collection8.find_one({"guild_id": guild_id})
    if not config:
        # Valeurs par défaut
        config = {
            "guild_id": guild_id,
            "start_chance": 50,
            "max_chance": 100,
            "max_bet": 20000
        }
        collection8.insert_one(config)
    return config

async def log_eco_channel(bot, guild_id, user, action, amount, balance_before, balance_after, note=""):
    config = collection9.find_one({"guild_id": guild_id})
    channel_id = config.get("eco_log_channel") if config else None

    if not channel_id:
        return  # Aucun salon configuré

    channel = bot.get_channel(channel_id)
    if not channel:
        return  # Salon introuvable (peut avoir été supprimé)

    embed = discord.Embed(
        title="💸 Log Économique",
        color=discord.Color.gold(),
        timestamp=datetime.utcnow()
    )
    embed.set_author(name=str(user), icon_url=user.avatar.url if user.avatar else None)
    embed.add_field(name="Action", value=action, inline=True)
    embed.add_field(name="Montant", value=f"{amount} <:ecoEther:1341862366249357374>", inline=True)
    embed.add_field(name="Solde", value=f"Avant: {balance_before}\nAprès: {balance_after}", inline=False)

    if note:
        embed.add_field(name="Note", value=note, inline=False)

    await channel.send(embed=embed)

def load_guild_settings(guild_id):
    # Charger les données de la collection principale
    ether_eco_data = collection.find_one({"guild_id": guild_id}) or {}
    ether_daily_data = collection2.find_one({"guild_id": guild_id}) or {}
    ether_slut_data = collection3.find_one({"guild_id": guild_id}) or {}
    ether_crime_data = collection4.find_one({"guild_id": guild_id}) or {}
    ether_collect = collection5.find_one({"guild_id": guild_id}) or {}
    ether_work_data = collection6.find_one({"guild_id": guild_id}) or {}
    ether_inventory_data = collection7.find_one({"guild_id": guild_id}) or {}
    info_cf_data = collection8.find_one({"guild_id": guild_id}) or {}
    info_logs_data = collection9.find_one({"guild_id": guild_id}) or {}
    info_bj_data = collection10.find_one({"guild_id": guild_id}) or {}
    info_rr_data = collection11.find_one({"guild_id": guild_id}) or {}
    info_roulette_data = collection12.find_one({"guild_id": guild_id}) or {}
    info_sm_roulette_data = collection13.find_one({"guild_id": guild_id}) or {}
    ether_rob_data = collection14.find_one({"guild_id": guild_id}) or {}

    # Débogage : Afficher les données de setup
    print(f"Setup data for guild {guild_id}: {setup_data}")

    combined_data = {
        "ether_eco": ether_eco_data,
        "ether_daily": ether_daily_data,
        "ether_slut": ether_slut_data,
        "ether_crime": ether_crime_data,
        "ether_collect": ether_collect_data,
        "ether_work": ether_work_data,
        "ether_inventory": ether_inventory_data,
        "info_cf": info_cf_data,
        "info_logs": info_logs_data,
        "info_bj": info_bj_data,
        "info_rr": info_rr_data,
        "info_roulette": info_roulette_data,
        "info_sm": info_sm_data,
        "ether_rob": ether_rob_data

    }

    return combined_data

@bot.event
async def on_ready():
    print(f"✅ Le bot {bot.user} est maintenant connecté ! (ID: {bot.user.id})")

    # Mise à jour du statut avec l'activité de stream "Etherya"
    activity = discord.Activity(type=discord.ActivityType.streaming, name="Etherya", url="https://www.twitch.tv/tonstream")
    await bot.change_presence(activity=activity, status=discord.Status.online)

    print(f"🎉 **{bot.user}** est maintenant connecté et affiche son activité de stream avec succès !")

    # Afficher les commandes chargées
    print("📌 Commandes disponibles 😊")
    for command in bot.commands:
        print(f"- {command.name}")

    try:
        # Synchroniser les commandes avec Discord
        synced = await bot.tree.sync()  # Synchronisation des commandes slash
        print(f"✅ Commandes slash synchronisées : {[cmd.name for cmd in synced]}")
    except Exception as e:
        print(f"❌ Erreur de synchronisation des commandes slash : {e}")

# Gestion des erreurs globales pour toutes les commandes
@bot.event
async def on_error(event, *args, **kwargs):
    print(f"Une erreur s'est produite : {event}")
    embed = discord.Embed(
        title="❗ Erreur inattendue",
        description="Une erreur s'est produite lors de l'exécution de la commande. Veuillez réessayer plus tard.",
        color=discord.Color.red()
    )
    await args[0].response.send_message(embed=embed)

@bot.event
async def on_message(message):
    # Ignorer les messages du bot lui-même
    if message.author.bot:
        return

    # Obtenir les informations de l'utilisateur
    user = message.author
    guild_id = message.guild.id
    user_id = user.id

    # Générer un montant aléatoire entre 5 et 20 coins
    coins_to_add = random.randint(5, 20)

    # Ajouter les coins au portefeuille de l'utilisateur
    collection.update_one(
        {"guild_id": guild_id, "user_id": user_id},
        {"$inc": {"wallet": coins_to_add}},
        upsert=True
    )

    # Appeler le traitement habituel des commandes
    await bot.process_commands(message)

@bot.hybrid_command(
    name="uptime",
    description="Affiche l'uptime du bot."
)
async def uptime(ctx):
    uptime_seconds = round(time.time() - start_time)
    days = uptime_seconds // (24 * 3600)
    hours = (uptime_seconds % (24 * 3600)) // 3600
    minutes = (uptime_seconds % 3600) // 60
    seconds = uptime_seconds % 60
    embed = discord.Embed(
        title="Uptime du bot",
        description=f"Le bot est en ligne depuis : {days} jours, {hours} heures, {minutes} minutes, {seconds} secondes",
        color=discord.Color.blue()
    )
    embed.set_footer(text=f"♥️by Iseyg", icon_url=ctx.author.avatar.url)
    await ctx.send(embed=embed)


@bot.hybrid_command(name="balance", aliases=["bal", "money"], description="Affiche ta balance ou celle d'un autre utilisateur.")
async def bal(ctx: commands.Context, user: discord.User = None):
    user = user or ctx.author
    guild_id = ctx.guild.id
    user_id = user.id

    # Cherche les données de l'utilisateur
    data = collection.find_one({"guild_id": guild_id, "user_id": user_id})

    # Si l'utilisateur n'a pas de données, on initialise avec 1500 coins en portefeuille
    if not data:
        data = {
            "guild_id": guild_id,
            "user_id": user_id,
            "wallet": 1500,
            "bank": 0
        }
        collection.insert_one(data)

    # Récupération des données à afficher
    balance = data.get("wallet", 0)
    bank = data.get("bank", 0)
    total = balance + bank

    # Création de l'embed
    embed = discord.Embed(title=f"💰 Balance de {user.display_name}", color=discord.Color.gold())
    embed.add_field(name="Portefeuille", value=f"{balance} <:ecoEther:1341862366249357374>", inline=True)
    embed.add_field(name="Banque", value=f"{bank} 🏦", inline=True)
    embed.add_field(name="Total", value=f"{total} 💵", inline=False)
    embed.set_footer(text=f"Demandé par {ctx.author}", icon_url=ctx.author.display_avatar.url)

    await ctx.send(embed=embed)

@bot.hybrid_command(name="deposit", aliases=["dep"], description="Dépose de l'argent de ton portefeuille vers ta banque.")
@app_commands.describe(amount="Montant à déposer (ou 'all')")
async def deposit(ctx: commands.Context, amount: str = None):
    if amount is None:
        return await ctx.send("❌ Tu dois spécifier un montant ou `all`.")

    user = ctx.author
    guild_id = ctx.guild.id
    user_id = user.id

    # Chercher les données actuelles
    data = collection.find_one({"guild_id": guild_id, "user_id": user_id}) or {"wallet": 0, "bank": 0}

    wallet = data.get("wallet", 0)
    bank = data.get("bank", 0)

    # Gérer le cas "all"
    if amount.lower() == "all":
        if wallet == 0:
            return await ctx.send("💸 Tu n'as rien à déposer.")
        deposited_amount = wallet
    else:
        # Vérifie que c'est un nombre valide
        if not amount.isdigit():
            return await ctx.send("❌ Montant invalide. Utilise un nombre ou `all`.")
        deposited_amount = int(amount)
        if deposited_amount <= 0:
            return await ctx.send("❌ Tu dois déposer un montant supérieur à zéro.")
        if deposited_amount > wallet:
            return await ctx.send("❌ Tu n'as pas assez d'argent dans ton portefeuille.")

    # Mise à jour dans la base de données
    collection.update_one(
        {"guild_id": guild_id, "user_id": user_id},
        {"$inc": {"wallet": -deposited_amount, "bank": deposited_amount}},
        upsert=True
    )

    # Création de l'embed de succès
    embed = discord.Embed(
        title="✅ Dépôt effectué avec succès!",
        description=f"Tu as déposé **{deposited_amount} <:ecoEther:1341862366249357374>** dans ta banque.",
        color=discord.Color.green()
    )
    embed.set_footer(text=f"Demande effectuée par {ctx.author}", icon_url=ctx.author.display_avatar.url)

    await ctx.send(embed=embed)

@bot.hybrid_command(name="withdraw", aliases=["with"], description="Retire de l'argent de ta banque vers ton portefeuille.")
async def withdraw(ctx: commands.Context, amount: str):
    user = ctx.author
    guild_id = ctx.guild.id
    user_id = user.id

    # Chercher les données actuelles
    data = collection.find_one({"guild_id": guild_id, "user_id": user_id}) or {"wallet": 0, "bank": 0}

    wallet = data.get("wallet", 0)
    bank = data.get("bank", 0)

    # Gérer le cas "all"
    if amount.lower() == "all":
        if bank == 0:
            return await ctx.send("💸 Tu n'as rien à retirer.")
        withdrawn_amount = bank
    else:
        # Vérifie que c'est un nombre valide
        if not amount.isdigit():
            return await ctx.send("❌ Montant invalide. Utilise un nombre ou `all`.")
        withdrawn_amount = int(amount)
        if withdrawn_amount <= 0:
            return await ctx.send("❌ Tu dois retirer un montant supérieur à zéro.")
        if withdrawn_amount > bank:
            return await ctx.send("❌ Tu n'as pas assez d'argent dans ta banque.")

    # Mise à jour dans la base de données
    collection.update_one(
        {"guild_id": guild_id, "user_id": user_id},
        {"$inc": {"wallet": withdrawn_amount, "bank": -withdrawn_amount}},
        upsert=True
    )

    # Création de l'embed de succès
    embed = discord.Embed(
        title="✅ Retrait effectué avec succès!",
        description=f"Tu as retiré **{withdrawn_amount} <:ecoEther:1341862366249357374>** de ta banque vers ton portefeuille.",
        color=discord.Color.green()
    )
    embed.set_footer(text=f"Demande effectuée par {ctx.author}", icon_url=ctx.author.display_avatar.url)

    await ctx.send(embed=embed)

@bot.hybrid_command(name="add-money", description="Ajoute de l'argent à un utilisateur (réservé aux administrateurs).")
@app_commands.describe(
    user="L'utilisateur à créditer",
    amount="Le montant à ajouter",
    account="Choisis où ajouter l'argent : bank ou wallet"
)
@commands.has_permissions(administrator=True)
async def add_money(ctx: commands.Context, user: discord.User, amount: int, account: str):
    if account.lower() not in ["wallet", "bank"]:
        return await ctx.send("❌ Veuillez choisir `wallet` ou `bank` comme compte cible.")

    if amount <= 0:
        return await ctx.send("❌ Le montant doit être supérieur à zéro.")

    guild_id = ctx.guild.id
    user_id = user.id

    # Récupérer l'état actuel du solde pour cet utilisateur
    balance_data = collection.find_one({"guild_id": guild_id, "user_id": user_id})
    balance_before = balance_data.get(account.lower(), 0) if balance_data else 0

    # Mise à jour MongoDB
    collection.update_one(
        {"guild_id": guild_id, "user_id": user_id},
        {"$inc": {account.lower(): amount}},
        upsert=True
    )

    # Nouveau solde après l'ajout
    balance_after = balance_before + amount

    # Log dans le salon de logs économique
    await log_eco_channel(
        bot,
        guild_id,
        user,
        "Ajout d'argent",
        amount,
        balance_before,
        balance_after,
        f"Ajout de {amount} <:ecoEther:1341862366249357374> dans le compte {account.lower()} de {user.mention} par {ctx.author.mention}."
    )

    # Création de l'embed de confirmation
    embed = discord.Embed(
        title="✅ Argent ajouté avec succès !",
        description=f"**{amount} <:ecoEther:1341862366249357374>** a été ajouté à {user.mention} dans son **{account.lower()}**.",
        color=discord.Color.green()
    )
    embed.set_footer(text=f"Action réalisée par {ctx.author}", icon_url=ctx.author.display_avatar.url)

    await ctx.send(embed=embed)

# Gestion des erreurs de permissions
@add_money.error
async def add_money_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("🚫 Tu n'as pas la permission d'utiliser cette commande.")

@bot.hybrid_command(name="remove-money", description="Retire de l'argent à un utilisateur.")
@app_commands.describe(user="L'utilisateur ciblé", amount="Le montant à retirer", location="Choisis entre wallet ou bank")
@app_commands.choices(location=[
    app_commands.Choice(name="Wallet", value="wallet"),
    app_commands.Choice(name="Bank", value="bank"),
])
@commands.has_permissions(administrator=True)
async def remove_money(ctx: commands.Context, user: discord.User, amount: int, location: app_commands.Choice[str]):
    if amount <= 0:
        return await ctx.send("❌ Le montant doit être supérieur à 0.")

    guild_id = ctx.guild.id
    user_id = user.id

    field = location.value

    # Vérifie le solde actuel
    data = collection.find_one({"guild_id": guild_id, "user_id": user_id}) or {"wallet": 0, "bank": 0}
    current_balance = data.get(field, 0)

    if current_balance < amount:
        return await ctx.send(f"❌ {user.display_name} n'a pas assez de fonds dans son `{field}` pour retirer {amount} <:ecoEther:1341862366249357374>.")

    # Solde avant le retrait
    balance_before = current_balance

    # Mise à jour dans la base de données
    collection.update_one(
        {"guild_id": guild_id, "user_id": user_id},
        {"$inc": {field: -amount}},
        upsert=True
    )

    # Solde après le retrait
    balance_after = balance_before - amount

    # Log dans le salon de logs économique
    await log_eco_channel(
        bot,
        guild_id,
        user,
        "Retrait d'argent",
        -amount,
        balance_before,
        balance_after,
        f"Retrait de {amount} <:ecoEther:1341862366249357374> dans le compte {field} de {user.mention} par {ctx.author.mention}."
    )

    # Création de l'embed de confirmation
    embed = discord.Embed(
        title="✅ Retrait effectué avec succès !",
        description=f"**{amount} <:ecoEther:1341862366249357374>** a été retiré de la **{field}** de {user.mention}.",
        color=discord.Color.green()
    )
    embed.set_footer(text=f"Action réalisée par {ctx.author}", icon_url=ctx.author.display_avatar.url)

    await ctx.send(embed=embed)

# Gestion des erreurs de permissions
@remove_money.error
async def remove_money_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Tu dois être administrateur pour utiliser cette commande.")
    else:
        await ctx.send("❌ Une erreur est survenue.")

@bot.hybrid_command(name="set-money", description="Définit un montant exact dans le wallet ou la bank d’un utilisateur.")
@app_commands.describe(user="L'utilisateur ciblé", amount="Le montant à définir", location="Choisis entre wallet ou bank")
@app_commands.choices(location=[
    app_commands.Choice(name="Wallet", value="wallet"),
    app_commands.Choice(name="Bank", value="bank"),
])
@commands.has_permissions(administrator=True)
async def set_money(ctx: commands.Context, user: discord.User, amount: int, location: app_commands.Choice[str]):
    if amount < 0:
        return await ctx.send("❌ Le montant ne peut pas être négatif.")

    guild_id = ctx.guild.id
    user_id = user.id
    field = location.value

    # Récupération du solde actuel avant modification
    data = collection.find_one({"guild_id": guild_id, "user_id": user_id}) or {"wallet": 0, "bank": 0}
    balance_before = data.get(field, 0)

    # Mise à jour de la base de données pour définir le montant exact
    collection.update_one(
        {"guild_id": guild_id, "user_id": user_id},
        {"$set": {field: amount}},
        upsert=True
    )

    # Log dans le salon de logs économiques
    await log_eco_channel(
        bot,
        guild_id,
        user,
        "Définition du solde",
        amount - balance_before,  # Calcul du changement de solde
        balance_before,
        amount,
        f"Le solde du compte `{field}` de {user.mention} a été défini à {amount} <:ecoEther:1341862366249357374> par {ctx.author.mention}."
    )

    # Création de l'embed de confirmation
    embed = discord.Embed(
        title="✅ Montant défini avec succès !",
        description=f"Le montant de **{field}** de {user.mention} a été défini à **{amount} <:ecoEther:1341862366249357374>**.",
        color=discord.Color.green()
    )
    embed.set_footer(text=f"Action réalisée par {ctx.author}", icon_url=ctx.author.display_avatar.url)

    await ctx.send(embed=embed)

# Gestion des erreurs de permissions
@set_money.error
async def set_money_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Tu dois être administrateur pour utiliser cette commande.")
    else:
        await ctx.send("❌ Une erreur est survenue.")

@bot.hybrid_command(name="pay", description="Paie un utilisateur avec tes coins.")
@app_commands.describe(user="L'utilisateur à qui envoyer de l'argent", amount="Montant à transférer")
async def pay(ctx: commands.Context, user: discord.User, amount: int):
    sender = ctx.author
    if user.id == sender.id:
        return await ctx.send("❌ Tu ne peux pas te payer toi-même.")
    if amount <= 0:
        return await ctx.send("❌ Le montant doit être supérieur à zéro.")

    guild_id = ctx.guild.id

    # Récupère les données de l'expéditeur
    sender_data = collection.find_one({"guild_id": guild_id, "user_id": sender.id}) or {"wallet": 0}
    if sender_data["wallet"] < amount:
        return await ctx.send("❌ Tu n’as pas assez d'argent dans ton wallet.")

    # Déduit les fonds de l'expéditeur
    collection.update_one(
        {"guild_id": guild_id, "user_id": sender.id},
        {"$inc": {"wallet": -amount}},
        upsert=True
    )

    # Ajoute les fonds au destinataire
    collection.update_one(
        {"guild_id": guild_id, "user_id": user.id},
        {"$inc": {"wallet": amount}},
        upsert=True
    )

    # Log dans le salon de logs économiques
    await log_eco_channel(
        bot,
        guild_id,
        user,
        "Paiement effectué",
        -amount,  # Le payeur perd de l'argent
        sender_data["wallet"],
        sender_data["wallet"] - amount,
        f"{sender.mention} a payé **{amount} <:ecoEther:1341862366249357374>** à {user.mention}."
    )

    # Création de l'embed de confirmation
    embed = discord.Embed(
        title="✅ Paiement effectué avec succès !",
        description=f"{sender.mention} a payé **{amount} <:ecoEther:1341862366249357374>** à {user.mention}.",
        color=discord.Color.green()
    )
    embed.set_footer(text=f"Demande effectuée par {ctx.author}", icon_url=ctx.author.display_avatar.url)

    await ctx.send(embed=embed)

# Gestion des erreurs
@pay.error
async def pay_error(ctx, error):
    await ctx.send("❌ Une erreur est survenue lors du paiement.")

@bot.hybrid_command(name="work", aliases=["wk"], description="Travaille et gagne de l'argent !")
async def work(ctx: commands.Context):
    user = ctx.author
    guild_id = ctx.guild.id
    user_id = user.id

    # Vérifier le cooldown de 30 minutes
    now = datetime.utcnow()
    cooldown_data = collection6.find_one({"guild_id": guild_id, "user_id": user_id}) or {}
    last_work_time = cooldown_data.get("last_work_time", None)

    if last_work_time:
        time_diff = now - last_work_time
        if time_diff < timedelta(minutes=30):
            remaining_time = timedelta(minutes=30) - time_diff
            minutes_left = remaining_time.total_seconds() // 60
            return await ctx.send(f"❌ Tu dois attendre encore **{int(minutes_left)} minutes** avant de pouvoir retravailler.")

    # Gagner de l'argent entre 200 et 2000
    amount = random.randint(200, 2000)

    # Liste de 20 messages possibles
    messages = [
        f"Tu as travaillé dur et gagné **{amount} <:ecoEther:1341862366249357374>**. Bien joué !",
        f"Bravo ! Tu as gagné **{amount} <:ecoEther:1341862366249357374>** après ton travail.",
        f"Tu as travaillé avec assiduité et tu récoltes **{amount} <:ecoEther:1341862366249357374>**.",
        f"Du bon travail ! Voici **{amount} <:ecoEther:1341862366249357374>** pour toi.",
        f"Félicitations, tu as gagné **{amount} <:ecoEther:1341862366249357374>** pour ton travail.",
        f"Grâce à ton travail, tu as gagné **{amount} <:ecoEther:1341862366249357374>**.",
        f"Tu as gagné **{amount} <:ecoEther:1341862366249357374>** après une journée de travail bien remplie !",
        f"Un bon travail mérite **{amount} <:ecoEther:1341862366249357374>**. Félicitations !",
        f"Après une journée difficile, tu récoltes **{amount} <:ecoEther:1341862366249357374>**.",
        f"Tu as travaillé dur et mérites tes **{amount} <:ecoEther:1341862366249357374>**.",
        f"Tu as fait un excellent travail et gagné **{amount} <:ecoEther:1341862366249357374>**.",
        f"Un travail acharné rapporte **{amount} <:ecoEther:1341862366249357374>**.",
        f"Bien joué ! **{amount} <:ecoEther:1341862366249357374>** ont été ajoutés à ta balance.",
        f"Ton travail t'a rapporté **{amount} <:ecoEther:1341862366249357374>**.",
        f"Tu as bien bossé et gagné **{amount} <:ecoEther:1341862366249357374>**.",
        f"Les fruits de ton travail : **{amount} <:ecoEther:1341862366249357374>**.",
        f"Un travail bien fait t'a rapporté **{amount} <:ecoEther:1341862366249357374>**.",
        f"Tu es payé pour ton dur labeur : **{amount} <:ecoEther:1341862366249357374>**.",
        f"Voici ta récompense pour ton travail : **{amount} <:ecoEther:1341862366249357374>**.",
        f"Ton travail t'a rapporté une belle somme de **{amount} <:ecoEther:1341862366249357374>**.",
        f"Tu as gagné **{amount} <:ecoEther:1341862366249357374>** pour ta persévérance et ton travail.",
    ]

    # Sélectionner un message au hasard
    message = random.choice(messages)

    # Récupérer le solde avant l'ajout d'argent
    user_data = collection.find_one({"guild_id": guild_id, "user_id": user_id}) or {"wallet": 0}
    initial_balance = user_data["wallet"]

    # Mettre à jour le cooldown et l'argent de l'utilisateur
    collection6.update_one(
        {"guild_id": guild_id, "user_id": user_id},
        {"$set": {"last_work_time": now}},
        upsert=True
    )

    # Ajouter de l'argent au wallet de l'utilisateur
    collection.update_one(
        {"guild_id": guild_id, "user_id": user_id},
        {"$inc": {"wallet": amount}},
        upsert=True
    )

    # Log dans le salon de logs économiques
    await log_eco_channel(
        bot,
        guild_id,
        user,
        "Travail effectué",
        amount,  # L'utilisateur gagne de l'argent
        initial_balance,
        initial_balance + amount,
        f"{user.mention} a gagné **{amount} <:ecoEther:1341862366249357374>** pour son travail."
    )

    # Création de l'embed de confirmation
    embed = discord.Embed(
        title="✅ Travail accompli avec succès !",
        description=f"{user.mention}, tu as gagné **{amount} <:ecoEther:1341862366249357374>** pour ton travail.",
        color=discord.Color.green()
    )
    embed.set_footer(text=f"Action effectuée par {ctx.author}", icon_url=ctx.author.display_avatar.url)

    await ctx.send(embed=embed)

# Gestion des erreurs
@work.error
async def work_error(ctx, error):
    await ctx.send("❌ Une erreur est survenue lors de la commande de travail.")

@bot.hybrid_command(name="slut", description="Essaie ta chance et gagne ou perds de l'argent.")
async def slut(ctx: commands.Context):
    user = ctx.author
    guild_id = ctx.guild.id
    user_id = user.id

    # Vérifier le cooldown de 30 minutes
    now = datetime.utcnow()
    cooldown_data = collection3.find_one({"guild_id": guild_id, "user_id": user_id}) or {}
    last_slut_time = cooldown_data.get("last_slut_time", None)

    if last_slut_time:
        time_diff = now - last_slut_time
        if time_diff < timedelta(minutes=30):
            remaining_time = timedelta(minutes=30) - time_diff
            minutes_left = remaining_time.total_seconds() // 60
            return await ctx.send(f"❌ Tu dois attendre encore **{int(minutes_left)} minutes** avant de pouvoir recommencer.")

    # Gagner ou perdre de l'argent
    gain_or_loss = random.choice(["gain", "loss"])

    if gain_or_loss == "gain":
        amount = random.randint(250, 2000)
        # Liste de 20 messages de succès
        messages = [
            f"Tu as eu de la chance et gagné **{amount} <:ecoEther:1341862366249357374>**.",
            f"Félicitations ! Tu as gagné **{amount} <:ecoEther:1341862366249357374>**.",
            f"Bravo, tu as gagné **{amount} <:ecoEther:1341862366249357374>** grâce à ta chance.",
            f"Tu as réussi à gagner **{amount} <:ecoEther:1341862366249357374>**.",
            f"Bien joué ! Tu as gagné **{amount} <:ecoEther:1341862366249357374>**.",
            f"Une grande chance t'a souri, tu as gagné **{amount} <:ecoEther:1341862366249357374>**.",
            f"Tu as gagné **{amount} <:ecoEther:1341862366249357374>**. Continue comme ça !",
            f"Tu as gagné **{amount} <:ecoEther:1341862366249357374>**. Bien joué !",
            f"Chanceux, tu as gagné **{amount} <:ecoEther:1341862366249357374>**.",
            f"Une belle récompense ! **{amount} <:ecoEther:1341862366249357374>** pour toi.",
            f"Tu as récolté **{amount} <:ecoEther:1341862366249357374>** grâce à ta chance.",
            f"Tu es vraiment chanceux, tu as gagné **{amount} <:ecoEther:1341862366249357374>**.",
            f"Tu as fait un gros coup, **{amount} <:ecoEther:1341862366249357374>** pour toi.",
            f"Tu as de la chance, tu as gagné **{amount} <:ecoEther:1341862366249357374>**.",
            f"Tu as fait le bon choix, tu as gagné **{amount} <:ecoEther:1341862366249357374>**.",
            f"Ta chance t'a permis de gagner **{amount} <:ecoEther:1341862366249357374>**.",
            f"Voici ta récompense de **{amount} <:ecoEther:1341862366249357374>** pour ta chance.",
            f"Bravo, tu es maintenant plus riche de **{amount} <:ecoEther:1341862366249357374>**.",
            f"Tu as gagné **{amount} <:ecoEther:1341862366249357374>**. Félicitations !",
            f"Ta chance t'a permis de remporter **{amount} <:ecoEther:1341862366249357374>**."
        ]
        # Sélectionner un message au hasard
        message = random.choice(messages)

        # Ajouter de l'argent au wallet de l'utilisateur
        collection.update_one(
            {"guild_id": guild_id, "user_id": user_id},
            {"$inc": {"wallet": amount}},
            upsert=True
        )

    else:
        amount = random.randint(250, 2000)
        # Liste de 20 messages de perte
        messages = [
            f"Malheureusement, tu as perdu **{amount} <:ecoEther:1341862366249357374>**.",
            f"Désolé, tu perds **{amount} <:ecoEther:1341862366249357374>**.",
            f"La chance ne t'a pas souri cette fois, tu as perdu **{amount} <:ecoEther:1341862366249357374>**.",
            f"T'as perdu **{amount} <:ecoEther:1341862366249357374>**. Mieux vaut retenter une autre fois.",
            f"Ah non, tu as perdu **{amount} <:ecoEther:1341862366249357374>**.",
            f"Pas de chance, tu perds **{amount} <:ecoEther:1341862366249357374>**.",
            f"Oups, tu perds **{amount} <:ecoEther:1341862366249357374>** cette fois.",
            f"Pas de chance, tu viens de perdre **{amount} <:ecoEther:1341862366249357374>**.",
            f"Tu as perdu **{amount} <:ecoEther:1341862366249357374>**. C'est dommage.",
            f"Tu as fait une mauvaise chance, tu perds **{amount} <:ecoEther:1341862366249357374>**.",
            f"Ce coup-ci, tu perds **{amount} <:ecoEther:1341862366249357374>**.",
            f"Malheureusement, tu perds **{amount} <:ecoEther:1341862366249357374>**.",
            f"T'es tombé sur une mauvaise chance, tu perds **{amount} <:ecoEther:1341862366249357374>**.",
            f"Tu perds **{amount} <:ecoEther:1341862366249357374>**. Retente ta chance !",
            f"T'as perdu **{amount} <:ecoEther:1341862366249357374>**. La prochaine sera la bonne.",
            f"Pas de chance, tu perds **{amount} <:ecoEther:1341862366249357374>**.",
            f"Tu as perdu **{amount} <:ecoEther:1341862366249357374>** cette fois.",
            f"Tu perds **{amount} <:ecoEther:1341862366249357374>**. Essaye encore !",
            f"Tu n'as pas eu de chance, tu perds **{amount} <:ecoEther:1341862366249357374>**.",
            f"Tu perds **{amount} <:ecoEther:1341862366249357374>**. La chance reviendra !"
        ]
        # Sélectionner un message de perte au hasard
        message = random.choice(messages)

        # Déduire de l'argent du wallet de l'utilisateur
        collection.update_one(
            {"guild_id": guild_id, "user_id": user_id},
            {"$inc": {"wallet": -amount}},
            upsert=True
        )

    # Mettre à jour le cooldown
    collection3.update_one(
        {"guild_id": guild_id, "user_id": user_id},
        {"$set": {"last_slut_time": now}},
        upsert=True
    )

    # Log dans le salon de logs économiques
    await log_eco_channel(
        bot,
        guild_id,
        user,
        "Chance",
        amount if gain_or_loss == "gain" else -amount,  # L'utilisateur gagne ou perd de l'argent
        None,  # Aucun solde avant, uniquement gain/perte
        None,  # Aucun solde après
        message  # Message de résultat
    )

    # Création de l'embed de résultat
    embed = discord.Embed(
        title="🎰 Résultat de ta chance",
        description=message,
        color=discord.Color.blue()
    )
    embed.set_footer(text=f"Action effectuée par {ctx.author}", icon_url=ctx.author.display_avatar.url)

    await ctx.send(embed=embed)

# Gestion des erreurs
@slut.error
async def slut_error(ctx, error):
    await ctx.send("❌ Une erreur est survenue lors de la commande.")

@bot.hybrid_command(name="crime", description="Participe à un crime pour essayer de gagner de l'argent, mais attention, tu pourrais perdre !")
async def crime(ctx: commands.Context):
    user = ctx.author
    guild_id = ctx.guild.id
    user_id = user.id

    # Vérifier le cooldown de 30 minutes
    now = datetime.utcnow()
    cooldown_data = collection4.find_one({"guild_id": guild_id, "user_id": user_id}) or {}
    last_crime_time = cooldown_data.get("last_crime_time", None)

    if last_crime_time:
        time_diff = now - last_crime_time
        if time_diff < timedelta(minutes=30):
            remaining_time = timedelta(minutes=30) - time_diff
            minutes_left = remaining_time.total_seconds() // 60
            return await ctx.send(f"❌ Tu dois attendre encore **{int(minutes_left)} minutes** avant de pouvoir recommencer.")

    # Gagner ou perdre de l'argent
    gain_or_loss = random.choice(["gain", "loss"])

    if gain_or_loss == "gain":
        amount = random.randint(250, 2000)
        # Liste de 20 messages de succès
        messages = [
            f"Tu as réussi ton crime et gagné **{amount} <:ecoEther:1341862366249357374>**.",
            f"Félicitations ! Tu as gagné **{amount} <:ecoEther:1341862366249357374>** après ton crime.",
            f"Bien joué, tu as gagné **{amount} <:ecoEther:1341862366249357374>** grâce à ton coup de maître.",
            # ... (les autres messages)
        ]
        # Sélectionner un message de succès au hasard
        message = random.choice(messages)

        # Ajouter de l'argent au wallet de l'utilisateur
        collection.update_one(
            {"guild_id": guild_id, "user_id": user_id},
            {"$inc": {"wallet": amount}},
            upsert=True
        )

        # Log dans le salon économique
        balance_before = collection.find_one({"guild_id": guild_id, "user_id": user_id}).get("wallet", 0)
        balance_after = balance_before + amount
        await log_eco_channel(bot, guild_id, user, "Gain après crime", amount, balance_before, balance_after)

    else:
        amount = random.randint(250, 2000)
        # Liste de 20 messages de perte
        messages = [
            f"Malheureusement, ton crime a échoué et tu as perdu **{amount} <:ecoEther:1341862366249357374>**.",
            f"Pas de chance, tu perds **{amount} <:ecoEther:1341862366249357374>** après ton crime.",
            f"Ton crime a échoué et tu perds **{amount} <:ecoEther:1341862366249357374>**.",
            # ... (les autres messages)
        ]
        # Sélectionner un message de perte au hasard
        message = random.choice(messages)

        # Déduire de l'argent du wallet de l'utilisateur
        collection.update_one(
            {"guild_id": guild_id, "user_id": user_id},
            {"$inc": {"wallet": -amount}},
            upsert=True
        )

        # Log dans le salon économique
        balance_before = collection.find_one({"guild_id": guild_id, "user_id": user_id}).get("wallet", 0)
        balance_after = balance_before - amount
        await log_eco_channel(bot, guild_id, user, "Perte après crime", amount, balance_before, balance_after)

    # Mettre à jour le cooldown
    collection4.update_one(
        {"guild_id": guild_id, "user_id": user_id},
        {"$set": {"last_crime_time": now}},
        upsert=True
    )

    # Création de l'embed de résultat
    embed = discord.Embed(
        title="💥 Résultat de ton crime",
        description=message,
        color=discord.Color.red()
    )
    embed.set_footer(text=f"Action effectuée par {ctx.author}", icon_url=ctx.author.display_avatar.url)

    await ctx.send(embed=embed)

# Gestion des erreurs
@crime.error
async def crime_error(ctx, error):
    await ctx.send("❌ Une erreur est survenue lors de la commande.")

@bot.command(name="buy", aliases=["chicken", "c", "h", "i", "k", "e", "n"])
async def buy_item(ctx, item: str = "chicken"):
    user = ctx.author
    guild_id = ctx.guild.id
    user_id = user.id

    # Forcer l'achat d'un chicken pour toutes les aliases
    item = "chicken"

    # Vérifier si l'utilisateur possède déjà un poulet
    data = collection7.find_one({"guild_id": guild_id, "user_id": user_id})
    if data and data.get("chicken", False):
        await ctx.send(f"{user.mention}, tu as déjà un poulet ! Tu ne peux pas en acheter un autre tant que tu n'as pas perdu le précédent.")
        return

    # Vérifier le solde de l'utilisateur
    balance_data = collection.find_one({"guild_id": guild_id, "user_id": user_id})
    balance = balance_data.get("wallet", 0) if balance_data else 0

    # Liste des objets à acheter et leurs prix
    items_for_sale = {
        "chicken": 100,
    }

    # Vérification de l'objet choisi
    if item in items_for_sale:
        price = items_for_sale[item]

        if balance >= price:
            # Retirer l'argent du wallet de l'utilisateur
            collection.update_one(
                {"guild_id": guild_id, "user_id": user_id},
                {"$inc": {"wallet": -price}},
                upsert=True
            )

            # Ajouter l'objet au profil de l'utilisateur (ici, un poulet)
            collection7.update_one(
                {"guild_id": guild_id, "user_id": user_id},
                {"$set": {item: True}},
                upsert=True
            )

            # Logs économiques
            balance_after = balance - price
            await log_eco_channel(
                bot, guild_id, user, "Achat", price, balance, balance_after,
                f"Achat d'un **{item}**"
            )

            # Création d'un embed pour rendre l'achat plus visuel
            embed = discord.Embed(
                title=f"Achat réussi !",
                description=f"{user.mention} a acheté un **{item}** pour **{price} <:ecoEther:1341862366249357374>** !",
                color=discord.Color.green()
            )
            embed.set_footer(text=f"Merci pour ton achat !")
            await ctx.send(embed=embed)

        else:
            await ctx.send(f"{user.mention}, tu n'as pas assez de coins pour acheter un **{item}** !")

    else:
        await ctx.send(f"{user.mention}, cet objet n'est pas disponible à l'achat.")

@bot.command(name="cock-fight", aliases=["cf"])
async def cock_fight(ctx, amount: str):
    user = ctx.author
    guild_id = ctx.guild.id
    user_id = user.id

    config = get_cf_config(guild_id)
    max_bet = config.get("max_bet", 20000)
    max_chance = config.get("max_chance", 100)
    start_chance = config.get("start_chance", 50)

    data = collection7.find_one({"guild_id": guild_id, "user_id": user_id})
    if not data or not data.get("chicken", False):
        await ctx.send(f"{user.mention}, tu n'as pas de poulet ! Utilise la commande `!!buy chicken` pour en acheter un.")
        return

    balance_data = collection.find_one({"guild_id": guild_id, "user_id": user_id})
    balance = balance_data.get("wallet", 0) if balance_data else 0

    if amount.lower() == "all":
        if balance == 0:
            await ctx.send(f"{user.mention}, ton portefeuille est vide.")
            return
        if balance > max_bet:
            await ctx.send(f"{user.mention}, ta mise dépasse la limite de **{max_bet} <:ecoEther:1341862366249357374>**.")
            return
        amount = balance

    elif amount.lower() == "half":
        if balance == 0:
            await ctx.send(f"{user.mention}, ton portefeuille est vide.")
            return
        amount = balance // 2
        if amount > max_bet:
            await ctx.send(f"{user.mention}, la moitié de ton portefeuille dépasse la limite de **{max_bet} <:ecoEther:1341862366249357374>**.")
            return

    else:
        try:
            amount = int(amount)
        except ValueError:
            await ctx.send(f"{user.mention}, entre un montant valide, ou utilise `all` ou `half`.")
            return

    if amount > balance:
        await ctx.send(f"{user.mention}, tu n'as pas assez de coins pour cette mise.")
        return
    if amount <= 0:
        await ctx.send(f"{user.mention}, la mise doit être positive.")
        return
    if amount > max_bet:
        await ctx.send(f"{user.mention}, la mise est limitée à **{max_bet} <:ecoEther:1341862366249357374>**.")
        return

    win_data = collection6.find_one({"guild_id": guild_id, "user_id": user_id})
    win_chance = win_data.get("win_chance") if win_data and "win_chance" in win_data else start_chance

    if random.randint(1, 100) <= win_chance:
        win_amount = amount
        collection.update_one(
            {"guild_id": guild_id, "user_id": user_id},
            {"$inc": {"wallet": win_amount}},
            upsert=True
        )
        new_chance = min(win_chance + 1, max_chance)
        collection6.update_one(
            {"guild_id": guild_id, "user_id": user_id},
            {"$set": {"win_chance": new_chance}},
            upsert=True
        )

        embed = discord.Embed(
            description=f"Your lil chicken won the fight, and made you <:ecoEther:1341862366249357374> **{win_amount}** richer! 🐓",
            color=discord.Color.green()
        )
        embed.set_author(name=str(user), icon_url=user.avatar.url if user.avatar else user.default_avatar.url)
        embed.set_footer(text=f"Chicken strength (chance of winning): {new_chance}%")
        await ctx.send(embed=embed)

        balance_after = balance + win_amount
        await log_eco_channel(
            bot, guild_id, user, "Victoire au Cock-Fight", win_amount, balance, balance_after,
            f"Victoire au Cock-Fight avec un gain de **{win_amount}**"
        )

    else:
        collection7.update_one(
            {"guild_id": guild_id, "user_id": user_id},
            {"$set": {"chicken": False}}
        )
        collection.update_one(
            {"guild_id": guild_id, "user_id": user_id},
            {"$inc": {"wallet": -amount}},
            upsert=True
        )
        collection6.update_one(
            {"guild_id": guild_id, "user_id": user_id},
            {"$set": {"win_chance": start_chance}},
            upsert=True
        )

        embed = discord.Embed(
            description="Your chicken died <:imageremovebgpreview53:1362693948702855360>",
            color=discord.Color.red()
        )
        embed.set_author(name=str(user), icon_url=user.avatar.url if user.avatar else user.default_avatar.url)
        embed.set_footer(text="Chicken strength reset.")
        await ctx.send(embed=embed)

        balance_after = balance - amount
        await log_eco_channel(
            bot, guild_id, user, "Défaite au Cock-Fight", -amount, balance, balance_after,
            f"Défaite au Cock-Fight avec une perte de **{amount}**"
        )

@bot.command(name="set-cf-depart-chance")
@commands.has_permissions(administrator=True)
async def set_depart_chance(ctx, pourcent: str = None):
    if pourcent is None:
        return await ctx.send("⚠️ Merci de spécifier un pourcentage (entre 1 et 100). Exemple : `!set-cf-depart-chance 50`")

    if not pourcent.isdigit():
        return await ctx.send("⚠️ Le pourcentage doit être un **nombre entier**.")

    pourcent = int(pourcent)
    if not 1 <= pourcent <= 100:
        return await ctx.send("❌ Le pourcentage doit être compris entre **1** et **100**.")

    # Mettre à jour la base de données avec la nouvelle valeur
    collection8.update_one({"guild_id": ctx.guild.id}, {"$set": {"start_chance": pourcent}}, upsert=True)

    # Envoyer un message dans le salon de log spécifique (si configuré)
    config = collection9.find_one({"guild_id": ctx.guild.id})
    channel_id = config.get("eco_log_channel") if config else None

    if channel_id:
        channel = bot.get_channel(channel_id)
        if channel:
            embed = discord.Embed(
                title="🔧 Log de Configuration",
                color=discord.Color.green(),
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="Action", value="Mise à jour de la chance de départ", inline=True)
            embed.add_field(name="Chance de départ", value=f"{pourcent}%", inline=True)
            await channel.send(embed=embed)

    await ctx.send(f"✅ La chance de départ a été mise à **{pourcent}%**.")


@bot.command(name="set-cf-max-chance")
@commands.has_permissions(administrator=True)
async def set_max_chance(ctx, pourcent: str = None):
    if pourcent is None:
        return await ctx.send("⚠️ Merci de spécifier un pourcentage (entre 1 et 100). Exemple : `!set-cf-max-chance 90`")

    if not pourcent.isdigit():
        return await ctx.send("⚠️ Le pourcentage doit être un **nombre entier**.")

    pourcent = int(pourcent)
    if not 1 <= pourcent <= 100:
        return await ctx.send("❌ Le pourcentage doit être compris entre **1** et **100**.")

    # Mettre à jour la base de données avec la nouvelle valeur
    collection8.update_one({"guild_id": ctx.guild.id}, {"$set": {"max_chance": pourcent}}, upsert=True)

    # Envoyer un message dans le salon de log spécifique (si configuré)
    config = collection9.find_one({"guild_id": ctx.guild.id})
    channel_id = config.get("eco_log_channel") if config else None

    if channel_id:
        channel = bot.get_channel(channel_id)
        if channel:
            embed = discord.Embed(
                title="🔧 Log de Configuration",
                color=discord.Color.green(),
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="Action", value="Mise à jour de la chance maximale de victoire", inline=True)
            embed.add_field(name="Chance maximale", value=f"{pourcent}%", inline=True)
            await channel.send(embed=embed)

    await ctx.send(f"✅ La chance maximale de victoire est maintenant de **{pourcent}%**.")

@bot.command(name="set-cf-mise-max")
@commands.has_permissions(administrator=True)
async def set_max_mise(ctx, amount: str = None):
    if amount is None:
        return await ctx.send("⚠️ Merci de spécifier une mise maximale (nombre entier positif). Exemple : `!set-cf-mise-max 1000`")

    if not amount.isdigit():
        return await ctx.send("⚠️ La mise maximale doit être un **nombre entier**.")

    amount = int(amount)
    if amount <= 0:
        return await ctx.send("❌ La mise maximale doit être un **nombre supérieur à 0**.")

    # Mettre à jour la base de données avec la nouvelle mise maximale
    collection8.update_one({"guild_id": ctx.guild.id}, {"$set": {"max_bet": amount}}, upsert=True)

    # Envoyer un message dans le salon de log spécifique (si configuré)
    config = collection9.find_one({"guild_id": ctx.guild.id})
    channel_id = config.get("eco_log_channel") if config else None

    if channel_id:
        channel = bot.get_channel(channel_id)
        if channel:
            embed = discord.Embed(
                title="🔧 Log de Configuration",
                color=discord.Color.green(),
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="Action", value="Mise à jour de la mise maximale", inline=True)
            embed.add_field(name="Mise maximale", value=f"{amount} <:ecoEther:1341862366249357374>", inline=True)
            await channel.send(embed=embed)

    await ctx.send(f"✅ La mise maximale a été mise à **{amount} <:ecoEther:1341862366249357374>**.")

# Gestion des erreurs liées aux permissions
@set_depart_chance.error
@set_max_chance.error
@set_max_mise.error
async def cf_config_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")
    elif isinstance(error, commands.CommandInvokeError):
        await ctx.send("❌ Une erreur est survenue lors de l’exécution de la commande.")
        print(f"[ERREUR] {error}")
    else:
        await ctx.send("⚠️ Une erreur inconnue est survenue.")
        print(f"[ERREUR INCONNUE] {error}")

class CFConfigView(ui.View):
    def __init__(self, guild_id):
        super().__init__(timeout=60)
        self.guild_id = guild_id

    @ui.button(label="🔄 Reset aux valeurs par défaut", style=discord.ButtonStyle.red)
    async def reset_defaults(self, interaction: Interaction, button: ui.Button):
        # Vérifier si l'utilisateur est admin
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("Tu n'as pas la permission de faire ça.", ephemeral=True)
            return

        # Reset config
        default_config = {
            "start_chance": 50,
            "max_chance": 100,
            "max_bet": 20000
        }
        collection8.update_one(
            {"guild_id": self.guild_id},
            {"$set": default_config},
            upsert=True
        )
        await interaction.response.send_message("✅ Les valeurs par défaut ont été rétablies.", ephemeral=True)

@bot.command(name="cf-config")
@commands.has_permissions(administrator=True)
async def cf_config(ctx):
    guild_id = ctx.guild.id
    config = get_cf_config(guild_id)

    start_chance = config.get("start_chance", 50)
    max_chance = config.get("max_chance", 100)
    max_bet = config.get("max_bet", 20000)

    embed = discord.Embed(
        title="⚙️ Configuration Cock-Fight",
        color=discord.Color.gold()
    )
    embed.add_field(name="🎯 Chance de départ", value=f"**{start_chance}%**", inline=False)
    embed.add_field(name="📈 Chance max", value=f"**{max_chance}%**", inline=False)
    embed.add_field(name="💰 Mise maximale", value=f"**{max_bet} <:ecoEther:1341862366249357374>**", inline=False)
    embed.set_footer(text=f"Demandé par {ctx.author.display_name}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)

    await ctx.send(embed=embed, view=CFConfigView(guild_id))

@bot.command(name="set-eco-log")
@commands.has_permissions(administrator=True)
async def set_eco_log(ctx, channel: discord.TextChannel):
    guild_id = ctx.guild.id
    collection9.update_one(
        {"guild_id": guild_id},
        {"$set": {"eco_log_channel": channel.id}},
        upsert=True
    )
    await ctx.send(f"✅ Les logs économiques seront envoyés dans {channel.mention}")

@bot.command(aliases=["bj"])
async def blackjack(ctx, mise: int):
    # Récupération de la configuration du Blackjack dans la base de données
    guild_id = ctx.guild.id
    user_id = ctx.author.id

    # Charger ou initialiser la configuration de la mise maximale
    bj_config = collection10.find_one({"guild_id": guild_id})
    if not bj_config:
        bj_config = {
            "guild_id": guild_id,
            "max_mise": 30000  # Valeur par défaut de la mise maximale
        }
        collection10.insert_one(bj_config)

    max_mise = bj_config["max_mise"]

    # Vérification que la mise est valide
    if mise <= 0 or mise > max_mise:
        embed = discord.Embed(
            title="❌ Mise invalide",
            description=f"La mise doit être comprise entre `1` et `{max_mise}` coins.",
            color=discord.Color.red()
        )
        return await ctx.send(embed=embed)

    # Récupération ou initialisation des données de l'utilisateur
    data = collection.find_one({"guild_id": guild_id, "user_id": user_id})
    if not data:
        data = {
            "guild_id": guild_id,
            "user_id": user_id,
            "wallet": 1500,
            "bank": 0
        }
        collection.insert_one(data)

    # Vérification si l'utilisateur a assez de coins
    if data["wallet"] < mise:
        embed = discord.Embed(
            title="💸 Fonds insuffisants",
            description="Tu n'as pas assez de coins dans ton portefeuille pour cette mise.",
            color=discord.Color.red()
        )
        return await ctx.send(embed=embed)

    # Fonction pour tirer une carte
    def get_card():
        cartes = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        return random.choice(cartes)

    # Fonction pour calculer la valeur d'une main
    def get_value(main):
        value = 0
        aces = 0
        for carte in main:
            if carte in ['J', 'Q', 'K']:
                value += 10
            elif carte == 'A':
                aces += 1
                value += 11
            else:
                value += int(carte)
        while value > 21 and aces:
            value -= 10
            aces -= 1
        return value

    # Création des mains initiales
    joueur = [get_card(), get_card()]
    croupier = [get_card(), get_card()]

    joueur_val = get_value(joueur)
    croupier_val = get_value(croupier)

    # Vue du Blackjack avec les boutons
    class BlackjackView(View):
        def __init__(self):
            super().__init__(timeout=60)  # 60 secondes pour jouer

        @discord.ui.button(label="🃏 Hit", style=discord.ButtonStyle.primary)
        async def hit(self, interaction: discord.Interaction, button: discord.ui.Button):
            nonlocal joueur, joueur_val
            carte = get_card()
            joueur.append(carte)
            joueur_val = get_value(joueur)

            embed = discord.Embed(
                title="🎰 Blackjack",
                description=f"Tu as tiré une carte : {carte}.",
                color=discord.Color.blue()
            )
            embed.add_field(name="🧑‍💼 Ta main", value=f"`{'  '.join(joueur)}` → **{joueur_val}**", inline=True)
            embed.add_field(name="🎲 Croupier", value=f"`{'  '.join(croupier)}` → **{croupier_val}**", inline=True)

            if joueur_val > 21:
                embed.add_field(name="💥 Résultat", value="Tu as dépassé 21. Tu perds ta mise.", inline=False)
                collection.update_one({"guild_id": guild_id, "user_id": user_id}, {"$inc": {"wallet": -mise}})
                # Log la perte
                await log_eco_channel(bot, guild_id, ctx.author, "Perte de mise", mise, data["wallet"], data["wallet"] - mise)
                self.stop()

            await interaction.response.edit_message(embed=embed, view=self)

        @discord.ui.button(label="✋ Stand", style=discord.ButtonStyle.danger)
        async def stand(self, interaction: discord.Interaction, button: discord.ui.Button):
            nonlocal croupier, croupier_val
            # Le croupier joue après le joueur
            while croupier_val < 17:
                carte = get_card()
                croupier.append(carte)
                croupier_val = get_value(croupier)

            embed = discord.Embed(
                title="🎰 Blackjack",
                description="Le croupier a fini de jouer.",
                color=discord.Color.green()
            )
            embed.add_field(name="🧑‍💼 Ta main", value=f"`{'  '.join(joueur)}` → **{joueur_val}**", inline=True)
            embed.add_field(name="🎲 Croupier", value=f"`{'  '.join(croupier)}` → **{croupier_val}**", inline=True)

            if croupier_val > 21 or joueur_val > croupier_val:
                embed.add_field(name="💰 Résultat", value="Tu gagnes ! Ta mise est doublée.", inline=False)
                collection.update_one({"guild_id": guild_id, "user_id": user_id}, {"$inc": {"wallet": mise}})
                # Log la victoire
                await log_eco_channel(bot, guild_id, ctx.author, "Gagné au Blackjack", mise, data["wallet"], data["wallet"] + mise)
            elif joueur_val < croupier_val:
                embed.add_field(name="💥 Résultat", value="Tu perds ta mise.", inline=False)
                collection.update_one({"guild_id": guild_id, "user_id": user_id}, {"$inc": {"wallet": -mise}})
                # Log la perte
                await log_eco_channel(bot, guild_id, ctx.author, "Perte de mise", mise, data["wallet"], data["wallet"] - mise)
            else:
                embed.add_field(name="🤝 Résultat", value="Égalité ! Ta mise est remboursée.", inline=False)

            self.stop()

            await interaction.response.edit_message(embed=embed, view=self)

    # Envoi de l'embed initial avec les boutons
    view = BlackjackView()
    embed = discord.Embed(
        title="🎰 Blackjack",
        description="Bienvenue dans le jeu de Blackjack ! Choisis `Hit` pour tirer une carte ou `Stand` pour rester.",
        color=discord.Color.blue()
    )
    embed.add_field(name="🧑‍💼 Ta main", value=f"`{'  '.join(joueur)}` → **{joueur_val}**", inline=True)
    embed.add_field(name="🎲 Croupier", value=f"`{'  '.join(croupier[:1])}` → **?**", inline=True)
    embed.add_field(name="💰 Mise", value=f"{mise} <:ecoEther:1341862366249357374>", inline=False)
    await ctx.send(embed=embed, view=view)

async def log_bj_max_mise(bot, guild_id, user, new_max_mise, old_max_mise):
    # Récupérer le canal de logs (peut être configuré dans la base de données)
    config = collection9.find_one({"guild_id": guild_id})
    channel_id = config.get("eco_log_channel") if config else None

    if not channel_id:
        return  # Aucun salon configuré

    channel = bot.get_channel(channel_id)
    if not channel:
        return  # Salon introuvable (peut avoir été supprimé)

    embed = discord.Embed(
        title="🃏 Log Blackjack - Mise maximale",
        color=discord.Color.gold(),
        timestamp=datetime.utcnow()
    )
    embed.set_author(name=str(user), icon_url=user.avatar.url if user.avatar else None)
    embed.add_field(name="Action", value="Changement de la mise maximale", inline=False)
    embed.add_field(name="Ancienne Mise Maximale", value=f"{old_max_mise} <:ecoEther:1341862366249357374>", inline=True)
    embed.add_field(name="Nouvelle Mise Maximale", value=f"{new_max_mise} <:ecoEther:1341862366249357374>", inline=True)

    await channel.send(embed=embed)

@bot.command(name="bj-max-mise", aliases=["set-max-bj"])
@commands.has_permissions(administrator=True)  # La commande est réservée aux admins
async def set_max_bj_mise(ctx, mise_max: int):
    # Vérification que la mise max est un entier et supérieure à 0
    if not isinstance(mise_max, int) or mise_max <= 0:
        embed = discord.Embed(
            title="❌ Mise maximale invalide",
            description="La mise maximale doit être un nombre entier positif.",
            color=discord.Color.red()
        )
        return await ctx.send(embed=embed)

    guild_id = ctx.guild.id

    # Charger les paramètres de Blackjack depuis la collection info_bj
    bj_config = collection10.find_one({"guild_id": guild_id})

    # Si la configuration n'existe pas, en créer une avec la mise max par défaut
    old_max_mise = 30000  # Valeur par défaut
    if bj_config:
        old_max_mise = bj_config.get("max_mise", 30000)

    # Mise à jour de la mise maximale
    collection10.update_one(
        {"guild_id": guild_id},
        {"$set": {"max_mise": mise_max}},
        upsert=True
    )

    embed = discord.Embed(
        title="✅ Mise maximale mise à jour",
        description=f"La mise maximale pour le Blackjack a été changée à {mise_max} coins.",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

    # Log des changements
    await log_bj_max_mise(ctx.bot, guild_id, ctx.author, mise_max, old_max_mise)

# Gestion de l'erreur si l'utilisateur n'est pas administrateur
@set_max_bj_mise.error
async def set_max_bj_mise_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="❌ Accès refusé",
            description="Tu n'as pas les permissions nécessaires pour changer la mise maximale.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

@bot.hybrid_command(name="rob", description="Voler entre 1% et 50% du portefeuille d'un autre utilisateur.")
async def rob(ctx, user: discord.User):
    # Récupérer l'ID du serveur et l'utilisateur
    guild_id = ctx.guild.id
    user_id = ctx.author.id
    target_id = user.id

    # Vérifier si l'utilisateur cible et l'attaquant sont différents
    if user_id == target_id:
        embed = discord.Embed(
            title="❌ Action interdite",
            description="Tu ne peux pas voler des coins à toi-même.",
            color=discord.Color.red()
        )
        return await ctx.send(embed=embed)

    # Vérification du cooldown pour cette action
    cooldown_data = collection14.find_one({"guild_id": guild_id, "user_id": user_id, "target_id": target_id})
    if cooldown_data:
        last_rob_time = cooldown_data.get("last_rob", datetime.utcnow())
        if datetime.utcnow() - last_rob_time < timedelta(hours=1):
            remaining_time = (timedelta(hours=1) - (datetime.utcnow() - last_rob_time)).seconds
            embed = discord.Embed(
                title="❌ Cooldown en cours",
                description=f"Tu dois attendre encore **{remaining_time // 60} minutes** avant de pouvoir voler à nouveau.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)

    # Chercher les données des utilisateurs
    user_data = collection.find_one({"guild_id": guild_id, "user_id": user_id})
    target_data = collection.find_one({"guild_id": guild_id, "user_id": target_id})

    # Si l'utilisateur ou la cible n'ont pas de données, initialiser les données
    if not user_data:
        user_data = {
            "guild_id": guild_id,
            "user_id": user_id,
            "wallet": 1500,
            "bank": 0
        }
        collection.insert_one(user_data)

    if not target_data:
        target_data = {
            "guild_id": guild_id,
            "user_id": target_id,
            "wallet": 1500,
            "bank": 0
        }
        collection.insert_one(target_data)

    # Vérifier si la cible a des fonds disponibles
    target_wallet = target_data.get("wallet", 0)
    if target_wallet <= 0:
        embed = discord.Embed(
            title="❌ Solde insuffisant",
            description=f"**{user.display_name}**, la cible n'a pas de coins à voler.",
            color=discord.Color.red()
        )
        return await ctx.send(embed=embed)

    # Calcul du montant à voler entre 1% et 50%
    steal_percentage = random.randint(1, 50)
    amount_stolen = (steal_percentage / 100) * target_wallet

    # Mise à jour des balances
    new_user_wallet = user_data["wallet"] + amount_stolen
    new_target_wallet = target_wallet - amount_stolen

    # Mise à jour des données dans la base
    collection.update_one({"guild_id": guild_id, "user_id": user_id}, {"$set": {"wallet": new_user_wallet}})
    collection.update_one({"guild_id": guild_id, "user_id": target_id}, {"$set": {"wallet": new_target_wallet}})

    # Enregistrement de l'action dans la collection des CDs
    collection14.update_one(
        {"guild_id": guild_id, "user_id": user_id, "target_id": target_id},
        {"$set": {"last_rob": datetime.utcnow()}},
        upsert=True
    )

    # Log de l'action dans le salon approprié
    await log_eco_channel(bot, guild_id, ctx.author, "Vol", amount_stolen, user_data["wallet"], new_user_wallet, f"Volé à {user.display_name}")

    # Création de l'embed de résultat
    embed = discord.Embed(
        title="💰 Vol réussi !",
        description=f"**{user.display_name}** a volé **{amount_stolen:.2f} <:ecoEther:1341862366249357374>** de **{user.display_name}** !",
        color=discord.Color.green()
    )
    embed.add_field(name="Solde actuel", value=f"**{user.display_name}**: {new_user_wallet:.2f} <:ecoEther:1341862366249357374>\n**{user.display_name}**: {new_target_wallet:.2f} <:ecoEther:1341862366249357374>", inline=False)
    await ctx.send(embed=embed)

# Token pour démarrer le bot (à partir des secrets)
# Lancer le bot avec ton token depuis l'environnement  
keep_alive()
bot.run(token)
