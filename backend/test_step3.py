# backend/test_step3.py
import networkx as nx
from graph_builder import ParkingGraphBuilder
from models import ParkingBuilding

# 1. Bangun Gedung & Graph
building = ParkingBuilding(slots_per_level=50)
graph_builder = ParkingGraphBuilder(building)
G = graph_builder.build_graph()

# 2. Cek Total Simpul & Jalur
print("\n--- VERIFIKASI STRUKTUR GRAPH ---")
print(f"Total Simpul (Nodes): {G.number_of_nodes()}")
print(f"Total Jalur (Edges): {G.number_of_edges()}")

# 3. Cek Jalur A* (Contoh 1: Dari Gerbang ke Lantai Paling Atas 7B-50)
print("\n--- TEST JALUR A* (Gate -> Slot 7A-50) ---")
try:
    path_high_floor = nx.shortest_path(
        G,
        source="GATE_ENTRY",
        target="7A-50",
        weight="weight",  # Kita hitung berdasarkan bobot (cost)
    )
    path_cost = nx.shortest_path_length(
        G, source="GATE_ENTRY", target="7A-50", weight="weight"
    )
    print(f"Rute: {path_high_floor[:3]}...{path_high_floor[-3:]}")
    print(f"Total Biaya Rute: {path_cost} unit")
except nx.NetworkXNoPath:
    print("ERROR: Tidak ada jalur yang ditemukan!")

# 4. Cek Jalur A* (Contoh 2: Dari Gerbang ke Lantai Bawah B-01)
print("\n--- TEST JALUR A* (Gate -> Slot B-01) ---")
path_low_floor = nx.shortest_path_length(
    G, source="GATE_ENTRY", target="B-01", weight="weight"
)
print(f"Total Biaya Rute ke Lantai B: {path_low_floor} unit")

# Perbandingan: Biaya Rute Jauh harus JAUH lebih besar daripada Biaya Rute Dekat.
# Jika Rute 7A lebih murah daripada A, berarti ada yang salah.
