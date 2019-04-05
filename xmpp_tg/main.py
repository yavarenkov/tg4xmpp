import logging
import logging.handlers
import os
import sys
import signal
import importlib

import xmpp_tg
import telethon
import sleekxmpp

xmpp_logger = logging.getLogger('sleekxmpp')


class StreamToLogger:
    """
    Stream logger.
    """
    def __init__(self, logger, level=logging.INFO, old_out=None):
        self.logger = logger
        self.level = level
        self.old_out = old_out
        self.linebuf = []
        self._buffer = ''
        self._prev = None

    def write(self, buf):
        if self._prev == buf == '\n':  
            self._prev = buf
            buf = ''
        else:
            self._prev = buf
        if buf != '\n':
            self.logger.log(self.level, buf)

        if self.old_out:
            self.old_out.write(buf)

    def flush(self):
        pass


def cli():
    config_module_name = sys.argv[1] if len(sys.argv) > 1 else 'config'
    try:
        CONFIG = importlib.import_module(config_module_name).CONFIG
    except ModuleNotFoundError:
        print(config_module_name + ' not found. It should be an importable python module (see config_example.py)')
        sys.exit(1)

    # Logger config
    logging.basicConfig(
        level=logging.DEBUG if CONFIG['debug'] else logging.INFO,
        format='%(asctime)s :: %(levelname)s:%(name)s :: %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p',
        handlers=[logging.handlers.RotatingFileHandler(filename=CONFIG['logfile']), logging.StreamHandler(sys.stdout)]
    )

    # Stdout/stderr
    logger_stdout = logging.getLogger('__stdout')
    sys.stdout = StreamToLogger(logger_stdout, logging.INFO)

    logger_stderr = logging.getLogger('__stderr')
    sys.stderr = StreamToLogger(logger_stderr, logging.ERROR)

    logging.getLogger().log(logging.INFO, '~'*81)
    logging.getLogger().log(logging.INFO, ' RESTART '*9)
    logging.getLogger().log(logging.INFO, '~'*81)
    print('----------------------------------------------------------------------')
    print('---             Telegram (MTProto) <-> XMPP Gateway                ---')
    print('----------------------------------------------------------------------')
    print()
    print('Starting...')
    print('Gate version: {}'.format(xmpp_tg.__version__))
    print('Process pid: {}'.format(os.getpid()))
    print('Using Telethon v{} and SleekXMPP v{}'.format(telethon.TelegramClient.__version__, sleekxmpp.__version__))
    print()

    gate = xmpp_tg.XMPPTelegram(CONFIG)
    signal.signal(signal.SIGINT, gate.handle_interrupt)
    gate.connect()
    gate.process()


if __name__ == '__main__':
    cli()
