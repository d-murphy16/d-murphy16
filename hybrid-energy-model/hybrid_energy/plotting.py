"""Quick result plots for a solved hybrid_energy network."""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
import pypsa


def plot_dispatch(n: pypsa.Network, start=None, end=None, ax=None):
    """Stacked generation/discharge vs. load, over an optional time window."""
    gen = n.generators_t.p.loc[start:end]
    battery = n.storage_units_t.p.loc[start:end]
    load = n.loads_t.p.loc[start:end].sum(axis=1)

    if ax is None:
        _, ax = plt.subplots(figsize=(11, 4))

    stacked = gen.clip(lower=0).copy()
    stacked["battery_discharge"] = battery["battery"].clip(lower=0)
    ax.stackplot(stacked.index, stacked.T, labels=stacked.columns)

    battery_charge = battery["battery"].clip(upper=0)
    if (battery_charge != 0).any():
        ax.plot(battery_charge.index, battery_charge, color="black", linestyle="--", label="battery_charge")

    ax.plot(load.index, load, color="red", linewidth=2, label="load")
    ax.set_ylabel("MW")
    ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1.0))
    ax.set_title("Dispatch")
    return ax


def plot_state_of_charge(n: pypsa.Network, start=None, end=None, ax=None):
    soc = n.storage_units_t.state_of_charge.loc[start:end]
    if ax is None:
        _, ax = plt.subplots(figsize=(11, 3))
    ax.plot(soc.index, soc["battery"])
    ax.set_ylabel("MWh")
    ax.set_title("Battery state of charge")
    return ax


def plot_capacities(n: pypsa.Network, ax=None):
    p_nom = n.generators.p_nom_opt.drop(labels=["unmet_demand"], errors="ignore")
    p_nom = pd.concat([p_nom, n.storage_units.p_nom_opt])

    if ax is None:
        _, ax = plt.subplots(figsize=(6, 4))
    p_nom.sort_values(ascending=False).plot(kind="bar", ax=ax, color="steelblue")
    ax.set_ylabel("Optimal capacity (MW)")
    ax.set_title("Optimal component sizing")
    return ax
