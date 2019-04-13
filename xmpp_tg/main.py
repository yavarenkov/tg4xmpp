import logging
import logging.handlers
import logging.config
import os
import sys
import signal
import importlib

import xmpp_tg
import telethon
import sleekxmpp

xmpp_logger = logging.getLogger('sleekxmpp')


def cli():
    config_module_name = sys.argv[1] if len(sys.argv) > 1 else 'config'
    try:
        config_module = importlib.import_module(config_module_name)
    except ModuleNotFoundError:
        print(config_module_name + ' not found. It should be an importable python module (see config_example.py)')
        sys.exit(1)

    # Logger config
    logging.basicConfig(
        level=logging.DEBUG if config_module.CONFIG['debug'] else logging.INFO,
        format='%(asctime)s :: %(levelname)s:%(name)s :: %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    if hasattr(config_module, 'LOGGING'):
        logging.config.dictConfig(config_module.LOGGING)

    logger = logging.getLogger()
    logger.info('----------------------------------------------------------------------')
    logger.info('---             Telegram (MTProto) <-> XMPP Gateway                ---')
    logger.info('----------------------------------------------------------------------')
    logger.info('Gate version: {}'.format(xmpp_tg.__version__))
    logger.info('Process pid: {}'.format(os.getpid()))
    logger.info('Using Telethon v{} and SleekXMPP v{}'.format(telethon.TelegramClient.__version__, sleekxmpp.__version__))

    gate = xmpp_tg.XMPPTelegram(config_module.CONFIG)
    signal.signal(signal.SIGINT, gate.handle_interrupt)
    gate.connect()
    gate.process()


if __name__ == '__main__':
    cli()
