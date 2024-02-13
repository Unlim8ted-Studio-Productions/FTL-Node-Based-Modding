from node_editor.node import Node

class store_Node(Node):
    def __init__(self):
        super().__init__()

        self.title_text = "Store"
        self.type_text = "XML Nodes"
        self.set_color(title_color=(255, 0, 0))

        self.add_pin(name="Ex In", is_output=False, execution=True)
        self.add_pin(name="Ex Out", is_output=True, execution=True)



# Add more node classes for different XML tags

# Example usage:
# event_node = EventNode()
# choice_node = ChoiceNode()
# text_node = TextNode()
# play_sound_node = PlaySoundNode()
