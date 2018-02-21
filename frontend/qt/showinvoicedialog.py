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

from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QGridLayout, QLabel, QFrame

from . import updatesignal



class HLine(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setFrameShadow(QFrame.Sunken)
        self.setFrameShape(QFrame.HLine)



class ShowInvoiceDialog(QDialog):
    def __init__(self, parent, backend, label, bolt11):
        super().__init__(parent)
        self.backend = backend

        self.label  = label
        self.bolt11 = bolt11

        self.setWindowTitle('New invoice data')

        layout = QGridLayout(self)

        labels = ['Label:', 'Description:', 'Amount:', 'Expiration date:']
        for i, txt in enumerate(labels):
            label = QLabel(txt, self)
            layout.addWidget(label, i, 0)

        layout.addWidget(HLine(self), 4, 0, 1, 2)

        #TODO: add bolt11 text and QR code

        dialogButtons = QDialogButtonBox(
            QDialogButtonBox.Close)
        dialogButtons.rejected.connect(self.reject)
        layout.addWidget(dialogButtons, 5, 0, 1, 2)

        self.setLayout(layout)

