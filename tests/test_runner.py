from pathlib import Path
from subprocess import CalledProcessError, CompletedProcess
import unittest
from unittest.mock import patch, MagicMock, Mock
import winreg

from com0com import Com0comException
from com0com.runner import (
    Com0comRunner, get_com0com_install_directory, MAX_PORTS
)


# Re-usable patch for get_com0com_install_directory. `new` is used so it 
# doesn't create a parameter when used as a decorator.
get_com0com_install_directory_patch = patch(
    'com0com.runner.get_com0com_install_directory',
    new=Mock(return_value=Path(R'C:\com0com'))
)


def patch_run(stdout: str):
    """Patch `run()`, returning the specified stdout."""

    return patch.object(Com0comRunner, 'run', return_value=stdout)


class GetCom0comInstallDirectoryTestCase(unittest.TestCase):
    @patch('winreg.QueryValueEx', return_value=[R'C:\com0com'])
    @patch('winreg.OpenKey')
    def test_ok(self, openkey_mock: Mock, queryvalueex_mock: Mock):
        # Dummy return value/context manager for registry handle object.
        key = MagicMock()
        key.__enter__.return_value = key
        openkey_mock.return_value = key

        res = get_com0com_install_directory()
        openkey_mock.assert_called_once_with(
            winreg.HKEY_LOCAL_MACHINE, 
            R'SOFTWARE\WOW6432Node\com0com'
        )
        queryvalueex_mock.assert_called_once_with(key, 'Install_Dir')
        self.assertEqual(res, Path(R'C:\com0com'))


@get_com0com_install_directory_patch
@patch('subprocess.run')
class RunTestCase(unittest.TestCase):
    def test_ok(self, run_mock: Mock):
        args = ['foo', 'bar']
        run_mock.return_value = CompletedProcess(args, 0, 'hello')
        
        runner = Com0comRunner()
        res = runner.run(args)
        
        run_mock.assert_called_once()
        self.assertEqual(run_mock.call_args[0][0][-2:], args)
        self.assertEqual(res, 'hello')

    def test_error(self, run_mock: Mock):
        args = []
        run_mock.side_effect = CalledProcessError(1, args, 'error')

        runner = Com0comRunner()
        # Check that the right exeption is called, and contains the stdout.
        with self.assertRaisesRegex(Com0comException, 'error'):
            runner.run(args)


@get_com0com_install_directory_patch
@patch_run('       CNCA1 PortName=-\n       CNCB1 PortName=-\nrubbish\n\n')
class InstallPairTestCase(unittest.TestCase):
    def test_no_params(self, run_mock: Mock):
        pair = Com0comRunner().install_pair({}, {})
        run_mock.assert_called_once_with(['install', '-', '-'])
        self.assertEqual(pair.a, 'CNCA1')
        self.assertEqual(pair.b, 'CNCB1')

    def test_port_a_1_param(self, run_mock: Mock):
        pair = Com0comRunner().install_pair({'foo': 'bar'}, {})
        run_mock.assert_called_once_with(['install', 'foo=bar', '-'])
        self.assertEqual(pair.a, 'CNCA1')
        self.assertEqual(pair.b, 'CNCB1')

    def test_port_b_2_params(self, run_mock: Mock):
        pair = Com0comRunner().install_pair({}, {'foo': 'bar', 'faz': 'baz'})
        run_mock.assert_called_once_with(['install', '-', 'foo=bar,faz=baz'])
        self.assertEqual(pair.a, 'CNCA1')
        self.assertEqual(pair.b, 'CNCB1')

    def test_both_port_params(self, run_mock: Mock):
        pair = Com0comRunner().install_pair({'aa': 'bb', 'cc': 'dd'}, 
                                            {'ee': 'ff'})
        run_mock.assert_called_once_with(['install', 'aa=bb,cc=dd', 'ee=ff'])
        self.assertEqual(pair.a, 'CNCA1')
        self.assertEqual(pair.b, 'CNCB1')

    def test_one_name_not_returned(self, run_mock: Mock):
        run_mock.return_value = '       CNCA1 PortName=-\nrubbish\n\n'
        with self.assertRaises(Com0comException):
            Com0comRunner().install_pair({}, {})
