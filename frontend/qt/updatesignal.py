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

from PyQt5 import QtCore



class Updater(QtCore.QObject):
    signal = QtCore.pyqtSignal()


    def connect(self, slot):
        self.signal.connect(slot)


    def update(self):
        self.signal.emit()



timer = QtCore.QTimer()
updater = Updater()



def initTimer():
    timer.timeout.connect(updater.update)


def setUpdateInterval(ms):
    timer.start(ms)


def update():
    updater.update()


def connect(slot):
    updater.connect(slot)

