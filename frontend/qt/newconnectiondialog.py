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

from PyQt5.QtWidgets import QLabel, QLineEdit

from . import updatesignal
from .genericdialog import GenericDialog



class NewConnectionDialog(GenericDialog):
    def __init__(self, parent, backend):
        super().__init__(parent, backend)
        self.backend = backend

        self.setWindowTitle('Create a new connection')
        self.setErrorMessage('Failed to create a new connection')

        self.linkText = QLineEdit(self)

        self.addWidget(QLabel('Enter the link of the node you want to connect to.', self))
        self.addRow('Format:', QLabel('id@host[:port]', self))
        self.addRow('Link:'  , self.linkText)


    def doCommand(self):
        self.backend.connect(self.linkText.text())
        updatesignal.update()

