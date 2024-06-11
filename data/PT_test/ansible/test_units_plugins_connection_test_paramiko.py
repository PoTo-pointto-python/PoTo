from __future__ import absolute_import, division, print_function
__metaclass__ = type
from io import StringIO
import pytest
from units.compat import unittest
from ansible.plugins.connection import paramiko_ssh
from ansible.playbook.play_context import PlayContext

class TestParamikoConnectionClass(unittest.TestCase):

    def test_paramiko_connection_module(self):
        play_context = PlayContext()
        play_context.prompt = '[sudo via ansible, key=ouzmdnewuhucvuaabtjmweasarviygqq] password: '
        in_stream = StringIO()
        self.assertIsInstance(paramiko_ssh.Connection(play_context, in_stream), paramiko_ssh.Connection)

def test_TestParamikoConnectionClass_test_paramiko_connection_module():
    ret = TestParamikoConnectionClass().test_paramiko_connection_module()