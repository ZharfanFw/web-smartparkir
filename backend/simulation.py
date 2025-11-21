import random
import traceback  # BIAR KELIATAN ERRORNYA

import networkx as nx
from graph_builder import ParkingGraphBuilder
from models import ParkingBuilding

# --- INIT GRAPH ---
print("🔄 Memuat Graph UPI...")
building = ParkingBuilding(slots_per_level=50)
graph_builder = ParkingGraphBuilder(building)
PARKING_GRAPH = graph_builder.build_graph()
print("✅ Graph Siap!")
# ------------------


class ParkingSimulation:
    def __init__(self, env):
        self.env = env
        self.building = building
        self.G = PARKING_GRAPH
        self.events = []

    def start(self):
        print("🚀 Simulasi DIMULAI...")
        self.env.process(self.generate_motors())

    def log_event(self, slot_id, status, message):
        print(f"[{self.env.now:.1f}s] {message}")
        self.events.append(
            {
                "id": slot_id,
                "status": status,
                "message": message,
                "time": f"{self.env.now:.1f}s",
            }
        )

    def find_best_slot_astar(self):
        source_node = "GATE_ENTRY"
        best_slot_id = None
        min_cost = float("inf")

        available_slots = [
            slot.id
            for id, slot in self.building.slots.items()
            if slot.status == "GREEN"
        ]

        if not available_slots:
            return None

        for target_id in available_slots:
            try:
                cost = nx.shortest_path_length(
                    self.G, source=source_node, target=target_id, weight="weight"
                )
                if cost < min_cost:
                    min_cost = cost
                    best_slot_id = target_id
            except nx.NetworkXNoPath:
                continue

        return best_slot_id

    def generate_motors(self):
        motor_id = 1
        while True:
            yield self.env.timeout(random.randint(1, 3))
            # Panggil motor_activity dengan Error Handling
            self.env.process(self.motor_activity(motor_id))
            motor_id += 1

    def motor_activity(self, motor_id):
        try:
            # --- LOGIKA UTAMA ---
            chosen_slot_id = self.find_best_slot_astar()

            if not chosen_slot_id:
                self.log_event(None, "FULL", f"Motor #{motor_id} PULANG (Penuh!)")
                return

            # Booking (YELLOW)
            self.building.update_status(chosen_slot_id, "YELLOW")
            self.log_event(
                chosen_slot_id, "YELLOW", f"Motor #{motor_id} Booking {chosen_slot_id}"
            )

            yield self.env.timeout(random.randint(3, 5))

            # Parkir (RED)
            self.building.update_status(chosen_slot_id, "RED")
            self.log_event(
                chosen_slot_id, "RED", f"Motor #{motor_id} Parkir di {chosen_slot_id}"
            )

            yield self.env.timeout(random.randint(10, 20))

            # Keluar (GREEN)
            self.building.update_status(chosen_slot_id, "GREEN")
            self.log_event(
                chosen_slot_id,
                "GREEN",
                f"Motor #{motor_id} Keluar dari {chosen_slot_id}",
            )

        except Exception:
            # INI DIA YANG KITA CARI: PENANGKAP ERROR
            print(f"🔥 ERROR PARAH di Motor #{motor_id}:")
            traceback.print_exc()  # Cetak error lengkap ke terminal
