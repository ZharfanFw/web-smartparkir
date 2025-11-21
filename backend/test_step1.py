from models import ParkingBuilding

gedung_upi = ParkingBuilding(slots_per_level=20)

print(f"\nTotal slot terbentuk: {len(gedung_upi.slots)}")

slot_b = gedung_upi.get_slot("B-05")
print(f"Cek Basement: {slot_b}")

slot_1a = gedung_upi.get_slot("1A-10")
slot_7b = gedung_upi.get_slot("7B-20")

print("Motor masuk ke 1A-10...")
gedung_upi.update_status("1A-10", "RED")
print(f"Status 1A-10: {gedung_upi.get_slot('1A-10')}")
