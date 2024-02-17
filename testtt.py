import xml.etree.ElementTree as ET

def parse_xml_to_nodes(xml_string):
    root = ET.fromstring(xml_string)
    nodes = []
    connections = []
    
    def parse_node(node_elem, parent_id=None):
        node = {"type": node_elem.tag, "internal-data": {}}
        
        if node_elem.tag == "event":
            node["internal-data"]["text"] = node_elem.get("name")
            node["internal-data"]["isunique"] = node_elem.get("unique")
        elif node_elem.tag == "text":
            node["internal-data"]["text"] = node_elem.text
        elif node_elem.tag == "playSound":
            node["internal-data"]["filepath"] = node_elem.text
        elif node_elem.tag == "ship":
            node["internal-data"]["text"] = node_elem.get("name")
            node["internal-data"]["ishostile"] = node_elem.get("hostile") == "True"
            node["internal-data"]["autoblueprint"] = node_elem.get("auto_blueprint")
        
        node_id = node_elem.get("uuid")
        nodes.append(node)
        
        if parent_id is not None:
            connections.append({"start_id": parent_id, "end_id": node_id, "start_pin": "Ex Out", "end_pin": "Ex In"})
        
        for child in node_elem.findall("*"):
            parse_node(child, parent_id=node_id)
    
    parse_node(root)
    
    return {"nodes": nodes, "connections": connections}

def convert_xml_to_json(xml_string):
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

# Convert XML to JSON
json_data = convert_xml_to_json(xml_string)

# Print JSON data
print(json.dumps(json_data, indent=4))
