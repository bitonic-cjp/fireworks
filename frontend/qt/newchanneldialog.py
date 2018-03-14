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

from PyQt5.QtWidgets import QLabel

from . import updatesignal
from .genericdialog import GenericDialog
from .amountinput import AmountInput



class NewChannelDialog(GenericDialog):
    def __init__(self, parent, backend, peerID, alias):
        super().__init__(parent, backend)
        self.backend = backend
        self.peerID = peerID

        self.setWindowTitle('Create a new channel')
        self.setErrorMessage('Failed to create a new channel')

        self.amountText = AmountInput(self, self.backend.getNativeCurrency())

        self.addRow('Peer ID:'   , QLabel(peerID, self))
        self.addRow('Peer alias:', QLabel(alias, self))
        self.addRow('Amount:'    , self.amountText)


    def doCommand(self):
        self.backend.makeChannel(
            peerID=self.peerID,
            amount=self.amountText.getValue()
            )
        updatesignal.update()

