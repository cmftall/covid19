import click


population = click.option("--population", "-p", default="Germany", show_default=True)
data_source = click.option("--data-source", "-s", default="rki", show_default=True)
with_immunity = click.option("--immunity/--no-immunity", "with_immunity", default=True)