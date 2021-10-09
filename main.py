# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import sys

from PyQt5 import QtWidgets, Qt
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtWidgets import QHeaderView, QItemDelegate, QPushButton, QHBoxLayout, QWidget, QFileDialog, QMessageBox

from server.server import start, openUrl
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


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setWindowTitle("Yuanrui upgrade server")

        self.file_list = {}

        self.tableview_model = QStandardItemModel()

        # 所有列自动拉伸，充满界面
        self.ui.tableView_clients.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # 所有列自动拉伸，充满界面
        self.ui.tableView_clients.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.ui.pushButton_upgrade_file.clicked.connect(self.pushButton_import_clicked)

    def pushButton_import_clicked(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Open file', 'c:\\', "upgrade files (*.bin)")

        if filename is not None and len(filename) > 0:
            try:
                self.ui.lineEdit_upgrade_file_path.setText(filename)
            except Exception as e:
                QMessageBox.information(self, self.windowTitle(), "indicated file error, {}".format(repr(e)))


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    port_number = 8000
    start(port_number)
    #openUrl(port_number)

    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
