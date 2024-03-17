"""Module for running com0com commands directly using the com0com CLI."""


from pathlib import Path
import re
import subprocess
from typing import Dict, List
import winreg

from com0com import Com0comBase, Com0comException, PortPair


# https://microsoft.github.io/windows-docs-rs/doc/windows/Win32/Devices/SerialCommunication/constant.COMDB_MAX_PORTS_ARBITRATED.html
MAX_PORTS = 4092


def get_com0com_install_directory():
    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                        R'SOFTWARE\WOW6432Node\com0com') as key:
        return Path(winreg.QueryValueEx(key, 'Install_Dir')[0])


class Com0comRunner(Com0comBase):
    """Class for running Com0com commands."""

    def __init__(self):
        self._com0com_dir = get_com0com_install_directory()

    def run(self, args: List[str]):
        """Run com0com with given `args` and return stdout.
        
        :param args: list of arguments to pass to com0com
        """

        args = [str(self._com0com_dir / 'setupc.exe'), '--silent'] + args
        try:
            # com0com generally prints errors to stdout, so we redirect stderr
            # there so we don't have to handle both streams.
            res = subprocess.run(args, cwd=self._com0com_dir, 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.STDOUT, 
                                 text=True, check=True)
        except subprocess.CalledProcessError as e:
            raise Com0comException(f'com0com command failed: {e.stdout}')
        return res.stdout
          
    def install_pair(self, a_params: Dict[str, str], 
                     b_params: Dict[str, str]) -> PortPair:
        
        def _make_param_str(params: Dict[str, str]):
            """Create string of paramaters for com0com from dict."""
            if not params:
                return '-'
            else:
                return ','.join(f'{k}={v}' for k, v in params.items())

        res = self.run(['install', _make_param_str(a_params), 
                        _make_param_str(b_params)])
        
        # Loop over each output line to find the port ID for A and B ports.
        lines = [line.strip() for line in res.splitlines()]
        a = b = None
        for line in lines:
            # Group 1 (outer group) is the port name.
            # Group 2 (inner group) is 'A' or 'B'.
            match = re.match(r'^(CNC([AB])[0-9]+) ', line)
            if match:
                if match.group(2) == 'A':
                    a = match.group(1)
                else:
                    b = match.group(1)
            if a is not None and b is not None:
                break
        else:
            raise Com0comException('did not get port name for each port')
        return PortPair(a, b)
    
    def remove_pair(self, port_pair: PortPair) -> None:
        pass

    def disable_all(self) -> None:
        pass
    
    def enable_all(self) -> None:
        pass

    def change_params(self, port: str, params: Dict[str, str]) -> None:
        pass

    def list_ports(self) -> Dict[str, Dict[str, str]]:
        pass
    
    def busynames(self, pattern: str) -> List[str]:
        pass
