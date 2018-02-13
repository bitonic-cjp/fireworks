import sys
import logging
from PyQt5.QtWidgets import QApplication

from frontend.qt.mainwindow import MainWindow



class Frontend:
    def __init__(self, config, backend):
        logging.info('Using Qt front-end')
        self.app = QApplication(sys.argv)
        self.ex = MainWindow(config, backend)


    def run(self):
        logging.info('Starting Qt front-end')
        sys.exit(self.app.exec_())



logging.info('Loaded Qt front-end module')
