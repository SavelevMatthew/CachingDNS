from nice_printers import info, error, warn
from byte_parser import parse_dns_query, get_dns_response
from storage import CacheStorage
import socket


class DNSServer:
    def __init__(self, params):
        self.parent_server = params['parent_dns']
        self.params = params
        self.cache = CacheStorage(params)

    def run(self):
        info('Running!')
        while True:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                sock.bind((self.params['ip'], self.params['port']))
                data, addr = sock.recvfrom(self.params['max_packet_size'])
                info('Packet was received, parsing...')
                if not data:
                    error('Empty data received, exiting....')
                    break
                parsed_data = parse_dns_query(data)
                info('Packet was parsed, checking cache...')
                entities = self.cache.get_entity(parsed_data)
                if entities is None:
                    response = self.request_from_parent(data)
                    if response is not None:
                        parsed_response = parse_dns_query(response)
                        self.cache.put_entity(parsed_response)
                    else:
                        warn('Timeout was reached...returning empty result!')
                        response = get_dns_response(parsed_data[0],
                                                    parsed_data[1], [], [], [])
                else:
                    response = get_dns_response(parsed_data[0],
                                                parsed_data[1], entities,
                                                [], [])
                info('Sending response')
                sock.sendto(response, addr)
            finally:
                sock.close()
                self.cache.save()

    def request_from_parent(self, data):
        info('Asking for parent DNS')
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(5.0)
        try:
            sock.bind(('', 0))
            sock.sendto(data, (self.parent_server, self.params['port']))
            return sock.recvfrom(self.params['max_packet_size'])[0]
        except socket.timeout:
            return None
        finally:
            sock.close()
