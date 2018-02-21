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

import logging

from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QGridLayout, QLabel, QFrame, QTextEdit
from PyQt5 import QtGui
from PyQt5.QtCore import Qt

from . import updatesignal
from .. import formatting



class HLine(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setFrameShadow(QFrame.Sunken)
        self.setFrameShape(QFrame.HLine)



class BigLabel(QTextEdit):
    def __init__(self, text, parent):
        super().__init__(text, parent)

        #make it look and feel like an ordinary label
        self.setReadOnly(True)
        self.setFrameStyle(QFrame.NoFrame)
        #pal = self.palette()
        #pal.setColor(QPalette.Base, Qt.transparent)
        #self.setPalette(pal)

        #wrap anywhere, adjust minimum height on the fly
        self.setLineWrapMode(QTextEdit.WidgetWidth)
        self.setWordWrapMode(QtGui.QTextOption.WrapAnywhere)
        self.document().documentLayout().documentSizeChanged.connect(
            self.adjustMinimumSize)


    def adjustMinimumSize(self, size):
        self.setMinimumHeight(size.height() + 2 * self.frameWidth())



class ShowInvoiceDialog(QDialog):
    def __init__(self, parent, backend, label, bolt11):
        super().__init__(parent)
        self.backend = backend

        self.label  = label
        self.bolt11 = bolt11

        boldFont = QtGui.QFont()
        boldFont.setBold(True)

        self.setWindowTitle('New invoice data')

        layout = QGridLayout(self)

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

        try:
            from qrcode import QRCode
            from PIL.ImageQt import ImageQt

            qr = QRCode(
                    box_size = 4,
                    border = 4,
                    )
            qr.add_data('lightning:' + self.bolt11)
            qr.make()

            img = qr.make_image()
            img = ImageQt(img)
            img = QtGui.QPixmap.fromImage(img)

            label = QLabel(self)
            label.setPixmap(img)
            layout.addWidget(label, 6, 0, 1, 2, Qt.AlignHCenter)

        except ImportError as e:
            logging.warning('Cannot display QR codes: ' + str(e))

        dialogButtons = QDialogButtonBox(
            QDialogButtonBox.Close)
        dialogButtons.rejected.connect(self.reject)
        layout.addWidget(dialogButtons, 7, 0, 1, 2)

        self.setLayout(layout)

        updatesignal.connect(self.update)
        self.update()


    def update(self):
        for invoice in self.backend.getInvoices():
            if invoice.label == self.label:
                self.amountLabel.setText(
                    formatting.formatAmount(invoice.amount))
                self.expirationLabel.setText(
                    formatting.formatTimestamp(invoice.expirationTime))
                self.statusLabel.setText(invoice.status)

                #TODO: grey out the dialog if the invoice is expired

                break

