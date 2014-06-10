"""
This plugin creates a convenient start() method and attaches it directly
to the client. More complex bots will likely want to create their own
initialization plugin, so StartPlugin stays out of the way unless you
call the start() method. However, the start() method is very convenient
for demos and tutorials, and illustrates the basic steps for initializing
a bot.
"""
from spock.mcp.mcpacket import Packet

from spock.mcp import mcpacket, mcdata
from spock.utils import pl_announce


@pl_announce('Start')
class StartPlugin:
    def __init__(self, ploader, settings):
        self.event = ploader.requires('Event')
        self.settings = ploader.requires('Settings')
        self.client = ploader.requires('Client')
        self.net = ploader.requires('Net')
        self.auth = ploader.requires('Auth')

        ploader.provides('Start', self)

    def start_client(self, host=None, port=None):
        if host is None:
            host = self.settings['host']
        if port is None:
            port = self.settings['port']

        if 'error' not in self.auth.start_session(
            self.settings['username'],
            self.settings['password']
        ):
            self.net.connect(host, port)
            self.handshake()
            self.login_start()
            self.event.event_loop()

    def handshake(self):
        self.net.push(mcpacket.Packet(
            ident='HANDSHAKE>Handshake',
            data = {
                'protocol_version': mcdata.MC_PROTOCOL_VERSION,
                'host': self.net.host,
                'port': self.net.port,
                'next_state': mcdata.LOGIN_STATE
            }
        ))

    def login_start(self):
        self.net.push(mcpacket.Packet(
            ident='LOGIN>Login Start',
            data = {'name': self.auth.username},
        ))
