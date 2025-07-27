import discord
from discord.ext import commands
from discord import app_commands, Embed
import random
import asyncio
import re

from utils import (
    create_embed, has_permission, is_higher_or_equal, send_log, send_dm,
    load_guild_settings, get_premium_servers, is_blacklisted, add_sanction,
    get_log_channel, get_cf_config, get_presentation_channel_id, get_user_partner_info,
    get_protection_data, format_mention, generate_global_status_bar, format_protection_field,
    notify_owner_of_protection_change, is_valid_url, is_admin_or_isey,
    THUMBNAIL_URL, EMOJIS_SERVEURS, ETHERYA_ID, boost_bar, sensitive_categories,
    word_to_category, active_alerts, giveaways, ended_giveaways, fast_giveaways,
    user_cooldown, sniped_messages, stats_collection33
)

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.collection27 = bot.db_collections["guild_troll"] # Collection pour les commandes troll

    async def check_troll_active(self, guild_id):
        troll_data = self.collection27.find_one({"guild_id": guild_id, "troll_active": True})
        return troll_data is not None

    @commands.command()
    async def gay(self, ctx, member: discord.Member = None):
        if not await self.check_troll_active(ctx.guild.id):
            await ctx.send("❌ Les commandes troll ne sont **pas activées** sur ce serveur. Utilisez `/activate-troll` pour les activer.")
            return
        if member is None:
            await ctx.send("Vous n'avez ciblé personne !")
            return
        percentage = random.randint(0, 100)
        embed = create_embed(
            "Analyse de gayitude 🌈",
            f"{member.mention} est gay à **{percentage}%** !\n\n*Le pourcentage varie en fonction des pulsions du membre.*",
            discord.Color.purple()
        )
        embed.set_thumbnail(url=member.avatar.url)
        embed.set_footer(text=f"Commandé par {ctx.author.name} ♥️by Iseyg", icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)

    @commands.command()
    async def singe(self, ctx, member: discord.Member = None):
        if not await self.check_troll_active(ctx.guild.id):
            await ctx.send("❌ Les commandes troll ne sont **pas activées** sur ce serveur. Utilisez `/activate-troll` pour les activer.")
            return
        if member is None:
            await ctx.send("Vous n'avez ciblé personne !")
            return
        percentage = random.randint(0, 100)
        embed = create_embed(
            "Analyse de singe 🐒",
            f"{member.mention} est un singe à **{percentage}%** !\n\n*Le pourcentage varie en fonction de l'énergie primate du membre.*",
            discord.Color.green()
        )
        embed.set_thumbnail(url=member.avatar.url)
        embed.set_footer(text=f"Commandé par {ctx.author.name} 🐵 by Isey", icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)

    @commands.command()
    async def racist(self, ctx, member: discord.Member = None):
        if not await self.check_troll_active(ctx.guild.id):
            await ctx.send("❌ Les commandes troll ne sont **pas activées** sur ce serveur. Utilisez `/activate-troll` pour les activer.")
            return
        if member is None:
            await ctx.send("Vous n'avez ciblé personne !")
            return
        percentage = random.randint(0, 100)
        embed = create_embed(
            "Analyse de racisme 🪄",
            f"{member.mention} est raciste à **{percentage}%** !\n\n*Le pourcentage varie en fonction des pulsions du membre.*",
            discord.Color.purple()
        )
        embed.set_thumbnail(url=member.avatar.url)
        embed.set_footer(text=f"Commandé par {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)

    @commands.command()
    async def sucre(self, ctx, member: discord.Member = None):
        if not await self.check_troll_active(ctx.guild.id):
            await ctx.send("❌ Les commandes troll ne sont **pas activées** sur ce serveur. Utilisez `/activate-troll` pour les activer.")
            return
        if member is None:
            await ctx.send("Vous n'avez ciblé personne !")
            return
        percentage = random.randint(0, 100)
        embed = create_embed(
            "Analyse de l'indice glycémique 🍬",
            f"L'indice glycémique de {member.mention} est de **{percentage}%** !\n\n*Le pourcentage varie en fonction des habitudes alimentaires de la personne.*",
            discord.Color.green()
        )
        embed.set_thumbnail(url=member.avatar.url)
        embed.set_footer(text=f"Commandé par {ctx.author.name} 🍏by Iseyg", icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)

    @commands.command()
    async def rat(self, ctx, member: discord.Member = None):
        if not await self.check_troll_active(ctx.guild.id):
            await ctx.send("❌ Les commandes troll ne sont **pas activées** sur ce serveur. Utilisez `/activate-troll` pour les activer.")
            return
        if member is None:
            await ctx.send("Vous n'avez ciblé personne !")
            return
        percentage = random.randint(0, 100)
        embed = create_embed(
            f"Analyse de radinerie 🐁",
            f"{member.mention} est un rat à **{percentage}%** !\n\n*Le pourcentage varie en fonction des actes du membre.*",
            discord.Color.purple()
        )
        embed.set_thumbnail(url=member.avatar.url)
        embed.set_footer(text=f"Commandé par {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)

    @commands.command()
    async def con(self, ctx, member: discord.Member = None):
        if not await self.check_troll_active(ctx.guild.id):
            await ctx.send("❌ Les commandes troll ne sont **pas activées** sur ce serveur. Utilisez `/activate-troll` pour les activer.")
            return
        if member is None:
            await ctx.send("Vous n'avez ciblé personne !")
            return
        percentage = random.randint(0, 100)
        embed = create_embed(
            "Analyse de connerie 🤡",
            f"{member.mention} est con à **{percentage}%** !\n\n*Le pourcentage varie en fonction des neurones actifs du membre.*",
            discord.Color.red()
        )
        embed.set_thumbnail(url=member.avatar.url)
        embed.set_footer(text=f"Commandé par {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)

    @commands.command()
    async def libido(self, ctx, member: discord.Member = None):
        if not await self.check_troll_active(ctx.guild.id):
            await ctx.send("❌ Les commandes troll ne sont **pas activées** sur ce serveur. Utilisez `/activate-troll` pour les activer.")
            return
        if member is None:
            await ctx.send("Vous n'avez ciblé personne !")
            return
        percentage = random.randint(0, 100)
        embed = create_embed(
            "Analyse de libido 🔥",
            f"{member.mention} a une libido à **{percentage}%** !\n\n*Le pourcentage varie en fonction de l'humeur et du climat.*",
            discord.Color.red()
        )
        embed.set_thumbnail(url=member.avatar.url)
        embed.set_footer(text=f"Commandé par {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)

    @commands.command()
    async def zizi(self, ctx, member: discord.Member = None):
        if not await self.check_troll_active(ctx.guild.id):
            await ctx.send("❌ Les commandes troll ne sont **pas activées** sur ce serveur. Utilisez `/activate-troll` pour les activer.")
            return
        if member is None:
            await ctx.send("Vous n'avez ciblé personne !")
            return
        value = random.randint(0, 50)
        embed = create_embed(
            "Analyse de la taille du zizi 🔥",
            f"{member.mention} a un zizi de **{value} cm** !\n\n*La taille varie selon l'humeur du membre.*",
            discord.Color.blue()
        )
        embed.set_thumbnail(url=member.avatar.url)
        embed.set_footer(text=f"Commandé par {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)

    @commands.command()
    async def fou(self, ctx, member: discord.Member = None):
        if not await self.check_troll_active(ctx.guild.id):
            await ctx.send("❌ Les commandes troll ne sont **pas activées** sur ce serveur. Utilisez `/activate-troll` pour les activer.")
            return
        if member is None:
            await ctx.send("Vous n'avez ciblé personne !")
            return
        percentage = random.randint(0, 100)
        embed = create_embed(
            f"Analyse de folie 🤪",
            f"{member.mention} est fou à **{percentage}%** !\n\n*Le pourcentage varie en fonction de l'état mental du membre.*",
            discord.Color.green()
        )
        embed.set_thumbnail(url=member.avatar.url)
        embed.set_footer(text=f"Commandé par {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)

    @commands.command()
    async def testo(self, ctx, member: discord.Member = None):
        if not await self.check_troll_active(ctx.guild.id):
            await ctx.send("❌ Les commandes troll ne sont **pas activées** sur ce serveur. Utilisez `/activate-troll` pour les activer.")
            return
        if member is None:
            await ctx.send("Vous n'avez ciblé personne !")
            return
        percentage = random.randint(0, 100)
        embed = create_embed(
            f"Analyse de testostérone 💪",
            f"{member.mention} a un taux de testostérone de **{percentage}%** !\n\n*Le pourcentage varie en fonction des niveaux de virilité du membre.*",
            discord.Color.blue()
        )
        embed.set_thumbnail(url=member.avatar.url)
        embed.set_footer(text=f"Commandé par {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)

    @app_commands.command(name="say", description="Fais dire un message au bot.")
    @app_commands.describe(text="Le texte à dire")
    async def say(self, interaction: discord.Interaction, *, text: str = None):
        if not interaction.user.guild_permissions.administrator and interaction.user.id != self.bot.config_ids["ISEY_ID"]:
            await interaction.response.send_message("Tu n'as pas les permissions nécessaires pour utiliser cette commande.", ephemeral=True)
            return
        if text is None:
            await interaction.response.send_message("Tu n'as pas écrit de texte à dire !", ephemeral=True)
            return
        await interaction.channel.send(text)
        await interaction.response.send_message("Message envoyé !", ephemeral=True) # Pour masquer la réponse de la slash command

    @commands.command()
    async def coinflip(self, ctx):
        result = random.choice(["Pile", "Face"])
        await ctx.send(f"Résultat du coinflip : {result}")

    @commands.command()
    async def roll(self, ctx, x: str = None):
        if x is None:
            embed = create_embed("Erreur", "Vous n'avez pas précisé de chiffre entre 1 et 500.", discord.Color.red())
            await ctx.send(embed=embed)
            return
        try:
            x = int(x)
        except ValueError:
            embed = create_embed("Erreur", "Le chiffre doit être un nombre entier.", discord.Color.red())
            await ctx.send(embed=embed)
            return
        if x < 1 or x > 500:
            embed = create_embed("Erreur", "Le chiffre doit être compris entre 1 et 500.", discord.Color.red())
            await ctx.send(embed=embed)
            return
        result = random.randint(1, x)
        embed = create_embed(
            "🎲 Résultat du tirage",
            f"Le nombre tiré au hasard entre 1 et {x} est : **{result}**",
            discord.Color.green()
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def enfant(self, ctx, parent1: discord.Member = None, parent2: discord.Member = None):
        if not parent1 or not parent2:
            await ctx.send("Tu dois mentionner deux membres ! Utilise `/enfant @membre1 @membre2`.")
            return
        prenom = parent1.name[:len(parent1.name)//2] + parent2.name[len(parent2.name)//2:]
        embed = create_embed(
            "👶 Voici votre enfant !",
            f"{parent1.mention} + {parent2.mention} = **{prenom}** 🍼",
            discord.Color.purple()
        )
        embed.set_footer(text=f"Prenez soin de votre bébé ! {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)
        embed.set_thumbnail(url=parent1.avatar.url if parent1.avatar else parent2.avatar.url)
        await ctx.send(embed=embed)

    @commands.command()
    async def superpouvoir(self, ctx, user: discord.Member = None):
        if not user:
            user = ctx.author
        pouvoirs = [
            "Téléportation instantanée 🌀 - Peut se déplacer n'importe où en un clin d'œil.",
            "Contrôle du feu 🔥 - Rien ne lui résiste… sauf l'eau.",
            "Super vitesse ⚡ - Peut courir plus vite qu'un TGV, mais oublie souvent où il va.",
            "Lecture des pensées 🧠 - Peut lire dans les esprits… sauf ceux qui ne pensent à rien.",
            "Invisibilité 🫥 - Peut disparaître… mais oublie que ses vêtements restent visibles.",
            "parler aux animaux 🦜 - Mais ils n'ont pas grand-chose d'intéressant à dire.",
            "Super force 💪 - Peut soulever une voiture, mais galère à ouvrir un pot de cornichons.",
            "Métamorphose 🦎 - Peut se transformer en n'importe quoi… mais pas revenir en humain.",
            "Chance infinie 🍀 - Gagne à tous les jeux… sauf au Uno.",
            "Création de portails 🌌 - Peut ouvrir des portails… mais ne sait jamais où ils mènent.",
            "Régénération 🩸 - Guérit instantanément… mais reste chatouilleux à vie.",
            "Capacité de voler 🕊️ - Mais uniquement à 10 cm du sol.",
            "Super charisme 😎 - Convainc tout le monde… sauf sa mère.",
            "Vision laser 🔥 - Brûle tout sur son passage… y compris ses propres chaussures.",
            "Invocation de clones 🧑‍🤝‍🧑 - Mais ils n’obéissent jamais.",
            "Télékinésie ✨ - Peut déplacer des objets… mais uniquement des plumes.",
            "Création de burgers 🍔 - Magique, mais toujours trop cuits ou trop crus.",
            "Respiration sous l'eau 🐠 - Mais panique dès qu'il voit une méduse.",
            "Contrôle de la gravité 🌍 - Peut voler, mais oublie souvent de redescendre.",
            "Capacité d’arrêter le temps ⏳ - Mais uniquement quand il dort.",
            "Voyage dans le temps ⏰ - Peut voyager dans le passé ou le futur… mais toujours à la mauvaise époque.",
            "Télépathie inversée 🧠 - Peut faire entendre ses pensées aux autres… mais ils ne peuvent jamais comprendre.",
            "Manipulation des rêves 🌙 - Peut entrer dans les rêves des gens… mais se retrouve toujours dans des cauchemars.",
            "Super mémoire 📚 - Se souvient de tout… sauf des choses qu’il vient de dire.",
            "Manipulation des ombres 🌑 - Peut faire bouger les ombres… mais ne peut jamais les arrêter.",
            "Création de pluie 🍃 - Peut faire pleuvoir… mais uniquement sur ses amis.",
            "Maîtrise des plantes 🌱 - Peut faire pousser des plantes à une vitesse folle… mais elles ne cessent de pousser partout.",
            "Contrôle des rêves éveillés 💤 - Peut contrôler ses rêves quand il est éveillé… mais se retrouve toujours dans une réunion ennuyante.",
            "Maîtrise de l’éclairage ✨ - Peut illuminer n'importe quelle pièce… mais oublie d’éteindre.",
            "Création de souvenirs 🧳 - Peut créer des souvenirs… mais ceux-ci sont toujours un peu bizarres.",
            "Changement de taille 📏 - Peut grandir ou rapetisser… mais n'arrive jamais à garder une taille stable.",
            "Vision nocturne 🌙 - Peut voir dans l’obscurité… mais tout est toujours en noir et blanc.",
            "Contrôle des éléments 🤹‍♂️ - Peut manipuler tous les éléments naturels… mais uniquement quand il pleut.",
            "Phasing à travers les murs 🚪 - Peut traverser les murs… mais parfois il traverse aussi les portes.",
            "Régénération de l’esprit 🧠 - Guérit les blessures mentales… mais les oublie instantanément après."
        ]
        pouvoir = random.choice(pouvoirs)
        embed = create_embed(
            "⚡ Super-Pouvoir Débloqué !",
            f"{user.mention} possède le pouvoir de **{pouvoir}** !",
            discord.Color.purple()
        )
        embed.set_footer(text=f"Utilise-le avec sagesse... ou pas. {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)

    @commands.command()
    async def totem(self, ctx, member: discord.Member = None):
        if not member:
            member = ctx.author
        animaux_totem = {
            "Loup 🐺": "Fidèle et protecteur, il veille sur sa meute.",
            "Renard 🦊": "Rusé et malin, il trouve toujours un moyen de s'en sortir.",
            "Hibou 🦉": "Sage et observateur, il comprend tout avant les autres.",
            "Dragon 🐉": "Puissant et imposant, il ne laisse personne indifférent.",
            "Dauphin 🐬": "Joueur et intelligent, il adore embêter les autres.",
            "Chat 🐱": "Mystérieux et indépendant, il fait ce qu’il veut, quand il veut.",
            "Serpent 🐍": "Discret et patient, il attend le bon moment pour frapper.",
            "Corbeau 🦅": "Intelligent et un peu sinistre, il voit ce que les autres ignorent.",
            "Panda 🐼": "Calme et adorable… jusqu’à ce qu’on lui prenne son bambou.",
            "Tortue 🐢": "Lente mais sage, elle gagne toujours à la fin.",
            "Aigle 🦅": "Libre et fier, il vole au-dessus de tous les problèmes.",
            "Chauve-souris 🦇": "Préférant l'obscurité, elle voit clair quand tout le monde est perdu.",
            "Tigre 🐯": "Puissant et rapide, personne ne l’arrête.",
            "Lapin 🐰": "Rapide et malin, mais fuit dès qu’il y a un problème.",
            "Singe 🐵": "Curieux et joueur, il adore faire des bêtises.",
            "Escargot 🐌": "Lent… mais au moins il arrive toujours à destination.",
            "Pigeon 🕊️": "Increvable et partout à la fois, impossible de s'en débarrasser.",
            "Licorne 🦄": "Rare et magique, il apporte de la lumière partout où il passe.",
            "Poisson rouge 🐠": "Mémoire de 3 secondes, mais au moins il ne s’inquiète jamais.",
            "Canard 🦆": "Semble idiot, mais cache une intelligence surprenante.",
            "Raton laveur 🦝": "Petit voleur mignon qui adore piquer des trucs.",
            "Lynx 🐆" : "Serré dans ses mouvements, il frappe avec précision et discrétion.",
            "Loup de mer 🌊🐺" : "Un loup qui conquiert aussi bien les océans que la terre, fier et audacieux.",
            "Baleine 🐋" : "Majestueuse et bienveillante, elle nage dans les eaux profondes avec sagesse.",
            "Léopard 🐆" : "Vif et agile, il disparaît dans la jungle avant même qu'on ait pu le voir.",
            "Ours 🐻" : "Fort et protecteur, il défend son territoire sans hésiter.",
            "Cygne 🦢" : "Gracieux et élégant, il incarne la beauté dans la tranquillité.",
            "Chameau 🐫" : "Patient et résistant, il traverse les déserts sans jamais se fatiguer.",
            "Grizzly 🐻‍❄️" : "Imposant et puissant, il est le roi des forêts froides.",
            "Koala 🐨" : "Doux et calme, il passe sa vie à dormir dans les arbres.",
            "Panthère noire 🐆" : "Silencieuse et mystérieuse, elle frappe toujours quand on s'y attend le moins.",
            "Zèbre 🦓" : "Unique et surprenant, il se distingue dans la foule grâce à ses rayures.",
            "Éléphant 🐘" : "Sage et majestueux, il marche au rythme de sa propre grandeur.",
            "Croco 🐊" : "Implacable et rusé, il attend patiemment avant de bondir.",
            "Mouflon 🐏" : "Fort et tenace, il n'a pas peur de braver les montagnes.",
            "Perroquet 🦜" : "Coloré et bavard, il ne cesse jamais de répéter ce qu'il entend.",
            "Rhinocéros 🦏" : "Imposant et robuste, il se fraye un chemin à travers tout sur son passage.",
            "Bison 🦬" : "Solide et puissant, il traverse les prairies avec une énergie inébranlable."
        }
        totem, description = random.choice(list(animaux_totem.items()))
        embed = create_embed(
            f"🌿 Totem de {member.name} 🌿",
            f"**{totem}** : {description}",
            discord.Color.green()
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
        embed.set_footer(text=f"Commandé par {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)

    @commands.command()
    async def futur(self, ctx, user: discord.Member = None):
        if not user:
            user = ctx.author
        predicions = [
            "Dans 5 minutes, tu découvriras un trésor caché… mais il sera rempli de bonbons.",
            "L'année prochaine, tu feras une rencontre étonnante avec un extraterrestre qui adore les chats.",
            "Demain, tu auras une conversation intense avec un pigeon, et il te donnera un conseil de vie précieux.",
            "Un chat va te confier un secret qui changera le cours de ton existence… mais tu ne te souviendras pas de ce secret.",
            "Dans quelques jours, tu seras élu meilleur joueur de cache-cache, mais tu te cacheras dans une pièce vide.",
            "Lundi, tu rencontreras quelqu'un qui aime les licornes autant que toi. Vous deviendrez amis pour la vie.",
            "Dans un futur proche, tu réussiras à inventer un gâteau qui ne se mange pas, mais il sera étonnamment populaire.",
            "Bientôt, un mystérieux inconnu t'offrira un paquet cadeau. Il contiendra un élastique et une noix de coco.",
            "Dans un mois, tu vivras une aventure épique où tu devras résoudre un mystère impliquant des chaussettes perdues.",
            "Prochainement, tu seras récompensé pour avoir trouvé une solution révolutionnaire au problème de la pizza froide.",
            "Dans un futur lointain, tu seras le leader d'une civilisation intergalactique. Tes sujets seront principalement des pandas."
            "Dans 5 minutes, tu rencontreras un robot qui te demandera comment faire des pancakes… mais il n'a pas de mains.",
            "Ce week-end, tu seras choisi pour participer à un concours de danse avec des flamants roses, mais tu devras danser sans musique.",
            "Demain, un magicien te proposera un vœu… mais il te le refusera en te montrant un tour de cartes.",
            "Un perroquet va te confier un secret très important, mais tu l'oublieras dès que tu entras dans une pièce.",
            "Dans quelques jours, tu découvriras un trésor enfoui sous ta maison… mais il sera composé uniquement de petites pierres colorées.",
            "Prochainement, tu feras une rencontre étrange avec un extraterrestre qui te demandera de lui apprendre à jouer aux échecs.",
            "Dans un futur proche, tu gagneras un prix prestigieux pour avoir créé un objet du quotidien, mais personne ne saura vraiment à quoi il sert.",
            "Bientôt, tu recevras une invitation pour un dîner chez des créatures invisibles. Le menu ? Des nuages et des rayons de lune.",
            "Dans un mois, tu seras choisi pour représenter ton pays dans un concours de chant… mais tu devras chanter sous l'eau.",
            "Dans un futur lointain, tu seras une légende vivante, reconnu pour avoir inventé la première machine à fabriquer des sourires."
            "Dans 5 minutes, tu verras un nuage prendre la forme de ton visage, mais il te fera une grimace étrange.",
            "Demain, tu seras invité à une réunion secrète de licornes qui discuteront des nouvelles tendances en matière de paillettes.",
            "Prochainement, un dauphin te confiera un message codé que tu devras résoudre… mais il sera écrit en chantant.",
            "Un dragon viendra te rendre visite et te proposera de partager son trésor… mais il s’avère que ce trésor est un stock infini de bonbons à la menthe.",
            "Dans quelques jours, tu apprendras à parler couramment le langage des grenouilles, mais seulement quand il pleut.",
            "Cette semaine, un voleur masqué viendra te voler une chaussette… mais il te laissera un billet pour un concert de musique classique.",
            "Prochainement, un fantôme te demandera de l'aider à retrouver ses clés perdues… mais tu découvriras qu'il a oublié où il les a mises.",
            "Dans un futur proche, tu seras élu président d'un club de fans de légumes, et tu recevras une médaille en forme de carotte.",
            "Bientôt, tu découvriras un raccourci secret qui te permettra de voyager dans des mondes parallèles… mais il te fera revenir à ton point de départ.",
            "Dans un mois, tu recevras une lettre d'invitation à un bal masqué organisé par des robots, mais tu ne pourras pas danser car tu porteras des chaussons trop grands."
        ]
        prediction = random.choice(predicions)
        embed = create_embed(
            f"🔮 Prédiction pour {user.name} 🔮",
            f"**Prédiction :**\n\n{prediction}",
            discord.Color.blue()
        )
        embed.set_footer(text=f"Le futur est incertain… mais amusant ! {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)

    blagues = [
        "Pourquoi les plongeurs plongent toujours en arrière et jamais en avant ? ||Parce que sinon ils tombent toujours dans le bateau.||",
        "Pourquoi les canards sont toujours à l'heure ? ||Parce qu'ils sont dans les starting-quack !||",
        "Quel est le comble pour un électricien ? ||De ne pas être au courant.||",
        "Pourquoi les maths sont tristes ? ||Parce qu'elles ont trop de problèmes.||",
        "Que dit une imprimante à une autre imprimante ? *||'T'as du papier ?'||",
        "Pourquoi les poissons détestent l'ordinateur ? ||Parce qu'ils ont peur du net !||",
        "Comment appelle-t-on un chat qui a perdu son GPS ? ||Un chat égaré.||",
        "Pourquoi les squelettes ne se battent-ils jamais entre eux ? ||Parce qu'ils n'ont pas de cœur !||",
        "Quel est le comble pour un plombier ? ||D'avoir un tuyau percé.||",
        "Comment appelle-t-on un chien magique ? ||Un labra-cadabra !||"
    ]

    @commands.command()
    async def blague(self, ctx):
        blague_choisie = random.choice(self.blagues)
        await ctx.send(blague_choisie)

async def setup(bot):
    await bot.add_cog(Fun(bot))

