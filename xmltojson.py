import json
import uuid
import xml.etree.ElementTree as ET

def parse_xml_to_nodes(xml_string):
    root = ET.fromstring(xml_string)
    nodes = []
    connections = []
    
    def parse_node(node_elem, parent_id=None, current_x=0, current_y=0):
        node_type = node_elem.tag
        text = node_elem.text
        internal_data = {}
        
        # Calculate x and y coordinates based on the number of nodes
        if node_type != "choice":
            x = current_x
            y = current_y
            current_x += 200  # Move horizontally for the next node
        else:
            x = current_x
            y = current_y + 200  # Move vertically down for the choice node
        
        node_uuid = str(uuid.uuid4())
        
        # Populate internal data based on node type
        if node_type == "event":
            internal_data = {"text": node_elem.get("name", ""), "isunique": node_elem.get("unique", False)}
            node_type = "event_Node"
        elif node_type == "text":
            internal_data = {"text": text}
            node_type = "text_Node"
        elif node_type == "choice":
            internal_data = {}
            node_type = "choice_Node"
        
        node = {
            "type": node_type,
            "x": x,
            "y": y,
            "uuid": node_uuid,
            "internal-data": internal_data
        }
        
        # Add node to the list
        nodes.append(node)
        
        # Add connection if parent exists
        if parent_id is not None:
            connections.append({"start_id": parent_id, "end_id": node_uuid, "start_pin": "Ex Out", "end_pin": "Ex In"})
        
        # Recursive call for children nodes
        for child in node_elem.findall("*"):
            parse_node(child, parent_id=node_uuid, current_x=current_x, current_y=current_y)
    
    parse_node(root)
    
    return {"nodes": nodes, "connections": connections}

def convert_xml_to_json(xml_string):
    #print(xml_string)
    nodes_data = parse_xml_to_nodes(xml_string)
    return nodes_data

# Example XML string
xml_string = """
<FTL>
    <unknown/>
    <event name="example" unique="True">
        <text>A zoltan ship hails you</text>
        <choice>
            <text>Tell them about your mission and ask for supplies</text>
            <event>
                <text>They give you some supplies to help you on your quest</text>
                <item type="scrap" amount="20"/>
            </event>
        </choice>
        <choice>
            <text>attack!</text>
            <event>
                <playSound>cheztax</playSound>
                <ship name="enemy-zoltan" auto_blueprint=""/>
                <ship load="enemy-zoltan" hostile="True"/>
            </event>
        </choice>
    </event>
</FTL>
"""

if __name__ == "__main__":
    # Convert XML to JSON
    json_data = convert_xml_to_json(xml_string)

    # Print JSON data
    print(json.dumps(json_data, indent=4))