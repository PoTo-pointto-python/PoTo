from __future__ import absolute_import, division, print_function
__metaclass__ = type
ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['preview'], 'supported_by': 'community'}
DOCUMENTATION = '\n---\nmodule: locale_gen\nshort_description: Creates or removes locales\ndescription:\n     - Manages locales by editing /etc/locale.gen and invoking locale-gen.\nversion_added: "1.6"\nauthor:\n- Augustus Kling (@AugustusKling)\noptions:\n    name:\n        description:\n             - Name and encoding of the locale, such as "en_GB.UTF-8".\n        required: true\n    state:\n      description:\n           - Whether the locale shall be present.\n      choices: [ absent, present ]\n      default: present\n'
EXAMPLES = '\n- name: Ensure a locale exists\n  locale_gen:\n    name: de_CH.UTF-8\n    state: present\n'
import os
import re
from subprocess import Popen, PIPE, call
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_native
LOCALE_NORMALIZATION = {'.utf8': '.UTF-8', '.eucjp': '.EUC-JP', '.iso885915': '.ISO-8859-15', '.cp1251': '.CP1251', '.koi8r': '.KOI8-R', '.armscii8': '.ARMSCII-8', '.euckr': '.EUC-KR', '.gbk': '.GBK', '.gb18030': '.GB18030', '.euctw': '.EUC-TW'}

def is_available(name, ubuntuMode):
    """Check if the given locale is available on the system. This is done by
    checking either :
    * if the locale is present in /etc/locales.gen
    * or if the locale is present in /usr/share/i18n/SUPPORTED"""
    if ubuntuMode:
        __regexp = '^(?P<locale>\\S+_\\S+) (?P<charset>\\S+)\\s*$'
        __locales_available = '/usr/share/i18n/SUPPORTED'
    else:
        __regexp = '^#{0,1}\\s*(?P<locale>\\S+_\\S+) (?P<charset>\\S+)\\s*$'
        __locales_available = '/etc/locale.gen'
    re_compiled = re.compile(__regexp)
    fd = open(__locales_available, 'r')
    for line in fd:
        result = re_compiled.match(line)
        if result and result.group('locale') == name:
            return True
    fd.close()
    return False

def is_present(name):
    """Checks if the given locale is currently installed."""
    output = Popen(['locale', '-a'], stdout=PIPE).communicate()[0]
    output = to_native(output)
    return any((fix_case(name) == fix_case(line) for line in output.splitlines()))

def fix_case(name):
    """locale -a might return the encoding in either lower or upper case.
    Passing through this function makes them uniform for comparisons."""
    for (s, r) in LOCALE_NORMALIZATION.items():
        name = name.replace(s, r)
    return name

def replace_line(existing_line, new_line):
    """Replaces lines in /etc/locale.gen"""
    try:
        f = open('/etc/locale.gen', 'r')
        lines = [line.replace(existing_line, new_line) for line in f]
    finally:
        f.close()
    try:
        f = open('/etc/locale.gen', 'w')
        f.write(''.join(lines))
    finally:
        f.close()

def set_locale(name, enabled=True):
    """ Sets the state of the locale. Defaults to enabled. """
    search_string = '#{0,1}\\s*%s (?P<charset>.+)' % name
    if enabled:
        new_string = '%s \\g<charset>' % name
    else:
        new_string = '# %s \\g<charset>' % name
    try:
        f = open('/etc/locale.gen', 'r')
        lines = [re.sub(search_string, new_string, line) for line in f]
    finally:
        f.close()
    try:
        f = open('/etc/locale.gen', 'w')
        f.write(''.join(lines))
    finally:
        f.close()

def apply_change(targetState, name):
    """Create or remove locale.

    Keyword arguments:
    targetState -- Desired state, either present or absent.
    name -- Name including encoding such as de_CH.UTF-8.
    """
    if targetState == 'present':
        set_locale(name, enabled=True)
    else:
        set_locale(name, enabled=False)
    localeGenExitValue = call('locale-gen')
    if localeGenExitValue != 0:
        raise EnvironmentError(localeGenExitValue, 'locale.gen failed to execute, it returned ' + str(localeGenExitValue))

def apply_change_ubuntu(targetState, name):
    """Create or remove locale.

    Keyword arguments:
    targetState -- Desired state, either present or absent.
    name -- Name including encoding such as de_CH.UTF-8.
    """
    if targetState == 'present':
        localeGenExitValue = call(['locale-gen', name])
    else:
        try:
            f = open('/var/lib/locales/supported.d/local', 'r')
            content = f.readlines()
        finally:
            f.close()
        try:
            f = open('/var/lib/locales/supported.d/local', 'w')
            for line in content:
                (locale, charset) = line.split(' ')
                if locale != name:
                    f.write(line)
        finally:
            f.close()
        localeGenExitValue = call(['locale-gen', '--purge'])
    if localeGenExitValue != 0:
        raise EnvironmentError(localeGenExitValue, 'locale.gen failed to execute, it returned ' + str(localeGenExitValue))

def main():
    module = AnsibleModule(argument_spec=dict(name=dict(type='str', required=True), state=dict(type='str', default='present', choices=['absent', 'present'])), supports_check_mode=True)
    name = module.params['name']
    state = module.params['state']
    if not os.path.exists('/etc/locale.gen'):
        if os.path.exists('/var/lib/locales/supported.d/'):
            ubuntuMode = True
        else:
            module.fail_json(msg='/etc/locale.gen and /var/lib/locales/supported.d/local are missing. Is the package "locales" installed?')
    else:
        ubuntuMode = False
    if not is_available(name, ubuntuMode):
        module.fail_json(msg="The locale you've entered is not available on your system.")
    if is_present(name):
        prev_state = 'present'
    else:
        prev_state = 'absent'
    changed = prev_state != state
    if module.check_mode:
        module.exit_json(changed=changed)
    else:
        if changed:
            try:
                if ubuntuMode is False:
                    apply_change(state, name)
                else:
                    apply_change_ubuntu(state, name)
            except EnvironmentError as e:
                module.fail_json(msg=to_native(e), exitValue=e.errno)
        module.exit_json(name=name, changed=changed, msg='OK')
if __name__ == '__main__':
    main()