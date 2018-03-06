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

from PyQt5.QtWidgets import QWidget, QMainWindow, QAction, QMessageBox, QVBoxLayout, QTabWidget, QStatusBar, QLabel

from .console import Console
from .overview import Overview
from .invoices import Invoices
from .payments import Payments
from . import updatesignal



class TabWidget(QWidget):
    def __init__(self, parent, tabDefinition):   
        super(QWidget, self).__init__(parent)
        layout = QVBoxLayout(self)
        self.subWidgets = []
 
        # Initialize tab screen
        tabs = QTabWidget()
        tabs.currentChanged.connect(self.onCurrentChanged)
 
        # Add tabs
        for name, widget in tabDefinition:
            tabs.addTab(widget, name)
            self.subWidgets.append(widget)
 
        # Add tabs to widget        
        layout.addWidget(tabs)
        self.setLayout(layout)


    def onCurrentChanged(self, index):
        if index < len(self.subWidgets):
            self.subWidgets[index].setFocus()



class MainWindow(QMainWindow):
    def __init__(self, config, backend):
        super().__init__()

        self.backend = backend

        self.setWindowTitle('Fireworks')
        self.setGeometry(10, 10, 640, 480)

        statusBar = QStatusBar(self)
        self.setStatusBar(statusBar)
        self.statusLabel = QLabel(statusBar)
        statusBar.addWidget(self.statusLabel)

        tabWidget = TabWidget(self,
            [
            ('Overview', Overview(None, backend)),
            ('Receive' , Invoices(None, backend)),
            ('Send'    , Payments(None, backend)),
            ('Channels', QWidget()),
            ('Console' , Console(None, backend))
            ])
        self.setCentralWidget(tabWidget)

        mainMenu = self.menuBar() 

        fileMenu = mainMenu.addMenu('File')
        exitButton = QAction('Exit', self)
        exitButton.setShortcut('Ctrl+Q')
        exitButton.setStatusTip('Exit application')
        exitButton.triggered.connect(self.close)
        fileMenu.addAction(exitButton)

        helpMenu = mainMenu.addMenu('Help')
        aboutButton = QAction('About', self)
        aboutButton.triggered.connect(self.showAbout)
        helpMenu.addAction(aboutButton)

        updatesignal.connect(self.update)

        self.show()


    def update(self):
        status = 'Not connected'
        if self.backend.isConnected():
            status = 'Connected to %s' % self.backend.getBackendName()

        self.statusLabel.setText(status)


    def showAbout(self):
        QMessageBox.about(self, 'Fireworks', \
'''
Fireworks
Copyright (C) 2018 Bitonic B.V.

Fireworks is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Fireworks is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Fireworks. If not, see <http://www.gnu.org/licenses/>.

The source code is available at https://github.com/bitonic-cjp/fireworks
''')

