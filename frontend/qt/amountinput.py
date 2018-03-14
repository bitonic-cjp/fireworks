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

from .. import formatting
from utils.currencies import currencyInfo



class AmountInput(QWidget):
    def __init__(self, parent, currency):
        super().__init__(parent)

        self.currency = currency
        info = currencyInfo[currency]

        layout = QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)

        self.input = QLineEdit(self)
        self.input.setText('0.00000000 000')
        layout.addWidget(self.input, 1)

        units = [(k,v) for k,v in info.multipliers.items()]
        units.sort(key = lambda x: x[1])
        units = [x[0] for x in units]
        self.unit = QComboBox(self)
        for i in range(len(units)):
            self.unit.insertItem(i, units[i])
        self.unit.setCurrentIndex(units.index(info.defaultUnit))
        layout.addWidget(self.unit, 0)

        self.setLayout(layout)


    def getValue(self):
        amountText = self.input.text() + ' ' + self.unit.currentText()
        return formatting.unformatAmount(amountText, self.currency)

