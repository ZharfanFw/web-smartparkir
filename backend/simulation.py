import random
import traceback
import networkx as nx
from graph_builder import ParkingGraphBuilder
from models import ParkingBuilding

# --- INIT GRAPH ---
print("🔄 Memuat Graph UPI...")
# UPDATE: slots_per_level diubah jadi 70 sesuai frontend
building = ParkingBuilding(slots_per_level=70) 
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
        # Format waktu disesuaikan agar enak dibaca di frontend
        time_str = f"{self.env.now:.1f}s"
        print(f"[{time_str}] {message}")
        
        self.events.append({
            "id": slot_id,
            "status": status,
            "message": message,
            "time": time_str
        })

    def find_best_slot_astar(self):
        source_node = "GATE_ENTRY"
        best_slot_id = None
        min_cost = float("inf")

        # Cari hanya yang GREEN
        available_slots = [
            slot.id for id, slot in self.building.slots.items()
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
            # BARU: Muncul sangat cepat (0.1 sampai 0.5 detik)
            yield self.env.timeout(random.uniform(0.1, 0.5))
            self.env.process(self.motor_activity(motor_id))
            motor_id += 1

    def motor_activity(self, motor_id):
        try:
            chosen_slot_id = self.find_best_slot_astar()

            if not chosen_slot_id:
                self.log_event(None, "FULL", f"Motor #{motor_id} PULANG (Penuh!)")
                return

            # 1. Booking (Kuning)
            self.building.update_status(chosen_slot_id, "YELLOW")
            self.log_event(chosen_slot_id, "YELLOW", f"Motor #{motor_id} Booking {chosen_slot_id}")

            # Waktu jalan ke slot
            yield self.env.timeout(random.randint(2, 4))

            # 2. Parkir (Merah)
            self.building.update_status(chosen_slot_id, "RED")
            self.log_event(chosen_slot_id, "RED", f"Motor #{motor_id} Parkir di {chosen_slot_id}")

            # Durasi Parkir
            yield self.env.timeout(random.randint(300, 420))

            # 3. Keluar (Hijau)
            self.building.update_status(chosen_slot_id, "GREEN")
            self.log_event(chosen_slot_id, "GREEN", f"Motor #{motor_id} Selesai {chosen_slot_id}")

        except Exception:
            print(f"🔥 ERROR di Motor #{motor_id}:")
            traceback.print_exc()