# Python
import unittest
from unittest.mock import Mock

# PyATS
from pyats.topology import (Device, loader)

# Metaparser
from genie.metaparser.util.exceptions import SchemaEmptyParserError

# junos ping
from genie.libs.parser.junos.ping import (Ping)


class TestShowArp(unittest.TestCase):
    """ Unit tests for:
            * ping {addr} count {count}
    """

    device = Device(name='aDevice')
    maxDiff = None
    empty_output = {'execute.return_value': ''}

    golden_output = {'execute.return_value': '''
        ping 10.189.5.94 count 5
        PING 10.189.5.94 (10.189.5.94): 56 data bytes
        64 bytes from 10.189.5.94: icmp_seq=0 ttl=62 time=2.261 ms
        64 bytes from 10.189.5.94: icmp_seq=1 ttl=62 time=1.823 ms
        64 bytes from 10.189.5.94: icmp_seq=2 ttl=62 time=2.399 ms
        64 bytes from 10.189.5.94: icmp_seq=3 ttl=62 time=2.218 ms
        64 bytes from 10.189.5.94: icmp_seq=4 ttl=62 time=2.173 ms

        --- 10.189.5.94 ping statistics ---
        5 packets transmitted, 5 packets received, 0% packet loss
        round-trip min/avg/max/stddev = 1.823/2.175/2.399/0.191 ms
    '''}
    
    golden_parsed_output = {}

    def test_empty(self):
        self.device = Mock(**self.empty_output)
        obj = Ping(device=self.device)
        with self.assertRaises(SchemaEmptyParserError):
            obj.parse(addr='10.189.5.94', count='5')

    def test_golden(self):
        self.device = Mock(**self.golden_output)
        obj = Ping(device=self.device)
        parsed_output = obj.parse(addr='10.189.5.94', count='5')
        self.assertEqual(parsed_output, self.golden_parsed_output)

if __name__ == '__main__':
    unittest.main()