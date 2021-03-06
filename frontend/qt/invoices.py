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
from .widgets import BigLabel, QRCode
from .newinvoicedialog import NewInvoiceDialog
from .showinvoicedialog import ShowInvoiceDialog



class InvoiceTable(QAbstractTableModel):
    def __init__(self, parent, missingFields):
        super().__init__(parent)

        self.showLabel = 'label' not in missingFields

        self.header = \
            ['Expiration date', 'Amount', 'Status']
        if self.showLabel:
            self.header = ['Label'] + self.header

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

        if self.showLabel:
            if col == 0:
                return invoice.label
            col -= 1

        if col == 0:
            return formatting.formatTimestamp(invoice.data.expirationTime)
        elif col == 1:
            return formatting.formatAmount(invoice.data.amount, invoice.data.currency)
        elif col == 2:
            return invoice.status

        return None


    def getInvoice(self, index):
        return self.dataList[index]


    def updateInvoices(self, invoices):
        oldDataList = self.dataList

        newDataList = copy.deepcopy(invoices)
        newDataList.sort(key=lambda x: x.data.expirationTime)
        newDataList.reverse()

        if newDataList != oldDataList:
            self.beginResetModel()
            self.dataList = newDataList
            self.endResetModel()



class Invoices(QWidget):
    def __init__(self, parent, backend):
        super().__init__(parent)
        self.backend = backend

        self.showLabel = 'label' not in self.backend.getMissingFields(self.backend.Invoice)

        layout = QHBoxLayout()

        #### LEFT SIDE ###
        listLayout = QVBoxLayout()
        layout.addLayout(listLayout, 0)

        newInvoiceButton = QPushButton('Create new invoice', self)
        listLayout.addWidget(newInvoiceButton, 0)
        newInvoiceButton.clicked.connect(self.onCreateNewInvoice)

        self.invoiceTable = InvoiceTable(self, self.backend.getMissingFields(self.backend.Invoice))
        tableView = QTableView(self)
        tableView.setModel(self.invoiceTable)
        tableView.setSelectionBehavior(QTableView.SelectRows)
        tableView.setSelectionMode(QTableView.SingleSelection)

        if self.showLabel:
            #Make all colums wide enough for their contents, except the label
            #column. Rationale: only the label column does not have a
            #reasonable upper bound size.
            tableView.horizontalHeader().setSectionResizeMode(
                QHeaderView.ResizeToContents)
            tableView.horizontalHeader().setSectionResizeMode(0,
                QHeaderView.Stretch)
        else:
            #Make all colums wide enough for their contents.
            #Stretch the amount column.
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
        detailLayout = QGridLayout()
        layout.addLayout(detailLayout, 0)

        labels = ['Label:', 'Expiration date:', 'Amount:', 'Status:', 'Description:', 'Invoice code:']
        if not self.showLabel:
            labels[0] = ''
        for i, txt in enumerate(labels):
            label = QLabel(txt, self)
            detailLayout.addWidget(label, i, 0)

        self.labelLabel = QLabel(self)
        self.expirationLabel = QLabel(self)
        self.amountLabel = QLabel(self)
        self.statusLabel = QLabel(self)
        self.descriptionLabel = QLabel(self)
        detailLayout.addWidget(self.labelLabel, 0, 1)
        detailLayout.addWidget(self.expirationLabel, 1, 1)
        detailLayout.addWidget(self.amountLabel, 2, 1)
        detailLayout.addWidget(self.statusLabel, 3, 1)
        detailLayout.addWidget(self.descriptionLabel, 4, 1)

        self.bolt11Label = BigLabel('', self)
        policy = self.bolt11Label.sizePolicy()
        policy.setHorizontalPolicy(QSizePolicy.Minimum)
        self.bolt11Label.setSizePolicy(policy)
        detailLayout.addWidget(self.bolt11Label, 5, 1)

        self.QRCode = QRCode(self)
        detailLayout.addWidget(self.QRCode, 6, 0, 1, 2, Qt.AlignHCenter)

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
            self.descriptionLabel.setText('')
            self.bolt11Label.setText('')
            self.QRCode.clear()

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
            self.descriptionLabel.setText('')
            self.bolt11Label.setText('')
            self.QRCode.clear()
            return

        row = tuple(rows)[0]
        invoice = self.invoiceTable.getInvoice(row)
        if self.showLabel:
            self.labelLabel.setText(invoice.label)
        self.expirationLabel.setText(formatting.formatTimestamp(invoice.data.expirationTime))
        self.amountLabel.setText(formatting.formatAmount(invoice.data.amount, invoice.data.currency))
        self.statusLabel.setText(invoice.status)
        self.descriptionLabel.setText(invoice.data.description)
        self.bolt11Label.setText(invoice.bolt11)
        #Upper case for more compact QR code:
        self.QRCode.setQRCode('LIGHTNING:' + invoice.bolt11.upper())


    def onCreateNewInvoice(self):
        #Make a label that does not exist yet
        existingLabels = \
        set([
        self.invoiceTable.getInvoice(i).label
        for i in range(self.invoiceTable.rowCount(None))
        ])
        counter = 1
        newLabel = 'Invoice %d' % counter
        while newLabel in existingLabels:
            counter += 1
            newLabel = 'Invoice %d' % counter

        try:
            dialog = NewInvoiceDialog(self, self.backend, newLabel)
        except self.backend.NotConnected:
            QMessageBox.critical(self, 'Failed to create a new invoice',
                'Creating a new invoice failed: back-end not connected.'
                )
            return

        if(dialog.exec() != dialog.Accepted):
            return

        bolt11 = dialog.bolt11

        #It can be None if invoice creation failed:
        if bolt11 is None:
            return

        dialog = ShowInvoiceDialog(self, self.backend, bolt11)
        dialog.exec()

