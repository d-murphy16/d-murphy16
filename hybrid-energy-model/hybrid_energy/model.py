"""Build and solve a PyPSA hybrid energy system: solar + wind + battery + grid.

Everything here is intentionally simple - one bus, a handful of components.
It's meant as a clear starting point to extend, not a production model.
"""

from __future__ import annotations

import pandas as pd
import pypsa

# Illustrative annualized cost assumptions (USD). Replace with real quotes /
# published cost databases (e.g. NREL ATB) once you're past the demo stage.
DEFAULT_COSTS = {
    "solar_capital": 60_000,  # $ / MW / year
    "wind_capital": 90_000,  # $ / MW / year
    "battery_power_capital": 30_000,  # $ / MW / year
    "battery_energy_capital": 20_000,  # $ / MWh / year
    "grid_price": 150,  # $ / MWh imported from the grid
    "battery_marginal": 1,  # $ / MWh throughput (small, discourages idle cycling)
    "voll": 10_000,  # $ / MWh of unmet demand ("value of lost load")
}


def build_network(
    load_kw: pd.Series,
    solar_cf: pd.Series,
    wind_cf: pd.Series,
    costs: dict | None = None,
    battery_max_hours: float = 4.0,
    grid_available: bool = True,
) -> pypsa.Network:
    """Assemble a single-bus PyPSA network from hourly profiles.

    load_kw, solar_cf, wind_cf must share the same DatetimeIndex.
    solar_cf / wind_cf are capacity factors in [0, 1].
    """
    costs = {**DEFAULT_COSTS, **(costs or {})}

    n = pypsa.Network()
    n.set_snapshots(load_kw.index)
    n.add("Bus", "main")
    n.add("Load", "demand", bus="main", p_set=load_kw.reindex(n.snapshots) / 1000.0)

    n.add(
        "Generator",
        "solar",
        bus="main",
        p_nom_extendable=True,
        capital_cost=costs["solar_capital"],
        marginal_cost=0.0,
        p_max_pu=solar_cf.reindex(n.snapshots),
    )
    n.add(
        "Generator",
        "wind",
        bus="main",
        p_nom_extendable=True,
        capital_cost=costs["wind_capital"],
        marginal_cost=0.0,
        p_max_pu=wind_cf.reindex(n.snapshots),
    )

    # StorageUnit only has one extendable size (p_nom, in MW); energy capacity
    # is p_nom * max_hours. So its annualized cost bundles power + energy cost.
    battery_capital_cost = (
        costs["battery_power_capital"] + costs["battery_energy_capital"] * battery_max_hours
    )
    n.add(
        "StorageUnit",
        "battery",
        bus="main",
        p_nom_extendable=True,
        capital_cost=battery_capital_cost,
        marginal_cost=costs["battery_marginal"],
        max_hours=battery_max_hours,
        efficiency_store=0.95,
        efficiency_dispatch=0.95,
        cyclic_state_of_charge=True,
    )

    if grid_available:
        n.add(
            "Generator",
            "grid_import",
            bus="main",
            p_nom=1e5,
            p_nom_extendable=False,
            marginal_cost=costs["grid_price"],
        )

    # Slack generator so the LP always stays feasible; its optimal dispatch
    # should be ~0 in a well-sized system. Non-zero output = unmet demand.
    n.add(
        "Generator",
        "unmet_demand",
        bus="main",
        p_nom=1e6,
        p_nom_extendable=False,
        marginal_cost=costs["voll"],
    )

    return n


def optimize_capacity(n: pypsa.Network, solver_name: str = "highs"):
    """Run the joint capacity + dispatch optimization. Returns (status, condition)."""
    return n.optimize(solver_name=solver_name)


def capacity_summary(n: pypsa.Network) -> pd.DataFrame:
    """Optimal sizes chosen by the solver, in MW (and MWh for the battery)."""
    rows = []
    for name, gen in n.generators.iterrows():
        if name == "unmet_demand":
            continue
        rows.append({"component": name, "type": "generator", "p_nom_opt_MW": gen.p_nom_opt})

    for name, su in n.storage_units.iterrows():
        rows.append(
            {
                "component": name,
                "type": "storage",
                "p_nom_opt_MW": su.p_nom_opt,
                "energy_capacity_opt_MWh": su.p_nom_opt * su.max_hours,
            }
        )
    return pd.DataFrame(rows).set_index("component")


def cost_summary(n: pypsa.Network) -> dict:
    """Total annualized system cost split into capital vs operational."""
    capital = (n.generators.p_nom_opt * n.generators.capital_cost).sum()
    capital += (n.storage_units.p_nom_opt * n.storage_units.capital_cost).sum()

    weights = n.snapshot_weightings.objective
    operational = (n.generators_t.p * n.generators.marginal_cost).mul(weights, axis=0).sum().sum()
    operational += (
        (n.storage_units_t.p.abs() * n.storage_units.marginal_cost)
        .mul(weights, axis=0)
        .sum()
        .sum()
    )

    unmet_mwh = float((n.generators_t.p["unmet_demand"] * weights).sum()) if "unmet_demand" in n.generators_t.p else 0.0

    return {
        "capital_cost_per_year": float(capital),
        "operational_cost_per_year": float(operational),
        "total_cost_per_year": float(capital + operational),
        "unmet_demand_MWh": unmet_mwh,
    }
