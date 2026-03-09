#!.venv/bin/python
import os
import argparse

def usage_info(name: str, exit_code: int = 0):
    script_name = str(name)
    code = int(exit_code)
    
    print(script_name, "usage [AOD] [MAC_ADDRESS] [IP_ADDRESS] [HOSTNAME]")
    print()
    print(script_name, "...where [AOD] is one of (ADD|OLD|DEL)")
    print(script_name, "...where [MAC_ADDRESS] is a colon separated xx:xx:xx:xx:xx:xx")
    print(script_name, "...where [IP_ADDRESS] is a IPv4 address")
    print(script_name, "...where [HOSTNAME] is the non-fully-qualified hostname")
    print()
    print(f'{script_name} ADD c2:b9:8f:da:1b:29 192.168.12.150 testme')
    print(f'{script_name} OLD c2:b9:8f:da:1b:29 192.168.12.150 testme')
    print(f'{script_name} DEL c2:b9:8f:da:1b:29 192.168.12.150 testme')
    print(f'DNSMASQ_DOMAIN=ha.home.arpa {script_name} ADD c2:b9:8f:da:1b:29 192.168.12.150 testme')
    
    if code > 0:
      exit(code)


#PROG_NAME = __main__
PROG_NAME = 'ddns_psupdate'
PROG_VERSION = '%(prog)s 1.0.0'
#DESCRIPTION = 'usage text'
DESCRIPTION = 'Update DNS upon DHCP lease'
LOG_LEVELS = ["DEBUG", "NOTICE", "INFO", "WARN", "CRIT", "ERROR"]
DEFAULT_CONFIG_FILE_PATH = "config/app.yml"
DEFAULT_LOG_LEVEL = 'INFO'
DEBUG = os.environ.get("DEBUG", False)

parser = \
    argparse.ArgumentParser(prog=PROG_NAME, description=DESCRIPTION)

parser.add_argument('--version', action='version', version=PROG_VERSION)
parser.add_argument('-l', '--log', default=DEFAULT_LOG_LEVEL, 
    help='Set the logging level', choices=LOG_LEVELS)
parser.add_argument('CMD', nargs=1, help='Command is one of (ADD|OLD|DEL)')
parser.add_argument('MAC', nargs=1, 
    help='MAC Address is a colon separated xx:xx:xx')
parser.add_argument('IPADDR', nargs=1, help='IPv4 address')
parser.add_argument('HOSTNAME', nargs=1, help='Short hostname')
parser.add_argument('-c', '--config', default=DEFAULT_CONFIG_FILE_PATH,
    help=f'The file path to the configuration file')

#parser.print_help()



args = parser.parse_args()
#if args and args.log.upper() in LEVELS:
    #LOG_LEVEL = args.log.upper()

#print(args.log)
#print(args.command)
print(f'DEBUG={DEBUG}')
print(f'LOG_LEVEL={args.log}')
#print(args)

opts = ["ADD", "OLD", "DEL"]
if args.CMD[0].upper() in opts:
    print(f"{args.IPADDR[0]} is {args.HOSTNAME[0]}")

if args.config:
    if not (os.path.isfile(args.config) and os.access(args.config, os.R_OK)):
      print(f"ERROR: The given file path at {args.config} does not exist.")
      exit(1)
    else:
       print(f"Found configuration file at {args.config}")

print("success!")
exit(0)
