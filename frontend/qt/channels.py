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

from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QScrollArea, QSizePolicy, QFrame, QPushButton, QMessageBox
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QEvent

from . import updatesignal
from .newconnectiondialog import NewConnectionDialog
from .newchanneldialog import NewChannelDialog



class HLine(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setFrameShadow(QFrame.Sunken)
        self.setFrameShape(QFrame.HLine)



class BalanceBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.channelData = None
        self.maxAmount = 1.0


    def setChannelData(self, channelData):
        self.channelData = channelData


    def setMaxAmount(self, maxAmount):
        self.maxAmount = maxAmount


    def paintEvent(self, event):
        painter = QtGui.QPainter(self)

        palette = self.style().standardPalette()
        if self.isEnabled():
            palette.setCurrentColorGroup(QtGui.QPalette.Active)
        else:
            palette.setCurrentColorGroup(QtGui.QPalette.Disabled)

        width = self.width()
        height = self.height()

        painter.setPen(palette.color(QtGui.QPalette.WindowText))
        painter.drawRect(0,0,width-1,height-1)

        if self.channelData is None:
            return
        ours      = self.channelData.ownFunds
        lockedIn  = self.channelData.lockedIncoming
        lockedOut = self.channelData.lockedOutgoing
        theirs    = self.channelData.peerFunds

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

        self.peers = None
        self.nodeLinks = None

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        updatesignal.connect(self.update)


    def update(self):
        try:
            self.nodeLinks = self.backend.getNodeLinks()
            newPeers = self.backend.getPeers()
            if newPeers == self.peers:
                return #no change - don't update
            self.peers = newPeers
            haveData = True
        except self.backend.NotConnected:
            self.nodeLinks = None
            self.peers = None
            haveData = False

        self.removeWidgets()
        if haveData:
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
            for c in peer.channels:
                oursTotal   = c.ownFunds + c.lockedOutgoing
                theirsTotal = c.peerFunds + c.lockedIncoming
                capacity = oursTotal + theirsTotal
                maxAmount = max(maxAmount, capacity)

        #TODO: scale widget

        label = QLabel('Links to this node:\n' + '\n'.join(self.nodeLinks), self)
        label.setTextInteractionFlags(
            Qt.TextSelectableByMouse | \
            Qt.TextSelectableByKeyboard
            )
        label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.layout.addWidget(label, 1, 1)

        newConnectionButton = QPushButton('Connect to another node', self)
        newConnectionButton.clicked.connect(self.onNewConnection)
        self.layout.addWidget(newConnectionButton, 2, 1)

        currentRow = 3

        for peer in self.peers:
            channels = peer.channels
            connected = 'Connected' if peer.connected else 'Not connected'

            self.layout.addWidget(HLine(self), currentRow, 0, 1, 4)
            currentRow += 1
            label = QLabel('%s\n%s' % (peer.alias, connected), self)
            label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            label.setEnabled(peer.connected)
            self.layout.addWidget(label, currentRow, 0, 1+len(channels), 1)

            for c in channels:
                bar = BalanceBar(self)
                bar.setChannelData(c)
                bar.setMaxAmount(maxAmount)
                bar.setEnabled(c.operational)
                self.layout.addWidget(bar, currentRow, 1)

                label = QLabel('State: ' + c.state, self)
                label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
                label.setEnabled(c.operational)
                self.layout.addWidget(label, currentRow, 2)

                def makeCloseChannelHandler(self, peer, fundingTxID):
                    def closeChannelHandler():
                        return self.onCloseChannel(peer, fundingTxID)
                    return closeChannelHandler
                button = QPushButton('Close', self)
                button.clicked.connect(makeCloseChannelHandler(
                    self, peer, c.fundingTxID
                    ))
                button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
                self.layout.addWidget(button, currentRow, 3)

                currentRow += 1

            def makeNewChannelHandler(self, peer, ):
                def newChannelHandler():
                    return self.onNewChannel(peer)
                return newChannelHandler
            button = QPushButton('New channel', self)
            button.clicked.connect(makeNewChannelHandler(self, peer))
            button.setEnabled(peer.connected)
            self.layout.addWidget(button, currentRow, 1)
            currentRow += 1


    def onNewConnection(self):
        dialog = NewConnectionDialog(self, self.backend)
        if(dialog.exec() != dialog.Accepted):
            return


    def onNewChannel(self, peer):
        peerID = peer.peerID
        alias = peer.alias
        try:
            dialog = NewChannelDialog(self, self.backend, peerID, alias)
        except self.backend.NotConnected:
            QMessageBox.critical(self, 'Failed to create a new channel',
                'Creating a new channel failed: back-end not connected.'
                )
        if(dialog.exec() != dialog.Accepted):
            return


    def onCloseChannel(self, peer, fundingTxID):
        #TODO: ask the user for confirmation
        #alias = peer.alias

        try:
            self.backend.closeChannel(fundingTxID)
            updatesignal.update()
        except self.backend.CommandFailed as e:
            QMessageBox.critical(self, 'Failed to close the channel',
                'Closing the channel failed with the following error message:\n\n'
                 + str(e)
                )
        except self.backend.NotConnected:
            QMessageBox.critical(self, 'Failed to close the channel',
                'Closing the channel failed: back-end not connected.'
                )



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
                self.widget().minimumSizeHint().width()
                )

        return super().eventFilter(obj, event)

