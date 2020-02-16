import json
import simple_logger as logger
from elasticsearch import Elasticsearch, ElasticsearchException


class MetanetElastic:
    def __init__(self, hostname='localhost', port=9200, index_name='metanet'):
        self.hostname = hostname
        self.port = port
        self.index_name = index_name
        self.__es_client = Elasticsearch(
            hosts=[{'host': hostname, 'port': port}])

    def setup(self, force_create=False):
        logger.log_debug(
            f"==> ES index setup\n"
            f"Host  : {self.hostname}\n"
            f"Port  : {self.port}\n"
            f"Index : {self.index_name}\n"
            f"Force : {force_create}")

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
                    "destination": {
                        "properties": {
                            "ip": {
                                "properties": {
                                    "ip_address": {"type": "ip"},
                                    "port": {"type": "integer"}
                                }
                            },
                            "dns": {
                                "properties": {
                                    "hostname": {"type": "text"},
                                    "domain": {"type": "keyword"},
                                    "subdomain": {"type": "keyword"},
                                    "fld": {"type": "keyword"}
                                }
                            },
                            "resource_type": {"type": "keyword"},
                            "category": {"type": "keyword"}
                        }
                    }
                }
            }
        }

        if self.__es_client.indices.exists(self.index_name):
            logger.log(f"Found existing index '{self.index_name}'")
            if not force_create:
                logger.log_error("Setup aborted. Use --force to overwrite")
                return
            logger.log_warning(f"Removing existing index '{self.index_name}'")
            self.__es_client.indices.delete(self.index_name)

        self.__es_client.indices.create(self.index_name,
                                        json.dumps(index_mapping))

        logger.log(f"Index '{self.index_name}' created: "
                   f"{json.dumps(index_mapping)}")

    def cleanup(self):
        logger.log("==> ES cleanup...")

        if self.__es_client.indices.exists(self.index_name):
            logger.log(f"Removing index '{self.index_name}'")
            self.__es_client.indices.delete(self.index_name)
        else:
            logger.log_warning(f"Index '{self.index_name}' not found")

        logger.log("Cleanup completed")


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
