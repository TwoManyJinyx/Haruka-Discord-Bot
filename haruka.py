
#! HARUKA BOT made by Jinyx
# if this bot was shared publicly, please do note that you have to credit the creator for this
# this is a work in progress build so i wouldn't even recommend it to be shared publicly either
# but uh yeah, important thing to do with her is to alwaysgiver her headpats
# idk why im writing this, anyways piss off

# TODO list
#* - reward system for the headpat streak
#// - add the /streak command to make it easier to see the streak status
#// - hide the token
#* - get this into git/github
#* - make an /about command

#* imports
import discord, random, sqlite3, os
from discord import app_commands
from discord.ext import commands
from datetime import date, datetime, timezone, timedelta
from dotenv import load_dotenv

#? ------  Database Setup (for streaks) --------
#* database for streak
db = sqlite3.connect("haruka.db")
db.execute("""
    CREATE TABLE IF NOT EXISTS streaks (
        user_id   INTEGER PRIMARY KEY,
        streak    INTEGER NOT NULL,
        best      INTEGER NOT NULL,
        last_date TEXT NOT NULL
    )
""")
db.commit()

#* milestones for the streak (wip)
# MILESTONES = {
#     3: {"title": "New Friend",  "message": haruka}
#     7:
#     14:
#     30:
# }

#* updating the streak
def update_streak(user_id: int):
    """Returns (streak, best, counted_today)."""
    today = datetime.now(timezone.utc).date()
    row = db.execute(
        "SELECT streak, best, last_date FROM streaks WHERE user_id = ?", (user_id,)
    ).fetchone()

    if row is None:
        streak, best = 1, 1
    else:
        streak, best, last = row[0], row[1], date.fromisoformat(row[2])
        if last == today:
            return streak, best, False
        streak = streak + 1 if last == today - timedelta(days=1) else 1
        best = max(best, streak)

    db.execute(
        """INSERT INTO streaks (user_id, streak, best, last_date)
           VALUES (?, ?, ?, ?)
           ON CONFLICT(user_id) DO UPDATE SET
               streak = excluded.streak,
               best = excluded.best,
               last_date = excluded.last_date""",
        (user_id, streak, best, today.isoformat()),
    )
    db.commit()
    return streak, best, True

#* getting the info about the streak
def get_streak(user_id: int):
    row = db.execute(
        "SELECT streak, best, last_date FROM streaks WHERE user_id = ?", (user_id, )
    ).fetchone()
    if row is None:
        return 0, 0, None
    return row[0], row[1], date.fromisoformat(row[2])


#? ------  Python Stuff  --------
GUILD_ID = discord.Object(id=1545758695097499659)

#* intents
intents = discord.Intents.default()
client = commands.Bot(command_prefix="!", intents=intents)

#* terminal stuff
@client.event
async def on_ready():
    client.tree.copy_global_to(guild=GUILD_ID)
    await client.tree.sync(guild=GUILD_ID)
    print(f'We have logged in as {client.user}')


#? ------  Global Variables  --------
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')



#? ------  Bot Commands  --------
#* dice command 
@client.tree.command(name="dice", description="Picks a random number between low and high (1-10 by default)")
@app_commands.describe(low="Lowest possible number", high="Highest possible number")
async def dice(interaction: discord.Interaction, low: int = 1, high: int = 10):
    if low > high:
        low, high = high, low

    value = random.randint(low, high)
    await interaction.response.send_message(f"The dice landed on: **{value}**!")

#* head pat command
@client.tree.command(name="headpat", description="Gives Haruka a headpat")
async def headpat(interaction: discord.Interaction):
    #* variables
    streak, best, counted = update_streak(interaction.user.id)
    username = interaction.user.name
    file = discord.File("assets/images/headpat.jpg", filename="headpat.jpg")

    embed = discord.Embed (
        title=f"{username} gave Haruka a headpat", 
        description="She's happy", 
        color=0x6934ad
    )
    embed.set_thumbnail(url="attachment://headpat.jpg")

    #* headpat streak system
    footer = f"Headpat streak: {streak} day{'s' if streak != 1 else ''} • Best: {best}"
    if not counted:
        footer += " • You have already gave Haruka her headpat today"
    embed.set_footer(text=footer)

    await interaction.response.send_message(embed=embed, file=file)

#* streak command
@client.tree.command(name="streak", description="Shows all of your streaks and details about your rewards")
async def streak(interaction: discord.Interaction):
    #* variables
    streak, best, counted = update_streak(interaction.user.id)
    username = interaction.user.name
    file = discord.File("assets/images/emoji.jpg", filename="emoji.jpg")

    embed = discord.Embed (
        title=f"{username}'s streaks",
        description="Here is your streaks",
        color=0x6934ad
    )
    embed.set_thumbnail(url="attachment://emoji.jpg")

    footer = f"Headpat streak: **{streak}**!"
    embed.set_footer(text=footer)

    await interaction.response.send_message(embed=embed, file=file)


#* to make the bot run
#* i should probably hid the token somewhere but im to lazy to do it today so im not gonna do that yet
client.run(TOKEN)
