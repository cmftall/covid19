import dataclasses
import datetime
from itertools import accumulate
from typing import Any, Dict

import click
import humanize
from tabulate import tabulate

from .main import main
from .utils import heading
from .. import simulation
from ..data import Population, populations


headers = [
    "days",
    "date",
    "infections\n(accumulated)",
    "infections",
    "infections%",
    "recoveries",
    "recoveries%",
    "cases",
    "cases%",
    "immune",
    "immune%",
]


def format_state(
    state: simulation.State, population: Population, accumulated_infections: int
) -> Dict[str, str]:
    result = dataclasses.asdict(state)
    result["date"] = population.start + datetime.timedelta(days=state.days - 1)
    result["infections\n(accumulated)"] = accumulated_infections
    result["infections%"] = state.infections / population.population
    result["recoveries%"] = state.recoveries / population.population
    result["cases%"] = state.cases / population.population
    result["immune%"] = state.immune / population.population

    for key, value in result.items():
        if isinstance(value, int):
            result[key] = humanize.intcomma(value)
        elif isinstance(value, float):
            result[key] = f"{100 * result[key]:.1f}%"
        elif isinstance(value, datetime.date):
            result[key] = (
                value.strftime("* %b %d %Y")
                if value == datetime.datetime.now().date()
                else value.strftime("%b %d %Y")
            )

    return [result[header] for header in headers]


def print_predictions(population: Population) -> None:
    states = list(simulation.simulate(population))
    rows = [
        format_state(state, population, accumulated_infections)
        for state, accumulated_infections in zip(
            states, accumulate(state.infections for state in states)
        )
    ]
    table = tabulate(rows, headers, stralign="right")
    text = f"""\
{heading(population.name)}

population = {humanize.intcomma(population.population)}
p = {states[-1].probability:.2f}

{table}
"""
    print(text)


@main.command()
def simulate():
    for population in populations:
        print_predictions(population)
