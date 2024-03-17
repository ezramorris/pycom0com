"""Provision of a base class for the runner & client."""

from abc import ABC, abstractmethod
from collections import namedtuple
from typing import List, Dict


_AVAILABLE_PARAMS_DOC = """

        Available parameters:
            PortName=<portname>     - set port name to <portname>
                                        (port identifier by default)
            EmuBR={yes|no}          - enable/disable baud rate emulation in the direction
                                        to the paired port (disabled by default)
            EmuOverrun={yes|no}     - enable/disable buffer overrun (disabled by default)
            EmuNoise=<n>            - probability in range 0-0.99999999 of error per
                                        character frame in the direction to the paired port
                                        (0 by default)
            AddRTTO=<n>             - add <n> milliseconds to the total time-out period
                                        for read operations (0 by default)
            AddRITO=<n>             - add <n> milliseconds to the maximum time allowed to
                                        elapse between the arrival of two characters for
                                        read operations (0 by default)
            PlugInMode={yes|no}     - enable/disable plug-in mode, the plug-in mode port
                                        is hidden and can't be open if the paired port is
                                        not open (disabled by default)
            ExclusiveMode={yes|no}  - enable/disable exclusive mode, the exclusive mode
                                        port is hidden if it is open (disabled by default)
            HiddenMode={yes|no}     - enable/disable hidden mode, the hidden mode port is
                                        hidden as it is possible for port enumerators
                                        (disabled by default)
            AllDataBits={yes|no}    - enable/disable all data bits transfer disregard
                                        data bits setting (disabled by default)
            cts=[!]<p>              - wire CTS pin to <p> (rrts by default)
            dsr=[!]<p>              - wire DSR pin to <p> (rdtr by default)
            dcd=[!]<p>              - wire DCD pin to <p> (rdtr by default)
            ri=[!]<p>               - wire RI pin to <p> (!on by default)
        """


class Com0comException(Exception):  
    """Exception class for this package."""


class PortPair(namedtuple('PortPair', 'a b')):
    """Representation of a pair of ports.

    :param a: name of port A e.g. 'CNCA1'
    :type a: str
    :param b: name of port B e.g. 'CNCB1'
    :type b: str
    """

    def __repr__(self):
        return f"{self.__class__.__name__}({self.a!r}, {self.b!r})"

    @property
    def pair_number(self):
        """Pair number; e.g for pair CNCA1/CNCB1, this would be `1`"""

        return int(self.a.lstrip('CNCA'))


class Com0comBase(ABC):
    """Abstact base class to provide common interface to running com0com
    commands, whether directly or via server.
    """

    @abstractmethod
    def install_pair(self, a_params: Dict[str, str], 
                     b_params: Dict[str, str]) -> PortPair:
        """Run `install` command, which creates a port pair.
        
        :param a_params: dict of parameters for CNCA port
        :param b_params: dict of parameters for CNCB port
        :returns: PortPair named tuple representing the port pair
        """ + _AVAILABLE_PARAMS_DOC
    
    @abstractmethod
    def remove_pair(self, port_pair: PortPair) -> None:
        """Run `remove` command, wich removes a port pair.
        
        :param port_pair: PortPair or tuple of 2 strings representing the port 
                          pair
        """

    @abstractmethod
    def disable_all(self) -> None:
        """Run `disable all` command, which disables all ports."""

    @abstractmethod
    def enable_all(self) -> None:
        """Run `enable all` command, which enables all ports."""

    @abstractmethod
    def change_params(self, port: str, params: Dict[str, str]) -> None:
        """Run `change` command, which changes parameters for a given port.
        
        :param port: port identifier e.g. 'CNCA1'
        :param params: dict of parameters to apply to specified port
        """ + _AVAILABLE_PARAMS_DOC

    @abstractmethod
    def list_ports(self) -> Dict[str, Dict[str, str]]:
        """Run `list` command, which retrieves all the ports and their
        parameters.

        Note: unlike the CLI, if a PortName is not set, that parameter won't be
        included (rather than returning '-').

        :returns: a dict of port to a dict of parameters
                  e.g. {
                           'CNCA1': {'EmuBR': 'no'},
                           'CNCB1': {'PortName': 'COM1'}
                        }
        """

    def get_params(self, port: str) -> Dict[str, str]:
        """Wrapper for `list` to return parameters for the specified port.
        
        :param port: port name
        :returns: dict of parameters
        """

        return self.list_ports()[port]
    
    @abstractmethod
    def busynames(self, pattern: str) -> List[str]:
        """Run `busynames` command, which lists existing ports matching the 
        pattern.
        
        :param pattern: pattern to check. '?' represents a single character, 
                        '*' represents 0 or more characters.
        :returns: list of names matching the pattern
        """
