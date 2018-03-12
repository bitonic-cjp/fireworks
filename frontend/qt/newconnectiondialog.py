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

from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QGridLayout, QLabel, QLineEdit, QMessageBox

from . import updatesignal



class NewConnectionDialog(QDialog):
    def __init__(self, parent, backend):
        super().__init__(parent)
        self.backend = backend

        self.setWindowTitle('Create a new connection')

        layout = QGridLayout(self)

        layout.addWidget(QLabel('Format: id@host[:port]' , self), 0, 0, 1, 2)
        layout.addWidget(QLabel('Link:', self), 1, 0)

        self.linkText = QLineEdit(self)
        layout.addWidget(self.linkText, 1, 1)

        dialogButtons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        dialogButtons.accepted.connect(self.accept)
        dialogButtons.rejected.connect(self.reject)
        layout.addWidget(dialogButtons, 2, 0, 1, 2)

        self.setLayout(layout)

        self.accepted.connect(self.onAccepted)


    def onAccepted(self):
        try:
            self.backend.connect(self.linkText.text())
        except self.backend.CommandFailed as e:
            updatesignal.update()
            QMessageBox.critical(self, 'Failed to create a new connection',
                'Creating a new connection failed with the following error message:\n\n'
                 + str(e)
                )
        except self.backend.NotConnected:
            QMessageBox.critical(self, 'Failed to create a new connection',
                'Creating a new connection failed: back-end not connected.'
                )

