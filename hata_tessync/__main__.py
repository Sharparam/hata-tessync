import asyncio
import logging
import toml

from .tgsyncer import TgSyncer
from .fbsyncer import FbSyncer

from .config.logging import setup_logging

# import code; code.interact(local=dict(globals(), **locals()))

log_name = 'hata_tessync' if __name__ == '__main__' else __name__

setup_logging()
log = logging.getLogger(log_name)

config = toml.load('config.toml')
tgconf = config['telegram']
fbconf = config['facebook']

tg = TgSyncer(tgconf)
fb = FbSyncer(fbconf)


def tg_callback(sender, message):
    fb.send_text(f"<{sender}>\n{message}")


async def fb_callback(sender, message):
    log.info('running fb_callback')
    await tg.send_text(f"<**{sender}**>\n{message}")

tg.set_simple_callback(tg_callback)
fb.set_simple_callback(fb_callback)

loop = asyncio.get_event_loop()


async def _amain() -> None:
    log.info('Starting up')

    try:
        await tg.start()
        log.debug('Awaiting sync tasks')
        await asyncio.wait([
            tg.run_until_disconnected(),
            fb.run_until_disconnected()])

        log.debug('Sync tasks finished')
    finally:
        await tg.stop()
        fb.stop()


def main() -> None:
    try:
        loop.run_until_complete(_amain())
    except KeyboardInterrupt:
        log.info('User pressed Ctrl-C, exiting')
        loop.run_until_complete(tg.stop())
        fb.stop()


if __name__ == '__main__':
    log.debug('__name__ is __main__, running main function')
    main()
