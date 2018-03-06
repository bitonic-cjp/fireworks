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

from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QGridLayout, QLabel, QPlainTextEdit, QFrame, QMessageBox

from .. import formatting
from . import updatesignal



class HLine(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setFrameShadow(QFrame.Sunken)
        self.setFrameShape(QFrame.HLine)



class NewPaymentDialog(QDialog):
    def __init__(self, parent, backend):
        super().__init__(parent)
        self.backend = backend

        self.bolt11 = None

        self.setWindowTitle('Perform a new payment')

        layout = QGridLayout(self)

        layout.addWidget(QLabel('Invoice code:', self), 0, 0)

        self.bolt11Text = QPlainTextEdit(self)
        self.bolt11Text.textChanged.connect(self.onBolt11Changed)
        layout.addWidget(self.bolt11Text, 0, 1)

        layout.addWidget(HLine(self), 1, 0, 1, 2)

        self.labels = [
            'Amount:',
            'Description:',
            'Creation time:',
            'Expiration time:',
            'To:']
        self.labels = [QLabel(txt, self) for txt in self.labels]
        for i, label in enumerate(self.labels):
            layout.addWidget(label, i+2, 0)

        self.amountLabel = QLabel(self)
        self.descriptionLabel = QLabel(self)
        self.creationTimeLabel = QLabel(self)
        self.expirationTimeLabel = QLabel(self)
        self.payeeLabel = QLabel(self)

        layout.addWidget(self.amountLabel        , 2, 1)
        layout.addWidget(self.descriptionLabel   , 3, 1)
        layout.addWidget(self.creationTimeLabel  , 4, 1)
        layout.addWidget(self.expirationTimeLabel, 5, 1)
        layout.addWidget(self.payeeLabel         , 6, 1)

        self.dialogButtons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.dialogButtons.accepted.connect(self.accept)
        self.dialogButtons.rejected.connect(self.reject)
        layout.addWidget(self.dialogButtons, 7, 0, 1, 2)

        self.setLayout(layout)

        self.setInvalidInvoice()

        self.accepted.connect(self.onAccepted)


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
        for label in self.labels:
            label.setEnabled(value)
        self.amountLabel.setEnabled(value)
        self.descriptionLabel.setEnabled(value)
        self.creationTimeLabel.setEnabled(value)
        self.expirationTimeLabel.setEnabled(value)
        self.payeeLabel.setEnabled(value)
        self.dialogButtons.button(QDialogButtonBox.Ok).setEnabled(value)


    def onAccepted(self):
        try:
            self.backend.pay(self.bolt11)
            updatesignal.update()
        except self.backend.CommandFailed as e:
            updatesignal.update()
            QMessageBox.critical(self, 'Failed to perform the payment',
                'Performing the payment failed with the following error message:\n\n'
                 + str(e)
                )
        except self.backend.NotConnected:
            QMessageBox.critical(self, 'Failed to perform the payment',
                'Performing the payment failed: back-end not connected.'
                )

