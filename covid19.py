from dataclasses import dataclass
import datetime
from itertools import count

import click


last_updated = datetime.date.fromisoformat("2020-03-14")
eta = 0.01


def to_rates(cases):
    return [(y / x) for x, y in zip(cases, cases[1:])]


class Population:
    @classmethod
    def rates(cls):
        return to_rates(cls.cases)


class Berlin(Population):
    population = 3_700_000
    start = datetime.date.fromisoformat("2020-03-02")
    cases = [1, 3, 6, 9, 15, 24, 28, 40, 48, 90, 137, 174, 216, 265, 300]


class Germany(Population):
    population = 82_900_000
    start = datetime.date.fromisoformat("2020-02-24")
    cases = [16, 18, 21, 26, 53, 66, 117, 150, 188, 242, 354, 534, 684, 847, 1112, 1460, 1884, 2369, 3062, 3795, 4838, 6012]


populations = Berlin, Germany


def predict_once(cases, rate, population):
    return int(cases * rate * (1 - (cases / population)))


def predict(days, cases, rate, population, exponential):
    if exponential:
        return int(cases * rate ** days)
    seq = list(range(days))
    with click.progressbar(seq, label="Predicting cases") as bar:
        for _ in bar:
            cases = predict_once(cases, rate, population)
    return cases


@dataclass
class Prediction:
    days: int
    date: datetime.date
    cases: int
    percent: float

    @classmethod
    def predict(cls, days, cases, rate, population, exponential):
        cases = predict(days, cases, rate, population, exponential)
        percent = min(100, 100 * cases / population)
        date = last_updated + datetime.timedelta(days=days)
        return cls(days, date, cases, percent)

    @classmethod
    def predict_class(cls, days, klass, exponential):
        return cls.predict(days, klass.cases[-1], klass.rates()[-1], klass.population, exponential)


def is_saturated(prediction, previous):
    if prediction.percent >= 100:
        return True

    if previous is not None:
        return prediction.cases / previous.cases < 1 + eta

    return False


def predict_saturation(klass, rate, exponential):
    prediction = None

    for days in count():
        previous = prediction
        prediction = Prediction.predict(days, klass.cases[-1], rate, klass.population, exponential)

        if is_saturated(prediction, previous):
            return prediction


def print_heading(heading):
    print()
    print(heading)
    print("=" * len(heading))
    print()


def print_predictions_by_day(klass, exponential):
    print_heading(f"{klass.__name__}, growth rate = {klass.rates()[-1]:.2f}")
    prediction = None

    for days in count():
        previous = prediction
        prediction = Prediction.predict_class(days, klass, exponential)
        print(f"{prediction.days:3}  {prediction.date:%b %d}  {prediction.percent:6.2f}%  {prediction.cases:8}")

        if is_saturated(prediction, previous):
            break


def print_saturation_date_for_growth_rates(klass, exponential):
    print_heading(f"{klass.__name__}")

    for rate in count(klass.rates()[-1], -0.01):
        if rate < 1.01:
            break
        prediction = predict_saturation(klass, rate, exponential)
        print(f"{rate:.2f}  |  {prediction.days:4} days  |  {prediction.date:%b %d %Y}  {prediction.percent:6.2f}%  {prediction.cases:8}")


@click.group()
def main():
    """COVID-19 analysis"""


@main.command()
def rates():
    for population in populations:
        print_heading(population.__name__)
        for rate in population.rates():
            print(f"{rate:.2f}", end=" ")
        print()


@main.command()
@click.option("--exponential", is_flag=True)
def prediction(exponential):
    for population in populations:
        print_predictions_by_day(population, exponential)


@main.command()
@click.option("--exponential", is_flag=True)
def saturation(exponential):
    for population in populations:
        print_saturation_date_for_growth_rates(population, exponential)
