import os
import click
import json
import generator
import plotter
import elastic
import kibana
import simple_logger as logger
import pcap
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
    logger.log_debug(f'Using ES instance at {hostname}:{port}')
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
# Kibana setup
##


class KibanaContext:
    def __init__(self, hostname, port):
        self.hostname = hostname
        self.port = port


pass_kibana_context = click.make_pass_decorator(KibanaContext)


@cli.group('kibana')
@click.option('-h', '--host', '--hostname', 'hostname',
              default='localhost',
              help='Kibana hostname')
@click.option('-p', '--port',
              default=5601,
              help='Kibana port')
@click.pass_context
def kibana_group(ctx, hostname, port):
    '''Kibana commands'''
    logger.log_debug(f'Using Kibana instance at {hostname}:{port}')
    kibana.verify_connection(hostname, port)
    ctx.obj = KibanaContext(hostname, port)


@kibana_group.command('setup')
@click.option('-i', '--index', 'index_name',
              type=str, default='metanet',
              help='ES index name')
@click.option('--force', 'force_setup',
              is_flag=True,
              help='Overwite existing dashboards if present')
@click.option('-r', '--resources', 'resource_file',
              type=click.File('r'),
              help='ndjson file with kibana exported dashboards',
              default=os.path.abspath(os.path.join(
                  os.path.abspath(__file__),
                  '../resources/kibana/kibana.ndjson')))
@pass_kibana_context
def kibana_setup(kibana_ctx, index_name, resource_file, force_setup):
    '''Initialize Kibana dashboards'''
    kibana.dashboard_setup(
        host=kibana_ctx.hostname,
        port=kibana_ctx.port,
        resource_file=resource_file,
        overwrite=force_setup
    )


##
# PCAP Analyizer
##
class PcapContext:
    def __init__(self, file_path):
        self.file_path = file_path


pass_pcap_context = click.make_pass_decorator(PcapContext)


@cli.group('pcap')
@click.option('-f', '--file', 'pcap_path',
              type=click.Path(exists=True),
              required=True,
              help='PCAP file path')
@click.pass_context
def pcap_group(ctx, pcap_path):
    '''PCAP commands'''
    logger.log_debug(f'Using PCAP file "{pcap_path}"')
    ctx.obj = PcapContext(pcap_path)


@pcap_group.command('scan')
@click.option('--pretty', is_flag=True)
@pass_pcap_context
def pcap_scan(pcap_ctx, pretty):
    packets = pcap.analize_packets(pcap_ctx.file_path)
    click.echo(json.dumps(packets, default=str, indent=2 if pretty else None))


@pcap_group.command('analyze')
@click.option('-h', '--host', '--hostname', 'hostname',
              default='localhost',
              help='ES hostname')
@click.option('-p', '--port',
              default=9200,
              help='ES port')
@pass_pcap_context
def pcap_analize(pcap_ctx, hostname, port):
    elastic.verify_connection(hostname, port)
    packets = pcap.analize_packets(pcap_ctx.file_path)

    client = elastic.MetanetElastic(
        hostname=hostname,
        port=port)

    client.index_packets(packets)
##
# Debug
##
@cli.command()
def debug():
    '''Debug command'''
    pass


if __name__ == "__main__":
    cli()
