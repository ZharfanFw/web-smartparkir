import networkx as nx

class ParkingGraphBuilder:
    def __init__(self, building):
        self.building = building
        self.G = nx.DiGraph()

    def build_graph(self):
        self.G.add_node("GATE_ENTRY")
        
        COST_FLAT = 1
        COST_RAMP = 100 # Tetap mahal agar lantai bawah penuh dulu

        floors = self.building.floor_list
        first_floor_aisle = f"A_{floors[0]}"
        self.G.add_edge("GATE_ENTRY", first_floor_aisle, weight=COST_FLAT)

        for i, floor in enumerate(floors):
            aisle_node = f"A_{floor}"
            self.G.add_node(aisle_node)

            floor_slots = [
                s for id, s in self.building.slots.items() if s.floor_name == floor
            ]

            for slot in floor_slots:
                # --- LOGIKA BARU SESUAI VISUAL FRONTEND ---
                
                # ZONA 1: Depan (Slot 01-10) -> Sangat Strategis
                if slot.number <= 10:
                    slot_weight = 1
                
                # ZONA 2: Tengah Bawah & Atas (Slot 11-50) -> Standar
                elif slot.number <= 50:
                    slot_weight = 5
                
                # ZONA 3: Belakang (Slot 51-60) -> Agak Jauh
                elif slot.number <= 60:
                    slot_weight = 8
                    
                # ZONA 4: Sayap Kiri & Kanan (Slot 61-70) -> Paling Jauh/Sempit
                else:
                    slot_weight = 12 

                # Hubungkan Aisle ke Slot
                self.G.add_edge(aisle_node, slot.id, weight=slot_weight)
                self.G.add_edge(slot.id, aisle_node, weight=slot_weight)

            # Koneksi antar lantai
            if i < len(floors) - 1:
                next_floor = floors[i + 1]
                ramp_up = f"R_{floor}_{next_floor}"
                next_aisle = f"A_{next_floor}"

                self.G.add_edge(aisle_node, ramp_up, weight=COST_FLAT)
                self.G.add_edge(ramp_up, next_aisle, weight=COST_RAMP)

        print(f"✅ Graph Terbentuk: {self.G.number_of_nodes()} Nodes (Support 70 Slot)")
        return self.G