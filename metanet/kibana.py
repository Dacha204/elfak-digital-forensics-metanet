import click
import requests
import simple_logger as logger


def verify_connection(hostname, port):
    logger.log_debug(f'Trying to connect to Kibana instance '
                     f'at {hostname}:{port}')

    try:
        response = requests.get(f'http://{hostname}:{port}/api/status')
        response.raise_for_status()

        kibana_status = response.json()
        logger.log_debug(f"Instance available. "
                         f"Version: {kibana_status['version']['number']}")
    except requests.exceptions.RequestException as ex:
        logger.log_error(ex)
        raise ConnectionError("Failed to connect to Kibana") from ex


def __create_space(host, port):
    logger.log_debug("Creating kibana 'metanet' space")

    request_data = {
        "id": "metanet",
        "name": "MetaNet",
        "description": "MetaNet Space",
        "color": "#1562A2",
        "initials": "MN",
    }

    response = requests.post(
        url=f'http://{host}:{port}/api/spaces/space',
        headers={"kbn-xsrf": "true"},
        json=request_data)

    response.raise_for_status()
    logger.log_debug("Kibana 'metanet' space created")


def __delete_space(host, port):
    logger.log_debug("Deleting kibana 'metanet' space")

    response = requests.delete(
        url=f'http://{host}:{port}/api/spaces/space/metanet',
        headers={"kbn-xsrf": "true"}
    )

    response.raise_for_status()
    logger.log_debug("Kibana 'metanet' space deleted")


def __space_exists(host, port):
    response = requests.get(
        url=f'http://{host}:{port}/api/spaces/space/metanet')

    if response.status_code == 200:
        logger.log_debug("Kibana 'metanet' space exists")
        return True
    else:
        logger.log_debug(f"Kibana 'metanet' space not found. "
                         f"Code: {response.status_code}")
        return False


def is_configured(host, port):
    return __space_exists(host, port)


def configure(host, port, resource_file, overwrite=False):
    logger.log_debug(
        f'Setup kibanna using objects from "{resource_file.name}"')

    if not __space_exists(host, port):
        __create_space(host, port)

    logger.log_debug('Importing kibana objects')
    import_response = requests.post(
        url=f'http://{host}:{port}/s/metanet/api/saved_objects/_import?'
            f'overwrite={overwrite}',
        headers={"kbn-xsrf": "true"},
        files={'file': resource_file}
    )

    import_status = import_response.json()
    if not import_status['success']:
        logger.log_error(f"Failed to setup kibana: {import_status['errors']}. "
                         f"Use --force to overwrite existing objects")
        return

    logger.log_debug(f"Kibana setup completed: "
                    f"successCount={import_status['successCount']}")


def cleanup(host, port):
    if is_configured(host, port):
        logger.log_debug("Cleaning up kibana")
        __delete_space(host, port)
        logger.log_debug("Cleanup completed")
    else:
        logger.log_debug("Nothing to cleanup")
