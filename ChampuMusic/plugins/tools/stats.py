import platform
from sys import version as pyver

import psutil
from pyrogram import __version__ as pyrover
from pyrogram import filters
from pyrogram.errors import MessageIdInvalid
from pyrogram.types import InputMediaPhoto, Message
try:
    from pytgcalls import __version__ as pytgver
except ImportError:
    try:
        from pytgcalls.__version__ import __version__ as pytgver
    except ImportError:
        pytgver = "1.2.9"

import config
from ChampuMusic import app
from ChampuMusic.core.userbot import assistants
from ChampuMusic.misc import SUDOERS, mongodb
from ChampuMusic.plugins import ALL_MODULES
from ChampuMusic.utils.database import get_served_chats, get_served_users, get_sudoers
from ChampuMusic.utils.decorators.language import language, languageCB
from ChampuMusic.utils.inline.stats import back_stats_buttons, stats_buttons
from config import BANNED_USERS

# Group Stats Command
@app.on_message(filters.command(["stats", "gstats"]) & filters.group & ~BANNED_USERS)
@language
async def stats_global(client, message: Message, _):
    upl = stats_buttons(_, message.from_user.id in SUDOERS)
    await message.reply_photo(
        photo=config.STATS_IMG_URL,
        caption=f"<b>📊 Global Stats Panel for {app.mention}</b>",
        reply_markup=upl,
    )

# Back to Stats Callback
@app.on_callback_query(filters.regex("stats_back") & ~BANNED_USERS)
@languageCB
async def home_stats(client, CallbackQuery, _):
    upl = stats_buttons(_, CallbackQuery.from_user.id in SUDOERS)
    await CallbackQuery.edit_message_text(
        text=f"<b>📊 Global Stats Panel for {app.mention}</b>",
        reply_markup=upl,
    )

# Top Overall Stats Callback
@app.on_callback_query(filters.regex("TopOverall") & ~BANNED_USERS)
@languageCB
async def overall_stats(client, CallbackQuery, _):
    await CallbackQuery.answer()
    upl = back_stats_buttons(_)
    served_chats = len(await get_served_chats())
    served_users = len(await get_served_users())
    text = (
        f"<b>📈 Bot Usage Summary</b>\n\n"
        f"<b>🤖 Bot Name:</b> {app.mention}\n"
        f"<b>🎛 Assistants:</b> <code>{len(assistants)}</code>\n"
        f"<b>🚫 Banned Users:</b> <code>{len(BANNED_USERS)}</code>\n"
        f"<b>💬 Served Chats:</b> <code>{served_chats}</code>\n"
        f"<b>👥 Served Users:</b> <code>{served_users}</code>\n"
        f"<b>📦 Modules Loaded:</b> <code>{len(ALL_MODULES)}</code>\n"
        f"<b>🛡️ Sudo Users:</b> <code>{len(SUDOERS)}</code>\n"
        f"<b>👋 Auto Leave Assistants:</b> <code>{config.AUTO_LEAVING_ASSISTANT}</code>\n"
        f"<b>⏱️ Max Song Duration:</b> <code>{config.DURATION_LIMIT_MIN} Minutes</code>\n"
    )
    med = InputMediaPhoto(media=config.STATS_IMG_URL, caption=text)
    try:
        await CallbackQuery.edit_message_media(media=med, reply_markup=upl)
    except MessageIdInvalid:
        await CallbackQuery.message.reply_photo(
            photo=config.STATS_IMG_URL, caption=text, reply_markup=upl
        )

# Bot System Stats for Sudo Users
@app.on_callback_query(filters.regex("bot_stats_sudo"))
@languageCB
async def bot_stats(client, CallbackQuery, _):
    if CallbackQuery.from_user.id not in SUDOERS:
        return await CallbackQuery.answer(_["gstats_4"], show_alert=True)

    upl = back_stats_buttons(_)
    await CallbackQuery.answer()

    p_core = psutil.cpu_count(logical=False)
    t_core = psutil.cpu_count(logical=True)
    ram = str(round(psutil.virtual_memory().total / (1024.0**3))) + " GB"
    try:
        cpu_freq = psutil.cpu_freq().current
        cpu_freq = f"{round(cpu_freq / 1000, 2)} GHz" if cpu_freq >= 1000 else f"{round(cpu_freq, 2)} MHz"
    except:
        cpu_freq = "Unavailable"

    hdd = psutil.disk_usage("/")
    total = hdd.total / (1024.0**3)
    used = hdd.used / (1024.0**3)
    free = hdd.free / (1024.0**3)

    call = await mongodb.command("dbstats")
    datasize = call["dataSize"] / 1024
    storage = call["storageSize"] / 1024
    served_chats = len(await get_served_chats())
    served_users = len(await get_served_users())
    sudo_count = len(await get_sudoers())

    text = (
        f"<b>📊 {app.mention} System Stats</b>\n\n"
        f"<b>🔧 System:</b>\n"
        f"• OS : <code>{platform.system()}</code>\n"
        f"• RAM : <code>{ram}</code>\n"
        f"• CPU Cores : <code>{p_core}</code> Physical | <code>{t_core}</code> Logical\n"
        f"• Frequency : <code>{cpu_freq}</code>\n\n"
        f"<b>💾 Disk & Database:</b>\n"
        f"• Disk : <code>{total:.2f}GB</code> Total | <code>{used:.2f} GB</code> Used | <code>{free:.2f} GB</code> Free\n"
        f"• DB Size : <code>{datasize:.2f} MB</code>\n"
        f"• Storage Used : <code>{storage:.2f} MB</code>\n"
        f"• Collections : <code>{call['collections']}</code> | Objects : <code>{call['objects']}</code>\n\n"
        f"<b>👥 Usage:</b>\n"
        f"• Served Chats : <code>{served_chats}</code>\n"
        f"• Served Users : <code>{served_users}</code>\n\n"
        f"<b>🔒 Moderation:</b>\n"
        f"• Banned Users : <code>{len(BANNED_USERS)}</code>\n"
        f"• Sudoers : <code>{sudo_count}</code>\n"
        f"• Modules : <code>{len(ALL_MODULES)}</code>\n\n"
        f"<b>⚙️ Software:</b>\n"
        f"• Python : <code>{pyver.split()[0]}</code>\n"
        f"• Pyrogram : <code>{pyrover}</code>\n"
        f"• PyTgCalls : <code>{pytgver}</code>"
    )

    med = InputMediaPhoto(media=config.STATS_IMG_URL, caption=text)
    try:
        await CallbackQuery.edit_message_media(media=med, reply_markup=upl)
    except MessageIdInvalid:
        await CallbackQuery.message.reply_photo(
            photo=config.STATS_IMG_URL, caption=text, reply_markup=upl
        )
