import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSpacerItem, QSizePolicy

class MyWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Create the header row using a horizontal box layout with center alignment
        header_layout = QHBoxLayout()
        header_label = QLabel("Header Row")
        
        # Center align items in the header layout
        header_layout.addStretch()  # Add stretch to push content to the center
        header_layout.addWidget(header_label)
        header_layout.addStretch()  # Add another stretch to balance it

        # Create the button row using another horizontal box layout
        button_row_layout = QHBoxLayout()
        
        for i in range(3):
            button = QPushButton(f"Button {i+1}")
            button_row_layout.addWidget(button)

        # Combine both layouts vertically
        main_layout = QVBoxLayout(self)
        
        # Add center alignment for the header
        main_layout.addLayout(header_layout)  # Add the centered header row to the main layout
        
        # Add a spacer before and after the buttons if you want them centered vertically as well
        main_layout.addStretch()  
        main_layout.addLayout(button_row_layout)
        main_layout.addStretch()

        self.setLayout(main_layout)

def main():
    app = QApplication(sys.argv)
    window = MyWindow()
    window.setWindowTitle("PySide6 Example")
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
