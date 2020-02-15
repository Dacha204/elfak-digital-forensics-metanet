import click
import numpy as np
from datetime import datetime

# Settings
verbose = False
batch_interval_generator_range = (60, 600)
domains = [
    'google.com',
    'youtube.com',
    'facebook.com',
    'wikipedia.com',
    'yahoo.com',
    'reddit.com',
    'netflix.com',
    'vk.com',
    'instagram.com',
    'linkedin.com',
    'microsoft.com',
    'twitter.com',
    'twitch.tv',
    'stackoverflow.com',
    'imdb.com',
    'github.com',
    'accuweather.com',
]


def __generate_packet(timestamp: int):
    '''Generate packet for random domain for specified timestamp'''

    date_time = datetime.fromtimestamp(timestamp)

    return {
        'datetime': {
            'timestamp': timestamp,
            'year': date_time.year,
            'month': date_time.month,
            'day': date_time.day,
            'hour': date_time.hour,
            'minute': date_time.minute,
            'second': date_time.second
        },
        'domain': domains[np.random.randint(0, len(domains))]
    }


def __generate_batch_packets(from_timestamp: int,
                             time_interval: int,
                             packet_density: float):
    '''Generate batch packets from specified timestamp, time interval and
    packet density
    '''
    to_timestamp = from_timestamp + time_interval
    packet_count = round(packet_density * time_interval)

    if verbose:
        click.secho(
            f'=> Generating batch packets\n'
            f'From     : {datetime.fromtimestamp(from_timestamp).isoformat()}\n'
            f'To       : {datetime.fromtimestamp(to_timestamp).isoformat()}\n'
            f'Interval : {time_interval}s\n'
            f'Density  : {packet_density}\n'
            f'Packets  : {packet_count}',
            dim=True)

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

    sample.sort(key=lambda x: x['datetime']['timestamp'])

    return {
        'from_timestamp': from_timestamp,
        'to_timestamp': to_timestamp,
        'density': current_density(sample),
        'packets': sample
    }
