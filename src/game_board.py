from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class Zone:
    """Represents a single area on the board."""
    zone_id: str  # e.g., "li_tian"
    palace: str   # e.g., "li"
    department: str # e.g., "tian"
    luoshu_number: int
    five_element: str

@dataclass
class GameBoard:
    """Represents the game board, including all zones and dynamic elements."""
    zones: Dict[str, Zone] = field(default_factory=dict)
    qimen_gates: Dict[str, str] = field(default_factory=dict) # Maps palace -> gate_id, e.g., {"li": "sheng_men"}

    def __post_init__(self):
        """Initializes the board with all 24 zones if not already provided."""
        if not self.zones:
            self._create_zones()

    def _create_zones(self):
        """Creates the 24 zones of the game board based on the rules."""
        # Simplified mapping for prototype purposes. A full implementation would use the detailed chart.
        palaces = {
            "kan": {"luoshu": 1, "element": "water"},
            "kun": {"luoshu": 2, "element": "earth"},
            "zhen": {"luoshu": 3, "element": "wood"},
            "xun": {"luoshu": 4, "element": "wood"},
            "zhong": {"luoshu": 5, "element": "earth"}, # Not a standard palace for zones
            "qian": {"luoshu": 6, "element": "metal"},
            "dui": {"luoshu": 7, "element": "metal"},
            "gen": {"luoshu": 8, "element": "earth"},
            "li": {"luoshu": 9, "element": "fire"},
        }
        departments = ["tian", "ren", "di"]

        for p_name, p_data in palaces.items():
            if p_name == "zhong": continue
            for dep in departments:
                zone_id = f"{p_name}_{dep}"
                self.zones[zone_id] = Zone(
                    zone_id=zone_id,
                    palace=p_name,
                    department=dep,
                    luoshu_number=p_data["luoshu"],
                    five_element=p_data["element"]
                )

        # Add the central palace as a special zone
        self.zones["zhong_gong"] = Zone(
            zone_id="zhong_gong",
            palace="zhong",
            department="zhong",
            luoshu_number=5,
            five_element="earth"
        )

    def get_zone(self, zone_id: str) -> Zone | None:
        return self.zones.get(zone_id)

    def get_palace_for_zone(self, zone_id: str) -> str | None:
        zone = self.get_zone(zone_id)
        return zone.palace if zone else None

    def update_qimen_gates(self, new_gates: Dict[str, str]):
        """Updates the positions of the Qi Men gates for a new Ju."""
        self.qimen_gates = new_gates
        print(f"Qi Men Gates updated: {self.qimen_gates}")