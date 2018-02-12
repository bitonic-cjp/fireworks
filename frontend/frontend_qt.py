import sys
import logging
from PyQt5.QtWidgets import QApplication, QWidget



class App(QWidget):
    def __init__(self, config, backend):
        super().__init__()
        self.title = 'Fireworks'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.initUI()

 
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
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
