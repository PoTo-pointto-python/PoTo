from __future__ import absolute_import, division, print_function
__metaclass__ = type
from io import StringIO
import sys
import pytest
from units.compat import mock
from units.compat import unittest
from units.compat.mock import MagicMock
from units.compat.mock import patch
from ansible.errors import AnsibleError
from ansible.playbook.play_context import PlayContext
from ansible.plugins.connection import ConnectionBase
from ansible.plugins.loader import become_loader

class TestConnectionBaseClass(unittest.TestCase):

    def setUp(self):
        self.play_context = PlayContext()
        self.play_context.prompt = '[sudo via ansible, key=ouzmdnewuhucvuaabtjmweasarviygqq] password: '
        self.in_stream = StringIO()

    def tearDown(self):
        pass

    def test_subclass_error(self):

        class ConnectionModule1(ConnectionBase):
            pass
        with self.assertRaises(TypeError):
            ConnectionModule1()

        class ConnectionModule2(ConnectionBase):

            def get(self, key):
                super(ConnectionModule2, self).get(key)
        with self.assertRaises(TypeError):
            ConnectionModule2()

    def test_subclass_success(self):

        class ConnectionModule3(ConnectionBase):

            @property
            def transport(self):
                pass

            def _connect(self):
                pass

            def exec_command(self):
                pass

            def put_file(self):
                pass

            def fetch_file(self):
                pass

            def close(self):
                pass
        self.assertIsInstance(ConnectionModule3(self.play_context, self.in_stream), ConnectionModule3)

    def test_check_password_prompt(self):
        local = b'[sudo via ansible, key=ouzmdnewuhucvuaabtjmweasarviygqq] password: \nBECOME-SUCCESS-ouzmdnewuhucvuaabtjmweasarviygqq\n'
        ssh_pipelining_vvvv = b'\ndebug3: mux_master_read_cb: channel 1 packet type 0x10000002 len 251\ndebug2: process_mux_new_session: channel 1: request tty 0, X 1, agent 1, subsys 0, term "xterm-256color", cmd "/bin/sh -c \'sudo -H -S  -p "[sudo via ansible, key=ouzmdnewuhucvuaabtjmweasarviygqq] password: " -u root /bin/sh -c \'"\'"\'echo BECOME-SUCCESS-ouzmdnewuhucvuaabtjmweasarviygqq; /bin/true\'"\'"\' && sleep 0\'", env 0\ndebug3: process_mux_new_session: got fds stdin 9, stdout 10, stderr 11\ndebug2: client_session2_setup: id 2\ndebug1: Sending command: /bin/sh -c \'sudo -H -S  -p "[sudo via ansible, key=ouzmdnewuhucvuaabtjmweasarviygqq] password: " -u root /bin/sh -c \'"\'"\'echo BECOME-SUCCESS-ouzmdnewuhucvuaabtjmweasarviygqq; /bin/true\'"\'"\' && sleep 0\'\ndebug2: channel 2: request exec confirm 1\ndebug2: channel 2: rcvd ext data 67\n[sudo via ansible, key=ouzmdnewuhucvuaabtjmweasarviygqq] password: debug2: channel 2: written 67 to efd 11\nBECOME-SUCCESS-ouzmdnewuhucvuaabtjmweasarviygqq\ndebug3: receive packet: type 98\n'
        ssh_nopipelining_vvvv = b'\ndebug3: mux_master_read_cb: channel 1 packet type 0x10000002 len 251\ndebug2: process_mux_new_session: channel 1: request tty 1, X 1, agent 1, subsys 0, term "xterm-256color", cmd "/bin/sh -c \'sudo -H -S  -p "[sudo via ansible, key=ouzmdnewuhucvuaabtjmweasarviygqq] password: " -u root /bin/sh -c \'"\'"\'echo BECOME-SUCCESS-ouzmdnewuhucvuaabtjmweasarviygqq; /bin/true\'"\'"\' && sleep 0\'", env 0\ndebug3: mux_client_request_session: session request sent\ndebug3: send packet: type 98\ndebug1: Sending command: /bin/sh -c \'sudo -H -S  -p "[sudo via ansible, key=ouzmdnewuhucvuaabtjmweasarviygqq] password: " -u root /bin/sh -c \'"\'"\'echo BECOME-SUCCESS-ouzmdnewuhucvuaabtjmweasarviygqq; /bin/true\'"\'"\' && sleep 0\'\ndebug2: channel 2: request exec confirm 1\ndebug2: exec request accepted on channel 2\n[sudo via ansible, key=ouzmdnewuhucvuaabtjmweasarviygqq] password: debug3: receive packet: type 2\ndebug3: Received SSH2_MSG_IGNORE\ndebug3: Received SSH2_MSG_IGNORE\n\nBECOME-SUCCESS-ouzmdnewuhucvuaabtjmweasarviygqq\ndebug3: receive packet: type 98\n'
        ssh_novvvv = b'[sudo via ansible, key=ouzmdnewuhucvuaabtjmweasarviygqq] password: \nBECOME-SUCCESS-ouzmdnewuhucvuaabtjmweasarviygqq\n'
        dns_issue = b'timeout waiting for privilege escalation password prompt:\nsudo: sudo: unable to resolve host tcloud014\n[sudo via ansible, key=ouzmdnewuhucvuaabtjmweasarviygqq] password: \nBECOME-SUCCESS-ouzmdnewuhucvuaabtjmweasarviygqq\n'
        nothing = b''
        in_front = b'\ndebug1: Sending command: /bin/sh -c \'sudo -H -S  -p "[sudo via ansible, key=ouzmdnewuhucvuaabtjmweasarviygqq] password: " -u root /bin/sh -c \'"\'"\'echo\n'

        class ConnectionFoo(ConnectionBase):

            @property
            def transport(self):
                pass

            def _connect(self):
                pass

            def exec_command(self):
                pass

            def put_file(self):
                pass

            def fetch_file(self):
                pass

            def close(self):
                pass
        c = ConnectionFoo(self.play_context, self.in_stream)
        c.set_become_plugin(become_loader.get('sudo'))
        c.become.prompt = '[sudo via ansible, key=ouzmdnewuhucvuaabtjmweasarviygqq] password: '
        self.assertTrue(c.check_password_prompt(local))
        self.assertTrue(c.check_password_prompt(ssh_pipelining_vvvv))
        self.assertTrue(c.check_password_prompt(ssh_nopipelining_vvvv))
        self.assertTrue(c.check_password_prompt(ssh_novvvv))
        self.assertTrue(c.check_password_prompt(dns_issue))
        self.assertFalse(c.check_password_prompt(nothing))
        self.assertFalse(c.check_password_prompt(in_front))

def test_TestConnectionBaseClass_setUp():
    ret = TestConnectionBaseClass().setUp()

def test_TestConnectionBaseClass_tearDown():
    ret = TestConnectionBaseClass().tearDown()

def test_TestConnectionBaseClass_test_subclass_error():
    ret = TestConnectionBaseClass().test_subclass_error()

def test_TestConnectionBaseClass_test_subclass_success():
    ret = TestConnectionBaseClass().test_subclass_success()

def test_TestConnectionBaseClass_test_check_password_prompt():
    ret = TestConnectionBaseClass().test_check_password_prompt()

def test_ConnectionModule2_get():
    ret = ConnectionModule2().get()

def test_ConnectionModule3_transport():
    ret = ConnectionModule3().transport()

def test_ConnectionModule3__connect():
    ret = ConnectionModule3()._connect()

def test_ConnectionModule3_exec_command():
    ret = ConnectionModule3().exec_command()

def test_ConnectionModule3_put_file():
    ret = ConnectionModule3().put_file()

def test_ConnectionModule3_fetch_file():
    ret = ConnectionModule3().fetch_file()

def test_ConnectionModule3_close():
    ret = ConnectionModule3().close()

def test_ConnectionFoo_transport():
    ret = ConnectionFoo().transport()

def test_ConnectionFoo__connect():
    ret = ConnectionFoo()._connect()

def test_ConnectionFoo_exec_command():
    ret = ConnectionFoo().exec_command()

def test_ConnectionFoo_put_file():
    ret = ConnectionFoo().put_file()

def test_ConnectionFoo_fetch_file():
    ret = ConnectionFoo().fetch_file()

def test_ConnectionFoo_close():
    ret = ConnectionFoo().close()