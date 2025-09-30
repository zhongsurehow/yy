from dataclasses import dataclass, field
from typing import List, Dict, Any

# Defines the circular adjacency of the eight palaces (Ba Gua)
PALACE_ADJACENCY = {
    "kan": ["qian", "gen"],
    "gen": ["kan", "zhen"],
    "zhen": ["gen", "xun"],
    "xun": ["zhen", "li"],
    "li": ["xun", "kun"],
    "kun": ["li", "dui"],
    "dui": ["kun", "qian"],
    "qian": ["dui", "kan"],
}

@dataclass
class Zone:
    """Represents a single area on the board."""
    zone_id: str  # e.g., "li_tian"
    palace: str   # e.g., "li"
    department: str # e.g., "tian"
    luoshu_number: int
    five_element: str
    gold_reward: int = 0
    gold_penalty: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the Zone object to a dictionary."""
        return {
            "zone_id": self.zone_id,
            "palace": self.palace,
            "department": self.department,
            "luoshu_number": self.luoshu_number,
            "five_element": self.five_element,
            "gold_reward": self.gold_reward,
            "gold_penalty": self.gold_penalty,
        }

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
        logging.info(f"Qi Men Gates updated for Ju: {new_gates}")

    def get_valid_moves(self, zone_id: str) -> List[str]:
        """
        Calculates all valid adjacent destination zones from a given zone_id,
        based on the game's movement rules.
        """
        current_zone = self.get_zone(zone_id)
        if not current_zone:
            return []

        valid_moves = []
        current_palace = current_zone.palace
        current_dept = current_zone.department

        if current_dept == 'di':
            # Can move up to own Ren
            valid_moves.append(f"{current_palace}_ren")
            # Can move to adjacent palaces' Di zones
            adjacent_palaces = PALACE_ADJACENCY.get(current_palace, [])
            for adj_palace in adjacent_palaces:
                valid_moves.append(f"{adj_palace}_di")
        elif current_dept == 'ren':
            # Can move up to own Tian or down to own Di
            valid_moves.append(f"{current_palace}_tian")
            valid_moves.append(f"{current_palace}_di")
        elif current_dept == 'tian':
            # Can move down to own Ren or into Zhong Gong
            valid_moves.append(f"{current_palace}_ren")
            valid_moves.append("zhong_gong")
        elif current_dept == 'zhong':
            # Must leave to the Di zone with the lowest Luo Shu number.
            # This is a simplified version; a full implementation would check for occupancy.
            di_zones = sorted(
                [z for z in self.zones.values() if z.department == 'di'],
                key=lambda z: z.luoshu_number
            )
            if di_zones:
                valid_moves.append(di_zones[0].zone_id)

        # Filter out moves to non-existent zones
        return [move for move in valid_moves if move in self.zones]

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the GameBoard object to a dictionary."""
        return {
            "zones": {zone_id: zone.to_dict() for zone_id, zone in self.zones.items()},
            "qimen_gates": self.qimen_gates,
        }