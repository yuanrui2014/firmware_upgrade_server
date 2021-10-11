# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import sys
import time

from PyQt5 import QtWidgets, Qt, QtGui
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QHeaderView, QItemDelegate, QPushButton, QHBoxLayout, QWidget, QFileDialog, QMessageBox

from server.download_server import start, openUrl, stop
from server.api_server import start_service
from ui.Ui_main import Ui_MainWindow


class AutomationButtonDelegate(QItemDelegate):
    def __init__(self, parent=None):
        super(AutomationButtonDelegate, self).__init__(parent)
        self.cellButtonClicked = None

    def setCellButtonClicked(self, cellButtonClicked):
        self.cellButtonClicked = cellButtonClicked

    def paint(self, painter, option, index):
        if not self.parent().indexWidget(index):
            button_run = QPushButton(self.tr('Run'), self.parent(), clicked=self.cellButtonClicked)
            button_edit = QPushButton(self.tr('Edit'), self.parent(), clicked=self.cellButtonClicked)
            button_remove = QPushButton(self.tr('Delete'), self.parent(), clicked=self.cellButtonClicked)
            h_box_layout = QHBoxLayout()
            h_box_layout.addWidget(button_run)
            h_box_layout.addWidget(button_edit)
            h_box_layout.addWidget(button_remove)
            h_box_layout.setContentsMargins(0, 0, 0, 0)
            h_box_layout.setAlignment(Qt.AlignCenter)
            widget = QWidget()
            widget.setLayout(h_box_layout)
            self.parent().setIndexWidget(index, widget)


class UpgradeSignal(QObject):
    upgrade_signal = pyqtSignal(dict)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setWindowTitle("Yuanrui upgrade server")

        self.file_list = {}

        self.COLUMNS = ['No.', 'Time', 'MAC', 'Version']

        self.tableview_model = QStandardItemModel()

        # 所有列自动拉伸，充满界面
        self.tableview_model.setColumnCount(len(self.COLUMNS))
        self.tableview_model.setHorizontalHeaderLabels(self.COLUMNS)
        self.ui.tableView_clients.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.tableView_clients.setModel(self.tableview_model)

        self.ui.pushButton_upgrade_file.clicked.connect(self.pushButton_import_clicked)

        self.ui.pushButton_action.clicked.connect(self.pushButton_action_clicked)

        self.upgrade_signal = UpgradeSignal()
        self.upgrade_signal.upgrade_signal.connect(self.upgrade_signal_accept)

        start_service(False, port=8080, client=self.upgrade_signal)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        stop()

    def pushButton_import_clicked(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Open file', 'c:\\', "upgrade files (*.bin)")

        if filename is not None and len(filename) > 0:
            try:
                self.ui.lineEdit_upgrade_file_path.setText(filename)
            except Exception as e:
                QMessageBox.information(self, self.windowTitle(), "indicated file error, {}".format(repr(e)))

    def upgrade_signal_accept(self, msg):
        try:
            data = msg
            print(data)

            for i in range(0, self.tableview_model.rowCount()):
                if self.tableview_model.item(i, 2) == msg['mac']:
                    print('repeated mac address {}'.format(msg['mac']))
                    return

            items = []

            item_no = QStandardItem()
            item_no.setText(str(self.tableview_model.rowCount()+1))
            items.append(item_no)

            item_time = QStandardItem()
            item_time.setText(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
            items.append(item_time)

            item_mac = QStandardItem()
            item_mac.setText(msg['mac'])
            items.append(item_mac)

            item_version = QStandardItem()
            item_version.setText(msg['version'])
            items.append(item_version)

            self.tableview_model.appendRow(items)
        except Exception as e:
            print("error message")

    def pushButton_action_clicked(self):
        if self.ui.pushButton_action.text() == "Start":
            port_number = 8000
            start(port_number)
            self.ui.pushButton_action.setText("Stop")
        else:
            stop()
            self.ui.pushButton_action.setText("Start")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
