from node_editor.node import Node


class text_Node(Node):
    def __init__(self):
        super().__init__()

        self.title_text = "Text"
        self.type_text = "XML Nodes"
        self.set_color(title_color=(255, 0, 0))

        self.add_pin(name="Ex In", is_output=False, execution=True)
        self.add_pin(name="Ex Out", is_output=True, execution=True)

        self.add_pin(name="Text Output", is_output=True)
        self.build()