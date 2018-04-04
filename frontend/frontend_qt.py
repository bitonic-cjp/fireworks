#    Copyright (C) 2018 by Bitonic B.V.
#
#    This file is part of Fireworks.
#
#    Fireworks is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Fireworks is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Fireworks. If not, see <http://www.gnu.org/licenses/>.

import sys
import logging
from PyQt5.QtWidgets import QApplication

from .qt.mainwindow import MainWindow
from .qt import updatesignal



class Frontend:
    def __init__(self, config):
        logging.info('Using Qt front-end')
        self.config = config


    def setBackend(self, backend):
        self.backend = backend


    def run(self):
        logging.info('Starting Qt front-end')

        app = QApplication(sys.argv)

        self.backend.startup()

        ex = MainWindow(self.config, self.backend)
        updatesignal.initTimer()
        updatesignal.setUpdateInterval(1000)

        updatesignal.update() #First update
        sys.exit(app.exec_())


    def getPassword(self, question):
        '''
        Arguments:
            question: str
        Returns: bytes
        '''
        return input(question).encode()



logging.info('Loaded Qt front-end module')
