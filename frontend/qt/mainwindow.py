from PyQt5.QtWidgets import QMainWindow, QAction



class MainWindow(QMainWindow):
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

