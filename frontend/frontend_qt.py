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

import sys
import logging
from PyQt5.QtWidgets import QApplication, QDialog, QDialogButtonBox, QVBoxLayout, QLabel, QLineEdit

from .qt.mainwindow import MainWindow
from .qt import updatesignal



class QuestionDialog(QDialog):
    def __init__(self, parent, question, isPassword=False):
        super().__init__(parent)

        layout = QVBoxLayout()

        label = QLabel(question, self)
        layout.addWidget(label)

        self.lineEdit = QLineEdit(self)
        if isPassword:
            self.lineEdit.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.lineEdit)

        self.dialogButtons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.dialogButtons.accepted.connect(self.accept)
        self.dialogButtons.rejected.connect(self.reject)
        layout.addWidget(self.dialogButtons)

        self.setLayout(layout)


    def getAnswer(self):
        return self.lineEdit.text()



class Frontend:
    def __init__(self, config):
        logging.info('Using Qt front-end')
        self.config = config
        self.ex = None


    def setBackend(self, backend):
        self.backend = backend


    def run(self):
        logging.info('Starting Qt front-end')

        app = QApplication(sys.argv)

        self.backend.startup()

        self.ex = MainWindow(self.config, self.backend)
        updatesignal.initTimer()
        updatesignal.setUpdateInterval(1000)

        updatesignal.update() #First update
        sys.exit(app.exec_())


    def getPassword(self, question):
        '''
        Arguments:
            question: str
        Returns: bytes
        '''

        dialog = QuestionDialog(self.ex, question, isPassword=True)
        if(dialog.exec() != dialog.Accepted):
            return None

        return dialog.getAnswer().encode()



logging.info('Loaded Qt front-end module')
