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

from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QGridLayout, QLabel, QPlainTextEdit, QLineEdit, QMessageBox

from . import updatesignal
from .amountinput import AmountInput



class NewInvoiceDialog(QDialog):
    def __init__(self, parent, backend):
        super().__init__(parent)
        self.backend = backend
        self.bolt11 = None
        self.expirationTime = None

        self.setWindowTitle('Create a new invoice')

        layout = QGridLayout(self)

        labels = ['Label:', 'Description:', 'Amount:', 'Expires:']
        for i, txt in enumerate(labels):
            label = QLabel(self)
            label.setText(txt)
            layout.addWidget(label, i, 0)

        self.labelText = QLineEdit(self)
        self.descriptionText = QPlainTextEdit(self)
        self.amountText = AmountInput(self)
        self.expiryText = QLineEdit(self) #TODO: custom widget

        layout.addWidget(self.labelText      , 0, 1)
        layout.addWidget(self.descriptionText, 1, 1)
        layout.addWidget(self.amountText     , 2, 1)
        layout.addWidget(self.expiryText     , 3, 1)


        dialogButtons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        dialogButtons.accepted.connect(self.accept)
        dialogButtons.rejected.connect(self.reject)
        layout.addWidget(dialogButtons, 4, 0, 1, 2)

        self.setLayout(layout)

        self.accepted.connect(self.onAccepted)


    def onAccepted(self):
        try:
            self.bolt11, self.expirationTime = self.backend.makeNewInvoice(
                label=self.labelText.text(),
                description=self.descriptionText.toPlainText(),
                amount=self.amountText.getValue(),
                expiry=int(self.expiryText.text()))
            updatesignal.update()
        except self.backend.CommandFailed as e:
            updatesignal.update()
            QMessageBox.critical(self, 'Failed to create a new invoice',
                'Creating a new invoice failed with the following error message:\n\n'
                 + str(e)
                )

