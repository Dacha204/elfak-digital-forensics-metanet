import click
import simple_logger as logger
import numpy as np
from datetime import datetime

# Settings
batch_interval_generator_range = (60, 600)
domains = [
    ('google.com', '172.217.18.78'),
    ('youtube.com', '172.217.19.110'),
    ('facebook.com', '31.13.84.36'),
    ('wikipedia.com', '91.198.174.192'),
    ('yahoo.com', '98.138.219.232'),
    ('reddit.com', '151.101.129.140'),
    ('netflix.com', '54.76.60.39'),
    ('vk.com', '87.240.190.67'),
    ('instagram.com', '3.224.210.52'),
    ('linkedin.com', '108.174.10.10'),
    ('microsoft.com', '40.76.4.15'),
    ('twitter.com', '104.244.42.193'),
    ('twitch.tv', '151.101.66.167'),
    ('stackoverflow.com', '151.101.1.69'),
    ('imdb.com', '52.94.228.167'),
    ('github.com', '140.82.113.4'),
    ('accuweather.com', '184.24.150.99')
]


def __generate_packet(timestamp: int):
    '''Generate packet for random domain for specified timestamp'''

    date_time = datetime.fromtimestamp(timestamp)
    random_domain = domains[np.random.randint(0, len(domains))]

    return {
        'timestamp': datetime.fromtimestamp(timestamp),
        'tcp_stream': -1,
        'src': {
            'ip': '127.0.0.1',
            'hostname': '127.0.0.1',
            'port': 13370,
            'domain': None,
            'subdomain': None,
            'fld': None
        },
        'dst': {
            'ip': random_domain[1],
            'hostname': random_domain[0],
            'port': 443,
            'domain': None,
            'subdomain': None,
            'fld': None
        },
        'metadata': {
            'resource_type': None
        }
    }


def __generate_batch_packets(from_timestamp: int,
                             time_interval: int,
                             packet_density: float):
    '''Generate batch packets from specified timestamp, time interval and
    packet density
    '''
    to_timestamp = from_timestamp + time_interval
    packet_count = round(packet_density * time_interval)

    logger.log_debug(
        f'=> Generating batch packets\n'
        f'From     : {datetime.fromtimestamp(from_timestamp).isoformat()}\n'
        f'To       : {datetime.fromtimestamp(to_timestamp).isoformat()}\n'
        f'Interval : {time_interval}s\n'
        f'Density  : {packet_density}\n'
        f'Packets  : {packet_count}')

    generated_timestamps = []
    while len(generated_timestamps) < packet_count:
        timestamp = np.random.randint(from_timestamp, to_timestamp)
        if timestamp not in generated_timestamps:
            generated_timestamps.append(timestamp)

    generated_timestamps.sort()

    generated_packets = [__generate_packet(timestamp)
                         for timestamp in generated_timestamps]

    return generated_packets


def __generate_batch(sample_from_timestamp: int, sample_to_timestamp: int):
    '''Generates random batch in specified timestamp limits'''

    batch_interval = np.random.randint(batch_interval_generator_range[0],
                                       batch_interval_generator_range[1])
    batch_density = np.random.random_sample() / 25  # TODO: Check magic number
    batch_from_timestamp = np.random.randint(sample_from_timestamp,
                                             sample_to_timestamp
                                             - batch_interval)

    batch = __generate_batch_packets(batch_from_timestamp,
                                     batch_interval,
                                     batch_density)

    return {
        'from_timestamp': batch_from_timestamp,
        'time_interval': batch_interval,
        'density': batch_density,
        'packets': batch
    }


def generate_sample(from_timestamp: int,
                    to_timestamp: int,
                    desired_density: float,
                    seed: int = None):
    '''Generates sample package in desired [from_timestamp, to_timestamp]
    interval with desired density of packets
    '''
    sample_interval = to_timestamp - from_timestamp
    if seed is not None:
        np.random.seed(seed)

    def current_density(packets):
        return len(packets)/sample_interval

    sample = []
    while current_density(sample) < desired_density:
        batch = __generate_batch(from_timestamp, to_timestamp)
        sample.extend(batch['packets'])

    sample.sort(key=lambda x: x['timestamp'])

    return {
        'from_timestamp': from_timestamp,
        'to_timestamp': to_timestamp,
        'density': current_density(sample),
        'packets': sample
    }
