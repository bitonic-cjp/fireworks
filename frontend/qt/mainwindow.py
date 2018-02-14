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

from PyQt5.QtWidgets import QWidget, QMainWindow, QAction, QMessageBox, QVBoxLayout, QTabWidget

from .console import Console
from .overview import Overview



class TabWidget(QWidget):
    def __init__(self, parent, tabDefinition):   
        super(QWidget, self).__init__(parent)
        layout = QVBoxLayout(self)
 
        # Initialize tab screen
        tabs = QTabWidget()
        #tabs.resize(300,200) 
 
        # Add tabs
        for name, widget in tabDefinition:
            tabs.addTab(widget, name)
 
        # Add tabs to widget        
        layout.addWidget(tabs)
        self.setLayout(layout)



class MainWindow(QMainWindow):
    def __init__(self, config, backend):
        super().__init__()

        self.setWindowTitle('Fireworks')
        self.setGeometry(10, 10, 640, 480)

        tabWidget = TabWidget(self,
            [
            ('Overview', Overview(None, backend)),
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

        self.show()


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

