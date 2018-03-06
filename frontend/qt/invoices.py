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

import copy

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QLabel, QPushButton, QTableView, QHeaderView, QSizePolicy, QMessageBox
from PyQt5.QtCore import Qt, QAbstractTableModel

from . import updatesignal
from .. import formatting
from .newinvoicedialog import NewInvoiceDialog
from .showinvoicedialog import ShowInvoiceDialog



class InvoiceTable(QAbstractTableModel):
    def __init__(self, parent):
        super().__init__(parent)
        self.header = \
            ['Expiration date', 'Label', 'Amount', 'Status']
        self.dataList = []


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

        invoice = self.dataList[index.row()]
        col = index.column()
        if col == 0:
            return formatting.formatTimestamp(invoice.expirationTime)
        elif col == 1:
            return invoice.label
        elif col == 2:
            return formatting.formatAmount(invoice.amount, invoice.currency)
        elif col == 3:
            return invoice.status

        return None


    def getInvoice(self, index):
        return self.dataList[index]


    def updateInvoices(self, invoices):
        oldDataList = self.dataList

        newDataList = copy.deepcopy(invoices)
        newDataList.sort(key=lambda x: x.expirationTime)
        newDataList.reverse()

        if newDataList != oldDataList:
            self.beginResetModel()
            self.dataList = newDataList
            self.endResetModel()



class Invoices(QWidget):
    def __init__(self, parent, backend):
        super().__init__(parent)
        self.backend = backend

        layout = QHBoxLayout(self)

        #### LEFT SIDE ###
        listLayout = QVBoxLayout(self)
        layout.addLayout(listLayout, 0)

        newInvoiceButton = QPushButton('Create new invoice', self)
        listLayout.addWidget(newInvoiceButton, 0)
        newInvoiceButton.clicked.connect(self.onCreateNewInvoice)

        self.invoiceTable = InvoiceTable(self)
        tableView = QTableView(self)
        tableView.setModel(self.invoiceTable)
        tableView.setSelectionBehavior(QTableView.SelectRows)
        tableView.setSelectionMode(QTableView.SingleSelection)

        #Make all colums wide enough for their contents, except the label
        #column. Rationale: only the label column does not have a
        #reasonable upper bound size.
        tableView.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents)
        tableView.horizontalHeader().setSectionResizeMode(1,
            QHeaderView.Stretch)

        policy = tableView.sizePolicy()
        policy.setHorizontalPolicy(QSizePolicy.Minimum)
        tableView.setSizePolicy(policy)
        tableView.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        tableView.selectionModel().selectionChanged.connect(self.onSelectInvoice)

        listLayout.addWidget(tableView, 0)

        #### RIGHT SIDE ###
        detailLayout = QGridLayout(self)
        layout.addLayout(detailLayout, 0)

        labels = ['Expiration date:', 'Label:', 'Amount:', 'Status:']
        for i, txt in enumerate(labels):
            label = QLabel(txt, self)
            detailLayout.addWidget(label, i, 0)

        self.expirationLabel = QLabel(self)
        self.labelLabel = QLabel(self)
        self.amountLabel = QLabel(self)
        self.statusLabel = QLabel(self)
        detailLayout.addWidget(self.expirationLabel, 0, 1)
        detailLayout.addWidget(self.labelLabel, 1, 1)
        detailLayout.addWidget(self.amountLabel, 2, 1)
        detailLayout.addWidget(self.statusLabel, 3, 1)

        self.setLayout(layout)

        updatesignal.connect(self.update)


    def update(self):
        try:
            invoices = self.backend.getInvoices()
            haveData = True
        except self.backend.NotConnected:
            invoices = []
            haveData = False
            self.expirationLabel.setText('')
            self.labelLabel.setText('')
            self.amountLabel.setText('')
            self.statusLabel.setText('')

        self.invoiceTable.updateInvoices(invoices)
        self.setEnabled(haveData)


    def onSelectInvoice(self, selected, deselected):
        rows = set()
        for index in selected.indexes():
            rows.add(index.row())
        if len(rows) != 1:
            self.expirationLabel.setText('')
            self.labelLabel.setText('')
            self.amountLabel.setText('')
            self.statusLabel.setText('')
            return

        row = tuple(rows)[0]
        invoice = self.invoiceTable.getInvoice(row)
        self.expirationLabel.setText(formatting.formatTimestamp(invoice.expirationTime))
        self.labelLabel.setText(invoice.label)
        self.amountLabel.setText(formatting.formatAmount(invoice.amount, invoice.currency))
        self.statusLabel.setText(invoice.status)


    def onCreateNewInvoice(self):
        try:
            dialog = NewInvoiceDialog(self, self.backend)
        except self.backend.NotConnected:
            QMessageBox.critical(self, 'Failed to create a new invoice',
                'Creating a new invoice failed: back-end not connected.'
                )
            return

        if(dialog.exec() != dialog.Accepted):
            return

        #These can be None if invoice creation failed:
        label = dialog.label
        bolt11 = dialog.bolt11
        expirationTime = dialog.expirationTime
        if None in (bolt11, expirationTime, label):
            return

        print(label, bolt11, expirationTime)

        dialog = ShowInvoiceDialog(self, self.backend, label, bolt11)
        dialog.exec()

