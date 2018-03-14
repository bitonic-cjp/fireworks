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

from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QGridLayout, QVBoxLayout, QLabel, QMessageBox



class GenericDialog(QDialog):
    def __init__(self, parent, backend):
        super().__init__(parent)
        self.backend = backend

        mainLayout = QVBoxLayout()
        self.layout = QGridLayout()
        mainLayout.addLayout(self.layout)

        self.errorMessage = ''
        self.labels = []
        self.numRows = 0

        self.dialogButtons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.dialogButtons.accepted.connect(self.accept)
        self.dialogButtons.rejected.connect(self.reject)
        mainLayout.addWidget(self.dialogButtons)

        self.setLayout(mainLayout)

        self.accepted.connect(self.onAccepted)


    def setErrorMessage(self, msg):
        self.errorMessage = msg


    def addRow(self, text, widget):
        label = QLabel(text, self)
        self.layout.addWidget(label , self.numRows, 0)
        self.layout.addWidget(widget, self.numRows, 1)
        self.labels.append(label)
        self.numRows += 1


    def addWidget(self, widget):
        self.layout.addWidget(widget, self.numRows, 0, 1, 2)
        self.numRows += 1


    def getLabels(self):
        return self.labels


    def getDialogButtons(self):
        return self.dialogButtons


    def doCommand(self):
        pass #To be overloaded in derived classes


    def onAccepted(self):
        try:
            self.doCommand()
        except self.backend.CommandFailed as e:
            QMessageBox.critical(self, self.errorMessage,
                self.errorMessage + ':\n\n'
                 + str(e)
                )
        except self.backend.NotConnected:
            QMessageBox.critical(self, self.errorMessage,
                self.errorMessage + ': back-end not connected.'
                )

