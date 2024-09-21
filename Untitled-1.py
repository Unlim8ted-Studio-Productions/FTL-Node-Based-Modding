class JsonToXmlConverter:
    def __init__(self, json_data):
        self.json_data = json_data
        self.uuid_to_node = {node["uuid"]: node for node in json_data["nodes"]}
        self.sort_nodes_by_connections()
        # Prepare choice outputs mapping from the JSON data
        self.choice_outputs = defaultdict(list)
        self.prepare_choice_outputs()

    def prepare_choice_outputs(self):
        for conn in self.json_data["connections"]:
            start_node = self.uuid_to_node.get(conn["start_id"])
            if start_node and start_node["type"] == "choice_Node":
                self.choice_outputs[start_node["uuid"]].append(conn)

    def sort_nodes_by_connections(self):
        graph = {node["uuid"]: [] for node in self.json_data["nodes"]}
        in_degree = {node["uuid"]: 0 for node in self.json_data["nodes"]}
        for conn in self.json_data["connections"]:
            graph[conn["start_id"]].append(conn["end_id"])
            in_degree[conn["end_id"]] += 1

        queue = deque([node for node in in_degree if in_degree[node] == 0])
        sorted_nodes = []
        while queue:
            node_id = queue.popleft()
            sorted_nodes.append(node_id)
            for child_id in graph[node_id]:
                in_degree[child_id] -= 1
                if in_degree[child_id] == 0:
                    queue.append(child_id)

        if len(sorted_nodes) != len(self.json_data["nodes"]):
            raise Exception(
                "The graph contains a cycle, which prevents topological sorting."
            )

        self.json_data["nodes"] = [
            self.uuid_to_node[node_id] for node_id in sorted_nodes
        ]

    def convert_json_to_xml(self):
        root = Element("FTL")
        # Assume the first event node is the starting point
        start_node_id = self.json_data["connections"][0]["start_id"]
        start_node = self.uuid_to_node.get(start_node_id)
        for node in self.json_data["nodes"]:
            self.process_node(node, root)
        return tostring(root, encoding="utf-8").decode("utf-8")

    def process_node(self, node, parent_element):
        node_type = node["type"]
        if node_type == "event_Node":
            event_element = SubElement(
                parent_element,
                "event",
                {"name": node.get("internal-data", {}).get("text", "default")},
            )
            self.process_children(node, event_element)
        elif node_type == "text_Node":
            SubElement(parent_element, "text").text = node.get("internal-data", {}).get(
                "text", ""
            )
        elif node_type == "choice_Node":
            self.process_choice_node(node, parent_element)
        elif node_type == "playsound_Node":
            SubElement(
                parent_element,
                "playsound",
                {"file": node.get("internal-data", {}).get("filepath", "default.wav")},
            )
        elif node_type == "loadship_Node":
            SubElement(
                parent_element,
                "ship",
                {
                    "name": node["internal-data"]["text"],
                    "hostile": str(node["internal-data"]["ishostile"]),
                },
            )
        elif node_type == "Reward_Node":
            SubElement(
                parent_element,
                "reward",
                {
                    "amount": str(node["internal-data"]["amount"]),
                    "index": str(node["internal-data"]["index"]),
                },
            )
        elif node_type == "giveweapon_Node":
            SubElement(
                parent_element, "weapon", {"name": node["internal-data"]["text"]}
            )
        elif node_type == "giveaugment_Node":
            SubElement(
                parent_element, "augment", {"name": node["internal-data"]["text"]}
            )
        # Add other node types here as needed

    def process_choice_node(self, choice_node, parent_element):
        outputs = self.choice_outputs[choice_node["uuid"]]
        for conn in outputs:
            end_node = self.uuid_to_node.get(conn["end_id"])
            if end_node and end_node["type"] == "text_Node":
                choice_element = SubElement(parent_element, "choice")
                text_element = SubElement(choice_element, "text")
                text_element.text = end_node.get("internal-data", {}).get("text", "")
                self.process_children(end_node, choice_element)

    def process_children(self, node, parent_element):
        for conn in filter(
            lambda c: c["start_id"] == node["uuid"], self.json_data["connections"]
        ):
            child_node = self.uuid_to_node.get(conn["end_id"])
            if child_node:
                self.process_node(child_node, parent_element)
                
for some reason the code above is outputting:

<FTL>
        <unknown/>
        <event name="example" unique="True">
                <text>A zoltan ship hails you</text>
                <choice>
                        <text>attack!</text>
                        <event>
                                <playSound/>
                                <ship name="enemy-zoltan" auto_blueprint=""/>
                                <ship>load='enemy-zoltan' hostile='True'</ship>
                        </event>
                </choice>
        </event>
        <choice>
                <text>Tell them about your mission and ask for supplies</text>
                <event>
                        <text>They give you some supplies to help you on your quest</text>
                        <item type="scrap" amount="20"/>
                </event>
        </choice>
</FTL>


instead of outputting this:
    
<FTL>
        <event name="example" unique="True">
                <text>A zoltan ship hails you</text>
                <choice>
                        <text>attack!</text>
                        <event>
                                <playSound/>
                                <ship name="enemy-zoltan" auto_blueprint=""/>
                                <ship>load='enemy-zoltan' hostile='True'</ship>
                        </event>
                </choice>
                <choice>
                <text>Tell them about your mission and ask for supplies</text>
                <event>
                        <text>They give you some supplies to help you on your quest</text>
                        <item type="scrap" amount="20"/>
                </event>
                </choice>
        </event>
</FTL>