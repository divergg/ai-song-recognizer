import aiohttp
from aiohttp import ClientTimeout
from src.configs import settings
from common_utils.log_util import setup_file_logger


logger = setup_file_logger(
    name="ai_functions_logger", log_file="ai_functions_logger.log")

async def get_lyrics(title: str, artist: str) -> str | None:
    """Function to retrieve lyrics from API"""

    lyrics_url = f'{settings.recognize.lyrics_url}/{artist.lower()}/{title.lower()}'
    timeout = ClientTimeout(total=10)
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(
                    url=lyrics_url, timeout=timeout,
                ) as response:
                    status = response.status
                    if status == 200:
                        result = await response.json()
                        lyrics = result.get('lyrics')
                    else:
                        logger.error(f'RECOGNITION API RESPONSE STATUS CODE - {status}')
                        lyrics = None
        except Exception as e:
            text = await response.text()
            logger.info(f"RESPONSE FROM API - {text}")
            logger.error(f'EXCEPTION IN RETRIEVING HITS DATA - {e}')
            lyrics = None
    return lyrics[:300] if isinstance(lyrics, str) else lyrics
