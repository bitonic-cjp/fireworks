import os.path
import logging

from .lightningd.lightning import LightningRpc



class Backend:
    class Error(Exception):
        pass

    def __init__(self, config):
        logging.info('Using Lightningd back-end')
        lightningDir = config.getValue('lightningd', 'lightning-dir')
        lightningDir = os.path.expanduser(lightningDir)
        lightningDir = os.path.abspath(lightningDir)
        socketFile = os.path.join(lightningDir, 'lightning-rpc')
        self.rpc = LightningRpc(socketFile)


    def runCommand(self, cmd):
        try:
            return str(self.rpc._call(cmd))
        except ValueError as e:
            raise Backend.Error(str(e))



logging.info('Loaded Lightningd back-end module')
