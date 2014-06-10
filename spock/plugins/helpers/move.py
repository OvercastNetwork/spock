import random
import math
from spock.mcp.mcpacket import Packet
from spock.mcp import mcpacket, mcdata
from spock.utils import pl_announce

TICK = 0.05

@pl_announce('Movement')
class MovementPlugin:
    def __init__(self, ploader, settings):
        self.client_info = ploader.requires('ClientInfo')
        self.event = ploader.requires('Event')
        self.net = ploader.requires('Net')
        self.timer = ploader.requires('Timers')
        self.timer.reg_event_timer(TICK, self.send_update, -1)
        self.event.reg_event_handler(mcdata.packet_idents['PLAY<Spawn Position'], self.initial_spawn)
        self.event.reg_event_handler(mcdata.packet_idents['PLAY<Open Window'], self.close_window)
        self.event.reg_event_handler(mcdata.packet_idents['PLAY<Update Health'], self.respawn_on_death)

        self.alive = False
        self.speed = 2
        self.randomize_direction()

        ploader.provides('Movement', self)

    def randomize_direction(self):
        self.direction = random.random() * 2 * math.pi
        self.client_info.position['yaw'] = math.degrees(self.direction)
        self.client_info.position['pitch'] = 0

    def move_around(self):
        if random.random() < 0.06:
            self.randomize_direction()
            # self.net.push(Packet(ident='PLAY>Chat Message', data={
            #     'message': "Changing direction: " + str(int(math.degrees(self.direction)))
            # }))

        pos = self.client_info.position
        pos['x'] += math.cos(self.direction) * self.speed * TICK
        pos['z'] += math.sin(self.direction) * self.speed * TICK

    def send_update(self, position=None):
        if not self.alive:
            return

        self.move_around()

        if position is None:
            position = self.client_info.position

        self.net.push(mcpacket.Packet(
            ident='PLAY>Player Position and Look',
            data=position,
            silent=True
        ))

    def send_respawn(self):
        self.net.push(Packet(ident='PLAY>Client Status', data={'action': 0}))

    # Initial spawn only
    def initial_spawn(self, name, event):
        if self.alive:
            return

        self.event.unreg_event_handler(mcdata.packet_idents['PLAY<Spawn Position'], self.initial_spawn)
        self.net.push(Packet(ident='PLAY>Client Settings', data={'locale': 'en_US',
                                                                 'view_distance': 12,
                                                                 'chat_flags': 0,
                                                                 'chat_colors': 1,
                                                                 'difficulty': 0,
                                                                 'show_cape': 1}))
        self.send_respawn()
        self.net.push(Packet(ident='PLAY>Chat Message', data={'message': "/join"}))

        self.alive = True

    def close_window(self, name, packet):
        self.net.push(Packet(ident='PLAY>Close Window', data={'window_id': packet.data['window_id']}))

    def respawn_on_death(self, name, packet):
        self.send_respawn()