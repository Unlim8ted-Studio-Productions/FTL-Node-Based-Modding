from node_editor.connection import Connection
from node_editor.pin import Pin
from node_editor.node import Node
from PySide6.QtWidgets import QGraphicsProxyWidget


def convert_to_readable_list(node_data):
    """Converts a given node data into a readable list of dictionaries containing relevant information about each item.
    Parameters:
        - node_data (list): A list of items to be converted into a readable list.
    Returns:
        - readable_list (list): A list of dictionaries containing relevant information about each item in the given node data.
    Processing Logic:
        - Extracts relevant data from QGraphicsProxyWidget, Pin, Node, and Connection objects.
        - If an item is not one of the specified types, it is added to the list as an "Unknown" type with its string representation.
        - The returned list contains dictionaries with the following keys: "type", "parent", "position", "flags", "title", "source", and "target".
        - The "type" key specifies the type of the item.
        - The "parent" key specifies the parent of the item, if applicable.
        - The "position" key specifies the position of the item.
        - The "flags" key specifies the flags of the item.
        - The "title" key specifies the title text of a Node.
        - The "source" key specifies the title text of the source Node of a Connection.
        - The "target" key specifies the title text of the target Node of a Connection.
    Example:
        Given the following node data:
        [QGraphicsProxyWidget, Pin, Node, Connection, "Unknown"]
        The function would return the following readable list:
        [
            {"type": "QGraphicsProxyWidget", "parent": "parent_name", "position": (x, y)},
            {"type": "Pin", "parent": "parent_name", "position": (x, y), "flags": "flags"},
            {"type": "Node", "title": "node_title", "position": (x, y), "flags": "flags"},
            {"type": "Connection", "source": "source_node_title", "target": "target_node_title", "flags": "flags"},
            {"type": "Unknown", "info": "Unknown"}
        ]"""
    readable_list = []

    for item in node_data:
        if isinstance(item, QGraphicsProxyWidget):
            # Extract relevant data from QGraphicsProxyWidget
            widget_data = {
                "type": "QGraphicsProxyWidget",
                "parent": str(item.parent()),
                "position": (item.pos().x(), item.pos().y()),
            }
            readable_list.append(widget_data)

        elif isinstance(item, Pin):
            # Extract relevant data from Pin
            pin_data = {
                "type": "Pin",
                "parent": str(item.parent()),
                "position": (item.pos().x(), item.pos().y()),
                "flags": str(item.flags()),
            }
            readable_list.append(pin_data)

        elif isinstance(item, Node):
            # Extract relevant data from Node
            node_data = {
                "type": "Node",
                "title": getattr(item, "title_text", ""),
                "position": (item.pos().x(), item.pos().y()),
                "flags": str(item.flags()),
            }
            readable_list.append(node_data)

        elif isinstance(item, Connection):
            # Extract relevant data from Connection
            connection_data = {
                "type": "Connection",
                "source": str(item.source.node.title_text if item.source else None),
                "target": str(item.target.node.title_text if item.target else None),
                "flags": str(item.flags()),
            }
            readable_list.append(connection_data)

        else:
            readable_list.append({"type": "Unknown", "info": str(item)})

    return readable_list


def object_to_dict(obj):
    # This function tries to convert an object into a dictionary format.
    obj_dict = {"type": type(obj).__name__, "attributes": {}}

    # Try to extract common attributes.
    try:
        obj_dict["attributes"]["position"] = (obj.x(), obj.y())
    except AttributeError:
        pass

    try:
        obj_dict["attributes"]["parent"] = str(obj.parent())
    except AttributeError:
        pass

    try:
        obj_dict["attributes"]["flags"] = obj.flags()
    except AttributeError:
        pass

    # Add custom attributes based on the type of object.
    if isinstance(obj, Pin):
        obj_dict["attributes"]["connected"] = [str(c) for c in obj.connections]

    elif isinstance(obj, Node):
        obj_dict["attributes"]["title_text"] = obj.title_text

    elif isinstance(obj, Connection):
        obj_dict["attributes"]["source"] = str(obj.source)
        obj_dict["attributes"]["target"] = str(obj.target)

    return obj_dict


def convert_objects_to_readable_list(objects):
    return [object_to_dict(obj) for obj in objects]



# The list of nodes and connections
readable_list = convert_objects_to_readable_list(your_node_data)

for item in readable_list:
    print(item)
