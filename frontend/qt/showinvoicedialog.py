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

from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QGridLayout, QLabel, QFrame, QTextEdit
from PyQt5 import QtGui
from PyQt5.QtCore import Qt

from . import updatesignal
from .. import formatting
from .widgets import HLine, BigLabel, QRCode



class ShowInvoiceDialog(QDialog):
    def __init__(self, parent, backend, bolt11):
        super().__init__(parent)
        self.backend = backend

        self.bolt11 = bolt11

        boldFont = QtGui.QFont()
        boldFont.setBold(True)

        self.setWindowTitle('New invoice data')

        layout = QGridLayout()

        labels = ['Amount:', 'Expiration date:', 'Status:']
        for i, txt in enumerate(labels):
            label = QLabel(txt, self)
            layout.addWidget(label, i, 0)

        self.amountLabel = QLabel(self)
        self.expirationLabel = QLabel(self)
        self.statusLabel = QLabel(self)
        layout.addWidget(self.amountLabel, 0, 1)
        layout.addWidget(self.expirationLabel, 1, 1)
        layout.addWidget(self.statusLabel, 2, 1)

        layout.addWidget(HLine(self), 3, 0, 1, 2)

        label = QLabel('Show this information to the payer:', self)
        label.setFont(boldFont)
        layout.addWidget(
            label,
            4, 0, 1, 2)

        layout.addWidget(
            QLabel('Invoice code:', self), 5, 0)

        label = BigLabel(self.bolt11, self)
        label.setFont(boldFont)
        label.setTextInteractionFlags(
            Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
        layout.addWidget(label, 5, 1)

        qr = QRCode(self)
        #Upper case for more compact QR code:
        qr.setQRCode('LIGHTNING:' + self.bolt11.upper())
        layout.addWidget(qr, 6, 0, 1, 2, Qt.AlignHCenter)

        dialogButtons = QDialogButtonBox(
            QDialogButtonBox.Close)
        dialogButtons.rejected.connect(self.reject)
        layout.addWidget(dialogButtons, 7, 0, 1, 2)

        self.setLayout(layout)

        updatesignal.connect(self.update)
        self.update()


    def update(self):
        try:
            invoices = self.backend.getInvoices()
        except self.backend.NotConnected:
            self.statusLabel.setText('Unknown (not connected to backend)')
            return

        for invoice in invoices:
            if invoice.bolt11 == self.bolt11:
                self.amountLabel.setText(
                    formatting.formatAmount(invoice.data.amount, invoice.data.currency))
                self.expirationLabel.setText(
                    formatting.formatTimestamp(invoice.data.expirationTime))
                self.statusLabel.setText(invoice.status)

                #TODO: grey out the dialog if the invoice is expired

                return

        #Fall through: apparently it's not in the list
        #If this ever happens, I think it indicates a bug in the backend.
        self.statusLabel.setText('Unknown (Invoice does not exist anymore?)')

