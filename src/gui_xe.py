#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Main application module for the Parking System.
Handles the GUI interface and core functionality.
"""

from typing import Dict, Any, Optional
import csv
import os
import datetime
import ast

from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import QObject, pyqtSlot, QEventLoop, QPointF
from PyQt5.QtGui import QFont, QPainter
from PyQt5.QtPrintSupport import QPrinter, QPrintPreviewDialog, QPrintDialog
from PyQt5.QtWebEngineWidgets import QWebEnginePage
from PyQt5.QtWidgets import QInputDialog, QDialog, QProgressDialog, QProgressBar, QMessageBox

from SqliteHelper import db
from config import FONT_FAMILY, FONT_SIZE, TICKET_TITLE, TICKET_SUBTITLE
from xuat_baocao import Ui_Dialog

# Global font settings
font = QFont(FONT_FAMILY, FONT_SIZE)

class PrintHandler(QObject):
    """Handles ticket printing functionality."""
    
    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.m_inPrintPreview = False
        self.waiting = False
        self.m_page = QWebEnginePage()

    def setPage(self, data: Any) -> None:
        """Set the page content for printing."""
        self.setHtml(data)
        self.m_page.printRequested.connect(self.printPreview)
        self.m_page.loadFinished.connect(self.pageLoaded)

    def pageLoaded(self) -> None:
        """Handle page load completion."""
        if self.waiting:
            self.waiting = False
            self.print()

    def setHtml(self, data: Any) -> None:
        """Set HTML content for the ticket."""
        if isinstance(data, str):
            data = ast.literal_eval(data)
        ngay_tao = datetime.datetime.strptime(data[2], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y %H:%M:%S')
        
        html = f'''
            <style>
                table {{margin-bottom: 10px;color: #000;border: 2px solid #000;font-size: 12px;}}
                table,tr {{width: 100%;}}
                td {{border: 1px solid #000;}}
                td {{padding: 5px;}}
                .bloder {{font-weight: bolder;}}
            </style>
            <table>        
                <tr style="font-size: 20px;text-align: center;">
                    <td>{TICKET_TITLE}</td>
                </tr>
                <tr style="font-size: 15px;">
                    <td>
                        {TICKET_SUBTITLE} <br/>
                        * SỐ XE : {data[1]}<br/>
                        * NGÀY : {ngay_tao}        
                    </td>
                </tr>
            </table>
            <style type="text/css">
                table {{ page-break-inside:auto;page-break-inside:avoid; }}
                @media print {{
                    footer {{page-break-after: always;}}
                }}
                p {{margin: 0;padding: 0;margin-top: 5px;}}
            </style>
        '''
        self.m_page.setHtml(html)

    @pyqtSlot()
    def print(self) -> None:
        """Handle print action."""
        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, self.m_page.view())
        if dialog.exec_() == QDialog.Accepted:
            self.printDocument(printer)

    @pyqtSlot()
    def printPreview(self) -> None:
        """Show print preview."""
        if not self.m_page or self.m_inPrintPreview:
            return
        self.m_inPrintPreview = True
        printer = QPrinter()
        preview = QPrintPreviewDialog(printer, self.m_page.view())
        preview.paintRequested.connect(self.printDocument)
        preview.exec_()
        self.m_inPrintPreview = False

    @pyqtSlot(QPrinter)
    def printDocument(self, printer: QPrinter) -> None:
        """Print the document."""
        loop = QEventLoop()
        result = False

        def printPreview(success: bool) -> None:
            nonlocal result
            result = success
            loop.quit()

        progressbar = QProgressDialog(self.m_page.view())
        progressbar.setWindowTitle('In')
        progressbar.findChild(QProgressBar).setTextVisible(False)
        progressbar.setLabelText("Vui lòng chờ...")
        progressbar.setRange(0, 0)
        progressbar.show()
        progressbar.canceled.connect(loop.quit)
        
        self.m_page.print(printer, printPreview)
        loop.exec_()
        progressbar.close()
        
        if not result:
            painter = QPainter()
            if painter.begin(printer):
                font = painter.font()
                font.setPixelSize(20)
                painter.setFont(font)
                painter.drawText(QPointF(10, 25), "Could not generate print preview.")
                painter.end()

class EditButtonsWidget(QtWidgets.QWidget):
    """Widget containing edit buttons for each row."""
    
    editCalled = QtCore.pyqtSignal(str)

    def __init__(self, row: int, col: int, parent: Optional[QtWidgets.QTableWidget] = None):
        super().__init__(parent)
        self.row = row
        self.col = col
        self.parent = parent
        
        # Create buttons
        btnPrint = QtWidgets.QPushButton('In')
        btnDelete = QtWidgets.QPushButton('Xóa')
        
        # Setup layout
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(btnPrint)
        layout.addWidget(btnDelete)
        self.setLayout(layout)
        
        # Connect signals
        btnDelete.clicked.connect(self.deleteBike)
        btnPrint.clicked.connect(self.printDialog)

    def getAllCellVal(self) -> None:
        """Get all cell values in the row."""
        itmVal = {}
        for col in range(3):
            itm = self.parent.item(self.row, col).text()
            itmVal[col] = str(itm)
        if itmVal:
            self.editCalled.emit(str(itmVal))

    def deleteBike(self) -> None:
        """Delete the bike entry."""
        xe_id = self.parent.item(self.row, 0).text()
        db.edit(f"DELETE FROM xe_gui WHERE id = {xe_id}")
        self.editCalled.emit("Deleted")

    def printDialog(self) -> None:
        """Handle print dialog."""
        self.getAllCellVal()

class Ui_MainWindow:
    """Main window UI class."""
    
    def setupUi(self, MainWindow: QtWidgets.QMainWindow) -> None:
        """Setup the main window UI."""
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 618)
        
        # Create central widget
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        # Create input field
        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setGeometry(QtCore.QRect(22, 9, 391, 61))
        font = QtGui.QFont()
        font.setPointSize(28)
        self.lineEdit.setFont(font)
        self.lineEdit.setMaxLength(16)
        self.lineEdit.returnPressed.connect(self.printInstant)
        self.lineEdit.setObjectName("lineEdit")
        
        # Create buttons
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(420, 10, 101, 41))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.printInstant)
        
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(420, 53, 101, 20))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.clicked.connect(self.openExportCsvDialog)
        
        # Create table
        self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidget.setGeometry(QtCore.QRect(20, 81, 1081, 481))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setRowCount(0)
        
        # Setup table headers
        for i, header in enumerate(["ID", "Số xe", "Ngày tạo", "Thao tác"]):
            item = QtWidgets.QTableWidgetItem()
            self.tableWidget.setHorizontalHeaderItem(i, item)
            item.setText(header)
        
        # Setup main window
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1112, 26))
        MainWindow.setMenuBar(self.menubar)
        
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        MainWindow.setStatusBar(self.statusbar)
        
        # Setup UI
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.loaddata()
        
        # Setup table style
        header = self.tableWidget.horizontalHeader()
        header.setStyleSheet("::section{Background-color:rgb(150,150,1)}")
        header.setMinimumSectionSize(100)
        self.tableWidget.setColumnHidden(0, True)
        self.tableWidget.setColumnWidth(1, 400)
        self.tableWidget.setColumnWidth(2, 150)
        self.tableWidget.setColumnWidth(3, 200)

    def retranslateUi(self, MainWindow: QtWidgets.QMainWindow) -> None:
        """Translate UI elements."""
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Gửi Xe GAMING"))
        self.lineEdit.setPlaceholderText(_translate("MainWindow", "Nhập số xe"))
        self.pushButton.setText(_translate("MainWindow", "In"))
        self.pushButton.setDefault(True)
        self.pushButton.setAutoDefault(False)
        self.pushButton_2.setText(_translate("MainWindow", ">>>"))

    def printInstant(self) -> None:
        """Handle instant print action."""
        so_xe = self.lineEdit.text().strip()
        if so_xe:
            data = self.addBike(so_xe)
            if data:
                self.print(data)
                self.loaddata()

    def addBike(self, so_xe: str) -> Optional[tuple]:
        """Add a new bike entry."""
        try:
            db.edit(f"INSERT INTO xe_gui (so_xe) VALUES ('{so_xe}')")
            last_id = db.getLastRowId()
            return db.fetch_one(f"SELECT * FROM xe_gui WHERE id = {last_id}")
        except Exception as e:
            self.show_error("Lỗi", f"Không thể thêm xe: {str(e)}")
            return None

    def actionBtnscallBack(self, values: str) -> None:
        """Handle button callbacks."""
        if values == "Deleted":
            self.loaddata()
        else:
            self.print(values)

    def print(self, data: Any) -> None:
        """Print ticket."""
        handler = PrintHandler()
        handler.setPage(data)
        handler.print()
        self.resetUserCursor()

    def resetUserCursor(self) -> None:
        """Reset input field."""
        self.lineEdit.clear()
        self.lineEdit.setFocus()

    def loaddata(self) -> None:
        """Load data into table."""
        try:
            bikes = db.select("SELECT * FROM xe_gui ORDER BY ngay_tao DESC")
            self.tableWidget.setRowCount(len(bikes))
            for row, bike in enumerate(bikes):
                for col, value in enumerate(bike):
                    item = QtWidgets.QTableWidgetItem(str(value))
                    self.tableWidget.setItem(row, col, item)
                widget = EditButtonsWidget(row, 3, self.tableWidget)
                widget.editCalled.connect(self.actionBtnscallBack)
                self.tableWidget.setCellWidget(row, 3, widget)
        except Exception as e:
            self.show_error("Lỗi", f"Không thể tải dữ liệu: {str(e)}")

    def openExportCsvDialog(self) -> None:
        """Open export CSV dialog."""
        try:
            dialog = QtWidgets.QDialog()
            ui = Ui_Dialog()
            ui.setupUi(dialog)
            if dialog.exec_() == QtWidgets.QDialog.Accepted:
                self.exportCSV({
                    "from": ui.dateEdit.text(),
                    "to": ui.dateEdit_2.text()
                })
        except Exception as e:
            self.show_error("Lỗi", f"Không thể mở hộp thoại xuất báo cáo: {str(e)}")

    def exportCSV(self, values: Dict[str, str]) -> None:
        """Export data to CSV."""
        try:
            f = datetime.datetime.strptime(values['from'], "%d/%m/%Y").strftime("%Y-%m-%d")
            t = datetime.datetime.strptime(values['to'], "%d/%m/%Y").strftime("%Y-%m-%d")
            
            data = db.select(f"SELECT * FROM xe_gui WHERE DATE(ngay_tao) BETWEEN '{f}' AND '{t}' ")
            if not data:
                self.show_warning("Không có dữ liệu", "Không có dữ liệu trong khoảng thời gian đã chọn.")
                return

            dlg = QtWidgets.QFileDialog()
            dlg.setNameFilters(["*.csv"])
            dlg.selectNameFilter("CSV Files (*.csv)")
            name = dlg.getSaveFileName(dlg, 'Xuất báo cáo', "", "CSV Files (*.csv)")
            
            if not name[0]:
                return

            with open(name[0], 'w', newline='', encoding='utf-8') as out_csv_file:
                csv_out = csv.writer(out_csv_file)
                csv_out.writerow(['ID', 'Số xe', 'Ngày tạo'])
                for result in data:
                    csv_out.writerow(result)
            
            self.show_info("Thành công", f"Đã xuất báo cáo thành công vào file: {name[0]}")
            
        except ValueError:
            self.show_error("Lỗi", "Định dạng ngày không hợp lệ.")
        except Exception as e:
            self.show_error("Lỗi", f"Không thể xuất báo cáo: {str(e)}")

    def show_error(self, title: str, message: str) -> None:
        """Show error message."""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(message)
        msg.setWindowTitle(title)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def show_warning(self, title: str, message: str) -> None:
        """Show warning message."""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(message)
        msg.setWindowTitle(title)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def show_info(self, title: str, message: str) -> None:
        """Show info message."""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.setWindowTitle(title)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
