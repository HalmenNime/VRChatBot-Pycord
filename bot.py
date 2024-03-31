import discord
from discord.ext import commands
import requests
import os
import shutil
from termcolor import colored
import git


if not os.path.exists(".env"):
    if os.path.exists("example.env"):
        shutil.copy("example.env", ".env")
        print(colored("File .env was not find, now created, please edit and start bot again!", "yellow"))
    else:
        print(colored("File .env was not find, create please and check example env in repository for copy and edit!", "yellow"))
    exit()

def check_repository_updates():
    if os.getenv("REPOSITORY_UPDATE_NOTIFICATION", True) == True:
        try:
            repo = git.Repo()
            origin = repo.remote()
            origin.fetch(tags=True)

            local_tags = [tag.name for tag in repo.tags]
            remote_tags = [tag.name for tag in origin.refs]

            latest_local_tag = max(local_tags) if local_tags else None
            latest_remote_tag = max(remote_tags) if remote_tags else None

            if latest_local_tag != latest_remote_tag:
                print(f"There's an update in the repository. The latest version is {latest_remote_tag}, while your local version is {latest_local_tag}.")
            else:
                print("The repository is up to date.")

        except git.exc.InvalidGitRepositoryError:
            print("This is not a valid Git repository.")
        except git.exc.GitCommandError as e:
            print(f"Error retrieving updates from the remote repository: {e}")


language_emojis = {
    "language_rus": "🇷🇺",
    "language_eng": "🇬🇧",
    "language_ukr": "🇺🇦",
    "language_deu": "🇩🇪",
    "language_fra": "🇫🇷",
    "language_spa": "🇪🇸",
    "language_por": "🇵🇹",
    "language_jpn": "🇯🇵",
    "language_ase": "🇦🇪",
    "language_kor": "🇰🇷",
    "language_zho": "🇨🇳",
    "language_ita": "🇮🇹",
    "language_pol": "🇵🇱",
    "language_tha": "🇹🇭",
    "language_nld": "🇳🇱",
    "language_ara": "🇦🇷",
    "language_dan": "🇩🇰",
    "language_nor": "🇳🇴",
    "language_tur": "🇹🇷",
    "language_swe": "🇸🇪",
    "language_vie": "🇻🇮",
    "language_ind": "🇮🇳",
    "language_tgl": "🇹🇬",
    "language_ces": "🇨🇿",
    "language_fin": "🇫🇮",
    "language_bfi": "🇧🇫",
    "language_ron": "🇷🇴",
    "language_hun": "🇭🇺",
}

platform_emojis = {
    "windows": "<:windows:1224011075599601674>",
    "android": "<:android:1224012767040634920>",
    "quest": "<:meta:1224015480696869104>"
}

intents = discord.Intents().all()
bot = commands.Bot(intents=intents)

@bot.event
async def on_ready():
    print(f"Bot {bot.user} started")

async def get_info_user(id):
    url = f"https://api.vrchat.cloud/api/1/users/{id}"
    headers = {
        "User-Agent": "MyApp/1.0 (contact@example.com)",
        "Cookie": f"auth={os.getenv('COOKIE_AUTH', 'YOUR_COOKIE_AUTH')}"
    }
    response = requests.get(url, headers=headers)

    return response

@bot.slash_command(description = "Check profile VRChat user")
async def profile(ctx, id = discord.Option(str, description="Check information about user VRChat via ID")):
    
    response = await get_info_user(id)

    if response.status_code == 200:
        data = response.json()
        currentAvatarThumbnail = data["currentAvatarThumbnailImageUrl"]
        username = data["displayName"]
        bio = data["bio"]
        last_platform = data["last_platform"]
        tags = data["tags"]
        langs = ','.join(language_emojis[tag] for tag in tags if tag in language_emojis) or "Not specified"
        
        if len(bio) < 1:
            bio = 'None'

        if last_platform == "standalonewindows":
            last_platform = f"Windows {platform_emojis['windows']}"
        elif last_platform == "android":
            last_platform = f"Android {platform_emojis['android']} or Quest {platform_emojis['quest']}"
        else:
            last_platform = f"{last_platform} ❓"
        
        embed = discord.Embed(title=f"Information about {username}", description=f"Bio: {bio}")
        embed.add_field(name="Platform:", value=last_platform, inline=False)
        embed.add_field(name="Languages:", value=langs, inline=False)
        embed.set_author(name="VRChat info", url="https://www.google.com/url?sa=i&url=https%3A%2F%2Fask.vrchat.com%2Ftag%2Fbug&psig=AOvVaw373wKWlf86aLr1OofimNsY&ust=1711971065371000&source=images&cd=vfe&opi=89978449&ved=0CBIQjRxqFwoTCKiK7qyznoUDFQAAAAAdAAAAABAJ")
        embed.set_thumbnail(url=currentAvatarThumbnail)
        await ctx.respond(embed=embed)
    
    elif response.status_code == 404:
        embed = discord.Embed(title="Error", description=f"User not found", color=discord.Color.red())
        await ctx.respond(embed=embed)
    
    elif response.status_code == 401:
        embed = discord.Embed(title="Error", description=f"Missing Credentials, something wrong with auth cookie", color=discord.Color.red())
        await ctx.respond(embed=embed)
    
    else:
        embed = discord.Embed(title="Error", description=f"Unexpected error code ``({response.status_code})``, more detail will show in logs", color=discord.Color.red())
        await ctx.respond(embed=embed)
        print(response.json())

try:
    bot.run(os.getenv('TOKEN_BOT', 'YOUR_TOKEN_BOT'))
except discord.errors.LoginFailure as e:
    print(colored(f"Fail login in bot, wrong token?: {e}", "yellow"))
except Exception as e:
    print(colored(f"Something problem with login in bot: {e}", "yellow"))
