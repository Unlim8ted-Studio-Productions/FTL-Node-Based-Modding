from PySide6 import QtWidgets

from node_editor.node import Node
from nodes.common_widgets import TextLineEdit


class loadsound_Node(Node):
    def __init__(self):
        super().__init__()

        self.title_text = "Load Sound"
        self.type_text = "Audio"
        self.set_color(title_color=(255, 165, 0))

        self.add_pin(name="Audio", is_output=True)

        self.build()

    def init_widget(self):
        self.widget = QtWidgets.QWidget()
        self.widget.setFixedWidth(100)
        layout = QtWidgets.QVBoxLayout()        # Create a button to open the file dialog
        self.open_button = QtWidgets.QPushButton("Open File")
        self.open_button.clicked.connect(self.open_file_dialog)

        # Create a text edit widget to display the selected file path
        self.file_path_textedit = ()
        self.file_path_textedit.setReadOnly(True)

        # Create a layout to organize the widgets
        layout.addWidget(self.open_button)
        layout.addWidget(self.file_path_textedit)
        self.widget.setLayout(layout)
        
        proxy = QtWidgets.QGraphicsProxyWidget()
        proxy.setWidget(self.widget)
        proxy.setParentItem(self)
        
        super().init_widget()

    def open_file_dialog(self):
        file_dialog = QtWidgets.QFileDialog(self)
        file_dialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)
        file_dialog.setNameFilter("All Files (*.*)")

        if file_dialog.exec_():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                file_path = selected_files[0]
                self.file_path_textedit.setPlainText(file_path)