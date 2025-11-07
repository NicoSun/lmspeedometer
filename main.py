import sys
from PySide6.QtWidgets import QHeaderView, QApplication, QMainWindow, QTableView, QPushButton, QVBoxLayout, QWidget, QMessageBox, QHBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel, QStandardItem, QFont

import lm_studio_interface
import benchexport


class LMSpeedometer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.checked = False

        self.setWindowTitle("LM Speedometer")
        self.setGeometry(100, 100, 600, 400)

        # Create a standard item model to hold the data
        self.model = QStandardItemModel()

        # Add columns (1 for checkboxes and another one for item names)
        self.model.setHorizontalHeaderLabels(["Select", "Model","Status"])

        # Example items
        models = lm_studio_interface.load_available_models()

        models_names = [name.model_key for name in models]

        # Populate the model with data
        for i, item in enumerate(models_names):
            checkbox_item = QStandardItem()
            checkbox_item.setCheckable(True)

            # Increase font size and checkbox size
            checkbox_font = QFont("Arial", 14)
            checkbox_item.setFont(checkbox_font)

            self.model.appendRow([checkbox_item, QStandardItem(item)])

        # Create a table view and set the model
        self.table_view = QTableView()
        self.table_view.setModel(self.model)

        # Increase font size for table items
        header_font = QFont("Arial", 16)
        self.table_view.horizontalHeader().setFont(header_font)
        self.table_view.horizontalHeader().resizeSection(0, 80)
        self.table_view.horizontalHeader().resizeSection(1, 300)
        
        item_delegate = self.create_item_delegate(14)
        self.table_view.setItemDelegateForColumn(2, item_delegate)

        # Add a submit button
        ssd_button = QPushButton("SSD Test")
        token_button = QPushButton("Token Test")
        select_all_button = QPushButton("Select All")
        unselect_all_button = QPushButton("UnSelect All")

        # Connect the button's clicked signal to the slot that prints selected items
        ssd_button.clicked.connect(self.ssd_test)
        token_button.clicked.connect(self.token_test)
        select_all_button.clicked.connect(self.select_all_items)
        unselect_all_button.clicked.connect(self.unselect_all_items)

        # Layout setup
        layout = QVBoxLayout()
        layout.addWidget(unselect_all_button)
        layout.addWidget(select_all_button)

        layout.addWidget(self.table_view)
        layout.addWidget(ssd_button)
        layout.addWidget(token_button)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        
        self.setCentralWidget(central_widget)

    def create_item_delegate(self, font_size):
        from PySide6.QtWidgets import QStyledItemDelegate

        class FontDelegate(QStyledItemDelegate):
            def __init__(self, parent=None):
                super().__init__(parent)

            def initStyleOption(self, option, index):
                super().initStyleOption(option, index)
                option.font.setPointSize(font_size)

        return FontDelegate()

    def select_all_items(self):
        for row in range(self.model.rowCount()):
            checkbox_item = self.model.item(row, 0)  # Get checkbox item
            checkbox_item.setCheckState(Qt.Checked)

    def unselect_all_items(self):
        for row in range(self.model.rowCount()):
            checkbox_item = self.model.item(row, 0)  # Get checkbox item
            checkbox_item.setCheckState(Qt.Unchecked)


    def ssd_test(self):
        selected_items = []

        # Iterate over each item in the model and check if it is checked
        for row in range(self.model.rowCount()):
            checkbox_item = self.model.item(row, 0)  # Get checkbox item
            if checkbox_item.checkState() == Qt.Checked:
                # If the checkbox is checked, get the corresponding text from the second column
                item_name = self.model.item(row, 1).text()
                selected_items.append(item_name)

        # Print or show the selected items (can also use QMessageBox to display)
        if not selected_items:
            QMessageBox.warning(self, "No Selections", "Please select at least one model.")
            return

        
        tableheader = ["Model", "Time (s)", "Size (MB)", "Speed (MB/s)"]
        additional_data_model = QStandardItemModel()
        additional_data_model.setHorizontalHeaderLabels(tableheader)

        datalist = [tableheader]
        # Populate the additional data table with details
        for item in selected_items:
            result_dict = lm_studio_interface.model_loading_test(item)
            datalist.append([item,result_dict["duration"],result_dict["size"],result_dict["transfer"]])
            
            # convert results to strings for table
            dict_strings = {k: str(v) for k, v in result_dict.items()}
            row = [QStandardItem(item), 
                   QStandardItem(dict_strings["duration"]), 
                   QStandardItem(dict_strings["size"]), 
                   QStandardItem(dict_strings["transfer"])]
            additional_data_model.appendRow(row)

        filename = 'drivebench'
        benchexport.export_csv(filename, datalist)
        # Create a table view to display the additional data
        additional_table_view = QTableView()
        additional_table_view.setModel(additional_data_model)

        # Set up a separate layout for displaying selected items and their details
        details_label = QLabel("Details of Selected Items:")
        details_layout = QVBoxLayout()
        details_layout.addWidget(details_label)
        details_layout.addWidget(additional_table_view)

        details_widget = QWidget()
        details_widget.setLayout(details_layout)

        # Adjust window size to accommodate both tables
        self.setCentralWidget(details_widget)
        self.resize(800, 600)

    def token_test(self):
        selected_items = []

        # Iterate over each item in the model and check if it is checked
        for row in range(self.model.rowCount()):
            checkbox_item = self.model.item(row, 0)  # Get checkbox item
            if checkbox_item.checkState() == Qt.Checked:
                # If the checkbox is checked, get the corresponding text from the second column
                item_name = self.model.item(row, 1).text()
                selected_items.append(item_name)

        # Print or show the selected items (can also use QMessageBox to display)
        if not selected_items:
            QMessageBox.warning(self, "No Selections", "Please select at least one model.")
            return

        tableheader = ["Model", "Tokens", "Speed (t/s)", "StopReason"]
        additional_data_model = QStandardItemModel()
        additional_data_model.setHorizontalHeaderLabels(tableheader)

        datalist = [tableheader]
        # Populate the additional data table with details
        for item in selected_items:
            result_dict = lm_studio_interface.tokenspeed(item)
            datalist.append([item,result_dict["tokens"],result_dict["speed"],result_dict["stop"]])
            
            # convert results to strings for table
            dict_strings = {k: str(v) for k, v in result_dict.items()}
            row = [QStandardItem(item), 
                   QStandardItem(dict_strings["tokens"]), 
                   QStandardItem(dict_strings["speed"]), 
                   QStandardItem(dict_strings["stop"])]
            additional_data_model.appendRow(row)

        filename = 'tokenbench'
        benchexport.export_csv(filename, datalist)
        # Create a table view to display the additional data
        additional_table_view = QTableView()
        additional_table_view.setModel(additional_data_model)

        # Set up a separate layout for displaying selected items and their details
        details_label = QLabel("Details of Selected Items:")
        details_layout = QVBoxLayout()
        details_layout.addWidget(details_label)
        details_layout.addWidget(additional_table_view)

        details_widget = QWidget()
        details_widget.setLayout(details_layout)

        # Adjust window size to accommodate both tables
        self.setCentralWidget(details_widget)
        self.resize(800, 600)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LMSpeedometer()
    window.show()
    sys.exit(app.exec())
