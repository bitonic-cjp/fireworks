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



class BalanceFrame(QFrame):
    def __init__(self, parent, title, elements):
        super().__init__(parent)
        self.setFrameShadow(QFrame.Raised)
        self.setFrameShape(QFrame.StyledPanel)

        layout = QGridLayout(self)

        boldFont = QtGui.QFont()
        boldFont.setBold(True)

        titleLabel = QLabel(self)
        titleLabel.setText(title)
        titleLabel.setFont(boldFont)
        layout.addWidget(titleLabel, 0, 0, 1, 2)

        self.amountWidgets = []
        for i in range(len(elements)):
            amountLabel = QLabel(self)
            amountLabel.setText(elements[i])
            layout.addWidget(amountLabel, 1+i, 0)

            amountWidget = QLabel(self)
            amountWidget.setText('0.00000000 000 BTC')
            amountWidget.setFont(boldFont)
            layout.addWidget(amountWidget, 1+i, 1)
            self.amountWidgets.append(amountWidget)

        self.setLayout(layout)



class Overview(QWidget):
    def __init__(self, parent, backend):
        super().__init__(parent)
        self.backend = backend
        layout = QHBoxLayout(self)

        sendFrame = BalanceFrame(self,
            'Available for sending',
            [
            'Inside Lightning:',
            'Outside Lightning (confirmed):',
            'Outside Lightning (unconfirmed):',
            'Total:'
            ])
        layout.addWidget(sendFrame, 0, Qt.AlignTop)

        lockedFrame = BalanceFrame(self,
            'Locked',
            [
            'For own transactions:',
            'For others\' transactions:'
            ])
        layout.addWidget(lockedFrame, 0, Qt.AlignTop)

        receiveFrame = BalanceFrame(self,
            'Available for receiving',
            [
            'Inside Lightning:'
            ])
        layout.addWidget(receiveFrame, 0, Qt.AlignTop)

        self.setLayout(layout)

