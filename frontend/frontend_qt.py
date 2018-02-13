import sys
import logging
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QAction



class App(QMainWindow):
    def __init__(self, config, backend):
        super().__init__()

        self.setWindowTitle('Fireworks')
        self.setGeometry(10, 10, 640, 480)

        mainMenu = self.menuBar() 

        fileMenu = mainMenu.addMenu('File')
        exitButton = QAction('Exit', self)
        exitButton.setShortcut('Ctrl+Q')
        exitButton.setStatusTip('Exit application')
        exitButton.triggered.connect(self.close)
        fileMenu.addAction(exitButton)

        helpMenu = mainMenu.addMenu('Help')
        aboutButton = QAction('About', self)
        helpMenu.addAction(aboutButton)

        self.show()



class Frontend:
    def __init__(self, config, backend):
        logging.info('Using Qt front-end')
        self.app = QApplication(sys.argv)
        self.ex = App(config, backend)


    def run(self):
        logging.info('Starting Qt front-end')
        sys.exit(self.app.exec_())



logging.info('Loaded Qt front-end module')
