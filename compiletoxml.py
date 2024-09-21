from xml.dom.minidom import parseString
from tkinter import filedialog


def convert_connections(nodes: list, connections: list):
    converted_data = []
    for node in nodes:
        for connection in connections:
            if connection["start_id"] == node["uuid"]:
                if not "connections" in node:
                    node["connections"] = {}
                    node["connections"]["start_id"] = []
                    node["connections"]["end_id"] = []
                    node["connections"]["start_pin"] = []
                    node["connections"]["end_pin"] = []
                node["connections"]["start_id"].append(connection["start_id"])
                node["connections"]["end_id"].append(connection["end_id"])
                node["connections"]["start_pin"].append(connection["start_pin"])
                node["connections"]["end_pin"].append(connection["end_pin"])
    converted_data = nodes
    # print(json.dumps(converted_data,indent=4))
    return converted_data


def find_previous_node(scene, uuid, newscene):
    connections = scene["connections"]
    for connection in connections:
        if connection["end_id"] == uuid:
            for s in newscene:
                if s["uuid"] == connection["start_id"]:
                    return s
    return None


def convert_node_to_xml(node, nodes, uuid, scene):
    node_type = node["type"]
    internal_data = node["internal-data"]

    if node_type == "choice_Node":
        return ""
    elif node_type == "event_Node":
        return f"<event name='{internal_data['text']}' unique='{internal_data['isunique']}'>"
    elif node_type == "text_Node":
        if find_previous_node(scene, uuid, nodes)["type"] == "choice_Node":
            return f"<choice><text>{internal_data['text']}</text><event>"
        return f"<text>{internal_data['text']}</text>"
    elif node_type == "playsound_Node":
        audio = ""
        for nod in convert_connections(scene["nodes"], scene["connections"]):
            if nod["type"] == "loadsound_Node":
                if "connections" in nod:
                    for i in nod["connections"]["end_id"]:
                        if i == uuid:
                            audio = nod["internal-data"]["filepath"]
                            print(audio + "hi")

        return f"<playSound>{audio}</playSound>"
    elif node_type == "quest_Node":
        places = ["RANDOM", "LAST", "NEXT"]
        beacon = places[internal_data["index"]]
        return f"<quest beacon='{beacon}' event='{internal_data['text']}'></quest>"
    elif node_type == "loadship_Node":
        return f"<ship name='{internal_data['text']}' auto_blueprint='{internal_data.get('autoblueprint')}'></ship><ship load='{internal_data.get('text')}' hostile='{internal_data.get('ishostile')}'></ship>"
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
        return (
            "<status type='limit' target='player' system='sensors' amount='1'></status>"
        )
    elif node_type == "autoReward":
        return "<autoReward></autoReward>"
    elif node_type == "surrender":
        return "<surrender chance='0' min='3' max='4'></surrender>"
    elif node_type == "store_Node":
        return "<store></store>"
    elif node_type == "end_of_event_Node":
        return "</event>"
    else:
        # print(node_type)
        return "<unknown></unknown>"


def convert_to_xml(nodes, scene):
    xml_output = "<FTL>"

    # Iterate through nodes
    # print(json.dumps(nodes,indent=4))
    for node in nodes:
        if node["type"] != "end_branch_Node":
            xml_output += convert_node_to_xml(node, nodes, node["uuid"], scene)
        else:
            xml_output += "</event></choice>"

    xml_output += "</FTL>"
    # print(xml_output)
    return xml_output


def sort_nodes_based_on_connections(nodes, connections):
    # Create a dictionary to map UUIDs to node objects
    uuid_to_node = {node["uuid"]: node for node in nodes}
    sorted_nodes = []

    def dfs_sort(node_uuid, visited=set()):
        if node_uuid in visited:
            return []
        visited.add(node_uuid)
        node = uuid_to_node[node_uuid]
        results = [node]

        # Handle choice nodes to prioritize paths ending with end_event_Node
        if node["type"] == "choice_Node":
            child_nodes = []
            end_event_paths = []

            # Separate children into normal and end_event paths
            for end_id in node["connections"]["end_id"]:
                sub_path = dfs_sort(end_id, visited.copy())
                if any(n["type"] == "end_of_event_Node" for n in sub_path):
                    end_event_paths.append(sub_path)
                else:
                    child_nodes.append(sub_path)

            # Append non-ending paths followed by paths ending in an event
            for path in child_nodes:
                results.extend(path)
            for path in end_event_paths:
                results.extend(path)
        else:
            if "connections" in node:
                for end_id in node["connections"]["end_id"]:
                    results.extend(dfs_sort(end_id, visited))

        return results

    # Start from the start_Node
    start_node_uuid = next(
        (node["uuid"] for node in nodes if node["type"] == "start_Node"), None
    )
    if start_node_uuid:
        sorted_nodes = dfs_sort(start_node_uuid)

    return sorted_nodes


def save_file(xml):
    # Open the save as file dialog
    file_path = filedialog.asksaveasfilename(
        defaultextension=".xml.append",
        filetypes=[("XML files", "*.xml.append;"), ("All files", "*.*")],
        title="Save as",
    )
    # Check if a file path was selected
    if file_path:
        print(f"File will be saved to: {file_path}")
        with open(file_path, "w") as file:
            file.write(xml)


def compile(scene):
    # print("base scene: " + json.dumps(a, indent = 4))
    # print(json.dumps(b["nodes"], indent=4))
    # print("sorted: " + json.dumps(b, indent=4))
    b = convert_connections(scene["nodes"], scene["connections"])
    # print("converted connections: " + json.dumps(b, indent=4))
    b = sort_nodes_based_on_connections(scene["nodes"], scene["connections"])
    # b = {"nodes": b, "connections": a["connections"]}
    b = convert_to_xml(b, scene)
    try:
        print(parseString(b).toprettyxml())
        xml = parseString(b).toprettyxml()
    except:
        print(b)
        xml = b

    save_file(xml)
