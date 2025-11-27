import networkx as nx


class ParkingGraphBuilder:
    def __init__(self, building):
        self.building = building
        self.G = nx.DiGraph()

    def build_graph(self):
        # Node Awal
        self.G.add_node("GATE_ENTRY")

        # --- KONFIGURASI BIAYA (LOGIKA JARAK) ---
        # Biaya jalan datar antar node utama
        COST_FLAT = 1
        # Biaya naik lantai (Ramp) -> Dibuat MAHAL biar dia menuhin lantai bawah dulu
        COST_RAMP = 100

        floors = self.building.floor_list

        # 1. Hubungkan GATE ke Jalur Utama Lantai Paling Bawah (B)
        # Ini memastikan dia ngecek Basement dulu
        first_floor_aisle = f"A_{floors[0]}"
        self.G.add_edge("GATE_ENTRY", first_floor_aisle, weight=COST_FLAT)

        for i, floor in enumerate(floors):
            # Node Jalur Utama per Lantai (Aisle)
            aisle_node = f"A_{floor}"
            self.G.add_node(aisle_node)

            # Ambil semua slot di lantai ini
            floor_slots = [
                s for id, s in self.building.slots.items() if s.floor_name == floor
            ]

            for slot in floor_slots:
                # --- LOGIKA BARU: BIAYA BERDASARKAN POSISI ---
                # Slot 01-10 (Depan/Bawah) -> Paling Murah (Jarak dekat)
                if slot.number <= 10:
                    slot_weight = 1
                # Slot 11-30 (Tengah) -> Sedang
                elif slot.number <= 30:
                    slot_weight = 5
                # Slot 31-50 (Belakang/Atas) -> Paling Jauh
                else:
                    slot_weight = 10

                # Hubungkan Aisle ke Slot dengan bobot dinamis tadi
                self.G.add_edge(aisle_node, slot.id, weight=slot_weight)
                self.G.add_edge(slot.id, aisle_node, weight=slot_weight)

            # 2. Hubungkan ke Lantai Berikutnya (Ramp Naik)
            if i < len(floors) - 1:
                next_floor = floors[i + 1]
                ramp_up = f"R_{floor}_{next_floor}"
                next_aisle = f"A_{next_floor}"

                # Aisle -> Ramp -> Next Aisle
                self.G.add_edge(aisle_node, ramp_up, weight=COST_FLAT)
                self.G.add_edge(ramp_up, next_aisle, weight=COST_RAMP)  # Denda Mahal!

        print(
            f"✅ Graph Terbentuk dengan Logic Jarak: {self.G.number_of_nodes()} Nodes"
        )
        return self.G
