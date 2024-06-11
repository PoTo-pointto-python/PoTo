from __future__ import absolute_import, division, print_function
__metaclass__ = type
ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['preview'], 'supported_by': 'community'}
DOCUMENTATION = '\n---\nmodule: ufw\nshort_description: Manage firewall with UFW\ndescription:\n    - Manage firewall with UFW.\nversion_added: 1.6\nauthor:\n    - Aleksey Ovcharenko (@ovcharenko)\n    - Jarno Keskikangas (@pyykkis)\n    - Ahti Kitsik (@ahtik)\nnotes:\n    - See C(man ufw) for more examples.\nrequirements:\n    - C(ufw) package\noptions:\n  state:\n    description:\n      - C(enabled) reloads firewall and enables firewall on boot.\n      - C(disabled) unloads firewall and disables firewall on boot.\n      - C(reloaded) reloads firewall.\n      - C(reset) disables and resets firewall to installation defaults.\n    type: str\n    choices: [ disabled, enabled, reloaded, reset ]\n  default:\n    description:\n      - Change the default policy for incoming or outgoing traffic.\n    type: str\n    choices: [ allow, deny, reject ]\n    aliases: [ policy ]\n  direction:\n    description:\n      - Select direction for a rule or default policy command.  Mutually\n        exclusive with I(interface_in) and I(interface_out).\n    type: str\n    choices: [ in, incoming, out, outgoing, routed ]\n  logging:\n    description:\n      - Toggles logging. Logged packets use the LOG_KERN syslog facility.\n    type: str\n    choices: [ \'on\', \'off\', low, medium, high, full ]\n  insert:\n    description:\n      - Insert the corresponding rule as rule number NUM.\n      - Note that ufw numbers rules starting with 1.\n    type: int\n  insert_relative_to:\n    description:\n      - Allows to interpret the index in I(insert) relative to a position.\n      - C(zero) interprets the rule number as an absolute index (i.e. 1 is\n        the first rule).\n      - C(first-ipv4) interprets the rule number relative to the index of the\n        first IPv4 rule, or relative to the position where the first IPv4 rule\n        would be if there is currently none.\n      - C(last-ipv4) interprets the rule number relative to the index of the\n        last IPv4 rule, or relative to the position where the last IPv4 rule\n        would be if there is currently none.\n      - C(first-ipv6) interprets the rule number relative to the index of the\n        first IPv6 rule, or relative to the position where the first IPv6 rule\n        would be if there is currently none.\n      - C(last-ipv6) interprets the rule number relative to the index of the\n        last IPv6 rule, or relative to the position where the last IPv6 rule\n        would be if there is currently none.\n    type: str\n    choices: [ first-ipv4, first-ipv6, last-ipv4, last-ipv6, zero ]\n    default: zero\n    version_added: "2.8"\n  rule:\n    description:\n      - Add firewall rule\n    type: str\n    choices: [ allow, deny, limit, reject ]\n  log:\n    description:\n      - Log new connections matched to this rule\n    type: bool\n  from_ip:\n    description:\n      - Source IP address.\n    type: str\n    default: any\n    aliases: [ from, src ]\n  from_port:\n    description:\n      - Source port.\n    type: str\n  to_ip:\n    description:\n      - Destination IP address.\n    type: str\n    default: any\n    aliases: [ dest, to]\n  to_port:\n    description:\n      - Destination port.\n    type: str\n    aliases: [ port ]\n  proto:\n    description:\n      - TCP/IP protocol.\n    type: str\n    choices: [ any, tcp, udp, ipv6, esp, ah, gre, igmp ]\n    aliases: [ protocol ]\n  name:\n    description:\n      - Use profile located in C(/etc/ufw/applications.d).\n    type: str\n    aliases: [ app ]\n  delete:\n    description:\n      - Delete rule.\n    type: bool\n  interface:\n    description:\n      - Specify interface for the rule.  The direction (in or out) used\n        for the interface depends on the value of I(direction).  See\n        I(interface_in) and I(interface_out) for routed rules that needs\n        to supply both an input and output interface.  Mutually\n        exclusive with I(interface_in) and I(interface_out).\n    type: str\n    aliases: [ if ]\n  interface_in:\n    description:\n      - Specify input interface for the rule.  This is mutually\n        exclusive with I(direction) and I(interface).  However, it is\n        compatible with I(interface_out) for routed rules.\n    type: str\n    aliases: [ if_in ]\n    version_added: "2.10"\n  interface_out:\n    description:\n      - Specify output interface for the rule.  This is mutually\n        exclusive with I(direction) and I(interface).  However, it is\n        compatible with I(interface_in) for routed rules.\n    type: str\n    aliases: [ if_out ]\n    version_added: "2.10"\n  route:\n    description:\n      - Apply the rule to routed/forwarded packets.\n    type: bool\n  comment:\n    description:\n      - Add a comment to the rule. Requires UFW version >=0.35.\n    type: str\n    version_added: "2.4"\n'
EXAMPLES = '\n- name: Allow everything and enable UFW\n  ufw:\n    state: enabled\n    policy: allow\n\n- name: Set logging\n  ufw:\n    logging: \'on\'\n\n# Sometimes it is desirable to let the sender know when traffic is\n# being denied, rather than simply ignoring it. In these cases, use\n# reject instead of deny. In addition, log rejected connections:\n- ufw:\n    rule: reject\n    port: auth\n    log: yes\n\n# ufw supports connection rate limiting, which is useful for protecting\n# against brute-force login attacks. ufw will deny connections if an IP\n# address has attempted to initiate 6 or more connections in the last\n# 30 seconds. See  http://www.debian-administration.org/articles/187\n# for details. Typical usage is:\n- ufw:\n    rule: limit\n    port: ssh\n    proto: tcp\n\n# Allow OpenSSH. (Note that as ufw manages its own state, simply removing\n# a rule=allow task can leave those ports exposed. Either use delete=yes\n# or a separate state=reset task)\n- ufw:\n    rule: allow\n    name: OpenSSH\n\n- name: Delete OpenSSH rule\n  ufw:\n    rule: allow\n    name: OpenSSH\n    delete: yes\n\n- name: Deny all access to port 53\n  ufw:\n    rule: deny\n    port: \'53\'\n\n- name: Allow port range 60000-61000\n  ufw:\n    rule: allow\n    port: 60000:61000\n    proto: tcp\n\n- name: Allow all access to tcp port 80\n  ufw:\n    rule: allow\n    port: \'80\'\n    proto: tcp\n\n- name: Allow all access from RFC1918 networks to this host\n  ufw:\n    rule: allow\n    src: \'{{ item }}\'\n  loop:\n    - 10.0.0.0/8\n    - 172.16.0.0/12\n    - 192.168.0.0/16\n\n- name: Deny access to udp port 514 from host 1.2.3.4 and include a comment\n  ufw:\n    rule: deny\n    proto: udp\n    src: 1.2.3.4\n    port: \'514\'\n    comment: Block syslog\n\n- name: Allow incoming access to eth0 from 1.2.3.5 port 5469 to 1.2.3.4 port 5469\n  ufw:\n    rule: allow\n    interface: eth0\n    direction: in\n    proto: udp\n    src: 1.2.3.5\n    from_port: \'5469\'\n    dest: 1.2.3.4\n    to_port: \'5469\'\n\n# Note that IPv6 must be enabled in /etc/default/ufw for IPv6 firewalling to work.\n- name: Deny all traffic from the IPv6 2001:db8::/32 to tcp port 25 on this host\n  ufw:\n    rule: deny\n    proto: tcp\n    src: 2001:db8::/32\n    port: \'25\'\n\n- name: Deny all IPv6 traffic to tcp port 20 on this host\n  # this should be the first IPv6 rule\n  ufw:\n    rule: deny\n    proto: tcp\n    port: \'20\'\n    to_ip: "::"\n    insert: 0\n    insert_relative_to: first-ipv6\n\n- name: Deny all IPv4 traffic to tcp port 20 on this host\n  # This should be the third to last IPv4 rule\n  # (insert: -1 addresses the second to last IPv4 rule;\n  #  so the new rule will be inserted before the second\n  #  to last IPv4 rule, and will be come the third to last\n  #  IPv4 rule.)\n  ufw:\n    rule: deny\n    proto: tcp\n    port: \'20\'\n    to_ip: "::"\n    insert: -1\n    insert_relative_to: last-ipv4\n\n# Can be used to further restrict a global FORWARD policy set to allow\n- name: Deny forwarded/routed traffic from subnet 1.2.3.0/24 to subnet 4.5.6.0/24\n  ufw:\n    rule: deny\n    route: yes\n    src: 1.2.3.0/24\n    dest: 4.5.6.0/24\n'
import re
from operator import itemgetter
from ansible.module_utils.basic import AnsibleModule

def compile_ipv4_regexp():
    r = '((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\\.){3,3}'
    r += '(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])'
    return re.compile(r)

def compile_ipv6_regexp():
    """
    validation pattern provided by :
    https://stackoverflow.com/questions/53497/regular-expression-that-matches-
    valid-ipv6-addresses#answer-17871737
    """
    r = '(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:'
    r += '|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}'
    r += '(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4})'
    r += '{1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]'
    r += '{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]'
    r += '{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4})'
    r += '{0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]'
    r += '|1{0,1}[0-9]){0,1}[0-9])\\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}'
    r += '[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}'
    r += '[0-9])\\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))'
    return re.compile(r)

def main():
    command_keys = ['state', 'default', 'rule', 'logging']
    module = AnsibleModule(argument_spec=dict(state=dict(type='str', choices=['enabled', 'disabled', 'reloaded', 'reset']), default=dict(type='str', aliases=['policy'], choices=['allow', 'deny', 'reject']), logging=dict(type='str', choices=['full', 'high', 'low', 'medium', 'off', 'on']), direction=dict(type='str', choices=['in', 'incoming', 'out', 'outgoing', 'routed']), delete=dict(type='bool', default=False), route=dict(type='bool', default=False), insert=dict(type='int'), insert_relative_to=dict(choices=['zero', 'first-ipv4', 'last-ipv4', 'first-ipv6', 'last-ipv6'], default='zero'), rule=dict(type='str', choices=['allow', 'deny', 'limit', 'reject']), interface=dict(type='str', aliases=['if']), interface_in=dict(type='str', aliases=['if_in']), interface_out=dict(type='str', aliases=['if_out']), log=dict(type='bool', default=False), from_ip=dict(type='str', default='any', aliases=['from', 'src']), from_port=dict(type='str'), to_ip=dict(type='str', default='any', aliases=['dest', 'to']), to_port=dict(type='str', aliases=['port']), proto=dict(type='str', aliases=['protocol'], choices=['ah', 'any', 'esp', 'ipv6', 'tcp', 'udp', 'gre', 'igmp']), name=dict(type='str', aliases=['app']), comment=dict(type='str')), supports_check_mode=True, mutually_exclusive=[['name', 'proto', 'logging'], ['direction', 'interface_in'], ['direction', 'interface_out']], required_one_of=[command_keys], required_by=dict(interface=('direction',)))
    cmds = []
    ipv4_regexp = compile_ipv4_regexp()
    ipv6_regexp = compile_ipv6_regexp()

    def filter_line_that_not_start_with(pattern, content):
        return ''.join([line for line in content.splitlines(True) if line.startswith(pattern)])

    def filter_line_that_contains(pattern, content):
        return [line for line in content.splitlines(True) if pattern in line]

    def filter_line_that_not_contains(pattern, content):
        return ''.join([line for line in content.splitlines(True) if not line.contains(pattern)])

    def filter_line_that_match_func(match_func, content):
        return ''.join([line for line in content.splitlines(True) if match_func(line) is not None])

    def filter_line_that_contains_ipv4(content):
        return filter_line_that_match_func(ipv4_regexp.search, content)

    def filter_line_that_contains_ipv6(content):
        return filter_line_that_match_func(ipv6_regexp.search, content)

    def is_starting_by_ipv4(ip):
        return ipv4_regexp.match(ip) is not None

    def is_starting_by_ipv6(ip):
        return ipv6_regexp.match(ip) is not None

    def execute(cmd, ignore_error=False):
        cmd = ' '.join(map(itemgetter(-1), filter(itemgetter(0), cmd)))
        cmds.append(cmd)
        (rc, out, err) = module.run_command(cmd, environ_update={'LANG': 'C'})
        if rc != 0 and (not ignore_error):
            module.fail_json(msg=err or out, commands=cmds)
        return out

    def get_current_rules():
        user_rules_files = ['/lib/ufw/user.rules', '/lib/ufw/user6.rules', '/etc/ufw/user.rules', '/etc/ufw/user6.rules', '/var/lib/ufw/user.rules', '/var/lib/ufw/user6.rules']
        cmd = [[grep_bin], ['-h'], ["'^### tuple'"]]
        cmd.extend([[f] for f in user_rules_files])
        return execute(cmd, ignore_error=True)

    def ufw_version():
        """
        Returns the major and minor version of ufw installed on the system.
        """
        out = execute([[ufw_bin], ['--version']])
        lines = [x for x in out.split('\n') if x.strip() != '']
        if len(lines) == 0:
            module.fail_json(msg='Failed to get ufw version.', rc=0, out=out)
        matches = re.search('^ufw.+(\\d+)\\.(\\d+)(?:\\.(\\d+))?.*$', lines[0])
        if matches is None:
            module.fail_json(msg='Failed to get ufw version.', rc=0, out=out)
        major = int(matches.group(1))
        minor = int(matches.group(2))
        rev = 0
        if matches.group(3) is not None:
            rev = int(matches.group(3))
        return (major, minor, rev)
    params = module.params
    commands = dict(((key, params[key]) for key in command_keys if params[key]))
    ufw_bin = module.get_bin_path('ufw', True)
    grep_bin = module.get_bin_path('grep', True)
    pre_state = execute([[ufw_bin], ['status verbose']])
    pre_rules = get_current_rules()
    changed = False
    for (command, value) in commands.items():
        cmd = [[ufw_bin], [module.check_mode, '--dry-run']]
        if command == 'state':
            states = {'enabled': 'enable', 'disabled': 'disable', 'reloaded': 'reload', 'reset': 'reset'}
            if value in ['reloaded', 'reset']:
                changed = True
            if module.check_mode:
                ufw_enabled = pre_state.find(' active') != -1
                if value == 'disabled' and ufw_enabled or (value == 'enabled' and (not ufw_enabled)):
                    changed = True
            else:
                execute(cmd + [['-f'], [states[value]]])
        elif command == 'logging':
            extract = re.search('Logging: (on|off)(?: \\(([a-z]+)\\))?', pre_state)
            if extract:
                current_level = extract.group(2)
                current_on_off_value = extract.group(1)
                if value != 'off':
                    if current_on_off_value == 'off':
                        changed = True
                    elif value != 'on' and value != current_level:
                        changed = True
                elif current_on_off_value != 'off':
                    changed = True
            else:
                changed = True
            if not module.check_mode:
                execute(cmd + [[command], [value]])
        elif command == 'default':
            if params['direction'] not in ['outgoing', 'incoming', 'routed', None]:
                module.fail_json(msg='For default, direction must be one of "outgoing", "incoming" and "routed", or direction must not be specified.')
            if module.check_mode:
                regexp = 'Default: (deny|allow|reject) \\(incoming\\), (deny|allow|reject) \\(outgoing\\), (deny|allow|reject|disabled) \\(routed\\)'
                extract = re.search(regexp, pre_state)
                if extract is not None:
                    current_default_values = {}
                    current_default_values['incoming'] = extract.group(1)
                    current_default_values['outgoing'] = extract.group(2)
                    current_default_values['routed'] = extract.group(3)
                    v = current_default_values[params['direction'] or 'incoming']
                    if v not in (value, 'disabled'):
                        changed = True
                else:
                    changed = True
            else:
                execute(cmd + [[command], [value], [params['direction']]])
        elif command == 'rule':
            if params['direction'] not in ['in', 'out', None]:
                module.fail_json(msg='For rules, direction must be one of "in" and "out", or direction must not be specified.')
            if not params['route'] and params['interface_in'] and params['interface_out']:
                module.fail_json(msg='Only route rules can combine interface_in and interface_out')
            cmd.append([module.boolean(params['route']), 'route'])
            cmd.append([module.boolean(params['delete']), 'delete'])
            if params['insert'] is not None:
                relative_to_cmd = params['insert_relative_to']
                if relative_to_cmd == 'zero':
                    insert_to = params['insert']
                else:
                    (dummy, numbered_state, dummy) = module.run_command([ufw_bin, 'status', 'numbered'])
                    numbered_line_re = re.compile('^\\[ *([0-9]+)\\] ')
                    lines = [(numbered_line_re.match(line), '(v6)' in line) for line in numbered_state.splitlines()]
                    lines = [(int(matcher.group(1)), ipv6) for (matcher, ipv6) in lines if matcher]
                    last_number = max([no for (no, ipv6) in lines]) if lines else 0
                    has_ipv4 = any([not ipv6 for (no, ipv6) in lines])
                    has_ipv6 = any([ipv6 for (no, ipv6) in lines])
                    if relative_to_cmd == 'first-ipv4':
                        relative_to = 1
                    elif relative_to_cmd == 'last-ipv4':
                        relative_to = max([no for (no, ipv6) in lines if not ipv6]) if has_ipv4 else 1
                    elif relative_to_cmd == 'first-ipv6':
                        relative_to = max([no for (no, ipv6) in lines if not ipv6]) + 1 if has_ipv4 else 1
                    elif relative_to_cmd == 'last-ipv6':
                        relative_to = last_number if has_ipv6 else last_number + 1
                    insert_to = params['insert'] + relative_to
                    if insert_to > last_number:
                        insert_to = None
                cmd.append([insert_to is not None, 'insert %s' % insert_to])
            cmd.append([value])
            cmd.append([params['direction'], '%s' % params['direction']])
            cmd.append([params['interface'], 'on %s' % params['interface']])
            cmd.append([params['interface_in'], 'in on %s' % params['interface_in']])
            cmd.append([params['interface_out'], 'out on %s' % params['interface_out']])
            cmd.append([module.boolean(params['log']), 'log'])
            for (key, template) in [('from_ip', 'from %s'), ('from_port', 'port %s'), ('to_ip', 'to %s'), ('to_port', 'port %s'), ('proto', 'proto %s'), ('name', "app '%s'")]:
                value = params[key]
                cmd.append([value, template % value])
            (ufw_major, ufw_minor, dummy) = ufw_version()
            if ufw_major == 0 and ufw_minor >= 35 or ufw_major > 0:
                cmd.append([params['comment'], "comment '%s'" % params['comment']])
            rules_dry = execute(cmd)
            if module.check_mode:
                nb_skipping_line = len(filter_line_that_contains('Skipping', rules_dry))
                if not (nb_skipping_line > 0 and nb_skipping_line == len(rules_dry.splitlines(True))):
                    rules_dry = filter_line_that_not_start_with('### tuple', rules_dry)
                    if is_starting_by_ipv4(params['from_ip']) or is_starting_by_ipv4(params['to_ip']):
                        if filter_line_that_contains_ipv4(pre_rules) != filter_line_that_contains_ipv4(rules_dry):
                            changed = True
                    elif is_starting_by_ipv6(params['from_ip']) or is_starting_by_ipv6(params['to_ip']):
                        if filter_line_that_contains_ipv6(pre_rules) != filter_line_that_contains_ipv6(rules_dry):
                            changed = True
                    elif pre_rules != rules_dry:
                        changed = True
    if module.check_mode:
        return module.exit_json(changed=changed, commands=cmds)
    else:
        post_state = execute([[ufw_bin], ['status'], ['verbose']])
        if not changed:
            post_rules = get_current_rules()
            changed = pre_state != post_state or pre_rules != post_rules
        return module.exit_json(changed=changed, commands=cmds, msg=post_state.rstrip())
if __name__ == '__main__':
    main()