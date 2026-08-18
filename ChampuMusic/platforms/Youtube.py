import asyncio
import os
import re
from typing import Union
import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from youtubesearchpython.__future__ import VideosSearch, Playlist
import aiohttp
import config

api_url = getattr(config, "API_URL", "https://shrutibots.site") or "https://shrutibots.site"
api_key = getattr(config, "API_KEY", "ShrutiBotsgBjhtWgeANS8EU8c0vsk") or "ShrutiBotsgBjhtWgeANS8EU8c0vsk"

DOWNLOAD_DIR = "downloads"


def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60 ** i for i, x in enumerate(reversed(stringt.split(":"))))


async def download_song(link: str) -> str:
    video_id = link.split("v=")[-1].split("&")[0] if "v=" in link else link
    if not video_id or len(video_id) < 3:
        return None

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.mp3")
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        return file_path

    current_api_url = (getattr(config, "API_URL", "https://shrutibots.site") or "https://shrutibots.site").rstrip("/")
    current_api_key = getattr(config, "API_KEY", "ShrutiBotsgBjhtWgeANS8EU8c0vsk") or "ShrutiBotsgBjhtWgeANS8EU8c0vsk"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{current_api_url}/download",
                params={"url": video_id, "type": "audio", "api_key": current_api_key},
                timeout=aiohttp.ClientTimeout(total=300)
            ) as resp:
                if resp.status != 200:
                    return None
                with open(file_path, "wb") as f:
                    async for chunk in resp.content.iter_chunked(131072):
                        f.write(chunk)
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            return file_path
        return None
    except Exception:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass
        return None


async def download_video(link: str) -> str:
    video_id = link.split("v=")[-1].split("&")[0] if "v=" in link else link
    if not video_id or len(video_id) < 3:
        return None

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.mp4")
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        return file_path

    current_api_url = (getattr(config, "API_URL", "https://shrutibots.site") or "https://shrutibots.site").rstrip("/")
    current_api_key = getattr(config, "API_KEY", "ShrutiBotsgBjhtWgeANS8EU8c0vsk") or "ShrutiBotsgBjhtWgeANS8EU8c0vsk"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{current_api_url}/download",
                params={"url": video_id, "type": "video", "api_key": current_api_key},
                timeout=aiohttp.ClientTimeout(total=600)
            ) as resp:
                if resp.status != 200:
                    return None
                with open(file_path, "wb") as f:
                    async for chunk in resp.content.iter_chunked(131072):
                        f.write(chunk)
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            return file_path
        return None
    except Exception:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass
        return None


class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.status = "https://www.youtube.com/oembed?url="
        self.listbase = "https://youtube.com/playlist?list="
        self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    async def exists(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        return bool(re.search(self.regex, link))

    async def url(self, message_1: Message) -> Union[str, None]:
        messages = [message_1]
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)
        for message in messages:
            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        text = message.text or message.caption
                        return text[entity.offset: entity.offset + entity.length]
            elif message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        return None

    async def details(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        try:
            results = VideosSearch(link, limit=1)
            res = await results.next()
            if res and res.get("result") and len(res["result"]) > 0:
                result = res["result"][0]
                title = result.get("title", "YouTube Track")
                duration_min = result.get("duration", "00:00")
                vidid = result.get("id", "")
                thumbnail = result["thumbnails"][0]["url"].split("?")[0] if result.get("thumbnails") else f"https://img.youtube.com/vi/{vidid}/hqdefault.jpg"
                duration_sec = int(time_to_seconds(duration_min)) if duration_min and duration_min != "None" else 0
                return title, duration_min, duration_sec, thumbnail, vidid
        except Exception:
            pass

        try:
            ytdl_opts = {"quiet": True, "no_warnings": True}
            with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
                info = ydl.extract_info(link, download=False)
                if info:
                    vidid = info.get("id", "")
                    title = info.get("title", "YouTube Track")
                    dur = info.get("duration", 0)
                    duration_min = str(dur)
                    thumbnail = info.get("thumbnail", f"https://img.youtube.com/vi/{vidid}/hqdefault.jpg")
                    return title, duration_min, int(dur) if dur else 0, thumbnail, vidid
        except Exception:
            pass

        return "YouTube Track", "00:00", 0, "https://telegra.ph/file/7e177561e54188f35fa03.jpg", ""

    async def title(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        res = await results.next()
        if res and res.get("result") and len(res["result"]) > 0:
            return res["result"][0]["title"]
        return "YouTube Track"

    async def duration(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        res = await results.next()
        if res and res.get("result") and len(res["result"]) > 0:
            return res["result"][0]["duration"]
        return "00:00"

    async def thumbnail(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        res = await results.next()
        if res and res.get("result") and len(res["result"]) > 0:
            return res["result"][0]["thumbnails"][0]["url"].split("?")[0]
        return "https://telegra.ph/file/7e177561e54188f35fa03.jpg"

    async def video(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        try:
            downloaded_file = await download_video(link)
            if downloaded_file:
                return 1, downloaded_file
            else:
                return 0, "Video download failed"
        except Exception as e:
            return 0, f"Video download error: {e}"

    async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None):
        if videoid:
            link = self.listbase + link
        if "&" in link:
            link = link.split("&")[0]
        try:
            plist = await Playlist.get(link)
        except:
            return []

        videos = plist.get("videos") or []
        ids = []
        for data in videos[:limit]:
            if not data:
                continue
            vid = data.get("id")
            if not vid:
                continue
            ids.append(vid)
        return ids

    async def track(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        try:
            results = VideosSearch(link, limit=1)
            res = await results.next()
            if res and res.get("result") and len(res["result"]) > 0:
                result = res["result"][0]
                title = result.get("title", "YouTube Track")
                duration_min = result.get("duration", "00:00")
                vidid = result.get("id", "")
                yturl = result.get("link", f"https://www.youtube.com/watch?v={vidid}")
                thumbnail = result["thumbnails"][0]["url"].split("?")[0] if result.get("thumbnails") else f"https://img.youtube.com/vi/{vidid}/hqdefault.jpg"
                track_details = {
                    "title": title,
                    "link": yturl,
                    "vidid": vidid,
                    "duration_min": duration_min,
                    "thumb": thumbnail,
                }
                return track_details, vidid
        except Exception:
            pass

        try:
            ytdl_opts = {"quiet": True, "no_warnings": True}
            with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
                info = ydl.extract_info(link, download=False)
                if info:
                    vidid = info.get("id", "")
                    title = info.get("title", "YouTube Track")
                    dur = info.get("duration", 0)
                    duration_min = str(dur)
                    thumbnail = info.get("thumbnail", f"https://img.youtube.com/vi/{vidid}/hqdefault.jpg")
                    yturl = info.get("webpage_url", f"https://www.youtube.com/watch?v={vidid}")
                    track_details = {
                        "title": title,
                        "link": yturl,
                        "vidid": vidid,
                        "duration_min": duration_min,
                        "thumb": thumbnail,
                    }
                    return track_details, vidid
        except Exception:
            pass

        raise AssistantErr("Could not fetch YouTube track details.")

    async def formats(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        ytdl_opts = {"quiet": True}
        ydl = yt_dlp.YoutubeDL(ytdl_opts)
        with ydl:
            formats_available = []
            r = ydl.extract_info(link, download=False)
            for format in r["formats"]:
                try:
                    if "dash" not in str(format["format"]).lower():
                        formats_available.append(
                            {
                                "format": format["format"],
                                "filesize": format.get("filesize"),
                                "format_id": format["format_id"],
                                "ext": format["ext"],
                                "format_note": format["format_note"],
                                "yturl": link,
                            }
                        )
                except:
                    continue
        return formats_available, link

    async def slider(self, link: str, query_type: int, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        a = VideosSearch(link, limit=10)
        result = (await a.next()).get("result")
        title = result[query_type]["title"]
        duration_min = result[query_type]["duration"]
        vidid = result[query_type]["id"]
        thumbnail = result[query_type]["thumbnails"][0]["url"].split("?")[0]
        return title, duration_min, thumbnail, vidid

    async def download(
        self,
        link: str,
        mystic,
        video: Union[bool, str] = None,
        videoid: Union[bool, str] = None,
        songaudio: Union[bool, str] = None,
        songvideo: Union[bool, str] = None,
        format_id: Union[bool, str] = None,
        title: Union[bool, str] = None,
    ) -> str:
        if videoid:
            link = self.base + link

        try:
            if video:
                downloaded_file = await download_video(link)
            else:
                downloaded_file = await download_song(link)

            if downloaded_file:
                return downloaded_file, True
            else:
                return None, False
        except Exception:
            return None, False