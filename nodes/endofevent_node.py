from PySide6 import QtWidgets

from node_editor.node import Node
from nodes.common_widgets import TextLineEdit


class end_of_event_Node(Node):
    def __init__(self):
        super().__init__()

        self.title_text = "End of Event"
        self.type_text = "REQUIRED"
        self.set_color(title_color=(255, 165, 0))

        self.add_pin(name="input", is_output=False, execution=True)

        self.build()
