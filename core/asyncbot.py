import asyncio
import aiohttp
import logging
import pprint
import config

TOKEN = config.token
pp = pprint.PrettyPrinter(indent=4)

logger = logging.getLogger(__name__)


class TelegramError(Exception):
    pass


async def api_request(method_name, method='GET', **kwargs):
    """
    Telegram API access
    """
    url = f'https://api.telegram.org/bot{TOKEN}/{method_name}'
    request = await aiohttp.request(method, url, params=kwargs)
    result = await request.json()
    if result["ok"]:
        return result["result"]
    else:
        raise TelegramError()


async def get_updates(offset=0, limit=100, timeout=0):
    """
    Telegram method getUpdates
    """
    updates = api_request('getUpdates', offset=offset, limit=limit, timeout=timeout)
    return await updates


async def send_message(**kwargs):
    """
    Telegram method sendMessage
    """
    request = api_request("sendMessage", **kwargs)
    await request


async def print_message(message):
    """
    Repeat message
    """
    chat_id = message["chat"]["id"]
    message_id = message["message_id"]
    text = message["text"]
    result = await send_message(chat_id=chat_id,
                                text=text,
                                reply_to_message_id=message_id)
    return result


async def process_update(update):
    """
    Send update
    """
    pp.pprint(update)
    pp.pprint((await print_message(update["message"])))
    return update["update_id"]


async def process_updates():
    """
    Getting updates and processes them
    """
    offset = 0
    while True:
        updates = await get_updates(offset, timeout=5)
        tasks = [
            asyncio.ensure_future(process_update(update)) for update in updates
        ]
        for future in asyncio.as_completed(tasks):
            update_id = await future
            offset = max(offset, update_id + 1)


def main():
    """
    Main bot entry point
    """
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(process_updates())
    except KeyboardInterrupt:
        loop.close()


if __name__ == '__main__':
    main()
