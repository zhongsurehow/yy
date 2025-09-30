from dataclasses import dataclass, field
from typing import Any, Dict, List

@dataclass
class Card:
    """Represents a single game card, loaded from its JSON definition."""
    card_id: str
    name: str
    card_type: str
    core_mechanism: Dict[str, Any] = field(default_factory=dict)
    effect: Dict[str, Any] = field(default_factory=dict)
    triggers: List[Dict[str, Any]] = field(default_factory=list)

    # Optional metadata
    symbol: str | None = None
    sequence: int | None = None
    pinyin: str | None = None
    strokes: int | None = None
    usage_limit: Dict[str, Any] | None = None

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'Card':
        """Creates a Card instance from a JSON data dictionary."""
        return cls(
            card_id=data.get("id"),
            name=data.get("name"),
            card_type=data.get("type"),
            core_mechanism=data.get("core_mechanism", {}),
            effect=data.get("effect", {}),
            triggers=data.get("triggers", []),
            symbol=data.get("symbol"),
            sequence=data.get("sequence"),
            pinyin=data.get("pinyin"),
            strokes=data.get("strokes"),
            usage_limit=data.get("usage_limit")
        )

    def __repr__(self) -> str:
        return f"Card(id='{self.card_id}', name='{self.name}')"

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the Card object to a dictionary."""
        return {
            "card_id": self.card_id,
            "name": self.name,
            "card_type": self.card_type,
            "strokes": self.strokes,
            "symbol": self.symbol,
        }