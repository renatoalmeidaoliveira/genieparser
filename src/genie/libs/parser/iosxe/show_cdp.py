'''  show_cdp.py

IOSXE parsers for the following show commands:

    * 'show cdp neighbors'
    * 'show cdp neighbors detail'

'''

# Python
import re

# Metaparser
from genie.metaparser import MetaParser
from genie.metaparser.util.schemaengine import Any, Optional


class ShowCdpNeighborsSchema(MetaParser):

    ''' Schema for:
        * 'show cdp neighbors'
    '''

    schema = {
        'cdp':
            {Optional('index'):
                {Any():
                    {'device_id': str,
                     'local_interface': str,
                     'hold_time': int,
                     Optional('capability'): str,
                     Optional('platform'): str,
                     'port_id': str, }, }, },
    }


class ShowCdpNeighborsDetailSchema(MetaParser):
    ''' Schema for:
        * 'show cdp neighbors detail'
    '''

    schema = {
        'total_entries_displayed': int,
        Optional('index'):
            {Any():
                {'device_id': str,
                 'platform': str,
                 'capabilities': str,
                 'local_interface': str,
                 'port_id': str,
                 'hold_time': int,
                 'software_version': str, 
                 'entry_addresses':
                    {Any():
                        {Optional('type'): str, }, },
                 'management_addresses':
                    {Any():
                        {Optional('type'): str, }, },
                 Optional('duplex_mode'): str,
                 Optional('advertisement_ver'): int,
                 Optional('native_vlan'): str,
                 Optional('vtp_mng_domain'): str},
            },
        }


# ================================
# Parser for 'show cdp neighbors'
# ================================
class ShowCdpNeighbors(ShowCdpNeighborsSchema):

    cli_command = 'show cdp neighbors'

    def cli(self, output=None):

        if output is None:
            out = self.device.execute(self.cli_command)
        else:
            out = output

        parsed_dict = {'cdp': {}}

        # R5.cisco.com Gig 0/0 125 R B Gig 0/0 
        p1 = re.compile(r'^(?P<device_id>\S+) +'
                         '(?P<local_interface>[a-zA-Z]+[\s]+[\d\/\.]+) +'
                         '(?P<hold_time>\d+) +(?P<capability>[A-Z\s]+)'
                         '(?: +(?P<platform>[\w\-]+) )? +'
                         '(?P<port_id>[a-zA-Z0-9\/\s]+)$')                     

        # device6 Gig 0 157 R S I C887VA-W- WGi 0 
        p2 = re.compile(r'^(?P<device_id>\S+) +'
                         '(?P<local_interface>[a-zA-Z]+[\s]+[\d\/\.]+) +'
                         '(?P<hold_time>\d+) +(?P<capability>[A-Z\s]+) +'
                         '(?P<platform>\S+) (?P<port_id>[a-zA-Z0-9\/\s]+)$') 

        device_id_index = 0        

        devices_dict_info = {}

        for line in out.splitlines():
            line = line.strip()

            result = p1.match(line)

            if not result:
                result = p2.match(line)
    
            if result:                

                device_id_index += 1

                device_dict = devices_dict_info.setdefault(device_id_index, {})                    

                group = result.groupdict()

                device_dict['device_id'] = group['device_id'].strip()
                device_dict['local_interface'] = group['local_interface'].strip()
                device_dict['hold_time'] = int(group['hold_time'])
                device_dict['capability'] = group['capability'].strip()
                if group['platform']:
                    device_dict['platform'] = group['platform'].strip()
                elif not group['platform']:
                    device_dict['platform'] = ''

                device_dict['port_id'] = group['port_id'].strip()
        if device_id_index:
             parsed_dict.setdefault('cdp', {}).\
                            setdefault('index', devices_dict_info)


        return parsed_dict


# =======================================
# Parser for 'show cdp neighbors details'
# =======================================
class ShowCdpNeighborsDetail(ShowCdpNeighborsDetailSchema):
    cli_command = 'show cdp neighbors detail'

    def cli(self, output=None):

        if output is None:
            out = self.device.execute(self.cli_command)
        else:
            out = output

        # Device ID: R7(9QBDKB58F76)
        deviceid_re = re.compile(r'Device\s+ID:\s*(?P<device_id>\S+)')

        # Platform: N9K-9000v,  Capabilities: Router Switch CVTA phone port
        platf_cap_re = re.compile(r'Platform:\s*(?P<platform>[a-zA-Z\d +\-]+)'
                                 '\s*\,\s*Capabilities:\s*'
                                 '(?P<capabilities>[a-zA-Z\d\s*\-\/]+)')

        # Interface: GigabitEthernet0/0,  Port ID (outgoing port): mgmt0
        interface_port_re = re.compile(r'Interface:\s*'
                                      '(?P<interface>[\w\s\-\/\/]+)\s*\,'
                                      '*\s*Port\s*ID\s*[\(\w\)\s]+:\s*'
                                      '(?P<port_id>\w+)')

        # Native VLAN: 42
        native_vlan_re = re.compile(r'Native\s*VLAN\s*:\s*'
                                    '(?P<native_vlan>\d+)')

        # VTP Management Domain: ‘Accounting Group’
        vtp_mng_domain_re = re.compile(r'VTP\s*Management\s*Domain\s*:\s*'
                                    '\W*(?P<vtp_mng_domain>([a-zA-Z\s]+))\W*')

        # Holdtime : 126 sec
        hold_time_re = re.compile(r'Holdtime\s*:\s*\s*(?P<hold_time>\d+)')

        # advertisement version: 2
        advertver_re = re.compile(r'advertisement\s*version:\s*'
                                 '(?P<advertisement_ver>\d+)')

        # Cisco IOS Software, IOSv Software (VIOS-ADVENTERPRISEK9-M), Version 15.7(3)M3, RELEASE SOFTWARE (fc2)
        software_version_re = re.compile(r'(?P<software_version>[\s\S]+)')


        # Duplex: full
        # Duplex Mode: half
        duplex_re = re.compile(r'Duplex\s*(Mode)*:\s*(?P<duplex_mode>\w+)')

        # Regexes for Flags:
        # Version:
        software_version_flag_re = re.compile(r'Version\s*:\s*')
        # Management address(es):
        mngaddress_re = re.compile(r'Management\s*address\s*\([\w]+\)\s*\:\s*')
        # Entry address(es):
        entryaddress_re = re.compile(r'Entry\s*address\s*\(\w+\)\s*\:\s*')

        # IPv6 address: FE80::203:E3FF:FE6A:BF81  (link-local)
        # IPv6 address: 4000::BC:0:0:C0A8:BC06  (global unicast)
        ipv6_adress_re = re.compile('IPv6\s*address\s*:\s*(?P<ip_adress>\S+)'
                                    '\s*\((?P<type>[\s\w\-]+)\)')
        # IP address: 172.16.1.204
        ipaddress_re = re.compile(r'\S*IP\s*address:\s*(?P<id_adress>\S*)')

        # 0 or 1 flags
        entry_address_flag = 0
        management_address_flag = 0
        software_version_flag = 0

        parsed_dict = {'total_entries_displayed': 0}
        index_device = 0
        devices_dict = {}

        for line in out.splitlines():
            line = line.strip()

            result = deviceid_re.match(line)

            if result:
                index_device += 1
                devices_dict[index_device] = {}
                device_id = result.group('device_id')
                devices_dict[index_device]['device_id'] = device_id
                management_address_flag = 0

                # Init keys
                devices_dict[index_device]['duplex_mode'] = ''
                devices_dict[index_device]['vtp_mng_domain'] = ''
                devices_dict[index_device]['native_vlan'] = ''
                devices_dict[index_device]['management_addresses'] = {}
                devices_dict[index_device]['entry_addresses'] = {}

                continue

            result = platf_cap_re.match(line)

            if result:
                platf_cap_dict = result.groupdict()

                devices_dict[index_device]['capabilities'] = \
                    platf_cap_dict['capabilities']
                devices_dict[index_device]['platform'] = \
                    platf_cap_dict['platform']

                entry_address_flag = 0

                continue

            result = advertver_re.match(line)

            if result:
                devices_dict[index_device]['advertisement_ver'] = \
                    result.group('advertisement_ver')

            result = interface_port_re.match(line)

            if result:
                interface_port_dict = result.groupdict()
                devices_dict[index_device]['port_id'] = \
                    interface_port_dict['port_id']
                devices_dict[index_device]['local_interface'] = \
                    interface_port_dict['interface']
                continue

            result = hold_time_re.match(line)

            if result:
                devices_dict[index_device]['hold_time'] = \
                    int(result.group('hold_time'))
                continue

            if mngaddress_re.match(line):
                management_address_flag = 1

            if entryaddress_re.match(line):
                entry_address_flag = 1

            result = ipaddress_re.match(line)

            if result:

                ip_adress = result.group('id_adress')

                if management_address_flag:
                    devices_dict[index_device]['management_addresses']\
                        [ip_adress] = {}

                if entry_address_flag:
                    devices_dict[index_device]['entry_addresses']\
                        [ip_adress] = {}

                continue

            result = ipv6_adress_re.match(line)

            if result:
                ipv6_address_dict = result.groupdict()

                if management_address_flag:
                    devices_dict[index_device]['management_addresses']\
                        [ipv6_address_dict['ip_adress']] = \
                        {'type': ipv6_address_dict['type']}

                if entry_address_flag:
                    devices_dict[index_device]['entry_addresses']\
                        [ipv6_address_dict['ip_adress']] = \
                        {'type': ipv6_address_dict['type']}

                continue

            result = advertver_re.match(line)

            if result:
                devices_dict[index_device]['advertisement_ver'] = \
                    int(result.group('advertisement_ver'))
                continue

            if software_version_flag_re.match(line):
                software_version_flag = 1
                continue

            result = software_version_re.match(line)

            if result and software_version_flag:
                devices_dict[index_device]['software_version'] = result.group('software_version')
                software_version_flag = 0

                continue

            result = native_vlan_re.match(line)

            if result:
                devices_dict[index_device]['native_vlan'] = \
                    result.group('native_vlan')
                continue

            result = vtp_mng_domain_re.match(line)

            if result:
                devices_dict[index_device]['vtp_mng_domain'] = \
                    result.group('vtp_mng_domain')
                continue

            result = duplex_re.match(line)

            if result:
                devices_dict[index_device]['duplex_mode'] = \
                    result.group('duplex_mode')
                continue

        if index_device:
            parsed_dict.setdefault('index', devices_dict)

        parsed_dict['total_entries_displayed'] = index_device
        return parsed_dict
