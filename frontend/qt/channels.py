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
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QEvent

from . import updatesignal



class HLine(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setFrameShadow(QFrame.Sunken)
        self.setFrameShape(QFrame.HLine)



class BalanceBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.amounts = (0,0,0,0)
        self.maxAmount = 1.0


    def setAmounts(self, amounts):
        self.amounts = amounts


    def setMaxAmount(self, maxAmount):
        self.maxAmount = maxAmount


    def paintEvent(self, event):
        painter = QtGui.QPainter(self)

        width = self.width()
        height = self.height()

        painter.setPen(Qt.black)
        painter.drawRect(0,0,width-1,height-1)

        ours, lockedIn, lockedOut, theirs = self.amounts

        scaleFactor = 0.5 * (width-4) / self.maxAmount
        ours      *= scaleFactor
        lockedIn  *= scaleFactor
        lockedOut *= scaleFactor
        theirs    *= scaleFactor

        painter.translate(width/2, 0)

        #TODO: draw lockedIn, lockedOut amounts

        painter.setPen(Qt.darkGreen)
        painter.setBrush(Qt.darkGreen)
        painter.drawRect(-ours-1,1,ours,height-3)

        painter.setPen(Qt.red)
        painter.setBrush(Qt.red)
        painter.drawRect(1,1,theirs,height-3)



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
        #Determine the scale
        maxAmount = 1000 #msatoshi; Never less than this
        for peer in self.peers:
            for ours, lockedIn, lockedOut, theirs in peer.channels:
                oursTotal   = ours + lockedOut
                theirsTotal = theirs + lockedIn
                maxAmount = max(maxAmount, oursTotal, theirsTotal)

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

            for amounts in channels:
                bar = BalanceBar(self)
                bar.setAmounts(amounts)
                bar.setMaxAmount(maxAmount)
                self.layout.addWidget(bar,   currentRow, 1)

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

