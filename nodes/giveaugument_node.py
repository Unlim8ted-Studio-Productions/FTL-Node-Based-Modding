from PySide6 import QtWidgets, QtGui, QtCore

from node_editor.node import Node
from nodes.common_widgets import TextLineEdit, checkbox


class giveaugument_Node(Node):
    def __init__(self):
        super().__init__()

        self.title_text = "give augument"
        self.type_text = "Items"
        self.set_color(title_color=(0, 128, 0))
        self.add_pin(name="Input", is_output=False, execution=True)
        self.add_pin(name="Output", is_output=True, execution=True)

        self.reward_types = ["RANDOM"]

        self.build()

    def init_widget(self):
        self.widget = QtWidgets.QWidget()
        self.widget.setFixedWidth(150)
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.type_label = QtWidgets.QLabel("Augument (do RANDOM for random augument):")
        layout.addWidget(self.type_label)

        self.amount_input = TextLineEdit()
        layout.addWidget(self.amount_input)

        self.widget.setLayout(layout)

        proxy = QtWidgets.QGraphicsProxyWidget()
        proxy.setWidget(self.widget)
        proxy.setParentItem(self)

        super().init_widget()

    def to_dict(self):
        node_dict = super().to_dict()
        node_dict["amount"] = self.amount_input.value()
        return node_dict

    def from_dict(self, node_dict):
        super().from_dict(node_dict)
        amount = node_dict.get("amount", 0)
        self.amount_input.setText(amount)

    def setinternaldata(self):
        self.amount_input.setText(self.internaldata["amount"])
        
    def setdata(self):
        
        self.internaldata["amount"] = self.amount_input.text()


         

# Usage: self.register_node_class(RewardNode)
