from PySide6 import QtWidgets, QtGui, QtCore

from node_editor.node import Node
from Example_Project.common_widgets import TextLineEdit, checkbox


class Reward_Node(Node):
    def __init__(self):
        super().__init__()

        self.title_text = "Reward"
        self.type_text = "container"
        self.set_color(title_color=(0, 128, 0))
        self.add_pin(name="Input", is_output=False)
        self.add_pin(name="Output", is_output=True)

        self.reward_types = ["Scrap", "Fuel", "Drone Parts", "Missiles"]

        self.build()

    def init_widget(self):
        self.widget = QtWidgets.QWidget()
        self.widget.setFixedWidth(150)
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.type_label = QtWidgets.QLabel("Type:")
        layout.addWidget(self.type_label)

        self.reward_type_dropdown = QtWidgets.QComboBox()
        self.reward_type_dropdown.addItems(self.reward_types)
        layout.addWidget(self.reward_type_dropdown)

        self.amount_label = QtWidgets.QLabel("Amount:")
        layout.addWidget(self.amount_label)

        self.amount_input = QtWidgets.QSpinBox()
        self.amount_input.setMinimum(0)
        self.amount_input.setMaximum(1000)
        layout.addWidget(self.amount_input)

        self.widget.setLayout(layout)

        proxy = QtWidgets.QGraphicsProxyWidget()
        proxy.setWidget(self.widget)
        proxy.setParentItem(self)

        super().init_widget()

    def to_dict(self):
        node_dict = super().to_dict()
        node_dict["reward_type"] = self.reward_type_dropdown.currentText()
        node_dict["amount"] = self.amount_input.value()
        return node_dict

    def from_dict(self, node_dict):
        super().from_dict(node_dict)
        reward_type = node_dict.get("reward_type", "")
        if reward_type in self.reward_types:
            index = self.reward_types.index(reward_type)
            self.reward_type_dropdown.setCurrentIndex(index)

        amount = node_dict.get("amount", 0)
        self.amount_input.setValue(amount)


# Usage: self.register_node_class(RewardNode)
