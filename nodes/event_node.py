from node_editor.node import Node
from PySide6 import QtWidgets

from node_editor.node import Node
from nodes.common_widgets import TextLineEdit, checkbox


class event_Node(Node):
    def __init__(self):
        super().__init__()

        self.title_text = "Event"
        self.type_text = "container"
        self.set_color(title_color=(255, 165, 0))

        self.add_pin(name="event_contain", is_output=True)

        self.build()

    def init_widget(self):
        self.widget = QtWidgets.QWidget()
        self.widget.setFixedWidth(100)
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.scaler_line = TextLineEdit()
        self.namelabel = QtWidgets.QLabel("name:")
        layout.addWidget(self.namelabel)
        layout.addWidget(self.scaler_line)
        self.label = QtWidgets.QLabel("is unique:")
        layout.addWidget(self.label)
        self.isunique = checkbox()
        layout.addWidget(self.isunique)
        self.widget.setLayout(layout)

        proxy = QtWidgets.QGraphicsProxyWidget()
        proxy.setWidget(self.widget)
        proxy.setParentItem(self)

        super().init_widget()
