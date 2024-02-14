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

        self.add_pin(name="event_contain", is_output=True, execution=True)
        self.add_pin(name="Start Node Connection", is_output=False, execution=True)

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
    def setinternaldata(self):
        self.scaler_line.setText(self.internaldata["text"])
        self.isunique.setChecked(self.internaldata["isunique"])
        
    def setdata(self):
        self.internaldata["text"] = self.scaler_line.text()
        self.internaldata["isunique"] = self.isunique.isChecked()
         
