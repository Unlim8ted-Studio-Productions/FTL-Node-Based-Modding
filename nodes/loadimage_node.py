from PySide6 import QtWidgets

from node_editor.node import Node
from nodes.common_widgets import TextLineEdit


class loadimage_Node(Node):
    def __init__(self):
        super().__init__()

        self.title_text = "Load Image"
        self.type_text = "image"
        self.set_color(title_color=(255, 165, 0))

        self.add_pin(name="img location", is_output=True, execution=True)

        self.build()

    def init_widget(self):
        self.widget = QtWidgets.QWidget()
        self.widget.setFixedWidth(100)
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.scaler_line = TextLineEdit()
        layout.addWidget(self.scaler_line)
        self.widget.setLayout(layout)

        proxy = QtWidgets.QGraphicsProxyWidget()
        proxy.setWidget(self.widget)
        proxy.setParentItem(self)

        super().init_widget()
