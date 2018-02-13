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



class Frontend:
    def __init__(self, config, backend):
        logging.info('Using Qt front-end')
        self.app = QApplication(sys.argv)
        self.ex = MainWindow(config, backend)


    def run(self):
        logging.info('Starting Qt front-end')
        sys.exit(self.app.exec_())



logging.info('Loaded Qt front-end module')
