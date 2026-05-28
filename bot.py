import asyncio
from telethon import TelegramClient, events

# ======= اینجا رو پر کن =======
API_ID = 30918199          # عدد api_id
API_HASH = '0ed2f85e1c63cf3726e8fb47ff03584e'
BOT_TOKEN = '8266764991:AAGZ95wo7Xsci-c5kL6g7IwQeA29AHW8zy0'
CHANNEL = 'https://t.me/+GBJ2-yPaRso5Yjg8'  # مثلاً @savemusic
# ================================

music_db = {'remix': [], 'dj_mix': [], 'artists': {}}

def get_info(msg):
    title, artist = '', ''
    if msg.file:
        title = msg.file.title or ''
        artist = msg.file.performer or ''
    return title.strip(), artist.strip()

def categorize(title, artist):
    t = (title + artist).lower()
    if 'remix' in t: return 'remix'
    if any(x in t for x in ['dj ', 'mix', 'ep ', 'club', 'podcast']): return 'dj'
    return 'artist'

async def build_index(client):
    music_db['remix'].clear()
    music_db['dj_mix'].clear()
    music_db['artists'].clear()
    ch = await client.get_entity(CHANNEL)
    async for msg in client.iter_messages(ch):
        if not (msg.audio or (msg.file and msg.file.mime_type and 'audio' in msg.file.mime_type)):
            continue
        title, artist = get_info(msg)
        if not title: continue
        link = f"https://t.me/{CHANNEL.replace('@','')}/{msg.id}"
        entry = f"[{title}]({link})" + (f" - {artist}" if artist else "")
        cat = categorize(title, artist)
        if cat == 'remix':
            music_db['remix'].append(entry)
        elif cat == 'dj':
            music_db['dj_mix'].append(entry)
        else:
            key = artist or 'سایر'
            music_db['artists'].setdefault(key, []).append(entry)

async def post_index(bot):
    total = len(music_db['remix']) + len(music_db['dj_mix']) + sum(len(v) for v in music_db['artists'].values())
    text = f"🎵 **ایندکس کانال Save Music**\n━━━━━━━━━━━━━━\n📊 مجموع: {total} آهنگ\n\n"
    
    if music_db['remix']:
        text += f"🔀 **ریمیکس‌ها ({len(music_db['remix'])})**\n"
        for t in music_db['remix']: text += f"  • {t}\n"
        text += "\n"
    
    if music_db['dj_mix']:
        text += f"🎧 **میکس DJ ({len(music_db['dj_mix'])})**\n"
        for t in music_db['dj_mix']: text += f"  • {t}\n"
        text += "\n"
    
    if music_db['artists']:
        text += "🎤 **بر اساس خواننده**\n\n"
        for artist, songs in sorted(music_db['artists'].items()):
            text += f"👤 **{artist}** ({len(songs)} آهنگ)\n"
            for s in songs: text += f"  • {s}\n"
            text += "\n"
    
    ch = await bot.get_entity(CHANNEL)
    msg = await bot.send_message(ch, text, parse_mode='md', link_preview=False)
    await bot.pin_message(ch, msg.id)
    print("✅ ایندکس ساخته و پین شد!")

async def main():
    user = TelegramClient('user_session', API_ID, API_HASH)
    await user.start()
    
    bot = TelegramClient('bot_session', API_ID, API_HASH)
    await bot.start(bot_token=BOT_TOKEN)
    
    print("📋 در حال خوندن موزیک‌ها...")
    await build_index(user)
    await post_index(bot)
    
    @user.on(events.NewMessage(chats=CHANNEL))
    async def handler(event):
        msg = event.message
        if not (msg.audio or (msg.file and msg.file.mime_type and 'audio' in msg.file.mime_type)):
            return
        title, artist = get_info(msg)
        if not title: return
        cat = categorize(title, artist)
        icons = {'remix': '🔀 ریمیکس', 'dj': '🎧 میکس DJ', 'artist': '🎵 آهنگ'}
        await bot.send_message(CHANNEL, f"{icons[cat]}\n🎤 {artist}\n🎵 {title}")
        print(f"🎵 موزیک جدید: {title}")
    
    print("🤖 ربات آماده‌ست و منتظر موزیک جدیده...")
    await user.run_until_disconnected()

asyncio.run(main())
