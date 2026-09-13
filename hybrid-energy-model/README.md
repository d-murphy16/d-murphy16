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

These steps only work against a **real local clone** of this repo (not
VS Code's "Open Remote Repository" / github.dev virtual view — that mode
has no real Python environment behind it, so notebooks and installs won't
work there).

### 0. Get the code onto your machine

Same on Mac and Windows. Open a terminal (macOS: Terminal app; Windows:
PowerShell or the VS Code integrated terminal) and run:

```bash
git clone https://github.com/d-murphy16/d-murphy16.git
cd d-murphy16
git checkout claude/claude-code-mechanics-np6sz4
cd hybrid-energy-model
code .
```

`code .` opens this folder in VS Code. From here on, use VS Code's
**integrated terminal** (``Terminal > New Terminal``, or `` Ctrl+` ``) so
you stay inside the folder you just opened.

### 1. Create a Python environment

Pick **one** of the two options below — don't mix them.

**Option A — `venv` (uses your system Python)**

macOS / Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows (PowerShell):
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Windows (cmd.exe):
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

**Option B — Anaconda / Miniconda (if you already use conda)**

Same commands on macOS and Windows, run from the **Anaconda Prompt** on
Windows (or any terminal with `conda` on PATH):

```bash
conda create -n hybrid-energy python=3.11
conda activate hybrid-energy
```

(Or use an existing environment, e.g. `conda activate base` — just make
sure the next step installs into the same environment you'll select as
the notebook kernel later.)

### 2. Install the dependencies + this package

With your environment from step 1 **activated**:

```bash
pip install -r requirements.txt
pip install -e .   # installs the hybrid_energy package itself, in editable mode
```

### 3. Open the notebook and select the right kernel

1. Open `notebooks/01_getting_started.ipynb` in VS Code (Jupyter extension
   required — VS Code usually prompts you to install it automatically).
2. Click the **kernel picker** in the top-right corner of the notebook.
3. Choose the environment you created in step 1 (e.g. `.venv` or
   `hybrid-energy` conda env) — not your system/base Python, unless that's
   what you installed into.
4. Run all cells (▶▶ "Run All", or run cells one by one with `Shift+Enter`).

If you ever see `ModuleNotFoundError: No module named 'hybrid_energy'`,
it means the selected kernel isn't the environment you ran
`pip install -e .` in — go back to step 3 and pick the right one, or
re-run step 2 with the kernel's environment activated.

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
