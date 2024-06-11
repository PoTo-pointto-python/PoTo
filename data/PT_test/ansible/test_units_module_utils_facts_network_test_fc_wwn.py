from __future__ import absolute_import, division, print_function
__metaclass__ = type
from ansible.module_utils.facts.network import fc_wwn
from units.compat.mock import Mock
LSDEV_OUTPUT = '\nfcs0 Defined   00-00 8Gb PCI Express Dual Port FC Adapter (df1000f114108a03)\nfcs1 Available 04-00 8Gb PCI Express Dual Port FC Adapter (df1000f114108a03)\n'
LSCFG_OUTPUT = '\n  fcs1             U78CB.001.WZS00ZS-P1-C9-T1  8Gb PCI Express Dual Port FC Adapter (df1000f114108a03)\n\n        Part Number.................00E0806\n        Serial Number...............1C4090830F\n        Manufacturer................001C\n        EC Level.................... D77161\n        Customer Card ID Number.....577D\n        FRU Number..................00E0806\n        Device Specific.(ZM)........3\n        Network Address.............10000090FA551508\n        ROS Level and ID............027820B7\n        Device Specific.(Z0)........31004549\n        Device Specific.(ZC)........00000000\n        Hardware Location Code......U78CB.001.WZS00ZS-P1-C9-T1\n'
FCINFO_OUTPUT = '\nHBA Port WWN: 10000090fa1658de\n        Port Mode: Initiator\n        Port ID: 30100\n        OS Device Name: /dev/cfg/c13\n        Manufacturer: Emulex\n        Model: LPe12002-S\n        Firmware Version: LPe12002-S 2.01a12\n        FCode/BIOS Version: Boot:5.03a0 Fcode:3.01a1\n        Serial Number: 4925381+13090001ER\n        Driver Name: emlxs\n        Driver Version: 3.3.00.1 (2018.01.05.16.30)\n        Type: N-port\n        State: online\n        Supported Speeds: 2Gb 4Gb 8Gb\n        Current Speed: 8Gb\n        Node WWN: 20000090fa1658de\n        NPIV Not Supported\n'

def mock_get_bin_path(cmd, required=False):
    result = None
    if cmd == 'lsdev':
        result = '/usr/sbin/lsdev'
    elif cmd == 'lscfg':
        result = '/usr/sbin/lscfg'
    elif cmd == 'fcinfo':
        result = '/usr/sbin/fcinfo'
    return result

def mock_run_command(cmd):
    rc = 0
    if 'lsdev' in cmd:
        result = LSDEV_OUTPUT
    elif 'lscfg' in cmd:
        result = LSCFG_OUTPUT
    elif 'fcinfo' in cmd:
        result = FCINFO_OUTPUT
    else:
        rc = 1
        result = 'Error'
    return (rc, result, '')

def test_get_fc_wwn_info(mocker):
    module = Mock()
    inst = fc_wwn.FcWwnInitiatorFactCollector()
    mocker.patch.object(module, 'get_bin_path', side_effect=mock_get_bin_path)
    mocker.patch.object(module, 'run_command', side_effect=mock_run_command)
    d = {'aix6': ['10000090FA551508'], 'sunos5': ['10000090fa1658de']}
    for (key, value) in d.items():
        mocker.patch('sys.platform', key)
        wwn_expected = {'fibre_channel_wwn': value}
        assert wwn_expected == inst.collect(module=module)