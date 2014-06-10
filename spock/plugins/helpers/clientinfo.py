from spock.mcp.mcpacket import Packet
from spock.mcp import mcdata
from spock.utils import pl_announce

HEAD_HEIGHT = 1.62

class ClientInfo:
    def __init__(self):
        self.eid = 0
        self.game_info = {
            'level_type': 0,
            'game_mode': None,
            'dimension': 0,
            'difficulty': 0,
            'max_players': 0,
        }
        self.spawn_position = {
            'x': 0,
            'y': 0,
            'z': 0,
        }
        self.health = {
            'health': 20,
            'food': 20,
            'food_saturation': 5,
        }
        self.position = {
            'x': 0,
            'feet': 0,
            'z': 0,
            'head': HEAD_HEIGHT,
            'yaw': 0,
            'pitch': 0,
            'on_ground': False,
        }
        self.player_list = {}

    def update_stance(self):
        self.position['feet'] = self.position['y']
        self.position['head'] = self.position['y'] + HEAD_HEIGHT

    def reset(self):
        self.__init__()


@pl_announce('ClientInfo')
class ClientInfoPlugin:
    def __init__(self, ploader, settings):
        self.event = ploader.requires('Event')
        self.emit = self.event.emit

        self.net = ploader.requires('Net')

        self.event.reg_event_handler(mcdata.packet_idents['PLAY<Join Game'], self.handle_join_game)
        self.event.reg_event_handler(mcdata.packet_idents['PLAY<Spawn Position'], self.handle_spawn_position)
        self.event.reg_event_handler(mcdata.packet_idents['PLAY<Update Health'], self.handle_update_health)
        self.event.reg_event_handler(mcdata.packet_idents['PLAY<Player Position and Look'], self.handle_position_update)
        for e in (mcdata.packet_idents['PLAY<Disconnect'], 'SOCKET_ERR', 'SOCKET_HUP'):
            self.event.reg_event_handler(e, self.handle_disconnect)

        self.client_info = ClientInfo()
        ploader.provides('ClientInfo', self.client_info)

    #Login Request - Update client state info
    def handle_join_game(self, name, packet):
        self.client_info.eid = packet.data['eid']
        self.client_info.game_info = packet.data
        self.emit('cl_login', packet.data)

    #Spawn Position - Update client Spawn Position state
    def handle_spawn_position(self, name, packet):
        self.client_info.spawn_position = packet.data
        self.emit('cl_spawn_update', packet.data)

    #Update Health - Update client Health state
    def handle_update_health(self, name, packet):
        self.client_info.health = packet.data
        self.emit('cl_health_update', packet.data)

    #Position Update Packets - Update client Position state
    def handle_position_update(self, name, packet):
        self.client_info.position['x'] =         packet.data['x']
        self.client_info.position['y'] =         packet.data['y'] - HEAD_HEIGHT
        self.client_info.position['z'] =         packet.data['z']
        self.client_info.position['yaw'] =       packet.data['yaw']
        self.client_info.position['pitch'] =     packet.data['pitch']
        self.client_info.position['on_ground'] = packet.data['on_ground']

        self.client_info.update_stance()

        self.net.push(Packet(ident='PLAY>Player Position and Look', data=self.client_info.position))

        self.emit('cl_position_update', self.client_info.position)

    def handle_disconnect(self, name, packet):
        self.client_info.reset()