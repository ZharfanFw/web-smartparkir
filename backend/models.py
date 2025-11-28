class ParkingSlot:
    def __init__(self, floor_name: str, number: int):
        self.floor_name = floor_name
        self.number = number
        # Format ID harus sama persis dengan frontend: "Lantai-Nomor" (contoh: 1A-05)
        self.id = f"{floor_name}-{number:02d}"
        self.status = "GREEN"

    def __repr__(self):
        return f"<Slot {self.id} | {self.status}>"


class ParkingBuilding:
    def __init__(self, slots_per_level=70):
        self.floor_list = [
            "B", "1A", "1B", "2A", "2B", "3A", "3B", 
            "4A", "4B", "5A", "5B", "6A", "6B", "7A"
        ]
        self.slots_per_level = slots_per_level
        self.slots = {}
        self._generate_slots()

    def _generate_slots(self):
        print(f"Membangun gedung dengan struktur: {self.floor_list}")
        for floor_name in self.floor_list:
            for number in range(1, self.slots_per_level + 1):
                new_slot = ParkingSlot(floor_name, number)
                self.slots[new_slot.id] = new_slot

        print(f"Selesai! Total slot terbentuk: {len(self.slots)}")

    def get_slot(self, slot_id):
        return self.slots.get(slot_id)

    def update_status(self, slot_id, new_status):
        if slot_id in self.slots:
            self.slots[slot_id].status = new_status
            return True
        return False