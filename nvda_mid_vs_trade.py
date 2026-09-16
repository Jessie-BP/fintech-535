import json
import os
from datetime import date, timedelta
from pathlib import Path

# Keep Matplotlib caches in a writable temporary location.
os.environ.setdefault("MPLCONFIGDIR", "/tmp/nvda-matplotlib")
os.environ.setdefault("MPLBACKEND", "Agg")

import matplotlib.pyplot as plt
import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parent
OPTIONS_PATH = PROJECT_ROOT / "NVDA-options-response.json"
OUTPUT_PATH = PROJECT_ROOT / "nvda_mid_vs_trade.png"
STATS_PATH = PROJECT_ROOT / "nvda_mid_vs_trade_stats.json"
WEB_DATA_PATH = PROJECT_ROOT / "nvda_mid_vs_trade_web.json"
MAX_WEB_POINTS = 1000


with OPTIONS_PATH.open("r", encoding="utf-8") as file:
    options_response = json.load(file)

points = []

for contract in options_response.get("added", []):
    expiry = date.fromisoformat(contract["expiry"])
    entry_date = expiry - timedelta(days=4)
    entry_timestamp = f"{entry_date.isoformat()} 14:00:00"

    for bar in contract.get("bars", []):
        # Use one synchronized cross-section per week: all near-the-money
        # calls at the strategy's Monday 10:00 ET entry timestamp.
        if bar.get("time") != entry_timestamp:
            continue

        bid = bar.get("bid")
        ask = bar.get("ask")
        trade = bar.get("trade")

        if bid is None or ask is None or trade is None:
            continue

        bid = float(bid)
        ask = float(ask)
        trade = float(trade)

        if bid < 0 or ask < bid or trade < 0:
            continue

        mid = (bid + ask) / 2
        points.append((mid, trade))

if len(points) < 2:
    raise RuntimeError("Need at least two valid BID/ASK/TRDPRC_1 observations.")

mid_values = np.array([point[0] for point in points], dtype=float)
trade_values = np.array([point[1] for point in points], dtype=float)

slope, intercept = np.polyfit(mid_values, trade_values, 1)
predicted = slope * mid_values + intercept

residual_sum_squares = np.sum((trade_values - predicted) ** 2)
total_sum_squares = np.sum((trade_values - np.mean(trade_values)) ** 2)
r_squared = 1 - residual_sum_squares / total_sum_squares

plot_min = min(float(mid_values.min()), float(trade_values.min()))
plot_max = max(float(mid_values.max()), float(trade_values.max()))
fit_x = np.linspace(plot_min, plot_max, 200)
fit_y = slope * fit_x + intercept

fig, ax = plt.subplots(figsize=(10, 7))
ax.scatter(
    mid_values,
    trade_values,
    s=10,
    alpha=0.22,
    color="#2563eb",
    edgecolors="none",
    label="Hourly option observations",
)
ax.plot(
    fit_x,
    fit_y,
    color="#dc2626",
    linewidth=2,
    label="OLS fit",
)
ax.plot(
    [plot_min, plot_max],
    [plot_min, plot_max],
    color="#64748b",
    linewidth=1.2,
    linestyle="--",
    label="45-degree line",
)

annotation = (
    f"TRDPRC_1 = {slope:.4f} × mid + {intercept:.4f}\n"
    f"R² = {r_squared:.4f}\n"
    f"n = {len(points):,}"
)
ax.text(
    0.03,
    0.97,
    annotation,
    transform=ax.transAxes,
    va="top",
    ha="left",
    fontsize=11,
    bbox={"boxstyle": "round", "facecolor": "white", "alpha": 0.9},
)

ax.set_title("NVDA Near-the-Money Calls: Trade Price vs Bid–Ask Mid")
ax.set_xlabel("Mid = (BID + ASK) / 2")
ax.set_ylabel("TRDPRC_1")
ax.grid(alpha=0.2)
ax.legend(loc="lower right")
fig.tight_layout()
fig.savefig(OUTPUT_PATH, dpi=180)
plt.close(fig)

stats = {
    "slope": float(slope),
    "intercept": float(intercept),
    "r_squared": float(r_squared),
    "point_count": len(points),
}

with STATS_PATH.open("w", encoding="utf-8") as file:
    json.dump(stats, file, indent=2)

# Fit on every valid entry-time chain observation. Keep the sampling guard for
# future larger datasets, although this assignment currently has only 81.
rng = np.random.default_rng(535)
sample_size = min(MAX_WEB_POINTS, len(points))
sample_indices = np.sort(
    rng.choice(len(points), size=sample_size, replace=False)
)
web_points = [
    {"mid": round(points[index][0], 6), "trade": round(points[index][1], 6)}
    for index in sample_indices
]
web_data = {
    "points": web_points,
    "slope": float(slope),
    "intercept": float(intercept),
    "r2": float(r_squared),
    "n": len(points),
    "displayedPoints": sample_size,
}

with WEB_DATA_PATH.open("w", encoding="utf-8") as file:
    json.dump(web_data, file, indent=2)

print(f"Observations: {len(points):,}")
print(f"Slope: {slope:.6f}")
print(f"Intercept: {intercept:.6f}")
print(f"R-squared: {r_squared:.6f}")
print(f"Chart saved to: {OUTPUT_PATH}")
print(f"Stats saved to: {STATS_PATH}")
print(f"Web data saved to: {WEB_DATA_PATH}")
print(f"Web points displayed: {sample_size:,}")
