from __future__ import absolute_import, division, print_function
__metaclass__ = type
import os
import pexpect
import sys
import termios
from ansible.module_utils.six import PY2
args = sys.argv[1:]
env_vars = {'ANSIBLE_ROLES_PATH': './roles', 'ANSIBLE_NOCOLOR': 'True', 'ANSIBLE_RETRY_FILES_ENABLED': 'False'}
try:
    backspace = termios.tcgetattr(sys.stdin.fileno())[6][termios.VERASE]
except Exception:
    backspace = b'\x7f'
if PY2:
    log_buffer = sys.stdout
else:
    log_buffer = sys.stdout.buffer
os.environ.update(env_vars)
playbook = 'pause-1.yml'
pause_test = pexpect.spawn('ansible-playbook', args=[playbook] + args, timeout=10, env=os.environ)
pause_test.logfile = log_buffer
pause_test.expect('Press enter to continue, Ctrl\\+C to interrupt:')
pause_test.send('\r')
pause_test.expect('Task after pause')
pause_test.expect(pexpect.EOF)
pause_test.close()
pause_test = pexpect.spawn('ansible-playbook', args=[playbook] + args, timeout=10, env=os.environ)
pause_test.logfile = log_buffer
pause_test.expect('Press enter to continue, Ctrl\\+C to interrupt:')
pause_test.send('\x03')
pause_test.expect("Press 'C' to continue the play or 'A' to abort")
pause_test.send('C')
pause_test.expect('Task after pause')
pause_test.expect(pexpect.EOF)
pause_test.close()
pause_test = pexpect.spawn('ansible-playbook', args=[playbook] + args, timeout=10, env=os.environ)
pause_test.logfile = log_buffer
pause_test.expect('Press enter to continue, Ctrl\\+C to interrupt:')
pause_test.send('\x03')
pause_test.expect("Press 'C' to continue the play or 'A' to abort")
pause_test.send('A')
pause_test.expect('user requested abort!')
pause_test.expect(pexpect.EOF)
pause_test.close()
playbook = 'pause-2.yml'
pause_test = pexpect.spawn('ansible-playbook', args=[playbook] + args, timeout=10, env=os.environ)
pause_test.logfile = log_buffer
pause_test.expect('Custom prompt:')
pause_test.send('\r')
pause_test.expect('Task after pause')
pause_test.expect(pexpect.EOF)
pause_test.close()
pause_test = pexpect.spawn('ansible-playbook', args=[playbook] + args, timeout=10, env=os.environ)
pause_test.logfile = log_buffer
pause_test.expect('Custom prompt:')
pause_test.send('\x03')
pause_test.expect("Press 'C' to continue the play or 'A' to abort")
pause_test.send('C')
pause_test.expect('Task after pause')
pause_test.expect(pexpect.EOF)
pause_test.close()
pause_test = pexpect.spawn('ansible-playbook', args=[playbook] + args, timeout=10, env=os.environ)
pause_test.logfile = log_buffer
pause_test.expect('Custom prompt:')
pause_test.send('\x03')
pause_test.expect("Press 'C' to continue the play or 'A' to abort")
pause_test.send('A')
pause_test.expect('user requested abort!')
pause_test.expect(pexpect.EOF)
pause_test.close()
playbook = 'pause-3.yml'
pause_test = pexpect.spawn('ansible-playbook', args=[playbook] + args, timeout=10, env=os.environ)
pause_test.logfile = log_buffer
pause_test.expect('Pausing for \\d+ seconds')
pause_test.expect("\\(ctrl\\+C then 'C' = continue early, ctrl\\+C then 'A' = abort\\)")
pause_test.expect('Task after pause')
pause_test.expect(pexpect.EOF)
pause_test.close()
pause_test = pexpect.spawn('ansible-playbook', args=[playbook] + args, timeout=10, env=os.environ)
pause_test.logfile = log_buffer
pause_test.expect('Pausing for \\d+ seconds')
pause_test.expect("\\(ctrl\\+C then 'C' = continue early, ctrl\\+C then 'A' = abort\\)")
pause_test.send('\x03')
pause_test.send('C')
pause_test.expect('Task after pause')
pause_test.expect(pexpect.EOF)
pause_test.close()
pause_test = pexpect.spawn('ansible-playbook', args=[playbook] + args, timeout=10, env=os.environ)
pause_test.logfile = log_buffer
pause_test.expect('Pausing for \\d+ seconds')
pause_test.expect("\\(ctrl\\+C then 'C' = continue early, ctrl\\+C then 'A' = abort\\)")
pause_test.send('\x03')
pause_test.send('A')
pause_test.expect('user requested abort!')
pause_test.expect(pexpect.EOF)
pause_test.close()
playbook = 'pause-4.yml'
pause_test = pexpect.spawn('ansible-playbook', args=[playbook] + args, timeout=10, env=os.environ)
pause_test.logfile = log_buffer
pause_test.expect('Pausing for \\d+ seconds')
pause_test.expect("\\(ctrl\\+C then 'C' = continue early, ctrl\\+C then 'A' = abort\\)")
pause_test.expect('Waiting for two seconds:')
pause_test.expect('Task after pause')
pause_test.expect(pexpect.EOF)
pause_test.close()
pause_test = pexpect.spawn('ansible-playbook', args=[playbook] + args, timeout=10, env=os.environ)
pause_test.logfile = log_buffer
pause_test.expect('Pausing for \\d+ seconds')
pause_test.expect("\\(ctrl\\+C then 'C' = continue early, ctrl\\+C then 'A' = abort\\)")
pause_test.expect('Waiting for two seconds:')
pause_test.send('\x03')
pause_test.send('C')
pause_test.expect('Task after pause')
pause_test.expect(pexpect.EOF)
pause_test.close()
pause_test = pexpect.spawn('ansible-playbook', args=[playbook] + args, timeout=10, env=os.environ)
pause_test.logfile = log_buffer
pause_test.expect('Pausing for \\d+ seconds')
pause_test.expect("\\(ctrl\\+C then 'C' = continue early, ctrl\\+C then 'A' = abort\\)")
pause_test.expect('Waiting for two seconds:')
pause_test.send('\x03')
pause_test.send('A')
pause_test.expect('user requested abort!')
pause_test.expect(pexpect.EOF)
pause_test.close()
playbook = 'pause-5.yml'
pause_test = pexpect.spawn('ansible-playbook', args=[playbook] + args, timeout=10, env=os.environ)
pause_test.logfile = log_buffer
pause_test.expect('Enter some text:')
pause_test.send('hello there')
pause_test.send('\r')
pause_test.expect('Enter some text to edit:')
pause_test.send('hello there')
pause_test.send(backspace * 4)
pause_test.send('ommy boy')
pause_test.send('\r')
pause_test.expect('Enter some text \\(output is hidden\\):')
pause_test.send('supersecretpancakes')
pause_test.send('\r')
pause_test.expect(pexpect.EOF)
pause_test.close()