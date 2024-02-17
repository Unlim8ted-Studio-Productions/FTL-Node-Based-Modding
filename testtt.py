import json
from xml.dom.minidom import parseString

a = {
    "nodes": [
        {
            "type": "end_branch_Node",
            "x": 5853,
            "y": 4891,
            "uuid": "095004db-9151-4375-ac7a-6d2d36c6279f",
            "internal-data": {}
        },
        {
            "type": "end_branch_Node",
            "x": 5906,
            "y": 4702,
            "uuid": "b1e6bcb1-bc01-440f-bcfb-1c7493944f4f",
            "internal-data": {}
        },
        {
            "type": "Reward_Node",
            "x": 5734,
            "y": 4725,
            "uuid": "468cf1dc-4d15-46a9-958f-1b27b7353820",
            "internal-data": {
                "amount": 20,
                "index": 0
            }
        },
        {
            "type": "text_Node",
            "x": 5551,
            "y": 4751,
            "uuid": "4142a167-4f62-469a-967a-6814ca3c4fc3",
            "internal-data": {
                "text": "They give you some supplies to help you on your quest"
            }
        },
        {
            "type": "loadship_Node",
            "x": 5699,
            "y": 4947,
            "uuid": "b73ad069-3b0f-49ee-aca9-9af33beee56c",
            "internal-data": {
                "text": "enemy-zoltan",
                "ishostile": False,
                "autoblueprint": ""
            }
        },
        {
            "type": "loadsound_Node",
            "x": 5348,
            "y": 5098,
            "uuid": "bf6b87c6-1d23-4a20-b5a8-34ccd36ffdf1",
            "internal-data": {
                "filepath": ""
            }
        },
        {
            "type": "playsound_Node",
            "x": 5514,
            "y": 4927,
            "uuid": "a3e094c7-a188-443e-8a72-b4dd6199f1eb",
            "internal-data": {}
        },
        {
            "type": "text_Node",
            "x": 5353,
            "y": 4952,
            "uuid": "11e6b28e-0473-487f-8480-0069fd412c47",
            "internal-data": {
                "text": "attack!"
            }
        },
        {
            "type": "text_Node",
            "x": 5380,
            "y": 4778,
            "uuid": "70ca10c1-dbe8-4673-9e5c-3dce08666aa6",
            "internal-data": {
                "text": "Tell them about your mission and ask for supplies"
            }
        },
        {
            "type": "text_Node",
            "x": 4973,
            "y": 4869,
            "uuid": "a0e8222a-ff19-498f-8c29-93e2f4257e2b",
            "internal-data": {
                "text": "A zoltan ship hails you"
            }
        },
        {
            "type": "event_Node",
            "x": 4814,
            "y": 4920,
            "uuid": "23e4b45c-461f-4a65-a112-5af01b77df81",
            "internal-data": {
                "text": "example",
                "isunique": True
            }
        },
        {
            "type": "choice_Node",
            "x": 5155,
            "y": 4866,
            "uuid": "2228cbfa-8029-478c-9d62-dc4685a866ae",
            "internal-data": {}
        },
        {
            "type": "start_Node",
            "x": 4571,
            "y": 4897,
            "uuid": "5254dc4a-da3a-4f64-a5d0-f43d57f6e084",
            "internal-data": {}
        }
    ],
    "connections": [
        {
            "start_id": "b73ad069-3b0f-49ee-aca9-9af33beee56c",
            "end_id": "095004db-9151-4375-ac7a-6d2d36c6279f",
            "start_pin": "Ex Out",
            "end_pin": "input"
        },
        {
            "start_id": "468cf1dc-4d15-46a9-958f-1b27b7353820",
            "end_id": "b1e6bcb1-bc01-440f-bcfb-1c7493944f4f",
            "start_pin": "Output",
            "end_pin": "input"
        },
        {
            "start_id": "2228cbfa-8029-478c-9d62-dc4685a866ae",
            "end_id": "11e6b28e-0473-487f-8480-0069fd412c47",
            "start_pin": "Choice Output1",
            "end_pin": "Ex In"
        },
        {
            "start_id": "2228cbfa-8029-478c-9d62-dc4685a866ae",
            "end_id": "70ca10c1-dbe8-4673-9e5c-3dce08666aa6",
            "start_pin": "Choice Output0",
            "end_pin": "Ex In"
        },
        {
            "start_id": "a0e8222a-ff19-498f-8c29-93e2f4257e2b",
            "end_id": "2228cbfa-8029-478c-9d62-dc4685a866ae",
            "start_pin": "Ex Out",
            "end_pin": "Ex In"
        },
        {
            "start_id": "23e4b45c-461f-4a65-a112-5af01b77df81",
            "end_id": "a0e8222a-ff19-498f-8c29-93e2f4257e2b",
            "start_pin": "event_contain",
            "end_pin": "Ex In"
        },
        {
            "start_id": "70ca10c1-dbe8-4673-9e5c-3dce08666aa6",
            "end_id": "4142a167-4f62-469a-967a-6814ca3c4fc3",
            "start_pin": "Ex Out",
            "end_pin": "Ex In"
        },
        {
            "start_id": "11e6b28e-0473-487f-8480-0069fd412c47",
            "end_id": "a3e094c7-a188-443e-8a72-b4dd6199f1eb",
            "start_pin": "Ex Out",
            "end_pin": "Ex In"
        },
        {
            "start_id": "bf6b87c6-1d23-4a20-b5a8-34ccd36ffdf1",
            "end_id": "a3e094c7-a188-443e-8a72-b4dd6199f1eb",
            "start_pin": "Audio",
            "end_pin": "AudioFile"
        },
        {
            "start_id": "a3e094c7-a188-443e-8a72-b4dd6199f1eb",
            "end_id": "b73ad069-3b0f-49ee-aca9-9af33beee56c",
            "start_pin": "Ex Out",
            "end_pin": "Ex In"
        },
        {
            "start_id": "4142a167-4f62-469a-967a-6814ca3c4fc3",
            "end_id": "468cf1dc-4d15-46a9-958f-1b27b7353820",
            "start_pin": "Ex Out",
            "end_pin": "Input"
        },
        {
            "start_id": "5254dc4a-da3a-4f64-a5d0-f43d57f6e084",
            "end_id": "23e4b45c-461f-4a65-a112-5af01b77df81",
            "start_pin": "output",
            "end_pin": "Start Node Connection"
        }
    ]
}

def convert_connections(nodes: list, connections: list):
    converted_data = []
    for node in nodes:
        for connection in connections:
            if connection["start_id"] == node["uuid"]:
                if not "connection" in node:
                    node["connections"] = {}
                    node["connections"]["start_id"] = []
                    node["connections"]["end_id"] = []
                    node["connections"]["start_pin"] = []
                    node["connections"]["end_pin"] = []
                node["connections"]["start_id"].append(connection["start_id"])
                node["connections"]["end_id"].append(connection["end_id"])
                node["connections"]["start_pin"].append(connection["start_pin"])
                node["connections"]["end_pin"].append(connection["end_pin"])
    converted_data=nodes
    #print(json.dumps(converted_data,indent=4))
    return converted_data

def find_previous_node(scene, uuid, newscene):
    connections = scene["connections"]
    for connection in connections:
        if connection["end_id"] == uuid:
            for s in newscene:
                if s["uuid"] == connection["start_id"]:
                    return s
    return None

def convert_node_to_xml(node, nodes, uuid):
    node_type = node["type"]
    internal_data = node["internal-data"]
    
    if node_type == "choice_Node":
        return ""
    elif node_type == "event_Node":
        return f"<event name='{internal_data['text']}' unique='{internal_data['isunique']}'></event>"
    elif node_type == "text_Node":
        if find_previous_node(a, uuid, nodes)["type"] == "choice_Node":
            return f"<choice><text>{internal_data['text']}</text><event>"
        return f"<text>{internal_data['text']}</text>"
    elif node_type == "playsound_Node":
        return "<playSound></playSound>"
    elif node_type == "quest_Node":
        places = ["RANDOM", "LAST", "NEXT"]
        beacon = places[internal_data["index"]]
        return f"<quest beacon='{beacon}' event='{internal_data['text']}'></quest>"
    elif node_type == "loadship_Node":
        return f"<ship name='{internal_data['text']}' auto_blueprint='{internal_data.get('autoblueprint')}'></ship><ship>load='{internal_data.get('text')}' hostile='{internal_data.get('ishostile')}'</ship>"
    elif node_type == "item_modify_Node":
        return "<item_modify></item_modify>"
    elif node_type == "Reward_Node":
        reward_types = ["scrap", "fuel", "drones", "missiles"]
        reward_type = reward_types[internal_data["index"]]
        return f"<item type='{reward_type}' amount='{internal_data['amount']}'></item>"
    elif node_type == "Damage_Node":
        effects = ["random", "all", "fire"]
        effect = effects[internal_data["Effect"]]
        return f"<damage amount='{internal_data['text']}' system='{internal_data['System']}' effect='{effect}'></damage>"
    elif node_type == "giveweapon_Node":
        return f"<weapon name='{internal_data['amount']}'></weapon>"
    elif node_type == "giveaugument_Node":
        return f"<augument name='{internal_data['amount']}'></augument>"
    elif node_type == "status":
        return "<status type='limit' target='player' system='sensors' amount='1'></status>"
    elif node_type == "autoReward":
        return "<autoReward></autoReward>"
    elif node_type == "surrender":
        return "<surrender chance='0' min='3' max='4'></surrender>"
    elif node_type == "store_Node":
        return "<store></store>"
    else:
        return "<unknown></unknown>"

def convert_to_xml(nodes):
    xml_output = "<FTL>"
    
    # Iterate through nodes
    for node in nodes:
        if node["type"] != "end_branch_Node":
            xml_output += convert_node_to_xml(node, nodes, node["uuid"])
        else:
            xml_output += "</event></choice>"

    xml_output += "</FTL>"
    print(xml_output)
    return xml_output

def sort_nodes_based_on_connections(nodes, connections):
    # Create a dictionary to store the graph
    graph = {node["uuid"]: [] for node in nodes}
    uuidtonode={}
    for node in nodes:
        uuidtonode[node["uuid"]] = node
    # Populate the graph based on connections
    for connection in connections:
        start_id = connection["start_id"]
        end_id = connection["end_id"]
        graph[start_id].append(end_id)

    # Perform topological sorting
    visited = set()
    sorted_nodes = []

    def dfs(node_id):
        if node_id not in visited:
            visited.add(node_id)
            for neighbor_id in graph[node_id]:
                dfs(neighbor_id)
            sorted_nodes.append(node_id)

    for node_id in graph.keys():
        dfs(node_id)

    # Reverse the sorted nodes to get them in correct order
    sorted_nodes.reverse()

    # Create a mapping of node UUIDs to their index in the sorted list
    node_index_map = {node["uuid"]: index for index, node in enumerate(nodes)}

    # Sort the nodes based on their index in the sorted list
    sorted_nodes_with_data = [nodes[node_index_map[node_id]] for node_id in sorted_nodes]

    return sorted_nodes_with_data

def compile(scene):
    a=scene
    #print("base scene: " + json.dumps(a, indent = 4))
    b = sort_nodes_based_on_connections(a["nodes"], a["connections"])
    b = {"nodes": b, "connections": a["connections"]}
    #print(json.dumps(b["nodes"], indent=4))
    #print("sorted: " + json.dumps(b, indent=4))
    b = convert_connections(b["nodes"], b["connections"])
    #print("converted connections: " + json.dumps(b, indent=4))
    b = convert_to_xml(b)
    try:
        print("converted to xml: " + parseString(b).toprettyxml())
    except:
        print("converted to xml: " + b)
compile(a)