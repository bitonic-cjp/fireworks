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

from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QGridLayout, QLabel, QMessageBox

from . import updatesignal
from .amountinput import AmountInput



class NewChannelDialog(QDialog):
    def __init__(self, parent, backend, peerID, alias):
        super().__init__(parent)
        self.backend = backend
        self.peerID = peerID

        self.setWindowTitle('Create a new channel')

        layout = QGridLayout()

        labels = ['Peer ID:', 'Peer alias:', 'Amount:']
        for i, txt in enumerate(labels):
            label = QLabel(txt, self)
            layout.addWidget(label, i, 0)

        layout.addWidget(QLabel(peerID, self), 0, 1)
        layout.addWidget(QLabel(alias, self), 1, 1)

        self.amountText = AmountInput(self, self.backend.getNativeCurrency())
        layout.addWidget(self.amountText, 2, 1)

        dialogButtons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        dialogButtons.accepted.connect(self.accept)
        dialogButtons.rejected.connect(self.reject)
        layout.addWidget(dialogButtons, 3, 0, 1, 2)

        self.setLayout(layout)

        self.accepted.connect(self.onAccepted)


    def onAccepted(self):
        try:
            self.backend.makeChannel(
                peerID=self.peerID,
                amount=self.amountText.getValue()
                )
            updatesignal.update()
        except self.backend.CommandFailed as e:
            updatesignal.update()
            QMessageBox.critical(self, 'Failed to create a new channel',
                'Creating a new channel failed with the following error message:\n\n'
                 + str(e)
                )
        except self.backend.NotConnected:
            QMessageBox.critical(self, 'Failed to create a new channel',
                'Creating a new channel failed: back-end not connected.'
                )

