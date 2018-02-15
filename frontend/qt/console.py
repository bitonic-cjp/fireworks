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

import pprint

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

        self.history = []
        self.history_index = 0

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


    def setCommand(self, command):
        if self.getCommand() == command:
            return

        doc = self.document()
        curr_line = doc.findBlockByLineNumber(doc.lineCount() - 1).text()
        self.moveCursor(QtGui.QTextCursor.End)
        for i in range(len(curr_line) - len(self.prompt)):
            self.moveCursor(QtGui.QTextCursor.Left, QtGui.QTextCursor.KeepAnchor)

        self.textCursor().removeSelectedText()
        self.textCursor().insertText(command)
        self.moveCursor(QtGui.QTextCursor.End)


    def getCursorPosition(self):
        c = self.textCursor()
        return c.position() - c.block().position() - len(self.prompt)


    def setCursorPosition(self, position):
        self.moveCursor(QtGui.QTextCursor.StartOfLine)
        for i in range(len(self.prompt) + position):
            self.moveCursor(QtGui.QTextCursor.Right)


    def moveCursorToLastLine(self):
        c = self.textCursor()
        if c.block() != self.document().lastBlock():
            self.moveCursor(QtGui.QTextCursor.End)


    def addToHistory(self, command):
        if command[0:1] == ' ':
            return

        if command and (not self.history or self.history[-1] != command):
            self.history.append(command)
        self.history_index = len(self.history)


    def getPrevHistoryEntry(self):
        if self.history:
            self.history_index = max(0, self.history_index - 1)
            return self.history[self.history_index]
        return ''

    def getNextHistoryEntry(self):
        if self.history:
            hist_len = len(self.history)
            self.history_index = min(hist_len, self.history_index + 1)
            if self.history_index < hist_len:
                return self.history[self.history_index]
        return ''


    def keyPressEvent(self, event):
        self.moveCursorToLastLine()

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
        elif event.key() == QtCore.Qt.Key_Up:
            self.setCommand(self.getPrevHistoryEntry())
            return
        elif event.key() == QtCore.Qt.Key_Down:
            self.setCommand(self.getNextHistoryEntry())
            return

        super(Console, self).keyPressEvent(event)


    def getWidthInCharacters(self):
        font = self.document().defaultFont()
        charWidth = QtGui.QFontMetrics(font).averageCharWidth()
        pageWidth = self.viewport().width()
        return max(10, int(pageWidth / charWidth) - 3)


    def runCommand(self):
        command = self.getCommand().strip()

        if command:
            self.addToHistory(command)

            #TODO: don't split on spaces inside quoted strings
            command = command.split(' ')

            try:
                output = self.backend.runCommand(*command)
            except self.backend.Error as e:
                output = str(e)

            output = pprint.pformat(output,
                indent=2,
                width=self.getWidthInCharacters())

            self.appendPlainText(output)

        self.newPrompt()

