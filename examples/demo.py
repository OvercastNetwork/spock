from threading import Thread
import signal
import sys
from spock.client import Client
from spock.plugins import DefaultPlugins
from spock.plugins.helpers.clientinfo import ClientInfoPlugin
from spock.plugins.helpers.move import MovementPlugin

PLAYER_NAMES = [
    "Alice",
    "Bernard",
    "Charlie",
    "Danika",
    "Evan",
    "Fara",
    "Gunther",
    "Hagar",
    "Iain",
    "Juniper",
    "Kelsey",
    "Lamar",
    "Monique",
    "Norbert",
    "Olivia",
    "Penelope",
    "Quinn",
    "Rutiger",
    "Simone",
    "Tyrone",
    "Usain",
    "Veronica",
    "Wesley",
    "Xavier",
    "Yolanda",
    "Zane",
]

plugins = DefaultPlugins
plugins.append(ClientInfoPlugin)
plugins.append(MovementPlugin)

settings = {
    'host': "192.168.2.19",
    'port': 25566,
    'authenticated': False, #Authenticate with authserver.mojang.com
    'bufsize': 4096,       #Size of socket buffer
    'sock_quit': True,     #Stop bot on socket error or hangup
    'sess_quit': True,     #Stop bot on failed session login
    'thread_workers': 5,   #Number of workers in the thread pool
    'packet_trace': False,
    'plugins': plugins,         #Plugins
    'plugin_settings': {}, #Extra settings for plugins
}

class ThreadedClient(Client, Thread):
    def run(self):
        super().run()
        self.start_client()

PLAYER_COUNT = 26
clients = []

def kill(*args):
    for client in clients:
        client.stop_client()

signal.signal(signal.SIGINT, kill)
signal.signal(signal.SIGTERM, kill)

for i in range(PLAYER_COUNT):
    available_names = len(PLAYER_NAMES)
    name_cycle = i // available_names
    name_offset = i % available_names
    name = PLAYER_NAMES[name_offset]

    if name_cycle > 0:
        name += str(name_cycle)

    if len(sys.argv) >= 2:
        name = sys.argv[1] + name

    client = ThreadedClient(settings=settings, username=name)
    client.start()
    clients.append(client)

for client in clients:
    client.join()
