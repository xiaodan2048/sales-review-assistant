"""重新计算评测页上的关键指标，确认文档里的数字和逐条数据一致。

用法：python3 eval/check_metrics.py
（S16 中 AI 标了“依据不足”的维度在 CSV 里留空，按“不一致”计。）
"""
import csv
from pathlib import Path
from statistics import correlation

HERE = Path(__file__).parent
DIMS = ["d1", "d2", "d3", "d4"]

rows = list(csv.DictReader(open(HERE / "scoring_v2.csv", encoding="utf-8")))
agree = exact = 0
per_dim = {d: 0 for d in DIMS}
diffs, mgr_tot, ai_tot = [], [], []
bad_disagree = bad_total_disagree = ai_higher = 0
for r in rows:
    has_all = True
    for d in DIMS:
        m, a = int(r[f"mgr_{d}"]), r[f"ai_{d}"]
        if a == "":
            has_all = False
            if r["quality"] == "差":
                bad_disagree += 1
            bad_total_disagree += 1
            continue
        a = int(a)
        diffs.append(a - m)
        if abs(a - m) <= 1:
            agree += 1
            per_dim[d] += 1
        else:
            bad_total_disagree += 1
            if r["quality"] == "差":
                bad_disagree += 1
            if a > m:
                ai_higher += 1
        exact += a == m
    if has_all:
        mgr_tot.append(sum(int(r[f"mgr_{d}"]) for d in DIMS) * 5)
        ai_tot.append(sum(int(r[f"ai_{d}"]) for d in DIMS) * 5)

n = len(rows) * 4
print(f"评分一致率        {agree}/{n} = {agree/n:.0%}")
print(f"  按维度 D1–D4     {[per_dim[d] for d in DIMS]}")
print(f"评分完全一致率    {exact}/{n} = {exact/n:.0%}")
print(f"总分相关系数      {correlation(mgr_tot, ai_tot):.2f}（{len(mgr_tot)} 段）")
print(f"评分偏差          {sum(diffs)/len(diffs):+.2f}")
print(f"不一致中“差”拜访  {bad_disagree}/{bad_total_disagree}；有分数的不一致里 AI 偏高 {ai_higher}")

ext = list(csv.DictReader(open(HERE / "extraction_v2.csv", encoding="utf-8")))
g = sum(int(r["gold_mentioned"]) for r in ext)
e = sum(int(r["ai_extracted"]) for r in ext)
c = sum(int(r["ai_correct"]) for r in ext)
print(f"抽取准确率        {c}/{e} = {c/e:.0%}")
print(f"抽取召回率        {c}/{g} = {c/g:.0%}")
