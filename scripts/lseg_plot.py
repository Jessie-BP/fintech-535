#!/usr/bin/env python3
"""
Pull one year of daily AAPL prices from LSEG and save an interactive Plotly chart.

Credentials:
  GitHub Actions: LSEG_APP_KEY, LSEG_USERNAME, LSEG_PASSWORD (repo secrets).
  Local runs:     same env vars, or ~/.lseg/{app_key,username,password}.

Output: gh-pages/helios/lseg-plot/aapl-price.html (self-contained, Plotly from CDN)
"""

import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import lseg.data as ld
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

RIC = "AAPL.O"
FIELDS = ["OPEN_PRC", "HIGH_1", "LOW_1", "TRDPRC_1", "ACVOL_UNS"]
OUT = Path(__file__).resolve().parent.parent / "gh-pages" / "helios" / "lseg-plot" / "aapl-price.html"


def cred(name: str) -> str | None:
    value = os.environ.get(f"LSEG_{name.upper()}")
    if value:
        return value.strip()
    path = Path.home() / ".lseg" / name
    return path.read_text().strip() if path.is_file() else None


def open_session() -> None:
    app_key, username, password = cred("app_key"), cred("username"), cred("password")
    if not all([app_key, username, password]):
        sys.exit("Missing LSEG_APP_KEY, LSEG_USERNAME, or LSEG_PASSWORD")
    session = ld.session.platform.Definition(
        app_key=app_key,
        grant=ld.session.platform.GrantPassword(username=username, password=password),
        signon_control=True,
    ).get_session()
    session.open()
    ld.session.set_default(session)
    print("LSEG platform session opened")


def fetch() -> pd.DataFrame:
    end = datetime.now(timezone.utc).date()
    start = end.replace(year=end.year - 1)
    df = ld.get_history(
        universe=RIC,
        fields=FIELDS,
        interval="daily",
        start=start.isoformat(),
        end=end.isoformat(),
    )
    df = df.apply(pd.to_numeric, errors="coerce").dropna(subset=["TRDPRC_1"])
    if df.empty:
        sys.exit(f"LSEG returned no rows for {RIC}")
    df.index = pd.to_datetime(df.index)
    return df


def build_figure(df: pd.DataFrame) -> go.Figure:
    df = df.copy()
    df["MA20"] = df["TRDPRC_1"].rolling(20).mean()
    df["MA50"] = df["TRDPRC_1"].rolling(50).mean()

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.75, 0.25], vertical_spacing=0.03)
    fig.add_trace(
        go.Candlestick(
            x=df.index, open=df["OPEN_PRC"], high=df["HIGH_1"], low=df["LOW_1"], close=df["TRDPRC_1"],
            name=RIC, increasing_line_color="#2fbf71", decreasing_line_color="#e5534b",
        ),
        row=1, col=1,
    )
    fig.add_trace(go.Scatter(x=df.index, y=df["MA20"], name="20-day MA", line=dict(width=1.4, color="#e3b341")), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["MA50"], name="50-day MA", line=dict(width=1.4, color="#58a6ff")), row=1, col=1)
    fig.add_trace(go.Bar(x=df.index, y=df["ACVOL_UNS"], name="Volume", marker_color="#5b6b66"), row=2, col=1)

    last = df.iloc[-1]
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    fig.update_layout(
        title=f"{RIC} daily, last close {last['TRDPRC_1']:.2f} on {df.index[-1]:%Y-%m-%d}  ·  updated {stamp}",
        template="plotly_dark",
        paper_bgcolor="#0b1512",
        plot_bgcolor="#0b1512",
        xaxis_rangeslider_visible=False,
        legend=dict(orientation="h", y=1.02, x=0),
        margin=dict(l=50, r=20, t=70, b=30),
        height=640,
    )
    fig.update_yaxes(title_text="Price (USD)", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)
    return fig


def main() -> None:
    open_session()
    try:
        df = fetch()
    finally:
        ld.close_session()
    print(f"Fetched {len(df)} rows, {df.index[0]:%Y-%m-%d} to {df.index[-1]:%Y-%m-%d}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    build_figure(df).write_html(OUT, include_plotlyjs="cdn", full_html=True)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
