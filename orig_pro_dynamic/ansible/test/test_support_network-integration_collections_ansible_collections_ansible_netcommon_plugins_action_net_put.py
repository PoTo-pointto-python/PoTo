from __future__ import absolute_import, division, print_function
__metaclass__ = type
import os
import uuid
import hashlib
from ansible.errors import AnsibleError
from ansible.module_utils._text import to_text, to_bytes
from ansible.module_utils.connection import Connection, ConnectionError
from ansible.plugins.action import ActionBase
from ansible.module_utils.six.moves.urllib.parse import urlsplit
from ansible.utils.display import Display
display = Display()

class ActionModule(ActionBase):

    def run(self, tmp=None, task_vars=None):
        socket_path = None
        network_os = self._get_network_os(task_vars).split('.')[-1]
        persistent_connection = self._play_context.connection.split('.')[-1]
        result = super(ActionModule, self).run(task_vars=task_vars)
        if persistent_connection != 'network_cli':
            result['failed'] = True
            result['msg'] = 'connection type %s is not valid for net_put module, please use fully qualified name of network_cli connection type' % self._play_context.connection
            return result
        try:
            src = self._task.args['src']
        except KeyError as exc:
            return {'failed': True, 'msg': 'missing required argument: %s' % exc}
        src_file_path_name = src
        dest = self._task.args.get('dest')
        proto = self._task.args.get('protocol')
        if proto is None:
            proto = 'scp'
        mode = self._task.args.get('mode')
        if mode is None:
            mode = 'binary'
        if mode == 'text':
            try:
                self._handle_template(convert_data=False)
            except ValueError as exc:
                return dict(failed=True, msg=to_text(exc))
            src = self._task.args.get('src')
            filename = str(uuid.uuid4())
            cwd = self._loader.get_basedir()
            output_file = os.path.join(cwd, filename)
            try:
                with open(output_file, 'wb') as f:
                    f.write(to_bytes(src, encoding='utf-8'))
            except Exception:
                os.remove(output_file)
                raise
        else:
            try:
                output_file = self._get_binary_src_file(src)
            except ValueError as exc:
                return dict(failed=True, msg=to_text(exc))
        if socket_path is None:
            socket_path = self._connection.socket_path
        conn = Connection(socket_path)
        sock_timeout = conn.get_option('persistent_command_timeout')
        if dest is None:
            dest = src_file_path_name
        try:
            changed = self._handle_existing_file(conn, output_file, dest, proto, sock_timeout)
            if changed is False:
                result['changed'] = changed
                result['destination'] = dest
                return result
        except Exception as exc:
            result['msg'] = 'Warning: %s idempotency check failed. Check dest' % exc
        try:
            conn.copy_file(source=output_file, destination=dest, proto=proto, timeout=sock_timeout)
        except Exception as exc:
            if to_text(exc) == 'No response from server':
                if network_os == 'iosxr':
                    result['msg'] = 'Warning: iosxr scp server pre close issue. Please check dest'
            else:
                result['failed'] = True
                result['msg'] = 'Exception received: %s' % exc
        if mode == 'text':
            os.remove(output_file)
        result['changed'] = changed
        result['destination'] = dest
        return result

    def _handle_existing_file(self, conn, source, dest, proto, timeout):
        """
        Determines whether the source and destination file match.

        :return: False if source and dest both exist and have matching sha1 sums, True otherwise.
        """
        cwd = self._loader.get_basedir()
        filename = str(uuid.uuid4())
        tmp_source_file = os.path.join(cwd, filename)
        try:
            conn.get_file(source=dest, destination=tmp_source_file, proto=proto, timeout=timeout)
        except ConnectionError as exc:
            error = to_text(exc)
            if error.endswith('No such file or directory'):
                if os.path.exists(tmp_source_file):
                    os.remove(tmp_source_file)
                return True
        try:
            with open(source, 'r') as f:
                new_content = f.read()
            with open(tmp_source_file, 'r') as f:
                old_content = f.read()
        except (IOError, OSError):
            os.remove(tmp_source_file)
            raise
        sha1 = hashlib.sha1()
        old_content_b = to_bytes(old_content, errors='surrogate_or_strict')
        sha1.update(old_content_b)
        checksum_old = sha1.digest()
        sha1 = hashlib.sha1()
        new_content_b = to_bytes(new_content, errors='surrogate_or_strict')
        sha1.update(new_content_b)
        checksum_new = sha1.digest()
        os.remove(tmp_source_file)
        if checksum_old == checksum_new:
            return False
        return True

    def _get_binary_src_file(self, src):
        working_path = self._get_working_path()
        if os.path.isabs(src) or urlsplit('src').scheme:
            source = src
        else:
            source = self._loader.path_dwim_relative(working_path, 'templates', src)
            if not source:
                source = self._loader.path_dwim_relative(working_path, src)
        if not os.path.exists(source):
            raise ValueError('path specified in src not found')
        return source

    def _get_working_path(self):
        cwd = self._loader.get_basedir()
        if self._task._role is not None:
            cwd = self._task._role._role_path
        return cwd

    def _get_network_os(self, task_vars):
        if 'network_os' in self._task.args and self._task.args['network_os']:
            display.vvvv('Getting network OS from task argument')
            network_os = self._task.args['network_os']
        elif self._play_context.network_os:
            display.vvvv('Getting network OS from inventory')
            network_os = self._play_context.network_os
        elif 'network_os' in task_vars.get('ansible_facts', {}) and task_vars['ansible_facts']['network_os']:
            display.vvvv('Getting network OS from fact')
            network_os = task_vars['ansible_facts']['network_os']
        else:
            raise AnsibleError('ansible_network_os must be specified on this host')
        return network_os

def test_ActionModule_run():
    ret = ActionModule().run()

def test_ActionModule__handle_existing_file():
    ret = ActionModule()._handle_existing_file()

def test_ActionModule__get_binary_src_file():
    ret = ActionModule()._get_binary_src_file()

def test_ActionModule__get_working_path():
    ret = ActionModule()._get_working_path()

def test_ActionModule__get_network_os():
    ret = ActionModule()._get_network_os()