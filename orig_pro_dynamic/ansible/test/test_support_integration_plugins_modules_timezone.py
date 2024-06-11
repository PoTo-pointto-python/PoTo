from __future__ import absolute_import, division, print_function
__metaclass__ = type
ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['preview'], 'supported_by': 'community'}
DOCUMENTATION = '\n---\nmodule: timezone\nshort_description: Configure timezone setting\ndescription:\n  - This module configures the timezone setting, both of the system clock and of the hardware clock. If you want to set up the NTP, use M(service) module.\n  - It is recommended to restart C(crond) after changing the timezone, otherwise the jobs may run at the wrong time.\n  - Several different tools are used depending on the OS/Distribution involved.\n    For Linux it can use C(timedatectl) or edit C(/etc/sysconfig/clock) or C(/etc/timezone) and C(hwclock).\n    On SmartOS, C(sm-set-timezone), for macOS, C(systemsetup), for BSD, C(/etc/localtime) is modified.\n    On AIX, C(chtz) is used.\n  - As of Ansible 2.3 support was added for SmartOS and BSDs.\n  - As of Ansible 2.4 support was added for macOS.\n  - As of Ansible 2.9 support was added for AIX 6.1+\n  - Windows and HPUX are not supported, please let us know if you find any other OS/distro in which this fails.\nversion_added: "2.2"\noptions:\n  name:\n    description:\n      - Name of the timezone for the system clock.\n      - Default is to keep current setting.\n      - B(At least one of name and hwclock are required.)\n    type: str\n  hwclock:\n    description:\n      - Whether the hardware clock is in UTC or in local timezone.\n      - Default is to keep current setting.\n      - Note that this option is recommended not to change and may fail\n        to configure, especially on virtual environments such as AWS.\n      - B(At least one of name and hwclock are required.)\n      - I(Only used on Linux.)\n    type: str\n    aliases: [ rtc ]\n    choices: [ local, UTC ]\nnotes:\n  - On SmartOS the C(sm-set-timezone) utility (part of the smtools package) is required to set the zone timezone\n  - On AIX only Olson/tz database timezones are useable (POSIX is not supported).\n    - An OS reboot is also required on AIX for the new timezone setting to take effect.\nauthor:\n  - Shinichi TAMURA (@tmshn)\n  - Jasper Lievisse Adriaanse (@jasperla)\n  - Indrajit Raychaudhuri (@indrajitr)\n'
RETURN = '\ndiff:\n  description: The differences about the given arguments.\n  returned: success\n  type: complex\n  contains:\n    before:\n      description: The values before change\n      type: dict\n    after:\n      description: The values after change\n      type: dict\n'
EXAMPLES = '\n- name: Set timezone to Asia/Tokyo\n  timezone:\n    name: Asia/Tokyo\n'
import errno
import os
import platform
import random
import re
import string
import filecmp
from ansible.module_utils.basic import AnsibleModule, get_distribution
from ansible.module_utils.six import iteritems

class Timezone(object):
    """This is a generic Timezone manipulation class that is subclassed based on platform.

    A subclass may wish to override the following action methods:
        - get(key, phase)   ... get the value from the system at `phase`
        - set(key, value)   ... set the value to the current system
    """

    def __new__(cls, module):
        """Return the platform-specific subclass.

        It does not use load_platform_subclass() because it needs to judge based
        on whether the `timedatectl` command exists and is available.

        Args:
            module: The AnsibleModule.
        """
        if platform.system() == 'Linux':
            timedatectl = module.get_bin_path('timedatectl')
            if timedatectl is not None:
                (rc, stdout, stderr) = module.run_command(timedatectl)
                if rc == 0:
                    return super(Timezone, SystemdTimezone).__new__(SystemdTimezone)
                else:
                    module.warn('timedatectl command was found but not usable: %s. using other method.' % stderr)
                    return super(Timezone, NosystemdTimezone).__new__(NosystemdTimezone)
            else:
                return super(Timezone, NosystemdTimezone).__new__(NosystemdTimezone)
        elif re.match('^joyent_.*Z', platform.version()):
            zonename_cmd = module.get_bin_path('zonename')
            if zonename_cmd is not None:
                (rc, stdout, _) = module.run_command(zonename_cmd)
                if rc == 0 and stdout.strip() == 'global':
                    module.fail_json(msg='Adjusting timezone is not supported in Global Zone')
            return super(Timezone, SmartOSTimezone).__new__(SmartOSTimezone)
        elif re.match('^Darwin', platform.platform()):
            return super(Timezone, DarwinTimezone).__new__(DarwinTimezone)
        elif re.match('^(Free|Net|Open)BSD', platform.platform()):
            return super(Timezone, BSDTimezone).__new__(BSDTimezone)
        elif platform.system() == 'AIX':
            AIXoslevel = int(platform.version() + platform.release())
            if AIXoslevel >= 61:
                return super(Timezone, AIXTimezone).__new__(AIXTimezone)
            else:
                module.fail_json(msg='AIX os level must be >= 61 for timezone module (Target: %s).' % AIXoslevel)
        else:
            return super(Timezone, Timezone).__new__(Timezone)

    def __init__(self, module):
        """Initialize of the class.

        Args:
            module: The AnsibleModule.
        """
        super(Timezone, self).__init__()
        self.msg = []
        self.value = dict()
        for key in module.argument_spec:
            value = module.params[key]
            if value is not None:
                self.value[key] = dict(planned=value)
        self.module = module

    def abort(self, msg):
        """Abort the process with error message.

        This is just the wrapper of module.fail_json().

        Args:
            msg: The error message.
        """
        error_msg = ['Error message:', msg]
        if len(self.msg) > 0:
            error_msg.append('Other message(s):')
            error_msg.extend(self.msg)
        self.module.fail_json(msg='\n'.join(error_msg))

    def execute(self, *commands, **kwargs):
        """Execute the shell command.

        This is just the wrapper of module.run_command().

        Args:
            *commands: The command to execute.
                It will be concatenated with single space.
            **kwargs:  Only 'log' key is checked.
                If kwargs['log'] is true, record the command to self.msg.

        Returns:
            stdout: Standard output of the command.
        """
        command = ' '.join(commands)
        (rc, stdout, stderr) = self.module.run_command(command, check_rc=True)
        if kwargs.get('log', False):
            self.msg.append('executed `%s`' % command)
        return stdout

    def diff(self, phase1='before', phase2='after'):
        """Calculate the difference between given 2 phases.

        Args:
            phase1, phase2: The names of phase to compare.

        Returns:
            diff: The difference of value between phase1 and phase2.
                This is in the format which can be used with the
                `--diff` option of ansible-playbook.
        """
        diff = {phase1: {}, phase2: {}}
        for (key, value) in iteritems(self.value):
            diff[phase1][key] = value[phase1]
            diff[phase2][key] = value[phase2]
        return diff

    def check(self, phase):
        """Check the state in given phase and set it to `self.value`.

        Args:
            phase: The name of the phase to check.

        Returns:
            NO RETURN VALUE
        """
        if phase == 'planned':
            return
        for (key, value) in iteritems(self.value):
            value[phase] = self.get(key, phase)

    def change(self):
        """Make the changes effect based on `self.value`."""
        for (key, value) in iteritems(self.value):
            if value['before'] != value['planned']:
                self.set(key, value['planned'])

    def get(self, key, phase):
        """Get the value for the key at the given phase.

        Called from self.check().

        Args:
            key:   The key to get the value
            phase: The phase to get the value

        Return:
            value: The value for the key at the given phase.
        """
        self.abort('get(key, phase) is not implemented on target platform')

    def set(self, key, value):
        """Set the value for the key (of course, for the phase 'after').

        Called from self.change().

        Args:
            key: Key to set the value
            value: Value to set
        """
        self.abort('set(key, value) is not implemented on target platform')

    def _verify_timezone(self):
        tz = self.value['name']['planned']
        tzfile = '/usr/share/zoneinfo/%s' % tz
        if not os.path.isfile(tzfile):
            self.abort('given timezone "%s" is not available' % tz)
        return tzfile

class SystemdTimezone(Timezone):
    """This is a Timezone manipulation class for systemd-powered Linux.

    It uses the `timedatectl` command to check/set all arguments.
    """
    regexps = dict(hwclock=re.compile('^\\s*RTC in local TZ\\s*:\\s*([^\\s]+)', re.MULTILINE), name=re.compile('^\\s*Time ?zone\\s*:\\s*([^\\s]+)', re.MULTILINE))
    subcmds = dict(hwclock='set-local-rtc', name='set-timezone')

    def __init__(self, module):
        super(SystemdTimezone, self).__init__(module)
        self.timedatectl = module.get_bin_path('timedatectl', required=True)
        self.status = dict()
        if 'name' in self.value:
            self._verify_timezone()

    def _get_status(self, phase):
        if phase not in self.status:
            self.status[phase] = self.execute(self.timedatectl, 'status')
        return self.status[phase]

    def get(self, key, phase):
        status = self._get_status(phase)
        value = self.regexps[key].search(status).group(1)
        if key == 'hwclock':
            if self.module.boolean(value):
                value = 'local'
            else:
                value = 'UTC'
        return value

    def set(self, key, value):
        if key == 'hwclock':
            if value == 'local':
                value = 'yes'
            else:
                value = 'no'
        self.execute(self.timedatectl, self.subcmds[key], value, log=True)

class NosystemdTimezone(Timezone):
    """This is a Timezone manipulation class for non systemd-powered Linux.

    For timezone setting, it edits the following file and reflect changes:
        - /etc/sysconfig/clock  ... RHEL/CentOS
        - /etc/timezone         ... Debian/Ubuntu
    For hwclock setting, it executes `hwclock --systohc` command with the
    '--utc' or '--localtime' option.
    """
    conf_files = dict(name=None, hwclock=None, adjtime='/etc/adjtime')
    allow_no_file = dict(name=True, hwclock=True, adjtime=True)
    regexps = dict(name=None, hwclock=re.compile('^UTC\\s*=\\s*([^\\s]+)', re.MULTILINE), adjtime=re.compile('^(UTC|LOCAL)$', re.MULTILINE))
    dist_regexps = dict(SuSE=re.compile('^TIMEZONE\\s*=\\s*"?([^"\\s]+)"?', re.MULTILINE), redhat=re.compile('^ZONE\\s*=\\s*"?([^"\\s]+)"?', re.MULTILINE))
    dist_tzline_format = dict(SuSE='TIMEZONE="%s"\n', redhat='ZONE="%s"\n')

    def __init__(self, module):
        super(NosystemdTimezone, self).__init__(module)
        if 'name' in self.value:
            tzfile = self._verify_timezone()
            self.update_timezone = ['%s --remove-destination %s /etc/localtime' % (self.module.get_bin_path('cp', required=True), tzfile)]
        self.update_hwclock = self.module.get_bin_path('hwclock', required=True)
        if self.module.get_bin_path('dpkg-reconfigure') is not None:
            if 'name' in self.value:
                self.update_timezone = ['%s -sf %s /etc/localtime' % (self.module.get_bin_path('ln', required=True), tzfile), '%s --frontend noninteractive tzdata' % self.module.get_bin_path('dpkg-reconfigure', required=True)]
            self.conf_files['name'] = '/etc/timezone'
            self.conf_files['hwclock'] = '/etc/default/rcS'
            self.regexps['name'] = re.compile('^([^\\s]+)', re.MULTILINE)
            self.tzline_format = '%s\n'
        else:
            if self.module.get_bin_path('tzdata-update') is not None:
                if not os.path.islink('/etc/localtime'):
                    self.update_timezone = [self.module.get_bin_path('tzdata-update', required=True)]
            self.conf_files['name'] = '/etc/sysconfig/clock'
            self.conf_files['hwclock'] = '/etc/sysconfig/clock'
            try:
                f = open(self.conf_files['name'], 'r')
            except IOError as err:
                if self._allow_ioerror(err, 'name'):
                    distribution = get_distribution()
                    if distribution == 'SuSE':
                        self.regexps['name'] = self.dist_regexps['SuSE']
                        self.tzline_format = self.dist_tzline_format['SuSE']
                    else:
                        self.regexps['name'] = self.dist_regexps['redhat']
                        self.tzline_format = self.dist_tzline_format['redhat']
                else:
                    self.abort('could not read configuration file "%s"' % self.conf_files['name'])
            else:
                sysconfig_clock = f.read()
                f.close()
                if re.search('^TIMEZONE\\s*=', sysconfig_clock, re.MULTILINE):
                    self.regexps['name'] = self.dist_regexps['SuSE']
                    self.tzline_format = self.dist_tzline_format['SuSE']
                else:
                    self.regexps['name'] = self.dist_regexps['redhat']
                    self.tzline_format = self.dist_tzline_format['redhat']

    def _allow_ioerror(self, err, key):
        if err.errno != errno.ENOENT:
            return False
        return self.allow_no_file.get(key, False)

    def _edit_file(self, filename, regexp, value, key):
        """Replace the first matched line with given `value`.

        If `regexp` matched more than once, other than the first line will be deleted.

        Args:
            filename: The name of the file to edit.
            regexp:   The regular expression to search with.
            value:    The line which will be inserted.
            key:      For what key the file is being editted.
        """
        try:
            file = open(filename, 'r')
        except IOError as err:
            if self._allow_ioerror(err, key):
                lines = []
            else:
                self.abort('tried to configure %s using a file "%s", but could not read it' % (key, filename))
        else:
            lines = file.readlines()
            file.close()
        matched_indices = []
        for (i, line) in enumerate(lines):
            if regexp.search(line):
                matched_indices.append(i)
        if len(matched_indices) > 0:
            insert_line = matched_indices[0]
        else:
            insert_line = 0
        for i in matched_indices[::-1]:
            del lines[i]
        lines.insert(insert_line, value)
        try:
            file = open(filename, 'w')
        except IOError:
            self.abort('tried to configure %s using a file "%s", but could not write to it' % (key, filename))
        else:
            file.writelines(lines)
            file.close()
        self.msg.append('Added 1 line and deleted %s line(s) on %s' % (len(matched_indices), filename))

    def _get_value_from_config(self, key, phase):
        filename = self.conf_files[key]
        try:
            file = open(filename, mode='r')
        except IOError as err:
            if self._allow_ioerror(err, key):
                if key == 'hwclock':
                    return 'n/a'
                elif key == 'adjtime':
                    return 'UTC'
                elif key == 'name':
                    return 'n/a'
            else:
                self.abort('tried to configure %s using a file "%s", but could not read it' % (key, filename))
        else:
            status = file.read()
            file.close()
            try:
                value = self.regexps[key].search(status).group(1)
            except AttributeError:
                if key == 'hwclock':
                    return 'n/a'
                elif key == 'adjtime':
                    return 'UTC'
                elif key == 'name':
                    if phase == 'before':
                        return 'n/a'
                    else:
                        self.abort('tried to configure %s using a file "%s", but could not find a valid value in it' % (key, filename))
            else:
                if key == 'hwclock':
                    if self.module.boolean(value):
                        value = 'UTC'
                    else:
                        value = 'local'
                elif key == 'adjtime':
                    if value != 'UTC':
                        value = value.lower()
        return value

    def get(self, key, phase):
        planned = self.value[key]['planned']
        if key == 'hwclock':
            value = self._get_value_from_config(key, phase)
            if value == planned:
                value = self._get_value_from_config('adjtime', phase)
        elif key == 'name':
            value = self._get_value_from_config(key, phase)
            if value == planned:
                if os.path.islink('/etc/localtime'):
                    if os.path.exists('/etc/localtime'):
                        path = os.readlink('/etc/localtime')
                        linktz = re.search('/usr/share/zoneinfo/(.*)', path, re.MULTILINE)
                        if linktz:
                            valuelink = linktz.group(1)
                            if valuelink != planned:
                                value = valuelink
                        else:
                            value = 'n/a'
                    else:
                        value = 'n/a'
                else:
                    try:
                        if not filecmp.cmp('/etc/localtime', '/usr/share/zoneinfo/' + planned):
                            return 'n/a'
                    except Exception:
                        return 'n/a'
        else:
            self.abort('unknown parameter "%s"' % key)
        return value

    def set_timezone(self, value):
        self._edit_file(filename=self.conf_files['name'], regexp=self.regexps['name'], value=self.tzline_format % value, key='name')
        for cmd in self.update_timezone:
            self.execute(cmd)

    def set_hwclock(self, value):
        if value == 'local':
            option = '--localtime'
            utc = 'no'
        else:
            option = '--utc'
            utc = 'yes'
        if self.conf_files['hwclock'] is not None:
            self._edit_file(filename=self.conf_files['hwclock'], regexp=self.regexps['hwclock'], value='UTC=%s\n' % utc, key='hwclock')
        self.execute(self.update_hwclock, '--systohc', option, log=True)

    def set(self, key, value):
        if key == 'name':
            self.set_timezone(value)
        elif key == 'hwclock':
            self.set_hwclock(value)
        else:
            self.abort('unknown parameter "%s"' % key)

class SmartOSTimezone(Timezone):
    """This is a Timezone manipulation class for SmartOS instances.

    It uses the C(sm-set-timezone) utility to set the timezone, and
    inspects C(/etc/default/init) to determine the current timezone.

    NB: A zone needs to be rebooted in order for the change to be
    activated.
    """

    def __init__(self, module):
        super(SmartOSTimezone, self).__init__(module)
        self.settimezone = self.module.get_bin_path('sm-set-timezone', required=False)
        if not self.settimezone:
            module.fail_json(msg='sm-set-timezone not found. Make sure the smtools package is installed.')

    def get(self, key, phase):
        """Lookup the current timezone name in `/etc/default/init`. If anything else
        is requested, or if the TZ field is not set we fail.
        """
        if key == 'name':
            try:
                f = open('/etc/default/init', 'r')
                for line in f:
                    m = re.match('^TZ=(.*)$', line.strip())
                    if m:
                        return m.groups()[0]
            except Exception:
                self.module.fail_json(msg='Failed to read /etc/default/init')
        else:
            self.module.fail_json(msg='%s is not a supported option on target platform' % key)

    def set(self, key, value):
        """Set the requested timezone through sm-set-timezone, an invalid timezone name
        will be rejected and we have no further input validation to perform.
        """
        if key == 'name':
            cmd = 'sm-set-timezone %s' % value
            (rc, stdout, stderr) = self.module.run_command(cmd)
            if rc != 0:
                self.module.fail_json(msg=stderr)
            m = re.match('^\\* Changed (to)? timezone (to)? (%s).*' % value, stdout.splitlines()[1])
            if not (m and m.groups()[-1] == value):
                self.module.fail_json(msg='Failed to set timezone')
        else:
            self.module.fail_json(msg='%s is not a supported option on target platform' % key)

class DarwinTimezone(Timezone):
    """This is the timezone implementation for Darwin which, unlike other *BSD
    implementations, uses the `systemsetup` command on Darwin to check/set
    the timezone.
    """
    regexps = dict(name=re.compile('^\\s*Time ?Zone\\s*:\\s*([^\\s]+)', re.MULTILINE))

    def __init__(self, module):
        super(DarwinTimezone, self).__init__(module)
        self.systemsetup = module.get_bin_path('systemsetup', required=True)
        self.status = dict()
        if 'name' in self.value:
            self._verify_timezone()

    def _get_current_timezone(self, phase):
        """Lookup the current timezone via `systemsetup -gettimezone`."""
        if phase not in self.status:
            self.status[phase] = self.execute(self.systemsetup, '-gettimezone')
        return self.status[phase]

    def _verify_timezone(self):
        tz = self.value['name']['planned']
        out = self.execute(self.systemsetup, '-listtimezones').splitlines()[1:]
        tz_list = list(map(lambda x: x.strip(), out))
        if tz not in tz_list:
            self.abort('given timezone "%s" is not available' % tz)
        return tz

    def get(self, key, phase):
        if key == 'name':
            status = self._get_current_timezone(phase)
            value = self.regexps[key].search(status).group(1)
            return value
        else:
            self.module.fail_json(msg='%s is not a supported option on target platform' % key)

    def set(self, key, value):
        if key == 'name':
            self.execute(self.systemsetup, '-settimezone', value, log=True)
        else:
            self.module.fail_json(msg='%s is not a supported option on target platform' % key)

class BSDTimezone(Timezone):
    """This is the timezone implementation for *BSD which works simply through
    updating the `/etc/localtime` symlink to point to a valid timezone name under
    `/usr/share/zoneinfo`.
    """

    def __init__(self, module):
        super(BSDTimezone, self).__init__(module)

    def __get_timezone(self):
        zoneinfo_dir = '/usr/share/zoneinfo/'
        localtime_file = '/etc/localtime'
        if not os.path.exists(localtime_file):
            self.module.warn('Could not read /etc/localtime. Assuming UTC.')
            return 'UTC'
        zoneinfo_file = localtime_file
        while not zoneinfo_file.startswith(zoneinfo_dir):
            try:
                zoneinfo_file = os.readlink(localtime_file)
            except OSError:
                break
        else:
            return zoneinfo_file.replace(zoneinfo_dir, '')
        for (dname, _, fnames) in sorted(os.walk(zoneinfo_dir)):
            for fname in sorted(fnames):
                zoneinfo_file = os.path.join(dname, fname)
                if not os.path.islink(zoneinfo_file) and filecmp.cmp(zoneinfo_file, localtime_file):
                    return zoneinfo_file.replace(zoneinfo_dir, '')
        self.module.warn('Could not identify timezone name from /etc/localtime. Assuming UTC.')
        return 'UTC'

    def get(self, key, phase):
        """Lookup the current timezone by resolving `/etc/localtime`."""
        if key == 'name':
            return self.__get_timezone()
        else:
            self.module.fail_json(msg='%s is not a supported option on target platform' % key)

    def set(self, key, value):
        if key == 'name':
            zonefile = '/usr/share/zoneinfo/' + value
            try:
                if not os.path.isfile(zonefile):
                    self.module.fail_json(msg='%s is not a recognized timezone' % value)
            except Exception:
                self.module.fail_json(msg='Failed to stat %s' % zonefile)
            suffix = ''.join([random.choice(string.ascii_letters + string.digits) for x in range(0, 10)])
            new_localtime = '/etc/localtime.' + suffix
            try:
                os.symlink(zonefile, new_localtime)
                os.rename(new_localtime, '/etc/localtime')
            except Exception:
                os.remove(new_localtime)
                self.module.fail_json(msg='Could not update /etc/localtime')
        else:
            self.module.fail_json(msg='%s is not a supported option on target platform' % key)

class AIXTimezone(Timezone):
    """This is a Timezone manipulation class for AIX instances.

    It uses the C(chtz) utility to set the timezone, and
    inspects C(/etc/environment) to determine the current timezone.

    While AIX time zones can be set using two formats (POSIX and
    Olson) the prefered method is Olson.
    See the following article for more information:
    https://developer.ibm.com/articles/au-aix-posix/

    NB: AIX needs to be rebooted in order for the change to be
    activated.
    """

    def __init__(self, module):
        super(AIXTimezone, self).__init__(module)
        self.settimezone = self.module.get_bin_path('chtz', required=True)

    def __get_timezone(self):
        """ Return the current value of TZ= in /etc/environment """
        try:
            f = open('/etc/environment', 'r')
            etcenvironment = f.read()
            f.close()
        except Exception:
            self.module.fail_json(msg='Issue reading contents of /etc/environment')
        match = re.search('^TZ=(.*)$', etcenvironment, re.MULTILINE)
        if match:
            return match.group(1)
        else:
            return None

    def get(self, key, phase):
        """Lookup the current timezone name in `/etc/environment`. If anything else
        is requested, or if the TZ field is not set we fail.
        """
        if key == 'name':
            return self.__get_timezone()
        else:
            self.module.fail_json(msg='%s is not a supported option on target platform' % key)

    def set(self, key, value):
        """Set the requested timezone through chtz, an invalid timezone name
        will be rejected and we have no further input validation to perform.
        """
        if key == 'name':
            zonefile = '/usr/share/lib/zoneinfo/' + value
            try:
                if not os.path.isfile(zonefile):
                    self.module.fail_json(msg='%s is not a recognized timezone.' % value)
            except Exception:
                self.module.fail_json(msg='Failed to check %s.' % zonefile)
            cmd = 'chtz %s' % value
            (rc, stdout, stderr) = self.module.run_command(cmd)
            if rc != 0:
                self.module.fail_json(msg=stderr)
            TZ = self.__get_timezone()
            if TZ != value:
                msg = 'TZ value does not match post-change (Actual: %s, Expected: %s).' % (TZ, value)
                self.module.fail_json(msg=msg)
        else:
            self.module.fail_json(msg='%s is not a supported option on target platform' % key)

def main():
    module = AnsibleModule(argument_spec=dict(hwclock=dict(type='str', choices=['local', 'UTC'], aliases=['rtc']), name=dict(type='str')), required_one_of=[['hwclock', 'name']], supports_check_mode=True)
    tz = Timezone(module)
    tz.check(phase='before')
    if module.check_mode:
        diff = tz.diff('before', 'planned')
        diff['after'] = diff.pop('planned')
    else:
        tz.change()
        tz.check(phase='after')
        (after, planned) = tz.diff('after', 'planned').values()
        if after != planned:
            tz.abort('still not desired state, though changes have made - planned: %s, after: %s' % (str(planned), str(after)))
        diff = tz.diff('before', 'after')
    changed = diff['before'] != diff['after']
    if len(tz.msg) > 0:
        module.exit_json(changed=changed, diff=diff, msg='\n'.join(tz.msg))
    else:
        module.exit_json(changed=changed, diff=diff)
if __name__ == '__main__':
    main()

def test_Timezone___new__():
    ret = Timezone().__new__()

def test_Timezone_abort():
    ret = Timezone().abort()

def test_Timezone_execute():
    ret = Timezone().execute()

def test_Timezone_diff():
    ret = Timezone().diff()

def test_Timezone_check():
    ret = Timezone().check()

def test_Timezone_change():
    ret = Timezone().change()

def test_Timezone_get():
    ret = Timezone().get()

def test_Timezone_set():
    ret = Timezone().set()

def test_Timezone__verify_timezone():
    ret = Timezone()._verify_timezone()

def test_SystemdTimezone__get_status():
    ret = SystemdTimezone()._get_status()

def test_SystemdTimezone_get():
    ret = SystemdTimezone().get()

def test_SystemdTimezone_set():
    ret = SystemdTimezone().set()

def test_NosystemdTimezone__allow_ioerror():
    ret = NosystemdTimezone()._allow_ioerror()

def test_NosystemdTimezone__edit_file():
    ret = NosystemdTimezone()._edit_file()

def test_NosystemdTimezone__get_value_from_config():
    ret = NosystemdTimezone()._get_value_from_config()

def test_NosystemdTimezone_get():
    ret = NosystemdTimezone().get()

def test_NosystemdTimezone_set_timezone():
    ret = NosystemdTimezone().set_timezone()

def test_NosystemdTimezone_set_hwclock():
    ret = NosystemdTimezone().set_hwclock()

def test_NosystemdTimezone_set():
    ret = NosystemdTimezone().set()

def test_SmartOSTimezone_get():
    ret = SmartOSTimezone().get()

def test_SmartOSTimezone_set():
    ret = SmartOSTimezone().set()

def test_DarwinTimezone__get_current_timezone():
    ret = DarwinTimezone()._get_current_timezone()

def test_DarwinTimezone__verify_timezone():
    ret = DarwinTimezone()._verify_timezone()

def test_DarwinTimezone_get():
    ret = DarwinTimezone().get()

def test_DarwinTimezone_set():
    ret = DarwinTimezone().set()

def test_BSDTimezone___get_timezone():
    ret = BSDTimezone().__get_timezone()

def test_BSDTimezone_get():
    ret = BSDTimezone().get()

def test_BSDTimezone_set():
    ret = BSDTimezone().set()

def test_AIXTimezone___get_timezone():
    ret = AIXTimezone().__get_timezone()

def test_AIXTimezone_get():
    ret = AIXTimezone().get()

def test_AIXTimezone_set():
    ret = AIXTimezone().set()