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

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QTableView
from PyQt5.QtCore import Qt, QAbstractTableModel

from . import updatesignal
from .. import formatting



class InvoiceTable(QAbstractTableModel):
    def __init__(self, parent, backend):
        super().__init__(parent)
        self.header = \
            ['Expiration date', 'Label', 'Amount', 'Status']
        self.dataList = []

        self.backend = backend
        updatesignal.connect(self.update)


    def rowCount(self, parent):
        return len(self.dataList)


    def columnCount(self, parent):
        return len(self.header)


    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.header[col]
        return None


    def data(self, index, role):
        if not index.isValid():
            return None
        elif role != Qt.DisplayRole:
            return None
        return self.dataList[index.row()][index.column()]


    def update(self):
        print('update')
        invoices = self.backend.getInvoices()
        oldDataList = self.dataList

        #Initially prepend every item with an unformatted timestamp
        newDataList = [
            [x[1], formatting.formatTimestamp(x[1]), x[0], formatting.formatAmount(x[2]), x[3]]
            for x in invoices
            ]
        #Then, reverse sort on the unformatted timestamp
        newDataList.sort(key=lambda x: x[0])
        newDataList.reverse()
        #Finally, remove the unformatted timestamp
        newDataList = [x[1:] for x in newDataList]

        if newDataList != oldDataList:
            self.beginResetModel()
            self.dataList = newDataList
            self.endResetModel()



class Invoices(QWidget):
    def __init__(self, parent, backend):
        super().__init__(parent)
        layout = QHBoxLayout(self)

        self.invoiceTable = InvoiceTable(self, backend)
        tableView = QTableView(self)
        tableView.setModel(self.invoiceTable)
        tableView.setSelectionBehavior(QTableView.SelectRows)
        tableView.setSelectionMode(QTableView.SingleSelection)
        layout.addWidget(tableView, 1)

        invoiceView = QWidget(self)
        layout.addWidget(invoiceView, 1)

        self.setLayout(layout)

