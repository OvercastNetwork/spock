from spock.plugins.core import event, net, timers, auth, threadpool
from spock.plugins.helpers import start, keepalive, clientinfo, world, move

DefaultPlugins = [
    event.EventPlugin,
    net.NetPlugin,
    timers.TimerPlugin,
    auth.AuthPlugin,
    threadpool.ThreadPoolPlugin,
    start.StartPlugin,
    keepalive.KeepalivePlugin,
    #world.WorldPlugin,
    #clientinfo.ClientInfoPlugin,
    #move.MovePlugin,
]