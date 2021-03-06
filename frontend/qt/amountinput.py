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

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QComboBox, QLineEdit
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QValidator

from .. import formatting
from utils.currencies import currencyInfo



class AmountValidator(QValidator):
    def __init__(self, parent, currency, unit):
        super().__init__(parent)
        self.currency = currency
        self.unit = unit


    def validate(self, input, pos):
        #Allow empty input, and interpret it as 0
        if input == '':
            input = '0'

        try:
            amount = formatting.unformatAmountWithoutUnit(input, self.currency, self.unit)
        except:
            return (QValidator.Invalid, input, pos)


        newInput = formatting.formatAmountWithoutUnit(amount, self.currency, self.unit)

        #Never have the cursor before the space separator:
        if pos < len(newInput) and newInput[pos] == ' ':
            pos += 1

        return (QValidator.Acceptable, newInput, pos)



class AmountLineEdit(QLineEdit):
    def __init__(self, parent):
        super().__init__(parent)
        self.setAlignment(Qt.AlignRight)

    def keyPressEvent(self, event):
        def default():
            return super(AmountLineEdit, self).keyPressEvent(event)

        text = self.text()
        cursor = self.cursorPosition()

        #Move the period when a new period is inserted
        if event.key() in (Qt.Key_Period, Qt.Key_Comma):
            #Remove the pre-existing period
            beforeCursor = text[:cursor].replace('.', '')
            afterCursor = text[cursor:].replace('.', '')
            #Remove '0's at start:
            if beforeCursor:
                beforeCursor = str(int(beforeCursor))

            self.setText(beforeCursor + '.' + afterCursor)
            self.setCursorPosition(len(beforeCursor)+1) #after the new period
            return

        #Don't delete an existing period
        elif event.key() == (Qt.Key_Delete):
            if cursor < len(text) and text[cursor] == '.':
                self.setCursorPosition(cursor+1) #only move right
                return
        elif event.key() == (Qt.Key_Backspace):
            if cursor > 0 and text[cursor-1] == '.':
                self.setCursorPosition(cursor-1) #only move left
                return

        default()



class AmountInput(QWidget):
    def __init__(self, parent, currency):
        super().__init__(parent)

        self.currency = currency
        info = currencyInfo[currency]

        layout = QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)

        self.input = AmountLineEdit(self)
        self.validator = AmountValidator(self.input, currency, info.defaultUnit)
        self.input.setValidator(self.validator)
        self.input.setText('0')
        layout.addWidget(self.input, 1)

        units = [(k,v) for k,v in info.multipliers.items()]
        units.sort(key = lambda x: x[1])
        units = [x[0] for x in units]
        self.unit = QComboBox(self)
        for i in range(len(units)):
            self.unit.insertItem(i, units[i])
        self.unit.setCurrentIndex(units.index(info.defaultUnit))
        self.unit.currentIndexChanged.connect(self.onUnitChange)
        layout.addWidget(self.unit, 0)

        self.setLayout(layout)


    def onUnitChange(self, event):
        newUnit = self.unit.currentText()

        self.validator.unit = newUnit
        self.input.setText('0' + self.input.text()) #Trigger the validator


    def getValue(self):
        return formatting.unformatAmountWithoutUnit(
            self.input.text(),
            self.currency,
            self.unit.currentText())

