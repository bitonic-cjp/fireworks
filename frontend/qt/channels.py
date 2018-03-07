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

from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QScrollArea, QSizePolicy, QFrame, QPushButton
from PyQt5.QtCore import Qt, QEvent

from . import updatesignal



class HLine(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setFrameShadow(QFrame.Sunken)
        self.setFrameShape(QFrame.HLine)



class ChannelsInScroll(QWidget):
    def __init__(self, parent, backend):
        super().__init__(parent)
        self.backend = backend

        layout = QGridLayout(self)

        #TODO: scale widget

        newConnectionButton = QPushButton('Add a new connection', self)
        layout.addWidget(newConnectionButton, 1, 1)

        for c in range(3):
            layout.addWidget(HLine(self),  2+4*c, 0, 1, 3)
            label = QLabel('Name\nConnected', self)
            label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            layout.addWidget(label,        3+4*c, 0, 2, 1)

            button = QPushButton('Close', self)
            button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            layout.addWidget(button,       3+4*c, 2)
            button = QPushButton('Close', self)
            button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            layout.addWidget(button,       4+4*c, 2)

            button = QPushButton('New channel', self)
            layout.addWidget(button,       5+4*c, 1)

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

