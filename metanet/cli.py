import click
import generator
import json
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
def generate_sample(from_datetime, to_datetime, density, interval_gen_range):

    generator.batch_interval_generator_range = interval_gen_range
    sample = generator.generate_sample(
        from_timestamp=datetime.timestamp(from_datetime),
        to_timestamp=datetime.timestamp(to_datetime),
        desired_density=density)

    generator.__dbg_plot_sample(sample)
    click.secho(json.dumps(sample))


@cli.command()
def debug():
    pass


if __name__ == "__main__":
    cli()
