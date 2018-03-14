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

from PyQt5.QtWidgets import QPlainTextEdit, QLineEdit

from . import updatesignal
from .genericdialog import GenericDialog
from .amountinput import AmountInput
from .durationinput import DurationInput



class NewInvoiceDialog(GenericDialog):
    def __init__(self, parent, backend, invoiceLabel):
        super().__init__(parent, backend)
        self.backend = backend

        self.label = None
        self.bolt11 = None
        self.expirationTime = None

        self.setWindowTitle('Create a new invoice')
        self.setErrorMessage('Failed to create a new invoice')

        self.labelText = QLineEdit(invoiceLabel, self)
        self.descriptionText = QPlainTextEdit(self)
        self.amountText = AmountInput(self, self.backend.getNativeCurrency())
        self.expiryText = DurationInput(self)

        self.addRow('Label:'      ,self.labelText)
        self.addRow('Description:',self.descriptionText)
        self.addRow('Amount:'     ,self.amountText)
        self.addRow('Expires:'    , self.expiryText)


    def doCommand(self):
        self.bolt11, self.expirationTime = self.backend.makeNewInvoice(
            label=self.labelText.text(),
            description=self.descriptionText.toPlainText(),
            amount=self.amountText.getValue(),
            expiry=self.expiryText.getValue()
            )
        self.label = self.labelText.text()
        updatesignal.update()

