import click
import json
import elastic
import generator
import plotter
import simple_logger as logger
from datetime import datetime


@click.group()
@click.option('-v', '--verbose', 'verbose_logging',
              is_flag=True, default=False,
              help='Enable verbose logging')
def cli(verbose_logging):
    '''Metanet Analyzer'''
    logger.verbose = verbose_logging


##
# Generator
##
@cli.command()
@click.option('--from', 'from_datetime',
              type=click.DateTime(), required=True,
              help='Starting datetime for sample')
@click.option('--to', 'to_datetime',
              type=click.DateTime(), required=True,
              help='Ending datetime for sample')
@click.option('--density',
              type=float, default=0.02, show_default=True,
              help='Minimum package count density for sample')
@click.option('--interval-gen-range',
              nargs=2, type=int, default=(60, 600), show_default=True,
              help='MIN and MAX seconds for time interval when generating '
              'time interval for batches')
@click.option('--plot',
              is_flag=True, default=False,
              help='Show graph of sample after generation completes')
@click.option('--seed', type=int, default=None,
              help='Seed value used in random generator')
def generate_sample(from_datetime, to_datetime, density, interval_gen_range,
                    plot, seed):
    '''Generate sample packages to use it in visualization'''

    generator.batch_interval_generator_range = interval_gen_range

    sample = generator.generate_sample(
        from_timestamp=datetime.timestamp(from_datetime),
        to_timestamp=datetime.timestamp(to_datetime),
        desired_density=density,
        seed=seed)

    click.secho(json.dumps(sample['packets']))

    if plot:
        plotter.plot_sample_packets(sample['packets'])


##
# ElasticSearch
##
class ElasticSearchContext:
    def __init__(self, hostname, port):
        self.hostname = hostname
        self.port = port


pass_es_context = click.make_pass_decorator(ElasticSearchContext)


@cli.group('es')
@click.option('-h', '--host', '--hostname', 'hostname',
              default='localhost',
              help='ES hostname')
@click.option('-p', '--port',
              default=9200,
              help='ES port')
@click.pass_context
def es_group(ctx, hostname, port):
    '''ElasticSearch commands'''
    logger.log(f'Using ES instance at {hostname}:{port}')
    elastic.verify_connection(hostname, port)
    ctx.obj = ElasticSearchContext(hostname, port)


@es_group.command('setup')
@click.option('-i', '--index', 'index_name',
              type=str, default='metanet',
              help='ES index name')
@click.option('--force', 'force_setup',
              is_flag=True,
              help='Overwite existing index if present')
@pass_es_context
def es_setup(es_ctx, index_name, force_setup):
    '''Initialize ES index'''
    client = elastic.MetanetElastic(
        hostname=es_ctx.hostname,
        port=es_ctx.port,
        index_name=index_name)

    client.setup(force_create=force_setup)


@es_group.command('cleanup')
@click.option('-i', '--index', 'index_name',
              type=str, default='metanet',
              help='ES index name')
@pass_es_context
def es_cleanup(es_ctx, index_name):
    '''Remove ES index and data'''
    client = elastic.MetanetElastic(
        hostname=es_ctx.hostname,
        port=es_ctx.port,
        index_name=index_name)

    click.confirm(f"Index '{index_name}' will be deleted. Continue?",
                  abort=True)

    client.cleanup()


@es_group.command('list-indices')
@pass_es_context
def es_list(es_ctx):
    '''Debug: List all indices in ES'''
    indices = elastic.list_indices(es_ctx.hostname, es_ctx.port)
    for index in indices:
        click.echo(index)


##
# Debug
##
@cli.command()
def debug():
    '''Debug command'''
    pass


if __name__ == "__main__":
    cli()
