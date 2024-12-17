import base64
import typing
from urllib.parse import urlparse, parse_qs
import ssl
import logging
import aiohttp


logger = logging.getLogger(__name__)


def get_qq_image_downloadable_url(image_url: str) -> tuple[str, dict]:
    """获取QQ图片的下载链接"""
    parsed = urlparse(image_url)
    query = parse_qs(parsed.query)
    return f"http://{parsed.netloc}{parsed.path}", query


async def get_qq_image_bytes(image_url: str) -> tuple[bytes, str]:
    """获取QQ图片的bytes"""
    image_url, query = get_qq_image_downloadable_url(image_url)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        'Referer': 'https://multimedia.nt.qq.com.cn/'
    }
    try:
        async with aiohttp.ClientSession(trust_env=True) as session:  # 尝试开启代理设置
            async with session.get(image_url, params=query, headers=headers) as resp:
                resp.raise_for_status()
                file_bytes = await resp.read()
                content_type = resp.headers.get('Content-Type')
                if not content_type or not content_type.startswith('image/'):
                   image_format = 'jpeg'
                else:
                  image_format = content_type.split('/')[-1]

                return file_bytes, image_format

    except aiohttp.ClientResponseError as e:
        logger.error(f"Error downloading image from {image_url}: {e}")
        logger.error(f"Response status code: {e.status}")
        try:
            content = await resp.text()
        except Exception:
            content = "<Response content is not text>"
        logger.error(f"Response content: {content}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred while downloading image from {image_url}: {e}")
        raise


async def qq_image_url_to_base64(
    image_url: str
) -> typing.Tuple[str, str]:
    """将QQ图片URL转为base64，并返回图片格式

    Args:
        image_url (str): QQ图片URL

    Returns:
        typing.Tuple[str, str]: base64编码和图片格式
    """
    logger.debug(f"Converting image URL to base64: {image_url}")
    file_bytes, image_format = await get_qq_image_bytes(image_url)

    base64_str = base64.b64encode(file_bytes).decode()

    return base64_str, image_format
