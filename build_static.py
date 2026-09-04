"""Build a self-contained GitHub Pages preview from the cached option data."""

from __future__ import annotations

import html
import pickle
from pathlib import Path

import pandas as pd
import plotly.io as pio

from options_surface_app.option_surface_plots import (
    candlestick_figure,
    coverage_heatmap,
    mid_vs_trade_figure,
    price_surface_figure,
)
from options_surface_app.option_surface_utils import (
    attach_underlying,
    flatten_lseg_options,
    pivot_trade_mid,
    summarize_sparsity,
    synthesize_demo_payload,
)

CACHE = Path("option_pipeline_data.pkl")
OUTPUT = Path("docs/index.html")


def _has_mid_price(payload: dict) -> bool:
    columns = payload.get("options", pd.DataFrame()).columns
    if not isinstance(columns, pd.MultiIndex):
        return False
    return any(
        str(value).upper() == "MID_PRICE"
        for level in range(columns.nlevels)
        for value in columns.get_level_values(level)
    )


def load_payload() -> dict:
    with CACHE.open("rb") as handle:
        payload = pickle.load(handle)
    if _has_mid_price(payload):
        return payload
    if payload.get("synthetic"):
        return synthesize_demo_payload(
            ticker_root=payload.get("ticker", "UUUU"), ticker_stock="UUUU.K"
        )
    raise ValueError(
        "The LSEG cache is stale and has no MID_PRICE. Fetch a new cache before building."
    )


def figure_html(figure, include_plotlyjs=False) -> str:
    return pio.to_html(
        figure,
        full_html=False,
        include_plotlyjs="cdn" if include_plotlyjs else False,
        config={"responsive": True, "displaylogo": False},
    )


def main() -> None:
    payload = load_payload()
    tidy = attach_underlying(flatten_lseg_options(payload["options"]), payload["stock"])
    wide = pivot_trade_mid(tidy)
    if wide.empty:
        raise ValueError("No option observations were available to build the site.")

    expiry_counts = wide.groupby("date")["expiry"].nunique()
    richest_dates = expiry_counts[expiry_counts == expiry_counts.max()].index
    asof = richest_dates.max() if len(richest_dates) else wide["date"].max()
    data_through = wide["date"].max()
    stats = summarize_sparsity(wide[wide["date"] == asof])
    median = stats["median_abs_diff"]
    ticker = html.escape(str(payload.get("ticker", "UUUU")))
    source = "Synthetic demonstration data" if payload.get("synthetic") else "Cached LSEG data"
    figures = [
        candlestick_figure(payload["stock"], ticker),
        price_surface_figure(wide, asof, cp="C", ticker=ticker),
        price_surface_figure(wide, asof, cp="P", ticker=ticker),
        mid_vs_trade_figure(wide, asof, ticker=ticker),
        coverage_heatmap(wide, asof, cp="C", field="MID_PRICE"),
        coverage_heatmap(wide, asof, cp="C", field="TRDPRC_1"),
        coverage_heatmap(wide, asof, cp="P", field="MID_PRICE"),
        coverage_heatmap(wide, asof, cp="P", field="TRDPRC_1"),
    ]
    plots = "".join(figure_html(fig, i == 0) for i, fig in enumerate(figures))
    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{ticker} Option Surface Lab</title>
<style>
body{{margin:0;background:#0d1117;color:#e6edf3;font:16px Inter,system-ui,sans-serif}}main{{max-width:1400px;margin:auto;padding:28px}}
h1{{color:#00ffcc;letter-spacing:2px}}.note{{color:#8b949e}}.metrics{{display:flex;gap:16px;flex-wrap:wrap;margin:22px 0}}
.card{{background:#161b22;border:1px solid #30363d;border-radius:9px;padding:16px;flex:1;min-width:190px}}.value{{font-size:30px;color:#00ffcc;font-weight:700}}
.plotly-graph-div{{width:100%!important}}section{{margin:22px 0}}p{{line-height:1.55}}
</style></head><body><main><h1>OPTIONS SURFACE LAB</h1>
<p class="note">{source} · data through {data_through:%Y-%m-%d} · charts shown as of {asof:%Y-%m-%d}</p>
<div class="metrics"><div class="card">Option series<div class="value">{wide['ric'].nunique()}</div></div>
<div class="card">Mid with no print<div class="value">{stats['pct_mid_no_trade']:.0f}%</div></div>
<div class="card">Median |mid − trade|<div class="value">{'n/a' if median is None else f'${median:.3f}'}</div></div></div>
<section>{plots}</section><section class="card"><h2>What the sparse surface tells us</h2>
<p>Price observations are densest around near-the-money strikes and shorter expiries, while the wings and longer maturities contain many empty cells.</p>
<p>Interpolating across empty cells on a $0.50 strike grid is dangerous because it creates apparently precise prices for contracts that may never have been quoted or traded.</p>
<p>I will treat MID_PRICE as the mark of the close and TRDPRC_1 as evidence that an actual trade occurred.</p>
</section></main></body></html>"""
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(page, encoding="utf-8")
    print(f"Built {OUTPUT}")


if __name__ == "__main__":
    main()
