import json
import click
import simple_logger as logger
from elasticsearch import Elasticsearch, ElasticsearchException


def verify_connection(hostname, port):
    es_client = Elasticsearch(
        hosts=[{'host': hostname, 'port': port}])

    logger.log_debug(f'Trying to connect to ES instance '
                     f'at {hostname}:{port}')

    try:
        if not es_client.ping():
            raise ConnectionError(f'Connection failed for ES instance '
                                  f'at {hostname}:{port}')

        logger.log_debug(f'Instance available')
    except Exception as ex:
        logger.log_error(ex)
        raise


def list_indices(hostname='localhost', port=9200):
    es_client = Elasticsearch(
        hosts=[{'host': hostname, 'port': port}])

    indices = es_client.indices.get_alias('*')
    return indices


class MetanetElastic:
    def __init__(self, hostname='localhost', port=9200, index_name='metanet'):
        self.hostname = hostname
        self.port = port
        self.index_name = index_name
        self.__es_client = Elasticsearch(
            hosts=[{'host': hostname, 'port': port}])

    def setup(self, force_create=False):
        logger.log_debug(f"ES index setup")

        index_mapping = {
            "settings": {
                "index.mapping.ignore_malformed": True
            },
            "mappings": {
                "properties": {
                    "datetime": {
                        "properties": {
                            "timestamp": {
                                "type": "date",
                                "format": "epoch_second"
                            },
                            "year": {"type": "integer"},
                            "month": {"type": "integer"},
                            "day": {"type": "integer"},
                            "hour": {"type": "integer"},
                            "minute": {"type": "integer"},
                            "second": {"type": "integer"}
                        }
                    },
                    "tcp_stream": {"type": "integer"},
                    "source": {
                        "properties": {
                            "ip": {"type": "ip"},
                            "port": {"type": "integer"},
                            "hostname": {"type": "text"},
                            "domain": {"type": "keyword"},
                            "subdomain": {"type": "keyword"},
                            "fld": {"type": "keyword"}
                        }
                    },
                    "destination": {
                        "properties": {
                            "ip": {"type": "ip"},
                            "port": {"type": "integer"},
                            "hostname": {"type": "text"},
                            "domain": {"type": "keyword"},
                            "subdomain": {"type": "keyword"},
                            "fld": {"type": "keyword"}
                        },
                    },
                    "resource": {
                        "properties": {
                            "type": {"type": "keyword"},
                            "category": {"type": "keyword"}
                        }
                    }
                }
            }
        }

        if self.__es_client.indices.exists(self.index_name):
            logger.log_info(f"Found existing index '{self.index_name}'")
            if not force_create:
                logger.log_error("Setup aborted. Use --force to overwrite")
                return
            logger.log_warning(f"Removing existing index '{self.index_name}'")
            self.__es_client.indices.delete(self.index_name)

        self.__es_client.indices.create(self.index_name,
                                        json.dumps(index_mapping))

        logger.log_info(f"Index '{self.index_name}' created: "
                        f"{json.dumps(index_mapping)}")

    def cleanup(self):
        logger.log_info("ES cleanup...")

        if self.__es_client.indices.exists(self.index_name):
            logger.log_info(f"Removing index '{self.index_name}'")
            self.__es_client.indices.delete(self.index_name)
        else:
            logger.log_warning(f"Index '{self.index_name}' not found")

        logger.log_info("Cleanup completed")

    def index_packets(self, packets):
        logger.log_info(f'Indexing {len(packets)} packets in ES')

        def convert_to_document(packet):
            return {
                'datetime': {
                    'timestamp': packet['timestamp'].timestamp(),
                    'year': packet['timestamp'].year,
                    'month': packet['timestamp'].month,
                    'day': packet['timestamp'].day,
                    'hour': packet['timestamp'].hour,
                    'minute': packet['timestamp'].minute,
                    'second': packet['timestamp'].second
                },
                'tcp_stream': packet['tcp_stream'],
                'source': {
                    'ip': packet['src']['ip'],
                    'port': packet['src']['port'],
                    'hostname': packet['src']['hostname'],
                    'domain': packet['src']['domain'],
                    'subdomain': packet['src']['subdomain'],
                    'fld': packet['src']['fld']
                },
                'destination': {
                    'ip': packet['dst']['ip'],
                    'port': packet['dst']['port'],
                    'hostname': packet['dst']['hostname'],
                    'domain': packet['dst']['domain'],
                    'subdomain': packet['dst']['subdomain'],
                    'fld': packet['dst']['fld']
                },
                'resource': {
                    'type': packet['metadata']['resource_type'],
                    'category': None
                }
            }

        with click.progressbar(packets, label='Indexing') as packets_bar:
            for packet in packets_bar:
                self.__es_client.index(index=self.index_name,
                                       body=convert_to_document(packet))

        logger.log_info("Indexing complete")
