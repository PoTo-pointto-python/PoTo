from __future__ import absolute_import, division, print_function
__metaclass__ = type
import syslog
from itertools import product
import pytest
import ansible.module_utils.basic
from ansible.module_utils.six import PY3

class TestAnsibleModuleLogSmokeTest:
    DATA = [u'Text string', u'Toshio くらとみ non-ascii test']
    DATA = DATA + [d.encode('utf-8') for d in DATA]
    DATA += [b'non-utf8 :\xff: test']

    @pytest.mark.parametrize('msg, stdin', ((m, {}) for m in DATA), indirect=['stdin'])
    def test_smoketest_syslog(self, am, mocker, msg):
        (msg,  stdin) = ((m, {}) for m in DATA)[0]
        mocker.patch('ansible.module_utils.basic.has_journal', False)
        am.log(u'Text string')
        am.log(u'Toshio くらとみ non-ascii test')
        am.log(b'Byte string')
        am.log(u'Toshio くらとみ non-ascii test'.encode('utf-8'))
        am.log(b'non-utf8 :\xff: test')

    @pytest.mark.skipif(not ansible.module_utils.basic.has_journal, reason='python systemd bindings not installed')
    @pytest.mark.parametrize('msg, stdin', ((m, {}) for m in DATA), indirect=['stdin'])
    def test_smoketest_journal(self, am, mocker, msg):
        (msg,  stdin) = ((m, {}) for m in DATA)[0]
        mocker.patch('ansible.module_utils.basic.has_journal', True)
        am.log(u'Text string')
        am.log(u'Toshio くらとみ non-ascii test')
        am.log(b'Byte string')
        am.log(u'Toshio くらとみ non-ascii test'.encode('utf-8'))
        am.log(b'non-utf8 :\xff: test')

class TestAnsibleModuleLogSyslog:
    """Test the AnsibleModule Log Method"""
    PY2_OUTPUT_DATA = [(u'Text string', b'Text string'), (u'Toshio くらとみ non-ascii test', u'Toshio くらとみ non-ascii test'.encode('utf-8')), (b'Byte string', b'Byte string'), (u'Toshio くらとみ non-ascii test'.encode('utf-8'), u'Toshio くらとみ non-ascii test'.encode('utf-8')), (b'non-utf8 :\xff: test', b'non-utf8 :\xff: test'.decode('utf-8', 'replace').encode('utf-8'))]
    PY3_OUTPUT_DATA = [(u'Text string', u'Text string'), (u'Toshio くらとみ non-ascii test', u'Toshio くらとみ non-ascii test'), (b'Byte string', u'Byte string'), (u'Toshio くらとみ non-ascii test'.encode('utf-8'), u'Toshio くらとみ non-ascii test'), (b'non-utf8 :\xff: test', b'non-utf8 :\xff: test'.decode('utf-8', 'replace'))]
    OUTPUT_DATA = PY3_OUTPUT_DATA if PY3 else PY2_OUTPUT_DATA

    @pytest.mark.parametrize('no_log, stdin', product((True, False), [{}]), indirect=['stdin'])
    def test_no_log(self, am, mocker, no_log):
        (no_log,  stdin) = product((True, False), [{}])[0]
        'Test that when no_log is set, logging does not occur'
        mock_syslog = mocker.patch('syslog.syslog', autospec=True)
        mocker.patch('ansible.module_utils.basic.has_journal', False)
        am.no_log = no_log
        am.log('unittest no_log')
        if no_log:
            assert not mock_syslog.called
        else:
            mock_syslog.assert_called_once_with(syslog.LOG_INFO, 'unittest no_log')

    @pytest.mark.parametrize('msg, param, stdin', ((m, p, {}) for (m, p) in OUTPUT_DATA), indirect=['stdin'])
    def test_output_matches(self, am, mocker, msg, param):
        (msg,  param,  stdin) = ((m, p, {}) for (m, p) in OUTPUT_DATA)[0]
        'Check that log messages are sent correctly'
        mocker.patch('ansible.module_utils.basic.has_journal', False)
        mock_syslog = mocker.patch('syslog.syslog', autospec=True)
        am.log(msg)
        mock_syslog.assert_called_once_with(syslog.LOG_INFO, param)

@pytest.mark.skipif(not ansible.module_utils.basic.has_journal, reason='python systemd bindings not installed')
class TestAnsibleModuleLogJournal:
    """Test the AnsibleModule Log Method"""
    OUTPUT_DATA = [(u'Text string', u'Text string'), (u'Toshio くらとみ non-ascii test', u'Toshio くらとみ non-ascii test'), (b'Byte string', u'Byte string'), (u'Toshio くらとみ non-ascii test'.encode('utf-8'), u'Toshio くらとみ non-ascii test'), (b'non-utf8 :\xff: test', b'non-utf8 :\xff: test'.decode('utf-8', 'replace'))]

    @pytest.mark.parametrize('no_log, stdin', product((True, False), [{}]), indirect=['stdin'])
    def test_no_log(self, am, mocker, no_log):
        (no_log,  stdin) = product((True, False), [{}])[0]
        journal_send = mocker.patch('systemd.journal.send')
        am.no_log = no_log
        am.log('unittest no_log')
        if no_log:
            assert not journal_send.called
        else:
            assert journal_send.called == 1
            assert journal_send.call_args[1]['MESSAGE'].endswith('unittest no_log'), 'Message was not sent to log'
            assert 'MODULE' in journal_send.call_args[1]
            assert 'basic.py' in journal_send.call_args[1]['MODULE']

    @pytest.mark.parametrize('msg, param, stdin', ((m, p, {}) for (m, p) in OUTPUT_DATA), indirect=['stdin'])
    def test_output_matches(self, am, mocker, msg, param):
        (msg,  param,  stdin) = ((m, p, {}) for (m, p) in OUTPUT_DATA)[0]
        journal_send = mocker.patch('systemd.journal.send')
        am.log(msg)
        assert journal_send.call_count == 1, 'journal.send not called exactly once'
        assert journal_send.call_args[1]['MESSAGE'].endswith(param)

    @pytest.mark.parametrize('stdin', ({},), indirect=['stdin'])
    def test_log_args(self, am, mocker):
        stdin = ({},)[0]
        journal_send = mocker.patch('systemd.journal.send')
        am.log('unittest log_args', log_args=dict(TEST='log unittest'))
        assert journal_send.called == 1
        assert journal_send.call_args[1]['MESSAGE'].endswith('unittest log_args'), 'Message was not sent to log'
        assert 'MODULE' in journal_send.call_args[1]
        assert 'basic.py' in journal_send.call_args[1]['MODULE']
        assert 'TEST' in journal_send.call_args[1]
        assert 'log unittest' in journal_send.call_args[1]['TEST']

def test_TestAnsibleModuleLogSmokeTest_test_smoketest_syslog():
    ret = TestAnsibleModuleLogSmokeTest().test_smoketest_syslog()

def test_TestAnsibleModuleLogSmokeTest_test_smoketest_journal():
    ret = TestAnsibleModuleLogSmokeTest().test_smoketest_journal()

def test_TestAnsibleModuleLogSyslog_test_no_log():
    ret = TestAnsibleModuleLogSyslog().test_no_log()

def test_TestAnsibleModuleLogSyslog_test_output_matches():
    ret = TestAnsibleModuleLogSyslog().test_output_matches()

def test_TestAnsibleModuleLogJournal_test_no_log():
    ret = TestAnsibleModuleLogJournal().test_no_log()

def test_TestAnsibleModuleLogJournal_test_output_matches():
    ret = TestAnsibleModuleLogJournal().test_output_matches()

def test_TestAnsibleModuleLogJournal_test_log_args():
    ret = TestAnsibleModuleLogJournal().test_log_args()