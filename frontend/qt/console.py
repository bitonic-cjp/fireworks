from PyQt5.QtWidgets import QPlainTextEdit, QAction
from PyQt5 import QtCore
from PyQt5 import QtGui



MONOSPACE_FONT = 'monospace'



class Console(QPlainTextEdit):
    def __init__(self, parent, backend):
        super().__init__(parent)
        self.backend = backend

        self.prompt = '> '

        self.setWordWrapMode(QtGui.QTextOption.WrapAnywhere)
        self.setUndoRedoEnabled(False)
        self.document().setDefaultFont(QtGui.QFont(MONOSPACE_FONT, 10, QtGui.QFont.Normal))

        self.newPrompt()


    def newPrompt(self):
        self.appendPlainText(self.prompt)
        self.moveCursor(QtGui.QTextCursor.End)


    def getCommand(self):
        doc = self.document()
        curr_line = doc.findBlockByLineNumber(doc.lineCount() - 1).text()
        curr_line = curr_line.rstrip()
        curr_line = curr_line[len(self.prompt):]
        return curr_line


    def getCursorPosition(self):
        c = self.textCursor()
        return c.position() - c.block().position() - len(self.prompt)

    def setCursorPosition(self, position):
        self.moveCursor(QtGui.QTextCursor.StartOfLine)
        for i in range(len(self.prompt) + position):
            self.moveCursor(QtGui.QTextCursor.Right)


    def keyPressEvent(self, event):
        if event.key() in (QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return):
            self.runCommand()
            return
        if event.key() == QtCore.Qt.Key_Home:
            self.setCursorPosition(0)
            return
        if event.key() == QtCore.Qt.Key_PageUp:
            return
        elif event.key() in (QtCore.Qt.Key_Left, QtCore.Qt.Key_Backspace):
            if self.getCursorPosition() == 0:
                return

        super(Console, self).keyPressEvent(event)


    def runCommand(self):
        command = self.getCommand()
        self.appendPlainText('Command output\n')
        self.newPrompt()

