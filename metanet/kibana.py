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
        raise


def dashboard_setup(host, port, resource_file, overwrite=False):

    logger.log_info(
        f'Setup kibanna dashboard. Using objects from "{resource_file.name}"')

    files = {'file': resource_file}
    headers = {"kbn-xsrf": "true"}

    logger.log_info('Importing kibana objects')

    import_response = requests.post(
        url=f'http://{host}:{port}/api/saved_objects/_import?overwrite={overwrite}',
        headers=headers,
        files=files
    )

    import_status = import_response.json()
    if not import_status['success']:
        logger.log_error(f"Failed to setup kibana: {import_status['errors']}")
        return

    logger.log_info(
        f"Kibana setup completed: successCount={import_status['successCount']}")
