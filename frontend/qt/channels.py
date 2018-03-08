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

        self.peers = []

        self.layout = QGridLayout(self)
        self.setLayout(self.layout)

        self.constructWidgets()

        updatesignal.connect(self.update)


    def update(self):
        try:
            newPeers = self.backend.getPeers()
            if newPeers == self.peers:
                return #no change - don't update
            self.peers = newPeers
            haveData = True
        except self.backend.NotConnected:
            self.peers = []
            haveData = False

        self.removeWidgets()
        self.constructWidgets()
        self.setEnabled(haveData)


    def removeWidgets(self):
        while True:
            item = self.layout.takeAt(0)
            if not item:
                break
            item.widget().deleteLater()


    def constructWidgets(self):
        #TODO: scale widget

        #connect peer_id=... host=... port=...
        newConnectionButton = QPushButton('Add a new connection', self)
        self.layout.addWidget(newConnectionButton, 1, 1)

        currentRow = 2

        for peer in self.peers:
            channels = peer.channels
            connected = 'Connected' if peer.connected else 'Not connected'

            self.layout.addWidget(HLine(self),  currentRow, 0, 1, 3)
            currentRow += 1
            label = QLabel('%s\n%s' % (peer.alias, connected), self)
            label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            self.layout.addWidget(label,        currentRow, 0, 1+len(channels), 1)

            for ourFunds,lockedIn,lockedOut,peerFunds in channels:
                button = QPushButton('Close', self)
                button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
                self.layout.addWidget(button,   currentRow, 2)
                currentRow += 1

            button = QPushButton('New channel', self)
            self.layout.addWidget(button,       currentRow, 1)
            currentRow += 1



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

