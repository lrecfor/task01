import bot
import notify_bot
import asyncio
from utils import set_logger


def main():
    """
    main function
    """
    set_logger()    # set logger
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(bot.dp.start_polling())
    loop.create_task(notify_bot.dp.start_polling())
    loop.run_forever()


if __name__ == '__main__':
    main()
