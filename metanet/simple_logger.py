import click
from datetime import datetime

verbose = False


def log_info(message):
    click.secho(f'[{datetime.now().isoformat()}][INF] {message}')


def log_warning(message):
    click.secho(f'[{datetime.now().isoformat()}][WRN] {message}',
                fg='yellow')


def log_error(message):
    click.secho(f'[{datetime.now().isoformat()}][ERR] {message}',
                fg='red')


def log_debug(message):
    if verbose:
        click.secho(f'[{datetime.now().isoformat()}][DBG] {message}',
                    dim=True)


def log(message):
    log_info(message)
