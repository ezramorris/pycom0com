from typing import Dict, List
from unittest import TestCase

from com0com.base import PortPair, Com0comBase


DUMMY_PORT_PAIR = PortPair('CNCA1', 'CNCB1')


# Function that does nothing.
def nop(*args, **kwargs):
    pass


# Dummy implementation of Com0comBase.
class Com0comDummy(Com0comBase):
    remove_pair = nop
    disable_all = nop
    enable_all = nop
    change_params = nop

    def install_pair(self, a_params: Dict[str, str], 
                     b_params: Dict[str, str]) -> PortPair:
        return DUMMY_PORT_PAIR
    
    def list_ports(self) -> Dict[str, Dict[str, str]]:
        return {
            DUMMY_PORT_PAIR.a: {'foo': 'aaa'},
            DUMMY_PORT_PAIR.b: {'foo': 'bbb'}
        }
    
    def busynames(self, pattern: str) -> List[str]:
        return ['COM1']
    

class PortPairTestCase(TestCase):
    def test_pair_number(self):
        pp = PortPair('CNCA1', 'CNCB1')
        self.assertEqual(pp.pair_number, 1)


class Com0comBaseTestCase(TestCase):
    def test_get_params(self):
        params = Com0comDummy().get_params(DUMMY_PORT_PAIR.a)
        self.assertDictEqual(params, {'foo': 'aaa'})
