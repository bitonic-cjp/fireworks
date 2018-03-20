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

import decimal

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QComboBox, QLineEdit
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator

from .. import formatting
from utils.currencies import currencyInfo



class DurationInput(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        layout = QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)

        self.input = QLineEdit(self)
        self.input.setAlignment(Qt.AlignRight)
        self.input.setValidator(QIntValidator(self.input))
        self.input.setText('1')
        layout.addWidget(self.input, 1)

        units = ['seconds', 'minutes', 'hours', 'days']
        self.unit = QComboBox(self)
        for i in range(len(units)):
            self.unit.insertItem(i, units[i])
        self.unit.setCurrentIndex(2) #hours
        layout.addWidget(self.unit, 0)

        self.setLayout(layout)



    def getValue(self):
        multiplier = \
        {
        'seconds': 1,
        'minutes': 60,
        'hours'  : 60*60,
        'days'   : 60*60*24
        }[self.unit.currentText()]
        value = decimal.Decimal(self.input.text())
        return int(value*multiplier)

