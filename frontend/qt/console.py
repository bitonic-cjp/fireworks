from PyQt5.QtWidgets import QTextEdit, QAction



class Console(QTextEdit):
    def __init__(self, parent, backend):
        super().__init__(parent)
        self.backend = backend

