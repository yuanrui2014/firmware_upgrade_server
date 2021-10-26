# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import datetime
import os
import re
import sys
import time

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import pyqtSignal, QObject, Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QBrush
from PyQt5.QtWidgets import QItemDelegate, QPushButton, QHBoxLayout, QWidget, QFileDialog, QMessageBox, QTableView

from server.api_server import start_server, stop_server
from server.udp_broadcast import UdpBroadcast
from ui.Ui_main import Ui_MainWindow
from utils import logger, SUPPORT_UPGRADE, FIRMWARE_VERSION
from utils.funcs import read_xls_file


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


class CallbackSignal(QObject):
    callback_signal = pyqtSignal(dict)

    def __init__(self):
        super(CallbackSignal, self).__init__()
        self._filename = ''
        self._folder = ''
        self._version = ''
        self._mac_addr_list = None

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, value):
        head, tail = os.path.split(value)
        self._filename = tail

    @property
    def folder(self):
        return self._folder

    @folder.setter
    def folder(self, value):
        self._folder = os.path.dirname(value)

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, value):
        self._version = value

    @property
    def mac_addr_list(self):
        return self._mac_addr_list

    @mac_addr_list.setter
    def mac_addr_list(self, value):
        self._mac_addr_list = value


ERROR_CODE_DESC = {
    0: 'OK',
    -1: 'Failure',
    0x101: 'Out of memory',
    0x102: 'Invalid argument',
    0x103: 'Invalid state',
    0x104: 'Invalid size',
    0x105: 'Requested resource not found',
    0x106: 'Operation or feature not supported',
    0x107: 'Operation timed out',
    0x108: 'Received response was invalid',
    0x109: 'CRC or checksum was invalid',
    0x10A: 'Version was invalid',
    0x10B: 'MAC address was invalid',
    0x3000: 'Starting number of WiFi error codes',
    0x4000: 'Starting number of MESH error codes',
    0x6000: 'Starting number of flash error codes'
}


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setWindowTitle("Yuanrui firmware utility")

        self.file_list = {}

        self.COLUMNS = ['No.', 'Time', 'MAC', 'Version', 'Status', 'Server']

        self.tableview_model = QStandardItemModel()
        self.ui.tableView_clients.setModel(self.tableview_model)

        # 所有列自动拉伸，充满界面
        self.tableview_model.setColumnCount(len(self.COLUMNS))
        self.tableview_model.setHorizontalHeaderLabels(self.COLUMNS)
        #self.ui.tableView_clients.horizontalHeader().setDefaultSectionSize(150)
        self.ui.tableView_clients.horizontalHeader().resizeSection(0, 50)  # 设置第1列的宽度
        self.ui.tableView_clients.horizontalHeader().resizeSection(1, 120)  # 设置第2列的宽度
        self.ui.tableView_clients.horizontalHeader().resizeSection(2, 120)  # 设置第3列的宽度
        self.ui.tableView_clients.horizontalHeader().resizeSection(3, 300)  # 设置第4列的宽度
        self.ui.tableView_clients.horizontalHeader().resizeSection(4, 300)  # 设置第5列的宽度
        self.ui.tableView_clients.horizontalHeader().resizeSection(5, 200)  # 设置第6列的宽度
        self.ui.tableView_clients.horizontalHeader().setStyleSheet("QHeaderView::section {""color: black;padding-left: 4px;border: 1px solid #6c6c6c;}")

        font = self.ui.tableView_clients.horizontalHeader().font()
        font.setBold(True)
        self.ui.tableView_clients.horizontalHeader().setFont(font)

        self.ui.tableView_clients.horizontalHeader().setHighlightSections(True)
        self.ui.tableView_clients.setEditTriggers(QTableView.NoEditTriggers)
        self.ui.tableView_clients.setAlternatingRowColors(True)

        self.ui.tableView_clients.verticalHeader().setVisible(False)

        self.ui.pushButton_upgrade_file.clicked.connect(self.pushButton_import_clicked)
        self.ui.pushButton_product_file.clicked.connect(self.pushButton_product_clicked)

        self.ui.pushButton_action.clicked.connect(self.pushButton_action_clicked)

        self.ui.lineEdit_upgrade_file_path.textChanged.connect(self.lineEdit_upgrade_file_changed)

        self.callback_signal = CallbackSignal()
        self.callback_signal.callback_signal.connect(self.callback_signal_accept)

        self.ui.pushButton_upgrade_file.setVisible(SUPPORT_UPGRADE)
        self.ui.lineEdit_upgrade_file_path.setVisible(SUPPORT_UPGRADE)
        self.ui.checkBox_upgrade.setVisible(SUPPORT_UPGRADE)

        self.udp_broadcast = None

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.stop()

    def stop(self):
        if self.udp_broadcast is not None:
            self.udp_broadcast.shutdown()
        stop_server()

    def pushButton_import_clicked(self):
        filename, _ = QFileDialog.getOpenFileName(self, caption='Open firmware file', directory='', filter="upgrade files (*.bin)")

        if filename is not None and len(filename) > 0:
            self.ui.lineEdit_upgrade_file_path.setText(filename)

    def pushButton_product_clicked(self):
        filename, _ = QFileDialog.getOpenFileName(self, caption='Open device file', directory='', filter="excel files (*.xls, *.xlsx)")

        if filename is not None and len(filename) > 0:
            self.ui.lineEdit_product_file_path.setText(filename)

    def __exists(self, mac):
        for i in range(0, self.tableview_model.rowCount()):
            if self.tableview_model.item(i, 2).text() == mac:
                return i
        return -1

    def __add_row(self, mac, version, status, server=''):
        items = []

        item_no = QStandardItem()
        item_no.setText(str(self.tableview_model.rowCount() + 1))
        item_no.setData(Qt.AlignCenter, role=Qt.TextAlignmentRole)
        items.append(item_no)

        item_time = QStandardItem()
        item_time.setText(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        item_time.setData(Qt.AlignCenter, role=Qt.TextAlignmentRole)
        items.append(item_time)

        item_mac = QStandardItem()
        item_mac.setText(mac)
        item_mac.setData(Qt.AlignCenter, role=Qt.TextAlignmentRole)
        items.append(item_mac)

        item_version = QStandardItem()
        item_version.setText(version)
        item_version.setData(Qt.AlignCenter, role=Qt.TextAlignmentRole)
        items.append(item_version)

        item_status = QStandardItem()
        item_status.setText(status)
        item_status.setData(Qt.AlignCenter, role=Qt.TextAlignmentRole)
        items.append(item_status)

        item_server = QStandardItem()
        item_server.setText(server)
        item_server.setData(Qt.AlignCenter, role=Qt.TextAlignmentRole)
        items.append(item_server)

        self.tableview_model.appendRow(items)

        return self.tableview_model.rowCount() - 1

    def do_connect(self, msg):
        index = self.__exists(msg['mac'])
        if index < 0:
            self.__add_row(msg['mac'], version=msg['version'], status='connected')

    def do_download(self, msg):
        index = self.__exists(msg['mac'])

        if index >= 0:
            self.tableview_model.item(index, 4).setText('downloading')

    def do_verify(self, msg):
        index = self.__exists(msg['mac'])

        if index >= 0:
            self.tableview_model.item(index, 4).setText(msg['result'])
        else:
            index = self.__add_row(msg['mac'], version=msg['version'], status=msg['result'], server=msg['server'])

        item_version = self.tableview_model.item(index, 3)
        item_version.setData(QBrush(Qt.red if msg['version'] != FIRMWARE_VERSION else Qt.green), role=Qt.BackgroundRole)
        item_version.setText('firmware version is {}, new version is {}'.format(msg['version'], FIRMWARE_VERSION) if msg['version'] != FIRMWARE_VERSION else msg['version'])

        item_result = self.tableview_model.item(index, 4)
        item_result.setData(QBrush(Qt.red if msg['code'] != 0 else Qt.green), role=Qt.BackgroundRole)

    def do_finish(self, msg):
        index = self.__exists(msg['mac'])

        if index < 0:
            return

        finish = msg['finish']
        finish_str = "download successfully" if finish == 0 else "download failure, error: {}, {}".format(finish, ERROR_CODE_DESC[finish])
        self.tableview_model.item(index, 4).setText(finish_str)
        self.tableview_model.item(index, 3).setText(msg['version'])

        file_path = os.getcwd()  # 获取当前工作路径
        filename = "{}\\{}.csv".format(file_path, datetime.date.today().strftime('%Y%m%d'))

        if not os.path.exists(filename):
            f = open(filename, "w")
            header = ",".join(self.COLUMNS)
            f.write("{}\n".format(header))
        else:
            f = open(filename, "a")

        row = "{},{},{},{},{}\n".format(self.tableview_model.item(index, 0).text(), self.tableview_model.item(index, 1).text(), self.tableview_model.item(index, 2).text(),
                                        self.tableview_model.item(index, 3).text(), self.tableview_model.item(index, 4).text())
        f.write(row)

        f.close()

    def callback_signal_accept(self, msg):
        try:
            logger.info('upgrade signal, msg: {}'.format(msg))

            data_type = msg['type']

            handlers = {'download': self.do_download, 'connect': self.do_connect, 'finish': self.do_finish, 'verify': self.do_verify}

            handlers[data_type](msg['content'])

        except Exception as e:
            print("error message, {}".format(repr(e)))

    def get_firmware_version(self, filename):
        folder, name = os.path.split(filename)
        match_obj = re.match(r'(.*)_v(.*)\.bin$', name, re.M | re.I)

        return match_obj.group(2)

    def _start_server(self, upgrade_filename, product_filename):
        if upgrade_filename is not None:
            self.callback_signal.filename = upgrade_filename
            self.callback_signal.folder = upgrade_filename
            self.callback_signal.version = self.get_firmware_version(upgrade_filename)

        if product_filename is not None:
            self.callback_signal.mac_addr_list = read_xls_file(product_filename)
            logger.info("mac address list: {}".format(self.callback_signal.mac_addr_list))

        logger.info("folder: {}, filename: {}, version: {}".format(self.callback_signal.folder, self.callback_signal.filename, self.callback_signal.version))

        self.udp_broadcast = UdpBroadcast(8888)
        self.udp_broadcast.start()

        start_server(port=8080, client=self.callback_signal)

        self.ui.pushButton_action.setText("Stop")

        self.ui.lineEdit_upgrade_file_path.setEnabled(False)
        self.ui.pushButton_upgrade_file.setEnabled(False)

    def _stop_server(self):
        self.udp_broadcast.shutdown()
        self.udp_broadcast = None

        stop_server()

        self.ui.pushButton_action.setText("Start")
        self.ui.lineEdit_upgrade_file_path.setEnabled(True)
        self.ui.pushButton_upgrade_file.setEnabled(True)

    def pushButton_action_clicked(self):
        if self.ui.checkBox_upgrade.isChecked():
            upgrade_filename = self.ui.lineEdit_upgrade_file_path.text().strip()
            if len(upgrade_filename) <= 0:
                QMessageBox.information(self, self.windowTitle(), "upgrade file is empty")
                return
        else:
            upgrade_filename = None

        if self.ui.checkBox_product.isChecked():
            product_filename = self.ui.lineEdit_product_file_path.text().strip()
            if len(product_filename) <= 0:
                QMessageBox.information(self, self.windowTitle(), "production file is empty")
                return
        else:
            product_filename = None

        if upgrade_filename is None and product_filename is None:
            QMessageBox.information(self, self.windowTitle(), "No any chose functions")
            return

        try:
            if self.ui.pushButton_action.text() == "Start":
                self._start_server(upgrade_filename, product_filename)
            else:
                self._stop_server()
        except Exception as e:
            QMessageBox.warning(self, self.windowTitle(), repr(e))

    def lineEdit_upgrade_file_changed(self, text):
        pass


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
