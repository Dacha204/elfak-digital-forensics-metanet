import click
import json
import generator
import utilities
from datetime import datetime


@click.group()
def cli():
    pass


@cli.command()
@click.option('--from', 'from_datetime',
              type=click.DateTime(), required=True)
@click.option('--to', 'to_datetime',
              type=click.DateTime(), required=True)
@click.option('--density',
              type=float, default=0.02, show_default=True)
@click.option('--interval-gen-range',
              nargs=2, type=int, default=(60, 600), show_default=True)
@click.option('--plot',
              is_flag=True, default=False)
@click.option('--seed', type=int, default=None)
def generate_sample(from_datetime, to_datetime,
                    density, interval_gen_range,
                    plot, seed):

    generator.batch_interval_generator_range = interval_gen_range
    sample = generator.generate_sample(
        from_timestamp=datetime.timestamp(from_datetime),
        to_timestamp=datetime.timestamp(to_datetime),
        desired_density=density,
        seed=seed)

    click.secho(json.dumps(sample))
    if plot:
        utilities.plot_sample(sample)


@cli.command()
def debug():
    pass


if __name__ == "__main__":
    cli()
