from copy import deepcopy
from spock.plugins import DefaultPlugins

class PluginLoader:
    def __init__(self, client, settings):
        self.plugins = settings.pop('plugins')
        self.plugin_settings = settings.pop('plugin_settings')

        self.loaded_plugins = {
            'Client': client,
            'Settings': settings
        }

        self.announced_plugins = {}
        for plugin_class in self.plugins:
            for ident in plugin_class.pl_announce:
                self.announced_plugins[ident] = plugin_class

        self.event = self.requires('Event')

        while self.plugins:
            plugin_class = self.plugins.pop()
            self.requires(plugin_class.pl_announce[0])

    def available(self, ident):
        return ident in self.announced_plugins or ident in self.loaded_plugins

    def requires(self, ident):
        if ident not in self.loaded_plugins:
            if ident in self.announced_plugins:
                plugin_class = self.announced_plugins[ident]
                plugin_class(self, self.plugin_settings.get(plugin_class, None))
            else:
                raise Exception("Missing required plugin {0}".format(ident))
        return self.loaded_plugins[ident]

    def provides(self, ident, obj):
        self.loaded_plugins[ident] = obj

    def reg_event_handler(self, event, handler):
        self.event.reg_event_handler(event, handler)


#2 values = Attribute&Setting name, default value
#3 values = Attribute name, setting name, default value
default_settings = [
    ('host', "localhost"),
    ('port', 25565),
    ('plugins', DefaultPlugins),
    ('plugin_settings', {}),
    ('username', 'Bot'),
    ('password', ''),
    ('authenticated', True),
    ('thread_workers', 5),
    ('bufsize', 4096),
    ('sock_quit', True),
    ('sess_quit', True),
    ('packet_trace', False)
]

for index, setting in enumerate(default_settings):
    if len(setting) == 2:
        default_settings[index] = (setting[0], setting[0], setting[1])

class Client:
    def __init__(self, **kwargs):
        super().__init__()
        #Grab some settings
        settings = deepcopy(kwargs.get('settings', {}))
        final_settings = {}
        for setting in default_settings:
            val = kwargs.get(setting[1], settings.get(setting[1], setting[2]))
            final_settings[setting[0]] = val

        loader = PluginLoader(self, final_settings)
        self.start_plugin = loader.requires('Start')
        self.event = loader.requires('Event')

    def start_client(self, host=None, port=None):
        self.start_plugin.start_client(host, port)

    def stop_client(self):
        self.event.kill()