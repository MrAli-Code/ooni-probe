import os

from twisted.scripts import twistd
from twisted.python import usage
from twisted.internet import reactor
from twisted.web import server
from twisted.application import service

from ooni.settings import config
from ooni.director import Director
from ooni.utils import log

from .server import WebUIAPI

class WebUIService(service.MultiService):
    portNum = 8822
    def startService(self):
        service.MultiService.startService(self)
        config.set_paths()
        config.initialize_ooni_home()
        config.read_config_file()
        director = Director()
        web_ui_api = WebUIAPI(config, director)
        root = server.Site(web_ui_api.app.resource())
        self._port = reactor.listenTCP(self.portNum, root)
        d = director.start()

    def stopService(self):
        if self._port:
            self._port.stopListening()

class StartOoniprobeWebUIPlugin:
    tapname = "ooniprobe"
    def makeService(self, so):
        return WebUIService()

class OoniprobeTwistdConfig(twistd.ServerOptions):
    subCommands = [("StartOoniprobeWebUI", None, usage.Options, "ooniprobe web ui")]

def start():
    twistd_args = ["--nodaemon"]
    twistd_config = OoniprobeTwistdConfig()
    twistd_args.append("StartOoniprobeWebUI")
    try:
        twistd_config.parseOptions(twistd_args)
    except usage.error, ue:
        print("ooniprobe: usage error from twistd: {}\n".format(ue))
    twistd_config.loadedPlugins = {"StartOoniprobeWebUI": StartOoniprobeWebUIPlugin()}
    twistd.runApp(twistd_config)
    return 0

if __name__ == "__main__":
    start()