import sys
from PySide6.QtWidgets import QHeaderView, QApplication, QMainWindow, QTableView, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QMessageBox, QLabel, QDialog
from PySide6.QtCore import Qt, QThread, Signal, Slot
from PySide6.QtGui import QStandardItemModel, QStandardItem, QFont
from functools import partial

import lm_studio_interface
import benchexport

class Worker(QThread):
    """ This worker does the benchmark in a seperate thread from the GUI """
    finished_signal = Signal(str,list)  # emit elapsed seconds

    def __init__(self, task, selected_items):
        super().__init__()
        self.task = task
        self.selected_items = selected_items
        self._running = True

    def run(self):
        '''Checks the Becnhmark Selection '''
        
        if self.task == 'ssd':
            datalist = self.llm_loading_test()
        elif self.task != 'ssd':
            datalist = self.token_test(self.task)

        self.finished_signal.emit(self.task,datalist)

    def stop(self):
        self._running = False

    def llm_loading_test(self):
        ''' Benches the model loading time '''

        #Return if no model was selected
        if not self.selected_items:
            return

        tableheader = ["Model", "Time (s)", "Size (MB)", "Speed (MB/s)"]
        datalist = [tableheader]
        for item in self.selected_items:
            result_dict = app_window.benchmarks.model_loading_test(item)
            datalist.append([item,result_dict["duration"],result_dict["size"],result_dict["transfer"]])

        filename = 'drivebench'
        benchexport.export_csv(filename, datalist)
        return datalist

    def token_test(self, length):
        ''' Benches the model speed in token per second '''

        #Return if no model was selected
        if not self.selected_items:
            return

        tableheader = ["Model", "Tokens", "Speed (t/s)", "StopReason"]
        datalist = [tableheader]
        resultlist = ["Model","Result"]
        for item in self.selected_items:
            result_dict = app_window.benchmarks.tokenspeed(item,length)
            datalist.append([item,result_dict["tokens"],result_dict["speed"],result_dict["stop"]])
            resultlist.append([item,result_dict["result"]])

        filename_token = f'tokenbench_{length}'
        filename_result = f'resultbench_{length}'
        benchexport.export_csv(filename_token, datalist)
        # benchexport.export_csv(filename_result, resultlist)
        return datalist

class ResultDialog(QDialog):
    """ Shows the Benchmark Result in a new QDialog window """
    def __init__(self, task: str, datalist: list, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Benchmark Result {task}")
        self.setModal(True)
        self.setGeometry(100, 100, 444, 400)
        result_layout = QVBoxLayout(self)
        # table_layout = QHBoxLayout(self)

        additional_data_model = QStandardItemModel()

        for sublist in datalist:
            # convert results to strings for table
            datalist_strings = [str(value) for value in sublist]
            row = [QStandardItem(datalist_strings[0]), 
                    QStandardItem(datalist_strings[1]), 
                    QStandardItem(datalist_strings[2]), 
                    QStandardItem(datalist_strings[3])]
            additional_data_model.appendRow(row)

        # Create a table view to display the result data
        additional_table_view = QTableView()
        additional_table_view.setModel(additional_data_model)
        result_layout.addWidget(additional_table_view)
        
        btn_close = QPushButton("Close", self)
        btn_close.clicked.connect(self.accept)      
  
        # result_layout.addLayout(table_layout)
        result_layout.addWidget(btn_close)
        

class LMSpeedometer(QMainWindow):
    """ This is the main GUI class.
        It includes user interaction buttons and shows the LLMs available for benchmarking
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LM Speedometer")
        # store per-button worker references to avoid GC and to track running state
        self.workers = {}  # per-button worker references
        self.benchbuttons = [] # list of buttons for easy enable/disable

        #check LM Studio Conenction
        lm_connection = False
        try:
            self.benchmarks = lm_studio_interface.LmBenchmarks()
            lm_connection = True
        except Exception as e:
            self.create_lm_connection_error(e)
            return

        #if connection, create main window
        if lm_connection:
            self.create_main_window()

    def create_lm_connection_error(self, error_message):
        ''' Shows error message if app can't connect to LM Studio '''
        layout = QVBoxLayout(self)
        message = QLabel(f"{error_message}")
        layout.addWidget(message)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        
        self.setCentralWidget(central_widget)

    def create_main_window(self):
        ''' Creates the main window '''
        self.setGeometry(100, 100, 600, 400)

        # Create a standard item model to hold the data
        self.model = QStandardItemModel()

        # Add columns (1 for checkboxes and another one for item names)
        self.model.setHorizontalHeaderLabels(["Select", "Model","Status"])

        # Example items
        models = self.benchmarks.load_available_models()

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

        # Add LLM Selection Buttons
        select_all_button = QPushButton("Select All")
        unselect_all_button = QPushButton("UnSelect All")
        select_all_button.clicked.connect(self.select_all_items)
        unselect_all_button.clicked.connect(self.unselect_all_items)

        # Add a benchmark buttons
        ssd_button = QPushButton("LLM Loading Test")

        token_header_layout = QHBoxLayout()
        header_label = QLabel("Token Test")
        token_header_layout.addStretch()  # Add stretch to push content to the center
        token_header_layout.addWidget(header_label)
        token_header_layout.addStretch()  # Add another stretch to balance it

        token_button_layout = QHBoxLayout()
        token_button_short = QPushButton("Short")
        token_button_medium = QPushButton("Medium")
        token_button_long = QPushButton("Long")

        token_button_layout.addWidget(token_button_short)
        token_button_layout.addWidget(token_button_medium)
        token_button_layout.addWidget(token_button_long)

        self.benchbuttons.append(ssd_button)
        self.benchbuttons.append(token_button_short)
        self.benchbuttons.append(token_button_medium)
        self.benchbuttons.append(token_button_long)

        ssd_button.clicked.connect(partial(self.bench_button_clicked,'ssd', ssd_button))
        token_button_short.clicked.connect(partial( self.bench_button_clicked,'short', token_button_short))
        token_button_medium.clicked.connect(partial(self.bench_button_clicked,'medium', token_button_medium))
        token_button_long.clicked.connect(partial(self.bench_button_clicked,'long', token_button_long))

        # Layout setup
        main_layout = QVBoxLayout()
        main_layout.addWidget(unselect_all_button)
        main_layout.addWidget(select_all_button)

        main_layout.addWidget(self.table_view)
        main_layout.addWidget(ssd_button)
        main_layout.addLayout(token_header_layout)
        main_layout.addLayout(token_button_layout)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        
        self.setCentralWidget(central_widget)

    @Slot()
    def bench_button_clicked(self,task, button: QPushButton):
        ''' Disables all benchmark buttons after a benchmark is started '''
        # If any worker is running, ignore (shouldn't happen if we disabled)
        if any(w.isRunning() for w in self.workers.values()):
            return

        # Set all buttons to busy/disabled
        self.set_all_buttons_busy(True, active_button=button)

        selected_items = self.get_selected_items()
        worker = Worker(task, selected_items)
        worker.finished_signal.connect(partial(self.on_task_finished, button))
        self.workers[button] = worker
        worker.start()

    @Slot(object, float)
    def on_task_finished(self, button: QPushButton, task: str, datalist: list):
        ''' Renenabes becnhmark buttons after task is finished, calls ResultDialog '''
        # Clean up worker
        worker = self.workers.get(button)
        if worker:
            worker.quit()
            worker.wait()
            del self.workers[button]

        # Re-enable all buttons and restore texts/styles
        self.set_all_buttons_busy(False)

        #don't show result Dialog for a non Bench
        if not datalist:
            return

        # Show result dialog (non-blocking)
        dlg = ResultDialog(task, datalist, parent=self)
        dlg.show()

    def set_all_buttons_busy(self, busy: bool, active_button: QPushButton | None = None):
        ''' Disables/Enables benchmark buttons '''
        if busy:
            for btn in self.benchbuttons:
                # show which one started the work
                if btn is active_button:
                    btn.setText(f"{btn.text()} (Active...)")
                else:
                    btn.setText(btn.text())  # keep label; could add suffix if desired
                btn.setStyleSheet("background-color: #d9534f; color: white;")
                btn.setEnabled(False)
        else:
            for btn in self.benchbuttons:
                # remove suffix if present
                btn.setText(btn.text().replace(" (Active...)", ""))
                btn.setStyleSheet("")
                btn.setEnabled(True)

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
        ''' Selects all available models '''
        for row in range(self.model.rowCount()):
            checkbox_item = self.model.item(row, 0)  # Get checkbox item
            checkbox_item.setCheckState(Qt.Checked)

    def unselect_all_items(self):
        ''' Unselects all available models '''
        for row in range(self.model.rowCount()):
            checkbox_item = self.model.item(row, 0)  # Get checkbox item
            checkbox_item.setCheckState(Qt.Unchecked)

    def get_selected_items(self):
        ''' get selected model for benchmark, shows error if none '''
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

        return selected_items

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app_window = LMSpeedometer()
    app_window.show()
    sys.exit(app.exec())
