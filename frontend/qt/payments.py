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

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QLabel, QPushButton, QTableView, QHeaderView, QSizePolicy
from PyQt5.QtCore import Qt, QAbstractTableModel

from . import updatesignal
from .. import formatting
from .newpaymentdialog import NewPaymentDialog



class PaymentTable(QAbstractTableModel):
    def __init__(self, parent):
        super().__init__(parent)
        self.header = \
            ['Date', 'Label', 'Amount', 'Status']
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

        payment = self.dataList[index.row()]
        col = index.column()
        if col == 0:
            return formatting.formatTimestamp(payment.timestamp)
        elif col == 1:
            return payment.label
        elif col == 2:
            return formatting.formatAmount(payment.amount, payment.currency)
        elif col == 3:
            return payment.status

        return None


    def getPayment(self, index):
        return self.dataList[index]


    def updatePayments(self, payments):
        oldDataList = self.dataList

        newDataList = copy.deepcopy(payments)
        newDataList.sort(key=lambda x: x.timestamp)
        newDataList.reverse()

        if newDataList != oldDataList:
            self.beginResetModel()
            self.dataList = newDataList
            self.endResetModel()



class Payments(QWidget):
    def __init__(self, parent, backend):
        super().__init__(parent)
        self.backend = backend

        layout = QHBoxLayout(self)

        #### LEFT SIDE ###
        listLayout = QVBoxLayout(self)
        layout.addLayout(listLayout, 0)

        newPaymentButton = QPushButton('Perform a new payment', self)
        listLayout.addWidget(newPaymentButton, 0)
        newPaymentButton.clicked.connect(self.onCreateNewPayment)

        self.paymentTable = PaymentTable(self)
        tableView = QTableView(self)
        tableView.setModel(self.paymentTable)
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

        tableView.selectionModel().selectionChanged.connect(self.onSelectPayment)
        listLayout.addWidget(tableView, 0)

        #### RIGHT SIDE ###
        detailLayout = QGridLayout(self)
        layout.addLayout(detailLayout, 0)

        labels = [
            'Date:',
            'Label:',
            'Amount:',
            'Status:',
            'Destination:',
            'Hash:',
            'Preimage:']
        for i, txt in enumerate(labels):
            label = QLabel(txt, self)
            detailLayout.addWidget(label, i, 0)

        self.dateLabel = QLabel(self)
        self.labelLabel = QLabel(self)
        self.amountLabel = QLabel(self)
        self.statusLabel = QLabel(self)
        self.destinationLabel = QLabel(self)
        self.hashLabel = QLabel(self)
        self.preimageLabel = QLabel(self)
        detailLayout.addWidget(self.dateLabel, 0, 1)
        detailLayout.addWidget(self.labelLabel, 1, 1)
        detailLayout.addWidget(self.amountLabel, 2, 1)
        detailLayout.addWidget(self.statusLabel, 3, 1)
        detailLayout.addWidget(self.destinationLabel, 4, 1)
        detailLayout.addWidget(self.hashLabel, 5, 1)
        detailLayout.addWidget(self.preimageLabel, 6, 1)

        self.setLayout(layout)

        updatesignal.connect(self.update)


    def update(self):
        try:
            payments = self.backend.getPayments()
        except self.backend.NotConnected:
            #TODO: erase and grey-out
            return
        self.paymentTable.updatePayments(payments)


    def onSelectPayment(self, selected, deselected):
        rows = set()
        for index in selected.indexes():
            rows.add(index.row())
        if len(rows) != 1:
            self.dateLabel.setText('')
            self.labelLabel.setText('')
            self.amountLabel.setText('')
            self.statusLabel.setText('')
            self.destinationLabel.setText('')
            self.hashLabel.setText('')
            self.preimageLabel.setText('')
            return

        row = tuple(rows)[0]
        payment = self.paymentTable.getPayment(row)
        self.dateLabel.setText(formatting.formatTimestamp(payment.timestamp))
        self.labelLabel.setText(payment.label)
        self.amountLabel.setText(formatting.formatAmount(payment.amount, payment.currency))
        self.statusLabel.setText(payment.status)
        self.destinationLabel.setText(payment.destination)
        self.hashLabel.setText(payment.paymentHash)
        self.preimageLabel.setText(payment.paymentPreimage)

    def onCreateNewPayment(self):
        dialog = NewPaymentDialog(self, self.backend)
        dialog.exec()

