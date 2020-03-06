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
# Setup
##


class SetupContext:
    def __init__(self, es_host, es_port, kibana_host, kibana_port):
        self.es_host = es_host
        self.es_port = es_port
        self.kibana_host = kibana_host
        self.kibana_port = kibana_port


pass_setup_context = click.make_pass_decorator(SetupContext)


@cli.group('setup')
@click.option('--es-host', 'es_host',
              default='localhost',
              help='Elasticsearch host')
@click.option('--es-port', 'es_port',
              default=9200,
              help='Elasticsearch port')
@click.option('--kibana-host', 'kibana_host',
              default='localhost',
              help='Kibana host')
@click.option('--kibana-port', 'kibana_port',
              default=5601,
              help='Kibana port')
@click.pass_context
def setup_group(ctx, es_host, es_port, kibana_host, kibana_port):
    '''Setup commands'''
    logger.log_info("Verify connection...")
    try:
        elastic.verify_connection(es_host, es_port)
        kibana.verify_connection(kibana_host, kibana_port)
    except ConnectionError as ex:
        raise click.ClickException(ex) from ex
    logger.log_info("Elasticsearch and Kibana available")

    ctx.obj = SetupContext(es_host, es_port, kibana_host, kibana_port)


@setup_group.command('init')
@click.option('--kibana-templates', 'kibana_templates',
              type=click.File('r'),
              help='ndjson file with kibana exported dashboards',
              default=os.path.abspath(os.path.join(
                  os.path.abspath(__file__),
                  '../resources/kibana/kibana.ndjson')))
@click.option('--force', 'force_setup',
              is_flag=True,
              help='Overwite existing configuration if present')
@pass_setup_context
def setup_init(setup_ctx, kibana_templates, force_setup):
    '''Configure Elasticsearch and Kibana for MetaNet usage'''
    logger.log_info("Setup Elasticsearch and Kibana")
    es = elastic.MetanetElastic(setup_ctx.es_host, setup_ctx.es_port)

    logger.log_info("Check for existing configuration...")
    es_configured = es.is_configured()
    kibana_configured = kibana.is_configured(setup_ctx.kibana_host,
                                             setup_ctx.kibana_port)
    if es_configured or kibana_configured:
        if not force_setup:
            logger.log_error("Existing configuration detected. "
                             "Use --force flag to overwrite")
            return
        logger.log_info("Existing configuration detected, overwriting... ")
    else:
        logger.log_info("No existing configuration detected")

    kibana.configure(setup_ctx.kibana_host, setup_ctx.kibana_port,
                     kibana_templates, force_setup)
    es.configure(force_setup)

    logger.log_info("Setup completed")


@setup_group.command('cleanup')
@pass_setup_context
def setup_cleanup(setup_ctx):
    '''Remove Elasticsearch and Kibana configuration'''
    logger.log_info("Cleanup configuration")

    logger.log_info("Removing Elasticsearch configuration...")
    es = elastic.MetanetElastic(setup_ctx.es_host, setup_ctx.es_port)
    es.cleanup()

    logger.log_info("Removing Kibana configuration...")
    kibana.cleanup(setup_ctx.kibana_host, setup_ctx.kibana_port)

    logger.log_info("Cleanup configuration completed")


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

    result = {
        'packets': packets,
        'count': len(packets)
    }

    click.echo(json.dumps(result, default=str, indent=2 if pretty else None))


@pcap_group.command('analyze')
@click.option('--es-host', 'es_host',
              default='localhost',
              help='Elasticsearch host')
@click.option('--es-port', 'es_port',
              default=9200,
              help='Elasticsearch port')
@pass_pcap_context
def pcap_analize(pcap_ctx, es_host, es_port):
    '''Analyze packets in PCAP file'''

    logger.log_info("Process packets")
    logger.log_info("Verify connection...")
    try:
        elastic.verify_connection(es_host, es_port)
    except ConnectionError as ex:
        raise click.ClickException(ex) from ex
    logger.log_info("Elasticsearch available")

    es = elastic.MetanetElastic(
        hostname=es_host,
        port=es_port)

    logger.log_info("Verify Elasticsearch configuration...")
    if not es.is_configured():
        logger.log_error("Elasticsearch is not configured. "
                         "Use 'setup init' to configure")
        return
    logger.log_info("Elasticsearch configured")

    logger.log_info("Processing packets...")
    packets = pcap.analize_packets(pcap_ctx.file_path)

    logger.log_info("Indexing packets...")
    es.truncate()
    es.index_packets(packets)

    logger.log_info("Process packets completed")

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


if __name__ == "__main__":
    cli()
