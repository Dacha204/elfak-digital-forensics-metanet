import click
import subprocess
import simple_logger as logger
import os
import json
import tld
import re
from datetime import datetime

__blacklist_hosts_path = os.path.abspath(os.path.join(
    os.path.abspath(__file__), '../resources/domain-lists/_all.txt'))

__assets_hosts_path = os.path.abspath(os.path.join(
    os.path.abspath(__file__), '../resources/domain-lists/assets/_all.txt'))

__ads_hosts_path = os.path.abspath(os.path.join(
    os.path.abspath(__file__), '../resources/domain-lists/ads/_all.txt'))


def __extract_packets(pcap_file_path,
                      filter="tcp.flags.syn==1 and tcp.flags.ack==0"):

    logger.log_debug(f'Extract "{pcap_file_path}" packets using "{filter}"')

    tshark_result = subprocess.run(["tshark",
                                    f"-r{os.path.abspath(pcap_file_path)}",
                                    f"-Tjson",
                                    f"-eframe.time_epoch",
                                    f"-eip.src",
                                    f"-eip.src_host",
                                    f"-eip.dst",
                                    f"-eip.dst_host",
                                    f"-etcp.srcport",
                                    f"-etcp.dstport",
                                    f"-etcp.stream",
                                    f"-NmnNtdv",
                                    f"{filter}"
                                    ],
                                   capture_output=True,
                                   text=True,
                                   check=True)

    tshark_packets = json.loads(tshark_result.stdout)

    def convert_packet(packet):
        return {
            'timestamp': datetime.fromtimestamp(
                float(packet['_source']['layers']['frame.time_epoch'][0])),
            'tcp_stream': int(packet['_source']['layers']['tcp.stream'][0]),
            'src': {
                'ip': packet['_source']['layers']['ip.src'][0],
                'hostname': str.lower(
                    packet['_source']['layers']['ip.src_host'][0]),
                'port': int(packet['_source']['layers']['tcp.srcport'][0]),
                'domain': None,
                'subdomain': None,
                'fld': None
            },
            'dst': {
                'ip': packet['_source']['layers']['ip.dst'][0],
                'hostname': str.lower(
                    packet['_source']['layers']['ip.dst_host'][0]),
                'port': int(packet['_source']['layers']['tcp.dstport'][0]),
                'domain': None,
                'subdomain': None,
                'fld': None
            },
            'metadata': {
                'resource_type': None
            }
        }

    packets = [convert_packet(packet) for packet in tshark_packets]
    logger.log_debug(f'Extracted {len(packets)} packets')

    return packets


def analize_packets_from_file(pcap_file_path):
    packets = __extract_packets(pcap_file_path)
    return analize_packets(packets)


def analize_packets(packets):
    logger.log_debug("Analize packets from file")

    logger.log_debug("Loading hosts lists")
    asset_hosts = [line.strip() for line in open(__assets_hosts_path, 'r')]
    ads_hosts = [line.strip() for line in open(__ads_hosts_path, 'r')]
    ipv4_regex = r'^(\d{1,3}\.){3}\d{1,3}'

    def analize_packet(packet):
        def fill_tld_data(field):
            try:
                lookup_hostname = packet[field]['hostname']

                if re.match(ipv4_regex, lookup_hostname):
                    logger.log_debug(
                        f'TLD lookup skipped: [{field}] {lookup_hostname}')
                    return

                tld_result = tld.get_tld(url=lookup_hostname,
                                         fix_protocol=True,
                                         as_object=True)
                packet[field]['domain'] = tld_result.domain
                packet[field]['subdomain'] = tld_result.subdomain
                packet[field]['fld'] = tld_result.fld
            except tld.exceptions.TldDomainNotFound:
                logger.log_error(
                    f'TLD lookup failed: [{field}] {lookup_hostname}')

        def fill_resource_type():
            is_asset = any(asset_host in packet['dst']['hostname']
                           for asset_host in asset_hosts)
            if is_asset:
                packet['metadata']['resource_type'] = 'asset'
                return

            is_ad = any(ads_host in packet['dst']['hostname']
                        for ads_host in ads_hosts)
            if is_ad:
                packet['metadata']['resource_type'] = 'ads'
                return

            packet['metadata']['resource_type'] = 'other'

        fill_tld_data('src')
        fill_tld_data('dst')
        fill_resource_type()

    with click.progressbar(packets) as packets_bar:
        for packet in packets_bar:
            analize_packet(packet)

    logger.log_debug("Analize packets completed")
    return packets
