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

def load_guild_settings(guild_id):
    # Charger les données de la collection principale
    ether_eco_data = collection.find_one({"guild_id": guild_id}) or {}
    ether_daily_data = collection2.find_one({"guild_id": guild_id}) or {}
    ether_slut_data = collection3.find_one({"guild_id": guild_id}) or {}
    ether_crime_data = collection4.find_one({"guild_id": guild_id}) or {}
    ether_collect = collection5.find_one({"guild_id": guild_id}) or {}
    ether_work_data = collection6.find_one({"guild_id": guild_id}) or {}
    ether_inventory_data = collection7.find_one({"guild_id": guild_id}) or {}

    # Débogage : Afficher les données de setup
    print(f"Setup data for guild {guild_id}: {setup_data}")

    combined_data = {
        "ether_eco": ether_eco_data,
        "ether_daily": ether_daily_data,
        "ether_slut": ether_slut_data,
        "ether_crime": ether_crime_data,
        "ether_collect": ether_collect_data,
        "ether_work": ether_work_data,
        "ether_inventory": ether_inventory_data

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


@bot.hybrid_command(name="bal", aliases=["balance", "money"], description="Affiche ta balance ou celle d'un autre utilisateur.")
async def bal(ctx: commands.Context, user: discord.User = None):
    # Utilise l'utilisateur appelant si aucun utilisateur n'est précisé
    user = user or ctx.author
    guild_id = ctx.guild.id
    user_id = user.id

    # Cherche les données de l'utilisateur dans la collection ether_eco
    data = collection.find_one({"guild_id": guild_id, "user_id": user_id})

    # Récupère les valeurs ou 0 si non trouvées
    balance = data.get("wallet", 0) if data else 0
    bank = data.get("bank", 0) if data else 0
    total = balance + bank

    # Création de l'embed
    embed = discord.Embed(title=f"💰 Balance de {user.display_name}", color=discord.Color.gold())
    embed.add_field(name="Portefeuille", value=f"{balance} <:ecoEther:1341862366249357374>", inline=True)
    embed.add_field(name="Banque", value=f"{bank} 🏦", inline=True)
    embed.add_field(name="Total", value=f"{total} 💵", inline=False)
    embed.set_footer(text=f"Demandé par {ctx.author}", icon_url=ctx.author.display_avatar.url)

    # Envoi du message avec l'embed
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

    # Mise à jour MongoDB
    collection.update_one(
        {"guild_id": guild_id, "user_id": user_id},
        {"$inc": {account.lower(): amount}},
        upsert=True
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

    # Mise à jour dans la base de données
    collection.update_one(
        {"guild_id": guild_id, "user_id": user_id},
        {"$inc": {field: -amount}},
        upsert=True
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

    # Mise à jour de la base de données
    collection.update_one(
        {"guild_id": guild_id, "user_id": user_id},
        {"$set": {field: amount}},
        upsert=True
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
            f"Tu as réussi à te faire un joli gain de **{amount} <:ecoEther:1341862366249357374>**.",
            f"Bravo, ton crime t'a rapporté **{amount} <:ecoEther:1341862366249357374>**.",
            f"Tu as récolté **{amount} <:ecoEther:1341862366249357374>** grâce à ton crime.",
            f"Ton crime a porté ses fruits, tu gagnes **{amount} <:ecoEther:1341862366249357374>**.",
            f"Félicitations, tu as gagné **{amount} <:ecoEther:1341862366249357374>** après ton braquage.",
            f"Ton crime a été couronné de succès, tu gagnes **{amount} <:ecoEther:1341862366249357374>**.",
            f"Tu as bien joué ! **{amount} <:ecoEther:1341862366249357374>** sont à toi.",
            f"Ton crime t'a rapporté **{amount} <:ecoEther:1341862366249357374>**.",
            f"Tu as bien tiré ton épingle du jeu avec **{amount} <:ecoEther:1341862366249357374>**.",
            f"Un joli gain de **{amount} <:ecoEther:1341862366249357374>** pour toi !",
            f"Tu as fait un coup de maître, tu as gagné **{amount} <:ecoEther:1341862366249357374>**.",
            f"Tu as gagné **{amount} <:ecoEther:1341862366249357374>** grâce à ta stratégie parfaite.",
            f"Bravo, tu as réussi à obtenir **{amount} <:ecoEther:1341862366249357374>**.",
            f"Ton crime a payé, tu as gagné **{amount} <:ecoEther:1341862366249357374>**.",
            f"Le butin est à toi ! **{amount} <:ecoEther:1341862366249357374>**.",
            f"Tu es un criminel chanceux, tu as gagné **{amount} <:ecoEther:1341862366249357374>**.",
            f"Ton coup a payé, tu gagnes **{amount} <:ecoEther:1341862366249357374>**."
        ]
        # Sélectionner un message de succès au hasard
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
            f"Malheureusement, ton crime a échoué et tu as perdu **{amount} <:ecoEther:1341862366249357374>**.",
            f"Pas de chance, tu perds **{amount} <:ecoEther:1341862366249357374>** après ton crime.",
            f"Ton crime a échoué et tu perds **{amount} <:ecoEther:1341862366249357374>**.",
            f"Oups, tu as perdu **{amount} <:ecoEther:1341862366249357374>** en tentant un crime.",
            f"Tu as fait une erreur et perdu **{amount} <:ecoEther:1341862366249357374>**.",
            f"Ton coup n'a pas fonctionné, tu perds **{amount} <:ecoEther:1341862366249357374>**.",
            f"Tu as perdu **{amount} <:ecoEther:1341862366249357374>** à cause de ton crime raté.",
            f"Dommage, tu perds **{amount} <:ecoEther:1341862366249357374>** cette fois.",
            f"Ton crime n'a pas payé, tu perds **{amount} <:ecoEther:1341862366249357374>**.",
            f"Tu as raté, tu perds **{amount} <:ecoEther:1341862366249357374>**.",
            f"Le crime ne paie pas, tu perds **{amount} <:ecoEther:1341862366249357374>**.",
            f"Tu perds **{amount} <:ecoEther:1341862366249357374>** après ton crime échoué.",
            f"Ce coup a échoué, tu perds **{amount} <:ecoEther:1341862366249357374>**.",
            f"Tu as perdu **{amount} <:ecoEther:1341862366249357374>** à cause d'un crime mal exécuté.",
            f"Pas de chance, tu perds **{amount} <:ecoEther:1341862366249357374>**.",
            f"Tu as perdu **{amount} <:ecoEther:1341862366249357374>** dans ce crime.",
            f"Le crime ne t'a pas souri, tu perds **{amount} <:ecoEther:1341862366249357374>**.",
            f"Tu perds **{amount} <:ecoEther:1341862366249357374>** à cause de ton erreur.",
            f"Ce crime ne t'a rien rapporté, tu perds **{amount} <:ecoEther:1341862366249357374>**.",
            f"Oups, tu perds **{amount} <:ecoEther:1341862366249357374>** dans ce crime.",
            f"Ton crime a échoué, tu perds **{amount} <:ecoEther:1341862366249357374>**."
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

    # Vérifier le solde de l'utilisateur
    data = collection.find_one({"guild_id": guild_id, "user_id": user_id})
    balance = data.get("wallet", 0) if data else 0

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
async def cock_fight(ctx, amount: int):
    user = ctx.author
    guild_id = ctx.guild.id
    user_id = user.id

    # Vérifier si l'utilisateur a un poulet
    data = collection7.find_one({"guild_id": guild_id, "user_id": user_id})
    if not data or not data.get("chicken", False):
        await ctx.send(f"{user.mention}, tu n'as pas de poulet ! Utilise la commande `!!buy chicken` pour en acheter un.")
        return

    # Supprimer le poulet utilisé
    collection7.update_one(
        {"guild_id": guild_id, "user_id": user_id},
        {"$set": {"chicken": False}}
    )

    # Vérifier le solde de l'utilisateur
    balance_data = collection.find_one({"guild_id": guild_id, "user_id": user_id})
    balance = balance_data.get("wallet", 0) if balance_data else 0

    if amount > balance:
        await ctx.send(f"{user.mention}, tu n'as pas assez de coins pour cette mise.")
        return
    if amount <= 0:
        await ctx.send(f"{user.mention}, la mise doit être positive.")
        return
    if amount > 20000:
        await ctx.send(f"{user.mention}, la mise est limitée à **20 000 🪙**.")
        return

    # Récupérer la streak
    win_data = collection6.find_one({"guild_id": guild_id, "user_id": user_id})
    win_streak = win_data.get("win_streak", 0) if win_data else 0

    # Calcul de la probabilité de victoire
    win_probability = min(50 + win_streak, 100)
    await ctx.send(f"⚔️ **Probabilité de victoire : {win_probability}%**")

    # Combat
    if random.randint(1, 100) <= win_probability:
        win_amount = amount * 2
        collection.update_one(
            {"guild_id": guild_id, "user_id": user_id},
            {"$inc": {"wallet": win_amount}},
            upsert=True
        )
        collection6.update_one(
            {"guild_id": guild_id, "user_id": user_id},
            {"$inc": {"win_streak": 1}},
            upsert=True
        )
        
        # Message de victoire avec Embed
        embed = discord.Embed(
            title="🐓 Victoire !",
            description=f"{user.mention}, tu as gagné **{win_amount} 🪙** ! Ta streak est maintenant de **{win_streak + 1}**.",
            color=discord.Color.green()
        )
        embed.set_footer(text="Bravo, continue sur ta lancée !")
        await ctx.send(embed=embed)
    else:
        collection.update_one(
            {"guild_id": guild_id, "user_id": user_id},
            {"$inc": {"wallet": -amount}},
            upsert=True
        )
        collection6.update_one(
            {"guild_id": guild_id, "user_id": user_id},
            {"$set": {"win_streak": 0}},
            upsert=True
        )
        
        # Message de défaite avec Embed
        embed = discord.Embed(
            title="💀 Défaite...",
            description=f"{user.mention}, tu as perdu **{amount} 🪙**. Ton poulet est KO. Ta streak est maintenant de **0**.",
            color=discord.Color.red()
        )
        embed.set_footer(text="La chance reviendra la prochaine fois !")
        await ctx.send(embed=embed)


# Token pour démarrer le bot (à partir des secrets)
# Lancer le bot avec ton token depuis l'environnement  
keep_alive()
bot.run(token)
