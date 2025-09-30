# -*- coding: utf-8 -*-
"""
Card Balance Analysis Script for 《天机变》.

This script performs a static analysis of all generated card data to provide
quantitative insights into the game's overall balance. It serves as a tool
to support data-driven design and balancing decisions, as required by the
project's core development guidelines (AGENTS.md).

Key Functions:
- Parses all generated JSON card files from the `assets/data/cards/` directory.
- Recursively traverses the data structure of each card to find all actions.
- Aggregates key metrics, such as resource gains/losses, damage output,
  control effects, and card advantage.
- Generates a summary report in Markdown format (`metrics/balance_summary.md`)
  that presents these metrics in a human-readable format.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Iterator
from collections import defaultdict
import datetime

# --- 1. Configuration & Constants ---

SCRIPT_DIR = Path(__file__).parent.resolve()
ROOT_DIR = SCRIPT_DIR.parent
CARD_DATA_DIR = ROOT_DIR / "assets" / "data" / "cards"
METRICS_DIR = ROOT_DIR / "metrics"

# Define categories for different actions to group them in the report.
ACTION_CATEGORIES = {
    "RESOURCE_GAIN": {"GAIN_RESOURCE"},
    "RESOURCE_LOSS": {"LOSE_RESOURCE", "PAY_COST"},
    "DAMAGE": {"DEAL_DAMAGE"},
    "CONTROL": {"DISCARD_CARD", "APPLY_STATUS", "SKIP_PHASE", "MODIFY_RULE"},
    "CARD_ADVANTAGE": {"DRAW_CARD", "RECOVER_CARD_FROM_DISCARD"},
    "UTILITY": {"MOVE", "SWAP_POSITION", "SWAP_RESOURCES", "SWAP_HAND_CARDS", "SWAP_DISCARD_PILES", "LOOKUP", "CHOICE", "CREATE_ENTITY", "DESTROY_ENTITY"},
}

# --- 2. Data Parsing and Traversal ---

def get_all_card_files(base_dir: Path) -> Iterator[Path]:
    """Yields all .json files from the card data directory."""
    if not base_dir.is_dir():
        print(f"Error: Card data directory not found at '{base_dir}'")
        return
    yield from base_dir.rglob("*.json")

def find_actions_recursively(data: Any) -> Iterator[Dict[str, Any]]:
    """Recursively finds and yields all action objects within a card's data."""
    if isinstance(data, dict):
        if "action" in data and "params" in data:
            yield data
        for value in data.values():
            yield from find_actions_recursively(value)
    elif isinstance(data, list):
        for item in data:
            yield from find_actions_recursively(item)

# --- 3. Metrics Aggregation ---

class BalanceAnalyzer:
    """Analyzes a collection of cards and aggregates balance metrics."""

    def __init__(self):
        self.metrics = {
            "total_cards": 0,
            "total_actions": 0,
            "action_counts": defaultdict(int),
            "resource_gain": defaultdict(int),
            "resource_loss": defaultdict(int),
            "total_damage": 0,
            "control_effects": defaultdict(int),
            "card_advantage": 0,
            "cards_with_high_risk_actions": defaultdict(set)
        }
        self.high_risk_actions = {"MODIFY_RULE", "EXECUTE_LATER", "COPY_EFFECT"}

    def analyze_card(self, card_data: Dict[str, Any]):
        """Analyzes a single card and updates the aggregate metrics."""
        self.metrics["total_cards"] += 1
        card_id = card_data.get("id", "UNKNOWN")

        for action in find_actions_recursively(card_data):
            action_name = action.get("action")
            if not action_name:
                continue

            self.metrics["total_actions"] += 1
            self.metrics["action_counts"][action_name] += 1

            if action_name in self.high_risk_actions:
                self.metrics["cards_with_high_risk_actions"][action_name].add(card_id)

            params = action.get("params", {})
            value = params.get("value", 0)

            # Ensure value is an integer for aggregation
            if not isinstance(value, int):
                value = 0 # Ignore complex values for this static analysis

            if action_name == "GAIN_RESOURCE":
                resource = params.get("resource")
                if resource in ["gold", "health"]:
                    self.metrics["resource_gain"][resource] += value
            elif action_name in ["LOSE_RESOURCE", "PAY_COST"]:
                resource = params.get("resource")
                if resource in ["gold", "health"]:
                    self.metrics["resource_loss"][resource] += value
            elif action_name == "DEAL_DAMAGE":
                self.metrics["total_damage"] += value
            elif action_name in ACTION_CATEGORIES["CARD_ADVANTAGE"]:
                count = params.get("count", 0)
                if isinstance(count, int):
                    self.metrics["card_advantage"] += count
            elif action_name == "DISCARD_CARD":
                count = params.get("count", 0)
                if isinstance(count, int):
                    self.metrics["control_effects"]["discard"] += count


    def generate_report(self) -> str:
        """Generates a Markdown summary of the aggregated metrics."""
        report = [f"# 《天机变》 - 卡牌平衡性量化分析报告\n"]
        report.append(f"> **生成时间:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        report.append(f"## 1. 总体概览\n")
        report.append(f"- **分析卡牌总数:** {self.metrics['total_cards']}")
        report.append(f"- **解析动作总数:** {self.metrics['total_actions']}\n")

        report.append(f"## 2. 核心指标分析\n")
        report.append(f"### 资源变动")
        report.append(f"- **总金币产出:** {self.metrics['resource_gain']['gold']}")
        report.append(f"- **总金币消耗/损失:** {self.metrics['resource_loss']['gold']}")
        report.append(f"- **总生命恢复:** {self.metrics['resource_gain']['health']}")
        report.append(f"- **总生命损失/支付:** {self.metrics['resource_loss']['health']}")
        report.append(f"- **总伤害输出:** {self.metrics['total_damage']}\n")

        report.append(f"### 卡牌优势与控制")
        report.append(f"- **总抽牌数:** {self.metrics['card_advantage']}")
        report.append(f"- **总弃牌数 (控制):** {self.metrics['control_effects']['discard']}\n")

        report.append(f"## 3. 高风险动作使用情况\n")
        report.append("此部分列出了使用了高风险动作的卡牌，需要重点进行代码审查和游戏测试。\n")
        for action, cards in self.metrics["cards_with_high_risk_actions"].items():
            report.append(f"- **`{action}`:**")
            for card_id in sorted(list(cards)):
                report.append(f"  - `{card_id}`")

        report.append(f"\n## 4. 动作频率分布\n")
        report.append("| 动作 (Action) | 使用次数 |")
        report.append("| :--- | :--- |")

        sorted_actions = sorted(self.metrics["action_counts"].items(), key=lambda item: item[1], reverse=True)
        for action, count in sorted_actions:
            report.append(f"| `{action}` | {count} |")

        return "\n".join(report)

# --- 4. Main Execution ---

def main():
    """Main function to orchestrate the analysis and report generation."""
    print("--- Starting Card Balance Analysis ---")

    analyzer = BalanceAnalyzer()

    for card_file in get_all_card_files(CARD_DATA_DIR):
        try:
            with card_file.open('r', encoding='utf-8') as f:
                card_data = json.load(f)
            analyzer.analyze_card(card_data)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not parse file {card_file.name}: {e}")

    print("Analysis complete. Generating report...")
    report_content = analyzer.generate_report()

    # Ensure the metrics directory exists
    METRICS_DIR.mkdir(exist_ok=True)
    report_path = METRICS_DIR / "balance_summary.md"

    try:
        with report_path.open('w', encoding='utf-8') as f:
            f.write(report_content)
        print(f"Successfully generated balance report at: {report_path}")
    except IOError as e:
        print(f"Error: Failed to write report file: {e}")

    print("\n--- Balance Analysis Complete ---")

if __name__ == "__main__":
    main()