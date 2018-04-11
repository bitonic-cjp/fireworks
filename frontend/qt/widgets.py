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

from PyQt5.QtWidgets import QFrame, QTextEdit
from PyQt5 import QtGui



class HLine(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setFrameShadow(QFrame.Sunken)
        self.setFrameShape(QFrame.HLine)



class BigLabel(QTextEdit):
    def __init__(self, text, parent):
        super().__init__(text, parent)

        #make it look and feel like an ordinary label
        self.setReadOnly(True)
        self.setFrameStyle(QFrame.NoFrame)
        #pal = self.palette()
        #pal.setColor(QPalette.Base, Qt.transparent)
        #self.setPalette(pal)

        #wrap anywhere, adjust minimum height on the fly
        self.setLineWrapMode(QTextEdit.WidgetWidth)
        self.setWordWrapMode(QtGui.QTextOption.WrapAnywhere)
        self.document().documentLayout().documentSizeChanged.connect(
            self.adjustMinimumSize)


    def adjustMinimumSize(self, size):
        self.setMinimumHeight(size.height() + 2 * self.frameWidth())

