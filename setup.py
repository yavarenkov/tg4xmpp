from setuptools import setup

setup(
    name='tg4xmpp',
    version='0.1',
    py_modules=['xmpp_tg'],
    install_requires=[
        'sleekxmpp==1.3.2',
        'Telethon==0.15.5',
        'pytz',
    ],
    entry_points='''
        [console_scripts]
        tg4xmpp=xmpp_tg.main:cli
    ''',
)