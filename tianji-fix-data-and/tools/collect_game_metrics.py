# Tianji Game Metrics Collector (Stub)
# 采集对局数据、卡牌使用率、胜率等核心指标，供平衡性分析
# 实际采集逻辑需集成到游戏主循环/模拟器

import json
import random
import argparse
from pathlib import Path

def simulate_metrics():
    # 示例：生成虚拟数据，实际应由游戏引擎埋点采集
    cards = [
        "basic_01_qian", "basic_02_kun", "basic_03_tun", "basic_04_meng", "basic_05_xu",
        "basic_06_song", "basic_07_shi", "basic_08_bi", "basic_09_xiao_chu", "basic_10_li"
    ]
    metrics = {
        "card_winrate": {cid: round(random.uniform(0.35, 0.65), 3) for cid in cards},
        "card_usage": {cid: random.randint(100, 500) for cid in cards},
        "avg_game_length": random.uniform(12, 22),
        "resource_curve": [random.uniform(0.8, 1.2) for _ in range(10)]
    }
    return metrics

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=str, default='metrics/latest_metrics.json')
    args = parser.parse_args()
    metrics = simulate_metrics()
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)
    print(f"[metrics] Output written to {args.output}")

if __name__ == '__main__':
    main()
