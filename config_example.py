# Rename to config.py
import os

CONFIG = {
    'title': 'XMPP <-> Telegram Gate',

    'debug': bool(int(os.getenv('DEBUG', 0))),
    'logfile': '/dev/null',

    'jid': os.getenv('JID', 'tlgrm.localhost'),
    'secret': os.getenv('SECRET', 'secret'),
    'server': os.getenv('SERVER', 'localhost'),
    'port': os.getenv('PORT', '5347'),

    'xmpp_use_roster_exchange': True,  # use XEP-0144 to import roster from Telegram

    'tg_api_id': os.getenv('TG_API_ID', '17349'),  # Telegram Desktop (GitHub)
    'tg_api_hash': os.getenv('TG_API_HASH', '344583e45741c457fe1862106095a5eb'),

    #'tg_server_ip': '149.154.167.50', 
    #'tg_server_port': 443,
    #'tg_server_dc': 2,

    'db_connect': os.getenv('DB_CONNECT', 'db.sqlite'),
    'persistence_path': os.getenv('TG_SESSIONS', '/var/tg4xmpp/session'),

    'media_external_formats': os.getenv('MEDIA_EXTERNAL_FORMATS', 'png|jpg|jpeg|gif|mp3|mp4|ogg'),

    'media_web_link_prefix': os.getenv('MEDIA_BASEURL', 'http://tlgrm.localhost/media/'),
    'media_store_path': os.getenv('MEDIA_PATH', '/var/tg4xmpp/media/'),
    'media_max_download_size': int(os.getenv('MEDIA_MAX_SIZE', 1024 * 1024 * 100)),  # in bytes

    'messages_max_max_cache_size': int(os.getenv('MSG_CACHE_SIZE', 300)),  # for quotes
}
