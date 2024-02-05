import json
import networkx as nx

with open("points_final.json", "r") as json_f:
    data = json.load(json_f)

G = nx.Graph()

for node_id, node_data in data.items():
    G.add_node(node_id, COORDONNEES=node_data["COORDONNEES"])

for node_id, node_data in data.items():
    for adjacent_node, weight in node_data["ADJACENTS"]:
        G.add_edge(node_id, adjacent_node, weight=weight)

# print("Nodes:", G.nodes(data=True))
# print("Edges:", G.edges(data=True))
# print(nx.algorithms.astar_path(G, "299", "179"))
# print(nx.algorithms.dijkstra_path(G, "299", "179"))

print(G.nodes["1"]["COORDONNEES"])

