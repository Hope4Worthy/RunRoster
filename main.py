# libraires
from __future__ import print_function
from pydoc import describe
from secrets import choice
import discord
from discord.ui import View
import time as tm
from datetime import datetime
from dateutil import parser, tz

# bot info
TOKEN = ""

# emojis
tank = "<:Tank:958144873402368000>"
heal = "<:Heal:958144828242288650>"
damage = "<:Damage:958144784298561556>"
remove = "<:Remove:958180465989287936>"
general = "<:Add:959545085610045440>"
delete = "\N{CROSS MARK}"

# lookup lists
# all entries are as follows
# 	['<abreviahtion>', '<full name>']
# entries are placed in alphebetical order
# if adding an entry ensure it is placed in the proper list as it effects other parts of the program such as auto roster seating
dungeonNames = [
    ["AC", "Arx Corninum"],
    ["BCI", "Banished Cells I"],
    ["BCII", "Banished Cells II"],
    ["BDC", "Blessed Crucible"],
    ["BDV", "Black Drake Villa"],
    ["BH", "Blackheart Haven"],
    ["BRF", "Bloodroot Forge"],
    ["CA", "The Coral Aerie"],
    ["COAI", "City of Ash I"],
    ["COAII", "City of Ash II"],
    ["COHI", "Crypt of Hearts I"],
    ["COHII", "Crypt of Hearts II"],
    ["COS", "Cradle of Shadows"],
    ["CU", "The Cauldron"],
    ["CT", "Castle Thorn"],
    ["DSCI", "Darkshade Cavers I"],
    ["DSCII", "Darkshade Cavers II"],
    ["DC", "The Dread Cellar"],
    ["DK", "Direfrost Keep"],
    ["DOM", "Depths of Malatar"],
    ["EHI", "Elden Hollow I"],
    ["EHII", "Elden Hollow II"],
    ["ERE", "Earthen Root Enclave"],
    ["FGI", "Fungal Grotto I"],
    ["FGII", "Fungal Grotto II"],
    ["FH", "Falkreath Hold"],
    ["FL", "Fang Lair"],
    ["Fv", "Frostvault"],
    ["GD", "Graven Deep"],
    ["ICP", "Imperial City Prison"],
    ["IR", "Icereach"],
    ["LOM", "Lair of Maarselok"],
    ["MGF", "Moongrave Fane"],
    ["MHK", "Moon Hunter Keep"],
    ["MOS", "March of Sacrifices"],
    ["ROM", "Ruins of Mazzatun"],
    ["RPB", "Red Petal Bastion"],
    ["SW", "Selene's Web"],
    ["SCI", "Spindleclutch I"],
    ["SCII", "Spindleclutch II"],
    ["SCP", "Scalecaller Peak"],
    ["SG", "Stone Garden"],
    ["SR", "Shipwright's Regret"],
    ["TI", "Tempest Island"],
    ["UHG", "Unhallowed Grave"],
    ["VOM", "Vaults of Madness"],
    ["VF", "Volenfell"],
    ["WGT", "White-Gold Tower"],
    ["WSI", "Wayrest Sewers I"],
    ["WSII", "Wayrest Sewers II"],
]
trialNames = [
    ["AA", "Aetherian Archive"],
    ["HRC", "hel Ra Citadel"],
    ["SO", "Sanctum Ophidia"],
    ["MOL", "Maw of Lorkhaj"],
    ["HOF", "Halls of Fabrication"],
    ["AS", "Asylum Sanctorium"],
    ["CR", "Cloudrest"],
    ["SS", "Sunspire"],
    ["KA", "Kyne's Aegis"],
    ["RG", "Rockgrove"],
    ["DsR", "Dreadsail Reef"],
]
arenaNames = [["DA", "Dragonstar Arena"], ["BRP", "Blackrose Prison"]]
activityTitles = []
for item in dungeonNames:
    activityTitles.append(item[1])
for item in trialNames:
    activityTitles.append(item[1])
for item in arenaNames:
    activityTitles.append(item[1])

tzinfos = {"EST": tz.gettz}

bot = discord.Bot()

# function for displaying dynamic time zones
def convert_to_unix_time(date: datetime) -> str:
    # Convert to unix time
    return f"<t:{int(date.timestamp())}:t>"


def convert_to_unix_date(date: datetime) -> str:
    # Convert to unix time
    return f"<t:{int(date.timestamp())}:d>"


# function for autocomplete lookup
async def get_activity(ctx: discord.AutocompleteContext):
    return [
        activity
        for activity in activityTitles
        if activity.lower().replace(" ", "").startswith(ctx.value.lower().replace(" ", ""))
    ]


class activityView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(
        placeholder="Select Option",
        custom_id="activityView:select",
        options=[
            discord.SelectOption(label="Register Tank", emoji=tank),
            discord.SelectOption(label="Register Healer", emoji=heal),
            discord.SelectOption(label="Register DPS", emoji=damage),
            discord.SelectOption(label="Remove", emoji=remove),
            discord.SelectOption(label="Delete Roster", emoji=delete),
        ],
    )
    async def select_callback(self, select, interaction):
        option = select.values[0]
        user = interaction.user
        message = interaction.message
        embed = message.embeds[0]

        if option == "Remove":
            await interaction.response.edit_message(embed=removeUser(user, embed))
        elif option == "Register Tank":
            await interaction.response.edit_message(embed=addTank(user, embed))
        elif option == "Register Healer":
            await interaction.response.edit_message(embed=addHealer(user, embed))
        elif option == "Register DPS":
            await interaction.response.edit_message(embed=addDPS(user, embed))
        elif option == "Delete Roster":
            if embed.fields[0].value == user.mention:
                await interaction.channel.delete()
            else:
                await interaction.response.send("fail")


class eventView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(
        placeholder="Select Option",
        custom_id="eventView:select",
        options=[
            discord.SelectOption(label="Register", emoji=general),
            discord.SelectOption(label="Remove", emoji=remove),
            discord.SelectOption(label="Delete Roster", emoji=delete),
        ],
    )
    async def select_callback(self, select, interaction):
        option = select.values[0]
        user = interaction.user
        message = interaction.message
        embed = message.embeds[0]

        if option == "Remove":
            await interaction.response.edit_message(embed=removeUser(user, embed))
        elif option == "Register":
            await interaction.response.edit_message(embed=addGeneral(user, embed))
        elif option == "Delete Roster":
            if embed.fields[0].value == user.mention:
                await interaction.channel.delete()
            else:
                await interaction.response.send("fail")


@bot.slash_command(name="roster-activity", description="create a roster for a dungeon, trial, or arena")
@discord.option("activity_name", description="Choose your activity", autocomplete=get_activity)
@discord.option(
    "level", description="Choose the level of the activity", choices=["Normal", "Veteran", "Veteran Hard Mode"]
)
@discord.option("timezone", description="Choose the appropriate Timezone", choices=["EST", "CST", "MST", "PST"])
@discord.option("date", description="Use the following format - mm/dd")
@discord.option("time", description="Use the followign format - hh:mm <am/pm>")
async def activityRoster(
    ctx, activity_name, level, date, time, timezone, tank_count=0, healer_count=0, dps_count=0, notes=""
):
    category = ctx.channel.category

    if timezone == "EST":
        time_offset = "-0500"
    elif timezone == "CST":
        time_offset = "-0600"
    elif timezone == "MST":
        time_offset = "-0700"
    if timezone == "PST":
        time_offset = "-0800"

    parse_string = date + "/" + str(tm.localtime(tm.time()).tm_year) + " " + time + " " + time_offset
    date_time = parser.parse(parse_string)

    if level == "Veteran Hard Mode":
        level_name = "Veteran Hard Mode "
        level_abr = "vHM"
    elif level == "Veteran":
        level_name = "Veteran "
        level_abr = "v"
    else:
        level_name = "Normal "
        level_abr = "n"

    eType, abr, activity_name = getType(activity_name)

    channel = await ctx.guild.create_text_channel(
        name=level_abr + " " + abr + " " + date.replace("/", "-"), category=category
    )

    if eType == "Trial":
        tankNum = 2
        healerNum = 2
        dpsNum = 8
        seats = 0
    elif eType == "Dungeon":
        tankNum = 1
        healerNum = 1
        dpsNum = 2
        seats = 0
    else:  # arena
        tankNum = 0
        healerNum = 0
        dpsNum = 0
        seats = 4

    if int(tank_count) != 0:
        tankNum = int(tank_count)
    if int(healer_count) != 0:
        healerNum = int(healer_count)
    if int(dps_count) != 0:
        dpsNum = int(dps_count)

    if eType == "Arena":
        message = await channel.send(
            view=eventView(),
            embed=createEmbed(
                ctx.author,
                eType,
                (level_name + " - " + activity_name),
                date_time,
                tankNum=tankNum,
                healerNum=healerNum,
                dpsNum=dpsNum,
                seats=seats,
                notes=notes,
            ),
        )
    else:
        message = await channel.send(
            view=activityView(),
            embed=createEmbed(
                ctx.author,
                eType,
                (level_name + " - " + activity_name),
                date_time,
                tankNum=tankNum,
                healerNum=healerNum,
                dpsNum=dpsNum,
                seats=seats,
                notes=notes,
            ),
        )
    await ctx.respond("created roster in " + channel.mention, ephemeral=True)
    return channel


@bot.slash_command(
    name="roster-event", description="create a roster for an event - set seats to -1 to create an expandable roster"
)
@discord.option("timezone", description="Choose the appropriate Timezone", choices=["EST", "CST", "MST", "PST"])
@discord.option("date", description="Use the following format - mm/dd")
@discord.option("time", description="Use the followign format - hh:mm <am/pm>")
async def eventRoster(ctx, event_name, date, time, timezone, seats, notes=""):
    channel = ctx.channel
    category = channel.category
    channel = await ctx.guild.create_text_channel(name=event_name + " " + date.replace("/", "-"), category=category)
    message = await channel.send(
        view=eventView(),
        embed=createEmbed(ctx.author, "Event", event_name, date, time, timezone, seats=int(seats), notes=notes),
    )
    await ctx.respond("created roster in " + channel.mention, ephemeral=True)


@bot.slash_command(name="roster-edit", description="edit the roseted contained in the currennt channel")
@discord.option(
    "level", description="Choose the level of the activity", choices=["Normal", "Veteran", "Veteran Hard Mode"]
)
@discord.option("timezone", description="Choose the appropriate Timezone", choices=["EST", "CST", "MST", "PST"])
@discord.option("date", description="Use the following format - mm/dd")
@discord.option("time", description="Use the followign format - hh:mm <am/pm>")
async def editRoster(ctx, date="", time="", timezone="", level=""):

    if level == "Veteran Hard Mode":
        level_abr = "vHM"
    elif level == "Veteran":
        level_abr = "v"
    else:
        level_abr = "n"

    channel = ctx.channel
    user = ctx.author
    message = channel.history(oldest_first=True)
    for message in await channel.history(oldest_first=True).flatten():
        if message.author.id == bot.user.id:
            msg = message
            break
    embed = msg.embeds[0]
    if embed.fields[0].value == user.mention:
        if date.strip():
            index = 2
            cName = channel.name
            nDate = ""
            flag = 0
            for char in cName:
                if char == "-":
                    nDate += char
                    flag += 1
                elif flag < 2:
                    nDate += char
                else:
                    break
            nDate += " " + date
            embed.set_field_at(index=index, name=embed.fields[index].name, value=date, inline=False)
            await channel.edit(name=nDate.replace("/", "-"))

        if time.strip():
            index = 3
            flag = 0
            tZone = ""
            for char in embed.fields[index].value:
                if char == "-":
                    flag = 1
                    continue
                elif flag == 0:
                    continue
                else:
                    tZone += char
            nTime = time + " -" + tZone
            embed.set_field_at(index=index, name=embed.fields[index].name, value=nTime, inline=False)

        if level.strip():
            nName = level + " "
            nTitle = level_abr
            oName = embed.title
            oTitle = channel.name
            flag = 0
            index = 1
            for char in oName:
                if flag:
                    nName += char
                else:
                    if char == "-":
                        nName += char
                        flag = 1
            flag = 0
            for char in oTitle:
                if flag:
                    nTitle += char
                else:
                    if char == "-":
                        nTitle += char
                        flag = 1
            embed.title = nName
            embed.set_field_at(index=index, name=embed.fields[index].name, value=nName, inline=False)
            await channel.edit(name=nTitle)

        await msg.edit(embed=embed)
        await ctx.respond("done", ephemeral=True)


def createEmbed(creator, eType, name, date_time, seats=0, tankNum=2, healerNum=2, dpsNum=8, notes=""):
    embed = discord.Embed(title=name, color=0x55CC78)
    embed.add_field(inline=False, name="Creator", value=creator.mention)
    embed.add_field(inline=False, name=eType, value=name)
    embed.add_field(inline=False, name="Date", value=convert_to_unix_date(date_time))
    embed.add_field(inline=False, name="Time", value=convert_to_unix_time(date_time))
    if eType == "Event" or eType == "Arena":
        peopleMessage = ""
        if int(seats) > 0:
            for i in range(int(seats)):
                peopleMessage += str(i + 1) + ":\n"
        else:
            peopleMessage = "** **"
        embed.add_field(inline=False, name="People", value=peopleMessage)
    else:
        tankMessage = ""
        healerMessage = ""
        dpsMessage = ""
        for i in range(int(tankNum)):
            tankMessage += str(i + 1) + ": \n"
        for i in range(int(healerNum)):
            healerMessage += str(i + 1) + ": \n"
        for i in range(int(dpsNum)):
            dpsMessage += str(i + 1) + ": \n"
        embed.add_field(inline=False, name="Tank " + tank, value=tankMessage)
        embed.add_field(inline=False, name="** **", value="** **")
        embed.add_field(inline=False, name="Healer " + heal, value=healerMessage)
        embed.add_field(inline=False, name="** **", value="** **")
        embed.add_field(inline=False, name="DPS " + damage, value=dpsMessage)
    if notes.strip() != "":
        embed.add_field(inline=False, name="Notes", value=notes)
    embed.add_field(
        inline=False,
        name="\u200b",
        value="Select the appropraite action from the list below.\nOnly the roster creator can delete the roster.\nTo change roles please remove yourself then add yourself back into the roster with the proper role.",
    )
    return embed


def getType(eName):
    eType = "Dungeon"
    length = len(eName)
    for abr, name in arenaNames:
        if abr in eName.upper() and length <= 4:
            return ["Arena", abr, name]
        elif name.upper() in eName.upper():
            return ["Arena", abr, name]
    for abr, name in trialNames:
        if abr in eName.upper() and length <= 4:
            return ["Trial", abr, name]
        elif name.upper() in eName.upper():
            return ["Trial", abr, name]
    for abr, name in dungeonNames:
        if abr in eName.upper() and length <= 4:
            return ["Dungeon", abr, name]
        elif name.upper() in eName.upper():
            return ["Dungeon", abr, name]
    return eType


def checkDuplicate(user, embed):
    for field in embed.fields:
        if user.mention in field.value:
            if "Creator" in field.name:
                continue
            else:
                return True
    return False


def removeUser(user, embed):
    index = 0
    for field in embed.fields:
        if user.mention in field.value:
            if not "Creator" in field.name:
                field = field
                break
            else:
                index += 1
        else:
            index += 1

    if not "-" in field.value:
        new = field.value.replace(user.mention, " ")
        embed.set_field_at(index=index, name=field.name, value=new, inline=False)
        return embed
    else:
        field = embed.fields[4]
        for i in range(1, 9999):
            if str(i) + "-" in field.value:
                new = field.value.replace(str(i) + "-" + user.mention, "")
                embed.set_field_at(index=4, name=field.name, value=new, inline=False)
                break
            elif not str(i) in field.value:
                break
            else:
                continue
        return embed


def addTank(user, embed):
    if checkDuplicate(user, embed):
        return embed
    index = 0
    for field in embed.fields:
        if "Tank" in field.name:
            field = field
            break
        else:
            index += 1
    for i in range(1, 13):
        if str(i) + ":<@" in field.value:
            continue
        elif str(i) + ":" in field.value:
            new = field.value.replace(str(i) + ":", str(i) + ":" + user.mention)
            embed.set_field_at(index=4, name=embed.fields[4].name, value=new)
            break
        else:
            break
    return embed


def addHealer(user, embed):
    if checkDuplicate(user, embed):
        return embed
    index = 1
    for field in embed.fields:
        if "Healer" in field.name:
            field = field
            index -= 1
            break
        else:
            index += 1

    for i in range(1, 13):
        if str(i) + ":<@" in field.value:
            continue
        elif str(i) + ":" in field.value:
            new = field.value.replace(str(i) + ":", str(i) + ":" + user.mention)
            embed.set_field_at(index=6, name=embed.fields[6].name, value=new)
            break
        else:
            break
    return embed


def addDPS(user, embed):
    if checkDuplicate(user, embed):
        return embed
    index = 1
    for field in embed.fields:
        if "DPS" in field.name:
            field = field
            index -= 1
            break
        else:
            index += 1

    for i in range(1, 13):
        if str(i) + ":<@" in field.value:
            continue
        elif str(i) + ":" in field.value:
            new = field.value.replace(str(i) + ":", str(i) + ":" + user.mention)
            embed.set_field_at(index=index, name=embed.fields[index].name, value=new)
            break
        else:
            break
    return embed


def addGeneral(user, embed):
    if checkDuplicate(user, embed):
        return embed
    field = embed.fields[4]
    if ":" in field.value:
        for i in range(1, 9999):
            if str(i) + ":<@" in field.value:
                continue
            elif str(i) + ":" in field.value:
                new = field.value.replace(str(i) + ":", str(i) + ":" + user.mention, 1)
                embed.set_field_at(index=4, name=embed.fields[4].name, value=new)
                break
            else:
                break
    else:
        for i in range(1, 9999):
            if str(i) + "-<@" in field.value:
                continue
            else:
                new = field.value + "\n" + str(i) + "-" + user.mention
                embed.set_field_at(index=4, name=embed.fields[4].name, value=new)
                break
    return embed


@bot.event
async def on_ready():
    print("********** BOT RUNNING **********")
    bot.add_view(activityView())
    bot.add_view(eventView())


bot.run(TOKEN)
