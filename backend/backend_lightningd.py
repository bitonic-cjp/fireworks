import os.path
import logging

from .lightningd.lightning import LightningRpc



class Backend:
    def __init__(self, config):
        logging.info('Using Lightningd back-end')
        lightningDir = config.getValue('lightningd', 'lightning-dir')
        lightningDir = os.path.expanduser(lightningDir)
        lightningDir = os.path.abspath(lightningDir)
        socketFile = os.path.join(lightningDir, 'lightning-rpc')
        self.rpc = LightningRpc(socketFile)
        print(self.rpc.dev_blockheight())



logging.info('Loaded Lightningd back-end module')
