# Hybrid Energy Model

A small toolkit for sizing and simulating a hybrid renewable energy system
(solar PV + wind + battery + grid connection) using
[PyPSA](https://pypsa.org/).

## What it does

Given an hourly electricity **load profile** and **solar/wind resource
profiles**, the model:

1. Builds a PyPSA network with a solar generator, a wind generator, a
   battery storage unit, and an optional grid connection.
2. Runs a **capacity expansion optimization** — PyPSA decides the optimal
   size (MW / MWh) of each component to meet the load at minimum cost.
3. Runs an **hourly dispatch simulation** using the optimized sizes, so you
   can see exactly how the system behaves hour by hour.
4. Produces summary plots: dispatch stack, state of charge, cost breakdown.

The starter version ships with **synthetic example data** (a made-up load
profile and solar/wind resource shapes) so you can run the whole pipeline
immediately. Swap in your own CSVs later — see "Using your own data" below.

## Setup

```bash
cd hybrid-energy-model
python3 -m venv .venv
source .venv/bin/activate   # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -e .   # installs the hybrid_energy package itself, in editable mode
```

Then open `notebooks/01_getting_started.ipynb` in VS Code (with the Jupyter
extension) and run all cells.

## Project layout

```
hybrid-energy-model/
├── hybrid_energy/        # reusable Python package
│   ├── data.py           # synthetic profile generators / CSV loaders
│   ├── model.py           # builds and solves the PyPSA network
│   └── plotting.py       # result plots
├── notebooks/
│   └── 01_getting_started.ipynb
├── data/                 # put your own CSVs here
└── requirements.txt
```

## Using your own data

Replace the synthetic profiles in the notebook with CSVs that have an
hourly `DatetimeIndex` and one value column, e.g.:

- `data/load_kw.csv` — electricity demand per hour
- `data/solar_cf.csv` — solar capacity factor per hour (0–1)
- `data/wind_cf.csv` — wind capacity factor per hour (0–1)

`hybrid_energy/data.py` has a `load_profile_csv()` helper for this.
