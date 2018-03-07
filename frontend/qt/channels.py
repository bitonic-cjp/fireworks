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

from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QScrollArea, QSizePolicy, QFrame
from PyQt5.QtCore import Qt, QEvent

from . import updatesignal



class ChannelsInScroll(QWidget):
    def __init__(self, parent, backend):
        super().__init__(parent)
        self.backend = backend

        layout = QGridLayout(self)

        for x in range(2):
            for y in range(100):
                label = QLabel('Zomaar een niet zo heel erg lange tekst', self)
                layout.addWidget(label, y, x)


        self.setLayout(layout)

        updatesignal.connect(self.update)


    def update(self):
        pass #TODO



class Channels(QScrollArea):
    def __init__(self, parent, backend):
        super().__init__(parent)

        inScroll = ChannelsInScroll(self, backend)
        self.setWidget(inScroll)
        inScroll.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        inScroll.installEventFilter(self)

        self.setFrameStyle(QFrame.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setWidgetResizable(True)


    def eventFilter(self, obj, event):
        if obj == self.widget() and event.type() == QEvent.Resize:
            self.setMinimumWidth(
                self.widget().minimumSizeHint().width() +
                self.verticalScrollBar().width()
                )

        return super().eventFilter(obj, event)

