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

from PyQt5.QtWidgets import QLabel, QPlainTextEdit, QFrame, QMessageBox, QDialogButtonBox

from .. import formatting
from . import updatesignal
from .widgets import HLine
from .genericdialog import GenericDialog



class NewPaymentDialog(GenericDialog):
    def __init__(self, parent, backend):
        super().__init__(parent, backend)
        self.backend = backend

        self.bolt11 = None

        self.setWindowTitle('Perform a new payment')
        self.setErrorMessage('Failed to perform the payment')

        self.bolt11Text = QPlainTextEdit(self)
        self.bolt11Text.textChanged.connect(self.onBolt11Changed)

        self.addRow('Invoice code:', self.bolt11Text)

        self.addWidget(HLine(self))

        self.amountLabel = QLabel(self)
        self.descriptionLabel = QLabel(self)
        self.creationTimeLabel = QLabel(self)
        self.expirationTimeLabel = QLabel(self)
        self.payeeLabel = QLabel(self)

        self.addRow('Amount:'         , self.amountLabel)
        self.addRow('Description:'    , self.descriptionLabel)
        self.addRow('Creation time:'  , self.creationTimeLabel)
        self.addRow('Expiration time:', self.expirationTimeLabel)
        self.addRow('To:'             , self.payeeLabel)

        self.setInvalidInvoice()


    def onBolt11Changed(self):
        self.bolt11 = self.bolt11Text.toPlainText()
        try:
            invoiceData = self.backend.decodeInvoiceData(self.bolt11)
        except self.backend.CommandFailed:
            self.setInvalidInvoice()
        except self.backend.NotConnected:
            QMessageBox.critical(self, 'Failed to perform the payment',
                'Error: back-end not connected.'
                )
            self.reject()
        else:
            self.setValidInvoice(invoiceData)


    def setInvalidInvoice(self):
        self.setEnabled(False)

        self.amountLabel.setText('')
        self.descriptionLabel.setText('')
        self.creationTimeLabel.setText('')
        self.expirationTimeLabel.setText('')
        self.payeeLabel.setText('')


    def setValidInvoice(self, invoiceData):
        self.setEnabled(True)

        self.amountLabel.setText(formatting.formatAmount(
            invoiceData.amount, invoiceData.currency))
        #TODO: input escaping on the description!!!
        self.descriptionLabel.setText(invoiceData.description)
        self.creationTimeLabel.setText(formatting.formatTimestamp(invoiceData.creationTime))
        self.expirationTimeLabel.setText(formatting.formatTimestamp(invoiceData.expirationTime))
        self.payeeLabel.setText(invoiceData.payee)


    def setEnabled(self, value):
        for label in self.getLabels():
            label.setEnabled(value)
        self.amountLabel.setEnabled(value)
        self.descriptionLabel.setEnabled(value)
        self.creationTimeLabel.setEnabled(value)
        self.expirationTimeLabel.setEnabled(value)
        self.payeeLabel.setEnabled(value)
        self.getDialogButtons().button(QDialogButtonBox.Ok).setEnabled(value)


    def doCommand(self):
        self.backend.pay(self.bolt11)
        updatesignal.update()

