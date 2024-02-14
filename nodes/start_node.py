from PySide6 import QtWidgets

from node_editor.node import Node
from nodes.common_widgets import TextLineEdit


class start_Node(Node):
    def __init__(self):
        super().__init__()

        self.title_text = "Start"
        self.type_text = "REQUIRED"
        self.set_color(title_color=(255, 165, 0))

        self.add_pin(name="output", is_output=True, execution=True)

        self.build()
