"""正規表現を使用してDiscordのURLを検索するためにreを使用しています。"""

import re
from datetime import datetime, timezone
from typing import Union

import discord


# Intents.allの場合、Presence, Server Members, Message ContentのIntentをすべてオンにしないと動きません。
# レートリミットを避けるため、現在は特定のギルドでのみ可能となっています。
intents = discord.Intents.all()
client = discord.Client(intents=intents)
guild = discord.Object(id=0)
tree = discord.app_commands.CommandTree(client)
pattern = r"https://discord.com/channels/\d+/\d+/\d+"


# メッセージ内に複数メッセージURLがあった場合、ほかのメッセージも閲覧できるようにviewを使用してセレクトを表示し、
# ほかのメッセージも見れるようにします。
class UrlsSelect(discord.ui.View):
    """セレクトから選択されたメッセージURLの展開やセレクトの作成を行います。"""

    def __init__(self, options: list, placeholder: str, is_disabled: bool):
        super().__init__(timeout=None)
        self.options = options
        self.placeholder = placeholder
        self.is_diasbled = is_disabled
        self.create_select()

    def create_select(self):
        """メッセージURLを選択するセレクトを作成"""
        select = discord.ui.Select(
            custom_id="urls_select",
            placeholder=self.placeholder,
            disabled=self.is_diasbled,
            options=self.options
        )
        select.callback = self.select
        self.add_item(select)

    async def select(self, interaction: discord.Interaction):
        """選択された際の処理"""
        await interaction.response.defer(thinking=True, ephemeral=True)
        values = interaction.data["values"]
        split = values[0].split("_")
        link = (
            "https://discord.com/channels/"
            + split[0] + "/"
            + split[1] + "/"
            + split[2]
        )
        link_message = await SearchUrl(link)
        embed, button_view = CreateMessage(link_message)
        await interaction.followup.send(embed=embed, view=button_view)


# もし展開先のメッセージに画像があった場合、このボットではその画像を表示するようにするボタンを付けるようにしています。
class ShowPhoto(discord.ui.DynamicItem[discord.ui.Button], template=r"(?P<guild>[0-9]+):(?P<channel>[0-9]+):(?P<message>[0-9]+)"):
    """展開先のメッセージにある画像を見れるようにするボタンの処理・作成をします。"""

    def __init__(self, link_guild_id: str, link_channel_id: str, link_message_id: str):
        super().__init__(
            discord.ui.Button(
                emoji="🖼️",
                style=discord.ButtonStyle.grey,
                custom_id=(
                    link_guild_id + ":"
                    + link_channel_id + ":"
                    + link_message_id
                )
            )
        )
        self.link_guild_id: str = link_guild_id
        self.link_channel_id: str = link_channel_id
        self.link_message_id: str = link_message_id

    @classmethod
    async def from_custom_id(cls, interaction: discord.Interaction, item: discord.ui.Button, match: re.Match[str], /):
        link_guild_id = str(match["guild"])
        link_channel_id = str(match["channel"])
        link_message_id = str(match["message"])
        return cls(link_guild_id, link_channel_id, link_message_id)

    async def callback(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(thinking=True, ephemeral=True)
        link_message = await SearchUrl(
            "https://discord.com/channels/"
            + self.link_guild_id + "/"
            + self.link_channel_id + "/"
            + self.link_message_id
        )
        show_photo_embeds = []
        embed = discord.Embed()
        for attachment in link_message.attachments:
            embed.set_image(url=attachment.url)
            show_photo_embeds.append(embed)
        await interaction.followup.send(embeds=show_photo_embeds)


# もし展開先のメッセージに埋め込みがあった場合、このボットではその埋め込みを表示するようにするボタンを付けるようにしています。
class ShowEmbed(discord.ui.DynamicItem[discord.ui.Button], template=r"(?P<guild>[0-9]+):(?P<channel>[0-9]+):(?P<message>[0-9]+)"):
    """展開先のメッセージにある埋め込みを見れるようにするボタンの処理・作成をします。"""

    def __init__(self, link_guild_id: str, link_channel_id: str, link_message_id: str):
        super().__init__(
            discord.ui.Button(
                emoji="📦",
                style=discord.ButtonStyle.grey,
                custom_id=(
                    link_guild_id + ":"
                    + link_channel_id + ":"
                    + link_message_id
                )
            )
        )
        self.link_guild_id: str = link_guild_id
        self.link_channel_id: str = link_channel_id
        self.link_message_id: str = link_message_id

    @classmethod
    async def from_custom_id(cls, interaction: discord.Interaction, item: discord.ui.Button, match: re.Match[str], /):
        link_guild_id = str(match["guild"])
        link_channel_id = str(match["channel"])
        link_message_id = str(match["message"])
        return cls(link_guild_id, link_channel_id, link_message_id)

    async def callback(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(thinking=True, ephemeral=True)
        link_message = await SearchUrl(
            "https://discord.com/channels/"
            + self.link_guild_id + "/"
            + self.link_channel_id + "/"
            + self.link_message_id
        )
        show_embeds = []
        for embed in link_message.embeds:
            show_embeds.append(embed)
        await interaction.followup.send(embeds=show_embeds)


# もしメッセージがいずれかの理由で取得できなかった場合は、NONEとしてlink_messageを返します。
async def SearchUrl(link: str):
    """メッセージURLを検索し、検索結果を返します。"""
    split = link.split("/")
    link_guild_id = int(split[4])
    link_channel_id = int(split[5])
    link_message_id = int(split[6])
    link_guild = client.get_guild(link_guild_id)
    if link_guild is not None:
        link_channel = link_guild.get_channel(link_channel_id)
        if link_channel is not None:
            try:
                link_message = await link_channel.fetch_message(link_message_id)
            except (discord.errors.NotFound, discord.errors.Forbidden, discord.errors.HTTPException):
                link_message = "NONE"
    return link_message


def CreateMessage(link_message: Union[discord.Message, str]):
    """URL先のメッセージ内容を記す埋め込みを作成します。"""
    embed = discord.Embed()
    button_view = []
    author_name = GetAuthorName(message=link_message)
    embed.set_thumbnail(url=link_message.author.display_avatar.url)
    if link_message == "NONE":
        embed.description = (
            "**メッセージが見つかりませんでした。**\n \n"
            + "ボットが展開先のサーバーに追加されていないか、"
            + "メッセージを閲覧する権限がない・メッセージが既に削除されている、存在していない可能性があります。"
        )
        embed.color = 0xe06e64
    else:
        if link_message.content:
            link_message_content = link_message.content
            if "```" not in link_message.content:
                link_message_content = "```" + link_message_content + "```"
        else:
            link_message_content = "内容が存在していません。"
        datetime_object = datetime.fromisoformat(str(link_message.created_at))
        timestamp = int(datetime_object.replace(tzinfo=timezone.utc).timestamp())
        description = (
            "**サーバー名:** `" + link_message.guild.name + "`\n"
            "**チャンネル:** " + link_message.channel.mention + "\n"
            "**送信者:** " + author_name + "\n"
            "**送信時間:** <t:" + str(timestamp) + ":F>\n"
            "**内容:** " + link_message_content
        )
        embed.set_footer(text="※メニューではボットが参加しておらず取得できなかったメッセージは省略しています")
        if link_message.embeds:
            button_view.append(
                ShowEmbed(
                    str(link_message.guild.id),
                    str(link_message.channel.id),
                    str(link_message.id)
                )
            )
            description += "\n \nこのメッセージには埋め込みが存在しています。\n埋め込みも表示する場合は下のボタンを押してください。"
        if link_message.attachments:
            button_view.append(
                ShowPhoto(
                    str(link_message.guild.id),
                    str(link_message.channel.id),
                    str(link_message.id)
                )
            )
            description += "\n \nこのメッセージには画像が存在しています。\n画像を表示する場合は下のボタンを押してください。"
        embed.description = link_message.jump_url + " のメッセージを表示しています...\n \n" + description
    return embed, button_view


# もし展開先のメッセージの送信者がニックネームを付けていたり、サーバーに残っている場合、送信者の表記をわかりやすくするために
# この処理を入れています。
def GetAuthorName(message: discord.Message):
    """展開先のメッセージの送信者の名前を見る"""
    author_name = message.author.name
    if message.author in message.guild.members:
        if message.author.nick is not None:
            author_name = message.author.nick
        elif message.author.global_name is not None:
            author_name = message.author.global_name
        author_name = "`" + author_name + "`" + " (" + message.author.mention + ")"
    else:
        author_name = "`" + author_name + "`"
    return author_name


@client.event
async def on_ready():
    """起動を知らせる処理"""
    print("起動したよ\nクライアント: "
          + str(client.user)
          + " , "
          + str(client.application_id))


# ボタン・セレクトは通常再起動すると動かなくなってしまいます。
# そのためこのsetup_hookを用いてPresistent化をして再起動後も動くようにします。
@client.event
async def setup_hook():
    """ボタン・セレクトをPresistent化する"""
    client.add_view(UrlsSelect(
        options=[
            discord.SelectOption(label="なにもないよ（笑）")
        ],
        is_disabled=False,
        placeholder="他にメッセージリンクがありません"
    )
    )
    client.add_dynamic_items(ShowPhoto)
    client.add_dynamic_items(ShowEmbed)


# 自動でsyncにすると、context_menuの名前を変更したとき以外もsyncされてしまうため、レートリミットにかかる可能性があります。
# 手動にすることであまり意味のないsyncも防ぐようにしています。
# また、特定のギルドにしかsyncされず、syncが可能なのはボットのオーナーのみです。
# clientを使用しているのでcommand_prefixが使えません。
@client.event
async def on_message(message: discord.Message):
    """syncするための処理"""
    if message.author == client.user:
        return
    elif message.author.id == client.application.owner.id:
        if message.content == "./ sync":
            await tree.sync(guild=guild)
            await message.reply("✅")


# メッセージ内に27個以上メッセージURLがある場合、26個以下のものしか読み込まれません。
# まあ、そんなに貼ってるメッセージなんてないと思いますがね（笑）
@tree.context_menu(name="メッセージURLを展開する")
@discord.app_commands.guilds(guild)
async def open_message_url(interaction: discord.Interaction, message: discord.Message):
    """展開するためのcontext menu"""
    await interaction.response.defer(thinking=True, ephemeral=True)
    ctx = message.content
    matches = re.findall(pattern, ctx)
    if not matches:
        await interaction.followup.send("### リンクがありません")
        return
    options = []
    is_disabled = False
    placeholder = "メッセージを選ぶ"
    link_message = await SearchUrl(link=str(matches[0]))
    embed, button_view = CreateMessage(link_message)
    if len(matches) == 1:
        options = [
            discord.SelectOption(label="なにもないよ（笑）")
        ]
        is_disabled = True
        placeholder = "他にメッセージリンクがありません"
    else:
        embed.description = embed.description + "\n \nメッセージ内にリンクが複数あります。\nほかのリンクの展開は下のセレクトから可能です。"
    for link in matches[1:]:
        if len(link) == 27:
            break
        split = link.split("/")
        link_guild_id = int(split[4])
        link_channel_id = int(split[5])
        link_message_id = int(split[6])
        link_guild = client.get_guild(link_guild_id)
        if link_guild is not None:
            link_channel = link_guild.get_channel(link_channel_id)
            try:
                await link_channel.fetch_message(link_message_id)
            except (discord.errors.NotFound, discord.errors.Forbidden, discord.errors.HTTPException):
                continue
            options.append(
                discord.SelectOption(
                    label=link_channel.name
                    + "での発言",
                    value=str(link_guild_id)
                    + "_"
                    + str(link_channel_id)
                    + "_"
                    + str(link_message_id)
                )
            )
    view = UrlsSelect(options, placeholder, is_disabled)
    for item in button_view:
        view.add_item(item)
    await interaction.followup.send(embed=embed, view=view)


client.run("BOT_TOKEN")
