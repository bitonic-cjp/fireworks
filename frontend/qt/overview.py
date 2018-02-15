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

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QGridLayout, QFrame, QLabel
from PyQt5 import QtGui
from PyQt5.QtCore import Qt

from . import updatesignal
from .. import amounts



class HLine(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setFrameShadow(QFrame.Sunken)
        self.setFrameShape(QFrame.HLine)



class BalanceFrame(QFrame):
    def __init__(self, parent, title, elements):
        super().__init__(parent)
        self.setFrameShadow(QFrame.Raised)
        self.setFrameShape(QFrame.StyledPanel)

        self.layout = QGridLayout(self)

        self.boldFont = QtGui.QFont()
        self.boldFont.setBold(True)

        titleLabel = QLabel(self)
        titleLabel.setText(title)
        titleLabel.setFont(self.boldFont)
        self.layout.addWidget(titleLabel, 0, 0, 1, 2)

        self.amountWidgets = []
        for i in range(len(elements)):
            if isinstance(elements[i], str):
                self.addAmountElement(i, elements[i])
            else:
                self.addWidgetElement(i, elements[i])

        self.setLayout(self.layout)


    def addAmountElement(self, index, label):
        amountLabel = QLabel(self)
        amountLabel.setText(label)
        self.layout.addWidget(amountLabel, 1+index, 0)

        amountWidget = QLabel(self)
        amountWidget.setText('0.00000000 000 BTC')
        amountWidget.setFont(self.boldFont)
        self.layout.addWidget(amountWidget, 1+index, 1, Qt.AlignRight)
        self.amountWidgets.append(amountWidget)


    def addWidgetElement(self, index, widget):
        widget.setParent(self)
        self.layout.addWidget(widget, 1+index, 0, 1, 2)


    def updateAmount(self, index, amount):
        widget = self.amountWidgets[index]
        widget.setText(amounts.format(amount))



class Overview(QWidget):
    def __init__(self, parent, backend):
        super().__init__(parent)
        self.backend = backend
        layout = QHBoxLayout(self)

        self.sendFrame = BalanceFrame(self,
            'Available for sending',
            [
            'Inside Lightning:',
            'Outside Lightning (confirmed):',
            'Outside Lightning (unconfirmed):',
            HLine(None),
            'Total:'
            ])
        layout.addWidget(self.sendFrame, 0, Qt.AlignTop)

        self.lockedFrame = BalanceFrame(self,
            'Locked',
            [
            'Incoming:',
            'Outgoing:',
            HLine(None),
            'Result:'
            ])
        layout.addWidget(self.lockedFrame, 0, Qt.AlignTop)

        self.receiveFrame = BalanceFrame(self,
            'Available for receiving',
            [
            'Inside Lightning:'
            ])
        layout.addWidget(self.receiveFrame, 0, Qt.AlignTop)

        updatesignal.connect(self.update)

        self.setLayout(layout)


    def update(self):
        nonChannelFunds = self.backend.getNonChannelFunds()
        channelFunds = self.backend.getChannelFunds()

        confirmed   = sum(x[0] for x in nonChannelFunds.values() if x[1])
        unconfirmed = sum(x[0] for x in nonChannelFunds.values() if not x[1])

        ours        = sum(x[1] for x in channelFunds.values())
        lockedIn    = sum(x[2] for x in channelFunds.values())
        lockedOut   = sum(x[3] for x in channelFunds.values())
        theirs      = sum(x[4] for x in channelFunds.values())

        total = ours + confirmed + unconfirmed

        lockedResult = lockedIn - lockedOut

        self.sendFrame.updateAmount(0, ours)
        self.sendFrame.updateAmount(1, confirmed)
        self.sendFrame.updateAmount(2, unconfirmed)
        self.sendFrame.updateAmount(3, total)

        self.lockedFrame.updateAmount(0, lockedIn)
        self.lockedFrame.updateAmount(1, lockedOut)
        self.lockedFrame.updateAmount(2, lockedResult)

        self.receiveFrame.updateAmount(0, theirs)

