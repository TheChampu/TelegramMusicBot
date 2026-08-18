import config
from youtubesearchpython.__future__ import VideosSearch


async def get_thumb(videoid: str):
    if not videoid:
        return config.YOUTUBE_IMG_URL
    try:
        url = f"https://www.youtube.com/watch?v={videoid}"
        results = VideosSearch(url, limit=1)
        res = await results.next()
        if res and res.get("result") and len(res["result"]) > 0:
            result = res["result"][0]
            if result.get("thumbnails"):
                return result["thumbnails"][0]["url"].split("?")[0]
    except Exception:
        pass

    return f"https://img.youtube.com/vi/{videoid}/hqdefault.jpg"