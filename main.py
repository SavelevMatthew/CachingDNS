from server import DNSServer
from config_parse import parse_config
from nice_printers import info, warn


def main():
    info('Starting!')
    info('Parsing config....')
    params = parse_config('config.ini')
    if params['port'] < 80:
        warn('You\'re using port which is less than 80 ({})'
             .format(params['port']))
        warn('Make sure you\'re running this script in sudo mode!')
    info('Creating server on {}:{}'.format(params['ip'], params['port']))
    server = DNSServer(params)
    info('Server was created!')
    server.run()


if __name__ == '__main__':
    main()
