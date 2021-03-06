from spock.mcp.mcpacket import Packet
from spock.mcp import mcdata
from spock.utils import pl_announce


@pl_announce('Keepalive')
class KeepalivePlugin:
    def __init__(self, ploader, settings):
        self.net = ploader.requires('Net')
        ploader.reg_event_handler(
            mcdata.packet_idents['PLAY<Keep Alive'],
            self.echo_keep_alive
        )

        ploader.provides('Keepalive', self)

    #Keep Alive - Reflects data back to server
    def echo_keep_alive(self, name, packet):
        self.net.push(Packet(ident='PLAY>Keep Alive', data={'keep_alive': packet.data['keep_alive']}))