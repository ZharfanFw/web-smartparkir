import networkx as nx
from models import ParkingBuilding

COST_SLOT = 1
COST_AISLE = 1
COST_RAMP = 20


class ParkingGraphBuilder:
    def __init__(self, building: ParkingBuilding):
        self.building = building
        self.G = nx.DiGraph()
        self.floor_list = building.floor_list

    def build_graph(self):
        self.G.add_node("GATE_ENTRY", type="GATE")

        for i, floor_name in enumerate(self.floor_list):
            self._build_floor_template(floor_name)

            if i < len(self.floor_list) - 1:
                next_floor = self.floor_list[i + 1]
                self._connect_floors(floor_name, next_floor)

        self.G.add_edge(
            "GATE_ENTRY", f"A_{self.floor_list[0]}_start", weight=COST_AISLE
        )

        print(f"Graph Selesai. Total Simpul (Nodes): {self.G.number_of_nodes()}")
        print(f"Total Jalur Edge (Edges): {self.G.number_of_edges()}")
        return self.G

    def _build_floor_template(self, floor_name):
        aisle_start = f"A_{floor_name}_start"
        aisle_mid = f"A_{floor_name}_mid"
        aisle_end = f"A_{floor_name}_end"

        self.G.add_nodes_from(
            [
                (aisle_start, {"type": "AISLE"}),
                (aisle_mid, {"type": "AISLE"}),
                (aisle_end, {"type": "AISLE"}),
            ]
        )

        self.G.add_edge(aisle_start, aisle_mid, weight=COST_AISLE)
        self.G.add_edge(aisle_mid, aisle_end, weight=COST_AISLE)

        floor_slots = [s for s in self.building.slots if s.startswith(f"{floor_name}-")]

        for i, slot_id in enumerate(floor_slots):
            if i < self.building.slots_per_level / 2:
                self.G.add_edge(aisle_start, slot_id, weight=COST_SLOT)

                self.G.add_edge(slot_id, aisle_start, weight=COST_SLOT)

            else:
                self.G.add_edge(aisle_mid, slot_id, weight=COST_SLOT)

                self.G.add_edge(slot_id, aisle_mid, weight=COST_SLOT)

    def _connect_floors(self, current_floor, next_floor):
        ramp_up_node = f"R_UP_{current_floor}_to_{next_floor}"
        self.G.add_node(ramp_up_node, type="RAMP")
        self.G.add_edge(f"A_{current_floor}_end", ramp_up_node, weight=COST_AISLE)
        self.G.add_edge(ramp_up_node, f"A_{next_floor}_start", weight=COST_RAMP)

        ramp_down_node = f"R_DOWN_{next_floor}_to_{current_floor}"
        self.G.add_node(ramp_down_node, type="RAMP")
        self.G.add_edge(f"A_{next_floor}_end", ramp_down_node, weight=COST_AISLE)
        self.G.add_edge(ramp_down_node, f"A_{current_floor}_start", weight=COST_RAMP)
