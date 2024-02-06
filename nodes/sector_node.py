from node_editor.node import Node
class sector_Node(Node):
    def __init__(self):
        super().__init__()

        self.title_text = "sector"
        self.type_text = "output"
        self.set_color(title_color=(0, 128, 0))

        self.add_pin(name="string", is_output=True, data_type="String")
        self.build()