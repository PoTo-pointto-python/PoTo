from __future__ import absolute_import, division, print_function
__metaclass__ = type
ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['preview'], 'supported_by': 'community'}
DOCUMENTATION = '\n---\nmodule: mysql_user\nshort_description: Adds or removes a user from a MySQL database\ndescription:\n   - Adds or removes a user from a MySQL database.\nversion_added: "0.6"\noptions:\n  name:\n    description:\n      - Name of the user (role) to add or remove.\n    type: str\n    required: true\n  password:\n    description:\n      - Set the user\'s password..\n    type: str\n  encrypted:\n    description:\n      - Indicate that the \'password\' field is a `mysql_native_password` hash.\n    type: bool\n    default: no\n    version_added: "2.0"\n  host:\n    description:\n      - The \'host\' part of the MySQL username.\n    type: str\n    default: localhost\n  host_all:\n    description:\n      - Override the host option, making ansible apply changes to all hostnames for a given user.\n      - This option cannot be used when creating users.\n    type: bool\n    default: no\n    version_added: "2.1"\n  priv:\n    description:\n      - "MySQL privileges string in the format: C(db.table:priv1,priv2)."\n      - "Multiple privileges can be specified by separating each one using\n        a forward slash: C(db.table:priv/db.table:priv)."\n      - The format is based on MySQL C(GRANT) statement.\n      - Database and table names can be quoted, MySQL-style.\n      - If column privileges are used, the C(priv1,priv2) part must be\n        exactly as returned by a C(SHOW GRANT) statement. If not followed,\n        the module will always report changes. It includes grouping columns\n        by permission (C(SELECT(col1,col2)) instead of C(SELECT(col1),SELECT(col2))).\n      - Can be passed as a dictionary (see the examples).\n    type: raw\n  append_privs:\n    description:\n      - Append the privileges defined by priv to the existing ones for this\n        user instead of overwriting existing ones.\n    type: bool\n    default: no\n    version_added: "1.4"\n  sql_log_bin:\n    description:\n      - Whether binary logging should be enabled or disabled for the connection.\n    type: bool\n    default: yes\n    version_added: "2.1"\n  state:\n    description:\n      - Whether the user should exist.\n      - When C(absent), removes the user.\n    type: str\n    choices: [ absent, present ]\n    default: present\n  check_implicit_admin:\n    description:\n      - Check if mysql allows login as root/nopassword before trying supplied credentials.\n    type: bool\n    default: no\n    version_added: "1.3"\n  update_password:\n    description:\n      - C(always) will update passwords if they differ.\n      - C(on_create) will only set the password for newly created users.\n    type: str\n    choices: [ always, on_create ]\n    default: always\n    version_added: "2.0"\n  plugin:\n    description:\n      - User\'s plugin to authenticate (``CREATE USER user IDENTIFIED WITH plugin``).\n    type: str\n    version_added: \'2.10\'\n  plugin_hash_string:\n    description:\n      - User\'s plugin hash string (``CREATE USER user IDENTIFIED WITH plugin AS plugin_hash_string``).\n    type: str\n    version_added: \'2.10\'\n  plugin_auth_string:\n    description:\n      - User\'s plugin auth_string (``CREATE USER user IDENTIFIED WITH plugin BY plugin_auth_string``).\n    type: str\n    version_added: \'2.10\'\n\nnotes:\n   - "MySQL server installs with default login_user of \'root\' and no password. To secure this user\n     as part of an idempotent playbook, you must create at least two tasks: the first must change the root user\'s password,\n     without providing any login_user/login_password details. The second must drop a ~/.my.cnf file containing\n     the new root credentials. Subsequent runs of the playbook will then succeed by reading the new credentials from\n     the file."\n   - Currently, there is only support for the `mysql_native_password` encrypted password hash module.\n\nseealso:\n- module: mysql_info\n- name: MySQL access control and account management reference\n  description: Complete reference of the MySQL access control and account management documentation.\n  link: https://dev.mysql.com/doc/refman/8.0/en/access-control.html\n- name: MySQL provided privileges reference\n  description: Complete reference of the MySQL provided privileges documentation.\n  link: https://dev.mysql.com/doc/refman/8.0/en/privileges-provided.html\n\nauthor:\n- Jonathan Mainguy (@Jmainguy)\n- Benjamin Malynovytch (@bmalynovytch)\n- Lukasz Tomaszkiewicz (@tomaszkiewicz)\nextends_documentation_fragment: mysql\n'
EXAMPLES = '\n- name: Removes anonymous user account for localhost\n  mysql_user:\n    name: \'\'\n    host: localhost\n    state: absent\n\n- name: Removes all anonymous user accounts\n  mysql_user:\n    name: \'\'\n    host_all: yes\n    state: absent\n\n- name: Create database user with name \'bob\' and password \'12345\' with all database privileges\n  mysql_user:\n    name: bob\n    password: 12345\n    priv: \'*.*:ALL\'\n    state: present\n\n- name: Create database user using hashed password with all database privileges\n  mysql_user:\n    name: bob\n    password: \'*EE0D72C1085C46C5278932678FBE2C6A782821B4\'\n    encrypted: yes\n    priv: \'*.*:ALL\'\n    state: present\n\n- name: Create database user with password and all database privileges and \'WITH GRANT OPTION\'\n  mysql_user:\n    name: bob\n    password: 12345\n    priv: \'*.*:ALL,GRANT\'\n    state: present\n\n- name: Create user with password, all database privileges and \'WITH GRANT OPTION\' in db1 and db2\n  mysql_user:\n    state: present\n    name: bob\n    password: 12345dd\n    priv:\n      \'db1.*\': \'ALL,GRANT\'\n      \'db2.*\': \'ALL,GRANT\'\n\n# Note that REQUIRESSL is a special privilege that should only apply to *.* by itself.\n- name: Modify user to require SSL connections.\n  mysql_user:\n    name: bob\n    append_privs: yes\n    priv: \'*.*:REQUIRESSL\'\n    state: present\n\n- name: Ensure no user named \'sally\'@\'localhost\' exists, also passing in the auth credentials.\n  mysql_user:\n    login_user: root\n    login_password: 123456\n    name: sally\n    state: absent\n\n- name: Ensure no user named \'sally\' exists at all\n  mysql_user:\n    name: sally\n    host_all: yes\n    state: absent\n\n- name: Specify grants composed of more than one word\n  mysql_user:\n    name: replication\n    password: 12345\n    priv: "*.*:REPLICATION CLIENT"\n    state: present\n\n- name: Revoke all privileges for user \'bob\' and password \'12345\'\n  mysql_user:\n    name: bob\n    password: 12345\n    priv: "*.*:USAGE"\n    state: present\n\n# Example privileges string format\n# mydb.*:INSERT,UPDATE/anotherdb.*:SELECT/yetanotherdb.*:ALL\n\n- name: Example using login_unix_socket to connect to server\n  mysql_user:\n    name: root\n    password: abc123\n    login_unix_socket: /var/run/mysqld/mysqld.sock\n\n- name: Example of skipping binary logging while adding user \'bob\'\n  mysql_user:\n    name: bob\n    password: 12345\n    priv: "*.*:USAGE"\n    state: present\n    sql_log_bin: no\n\n- name: Create user \'bob\' authenticated with plugin \'AWSAuthenticationPlugin\'\n  mysql_user:\n    name: bob\n    plugin: AWSAuthenticationPlugin\n    plugin_hash_string: RDS\n    priv: \'*.*:ALL\'\n    state: present\n\n# Example .my.cnf file for setting the root password\n# [client]\n# user=root\n# password=n<_665{vS43y\n'
import re
import string
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.database import SQLParseError
from ansible.module_utils.mysql import mysql_connect, mysql_driver, mysql_driver_fail_msg
from ansible.module_utils.six import iteritems
from ansible.module_utils._text import to_native
VALID_PRIVS = frozenset(('CREATE', 'DROP', 'GRANT', 'GRANT OPTION', 'LOCK TABLES', 'REFERENCES', 'EVENT', 'ALTER', 'DELETE', 'INDEX', 'INSERT', 'SELECT', 'UPDATE', 'CREATE TEMPORARY TABLES', 'TRIGGER', 'CREATE VIEW', 'SHOW VIEW', 'ALTER ROUTINE', 'CREATE ROUTINE', 'EXECUTE', 'FILE', 'CREATE TABLESPACE', 'CREATE USER', 'PROCESS', 'PROXY', 'RELOAD', 'REPLICATION CLIENT', 'REPLICATION SLAVE', 'SHOW DATABASES', 'SHUTDOWN', 'SUPER', 'ALL', 'ALL PRIVILEGES', 'USAGE', 'REQUIRESSL', 'CREATE ROLE', 'DROP ROLE', 'APPLICATION_PASSWORD_ADMIN', 'AUDIT_ADMIN', 'BACKUP_ADMIN', 'BINLOG_ADMIN', 'BINLOG_ENCRYPTION_ADMIN', 'CLONE_ADMIN', 'CONNECTION_ADMIN', 'ENCRYPTION_KEY_ADMIN', 'FIREWALL_ADMIN', 'FIREWALL_USER', 'GROUP_REPLICATION_ADMIN', 'INNODB_REDO_LOG_ARCHIVE', 'NDB_STORED_USER', 'PERSIST_RO_VARIABLES_ADMIN', 'REPLICATION_APPLIER', 'REPLICATION_SLAVE_ADMIN', 'RESOURCE_GROUP_ADMIN', 'RESOURCE_GROUP_USER', 'ROLE_ADMIN', 'SESSION_VARIABLES_ADMIN', 'SET_USER_ID', 'SYSTEM_USER', 'SYSTEM_VARIABLES_ADMIN', 'SYSTEM_USER', 'TABLE_ENCRYPTION_ADMIN', 'VERSION_TOKEN_ADMIN', 'XA_RECOVER_ADMIN', 'LOAD FROM S3', 'SELECT INTO S3'))

class InvalidPrivsError(Exception):
    pass

def use_old_user_mgmt(cursor):
    cursor.execute('SELECT VERSION()')
    result = cursor.fetchone()
    version_str = result[0]
    version = version_str.split('.')
    if 'mariadb' in version_str.lower():
        if int(version[0]) * 1000 + int(version[1]) < 10002:
            return True
        else:
            return False
    elif int(version[0]) * 1000 + int(version[1]) < 5007:
        return True
    else:
        return False

def get_mode(cursor):
    cursor.execute('SELECT @@GLOBAL.sql_mode')
    result = cursor.fetchone()
    mode_str = result[0]
    if 'ANSI' in mode_str:
        mode = 'ANSI'
    else:
        mode = 'NOTANSI'
    return mode

def user_exists(cursor, user, host, host_all):
    if host_all:
        cursor.execute('SELECT count(*) FROM mysql.user WHERE user = %s', [user])
    else:
        cursor.execute('SELECT count(*) FROM mysql.user WHERE user = %s AND host = %s', (user, host))
    count = cursor.fetchone()
    return count[0] > 0

def user_add(cursor, user, host, host_all, password, encrypted, plugin, plugin_hash_string, plugin_auth_string, new_priv, check_mode):
    if host_all:
        return False
    if check_mode:
        return True
    if password and encrypted:
        cursor.execute('CREATE USER %s@%s IDENTIFIED BY PASSWORD %s', (user, host, password))
    elif password and (not encrypted):
        cursor.execute('CREATE USER %s@%s IDENTIFIED BY %s', (user, host, password))
    elif plugin and plugin_hash_string:
        cursor.execute('CREATE USER %s@%s IDENTIFIED WITH %s AS %s', (user, host, plugin, plugin_hash_string))
    elif plugin and plugin_auth_string:
        cursor.execute('CREATE USER %s@%s IDENTIFIED WITH %s BY %s', (user, host, plugin, plugin_auth_string))
    elif plugin:
        cursor.execute('CREATE USER %s@%s IDENTIFIED WITH %s', (user, host, plugin))
    else:
        cursor.execute('CREATE USER %s@%s', (user, host))
    if new_priv is not None:
        for (db_table, priv) in iteritems(new_priv):
            privileges_grant(cursor, user, host, db_table, priv)
    return True

def is_hash(password):
    ishash = False
    if len(password) == 41 and password[0] == '*':
        if frozenset(password[1:]).issubset(string.hexdigits):
            ishash = True
    return ishash

def user_mod(cursor, user, host, host_all, password, encrypted, plugin, plugin_hash_string, plugin_auth_string, new_priv, append_privs, module):
    changed = False
    msg = 'User unchanged'
    grant_option = False
    if host_all:
        hostnames = user_get_hostnames(cursor, [user])
    else:
        hostnames = [host]
    for host in hostnames:
        if bool(password):
            old_user_mgmt = use_old_user_mgmt(cursor)
            cursor.execute("\n                SELECT COLUMN_NAME FROM information_schema.COLUMNS\n                WHERE TABLE_SCHEMA = 'mysql' AND TABLE_NAME = 'user' AND COLUMN_NAME IN ('Password', 'authentication_string')\n                ORDER BY COLUMN_NAME DESC LIMIT 1\n            ")
            colA = cursor.fetchone()
            cursor.execute("\n                SELECT COLUMN_NAME FROM information_schema.COLUMNS\n                WHERE TABLE_SCHEMA = 'mysql' AND TABLE_NAME = 'user' AND COLUMN_NAME IN ('Password', 'authentication_string')\n                ORDER BY COLUMN_NAME ASC  LIMIT 1\n            ")
            colB = cursor.fetchone()
            cursor.execute("\n                SELECT COALESCE(\n                        CASE WHEN %s = '' THEN NULL ELSE %s END,\n                        CASE WHEN %s = '' THEN NULL ELSE %s END\n                    )\n                FROM mysql.user WHERE user = %%s AND host = %%s\n                " % (colA[0], colA[0], colB[0], colB[0]), (user, host))
            current_pass_hash = cursor.fetchone()[0]
            if isinstance(current_pass_hash, bytes):
                current_pass_hash = current_pass_hash.decode('ascii')
            if encrypted:
                encrypted_password = password
                if not is_hash(encrypted_password):
                    module.fail_json(msg='encrypted was specified however it does not appear to be a valid hash expecting: *SHA1(SHA1(your_password))')
            else:
                if old_user_mgmt:
                    cursor.execute('SELECT PASSWORD(%s)', (password,))
                else:
                    cursor.execute("SELECT CONCAT('*', UCASE(SHA1(UNHEX(SHA1(%s)))))", (password,))
                encrypted_password = cursor.fetchone()[0]
            if current_pass_hash != encrypted_password:
                msg = 'Password updated'
                if module.check_mode:
                    return (True, msg)
                if old_user_mgmt:
                    cursor.execute('SET PASSWORD FOR %s@%s = %s', (user, host, encrypted_password))
                    msg = 'Password updated (old style)'
                else:
                    try:
                        cursor.execute('ALTER USER %s@%s IDENTIFIED WITH mysql_native_password AS %s', (user, host, encrypted_password))
                        msg = 'Password updated (new style)'
                    except mysql_driver.Error as e:
                        if e.args[0] == 1396:
                            cursor.execute("UPDATE user SET plugin = %s, authentication_string = %s, Password = '' WHERE User = %s AND Host = %s", ('mysql_native_password', encrypted_password, user, host))
                            cursor.execute('FLUSH PRIVILEGES')
                            msg = 'Password forced update'
                        else:
                            raise e
                changed = True
        if plugin:
            cursor.execute('SELECT plugin, authentication_string FROM mysql.user WHERE user = %s AND host = %s', (user, host))
            current_plugin = cursor.fetchone()
            update = False
            if current_plugin[0] != plugin:
                update = True
            if plugin_hash_string and current_plugin[1] != plugin_hash_string:
                update = True
            if plugin_auth_string and current_plugin[1] != plugin_auth_string:
                update = True
            if update:
                if plugin_hash_string:
                    cursor.execute('ALTER USER %s@%s IDENTIFIED WITH %s AS %s', (user, host, plugin, plugin_hash_string))
                elif plugin_auth_string:
                    cursor.execute('ALTER USER %s@%s IDENTIFIED WITH %s BY %s', (user, host, plugin, plugin_auth_string))
                else:
                    cursor.execute('ALTER USER %s@%s IDENTIFIED WITH %s', (user, host, plugin))
                changed = True
        if new_priv is not None:
            curr_priv = privileges_get(cursor, user, host)
            for (db_table, priv) in iteritems(curr_priv):
                if 'GRANT' in priv:
                    grant_option = True
                if db_table not in new_priv:
                    if user != 'root' and 'PROXY' not in priv and (not append_privs):
                        msg = 'Privileges updated'
                        if module.check_mode:
                            return (True, msg)
                        privileges_revoke(cursor, user, host, db_table, priv, grant_option)
                        changed = True
            for (db_table, priv) in iteritems(new_priv):
                if db_table not in curr_priv:
                    msg = 'New privileges granted'
                    if module.check_mode:
                        return (True, msg)
                    privileges_grant(cursor, user, host, db_table, priv)
                    changed = True
            db_table_intersect = set(new_priv.keys()) & set(curr_priv.keys())
            for db_table in db_table_intersect:
                priv_diff = set(new_priv[db_table]) ^ set(curr_priv[db_table])
                if len(priv_diff) > 0:
                    msg = 'Privileges updated'
                    if module.check_mode:
                        return (True, msg)
                    if not append_privs:
                        privileges_revoke(cursor, user, host, db_table, curr_priv[db_table], grant_option)
                    privileges_grant(cursor, user, host, db_table, new_priv[db_table])
                    changed = True
    return (changed, msg)

def user_delete(cursor, user, host, host_all, check_mode):
    if check_mode:
        return True
    if host_all:
        hostnames = user_get_hostnames(cursor, [user])
        for hostname in hostnames:
            cursor.execute('DROP USER %s@%s', (user, hostname))
    else:
        cursor.execute('DROP USER %s@%s', (user, host))
    return True

def user_get_hostnames(cursor, user):
    cursor.execute('SELECT Host FROM mysql.user WHERE user = %s', user)
    hostnames_raw = cursor.fetchall()
    hostnames = []
    for hostname_raw in hostnames_raw:
        hostnames.append(hostname_raw[0])
    return hostnames

def privileges_get(cursor, user, host):
    """ MySQL doesn't have a better method of getting privileges aside from the
    SHOW GRANTS query syntax, which requires us to then parse the returned string.
    Here's an example of the string that is returned from MySQL:

     GRANT USAGE ON *.* TO 'user'@'localhost' IDENTIFIED BY 'pass';

    This function makes the query and returns a dictionary containing the results.
    The dictionary format is the same as that returned by privileges_unpack() below.
    """
    output = {}
    cursor.execute('SHOW GRANTS FOR %s@%s', (user, host))
    grants = cursor.fetchall()

    def pick(x):
        if x == 'ALL PRIVILEGES':
            return 'ALL'
        else:
            return x
    for grant in grants:
        res = re.match('GRANT (.+) ON (.+) TO ([\'`"]).*\\3@([\'`"]).*\\4( IDENTIFIED BY PASSWORD ([\'`"]).+\\6)? ?(.*)', grant[0])
        if res is None:
            raise InvalidPrivsError('unable to parse the MySQL grant string: %s' % grant[0])
        privileges = res.group(1).split(', ')
        privileges = [pick(x) for x in privileges]
        if 'WITH GRANT OPTION' in res.group(7):
            privileges.append('GRANT')
        if 'REQUIRE SSL' in res.group(7):
            privileges.append('REQUIRESSL')
        db = res.group(2)
        output[db] = privileges
    return output

def privileges_unpack(priv, mode):
    """ Take a privileges string, typically passed as a parameter, and unserialize
    it into a dictionary, the same format as privileges_get() above. We have this
    custom format to avoid using YAML/JSON strings inside YAML playbooks. Example
    of a privileges string:

     mydb.*:INSERT,UPDATE/anotherdb.*:SELECT/yetanother.*:ALL

    The privilege USAGE stands for no privileges, so we add that in on *.* if it's
    not specified in the string, as MySQL will always provide this by default.
    """
    if mode == 'ANSI':
        quote = '"'
    else:
        quote = '`'
    output = {}
    privs = []
    for item in priv.strip().split('/'):
        pieces = item.strip().rsplit(':', 1)
        dbpriv = pieces[0].rsplit('.', 1)
        parts = dbpriv[0].split(' ', 1)
        object_type = ''
        if len(parts) > 1 and (parts[0] == 'FUNCTION' or parts[0] == 'PROCEDURE'):
            object_type = parts[0] + ' '
            dbpriv[0] = parts[1]
        for (i, side) in enumerate(dbpriv):
            if side.strip('`') != '*':
                dbpriv[i] = '%s%s%s' % (quote, side.strip('`'), quote)
        pieces[0] = object_type + '.'.join(dbpriv)
        if '(' in pieces[1]:
            output[pieces[0]] = re.split(',\\s*(?=[^)]*(?:\\(|$))', pieces[1].upper())
            for i in output[pieces[0]]:
                privs.append(re.sub('\\s*\\(.*\\)', '', i))
        else:
            output[pieces[0]] = pieces[1].upper().split(',')
            privs = output[pieces[0]]
        new_privs = frozenset(privs)
        if not new_privs.issubset(VALID_PRIVS):
            raise InvalidPrivsError('Invalid privileges specified: %s' % new_privs.difference(VALID_PRIVS))
    if '*.*' not in output:
        output['*.*'] = ['USAGE']
    if 'REQUIRESSL' in priv and (not set(output['*.*']).difference(set(['GRANT', 'REQUIRESSL']))):
        output['*.*'].append('USAGE')
    return output

def privileges_revoke(cursor, user, host, db_table, priv, grant_option):
    db_table = db_table.replace('%', '%%')
    if grant_option:
        query = ['REVOKE GRANT OPTION ON %s' % db_table]
        query.append('FROM %s@%s')
        query = ' '.join(query)
        cursor.execute(query, (user, host))
    priv_string = ','.join([p for p in priv if p not in ('GRANT', 'REQUIRESSL')])
    query = ['REVOKE %s ON %s' % (priv_string, db_table)]
    query.append('FROM %s@%s')
    query = ' '.join(query)
    cursor.execute(query, (user, host))

def privileges_grant(cursor, user, host, db_table, priv):
    db_table = db_table.replace('%', '%%')
    priv_string = ','.join([p for p in priv if p not in ('GRANT', 'REQUIRESSL')])
    query = ['GRANT %s ON %s' % (priv_string, db_table)]
    query.append('TO %s@%s')
    if 'REQUIRESSL' in priv:
        query.append('REQUIRE SSL')
    if 'GRANT' in priv:
        query.append('WITH GRANT OPTION')
    query = ' '.join(query)
    cursor.execute(query, (user, host))

def convert_priv_dict_to_str(priv):
    """Converts privs dictionary to string of certain format.

    Args:
        priv (dict): Dict of privileges that needs to be converted to string.

    Returns:
        priv (str): String representation of input argument.
    """
    priv_list = ['%s:%s' % (key, val) for (key, val) in iteritems(priv)]
    return '/'.join(priv_list)

def main():
    module = AnsibleModule(argument_spec=dict(login_user=dict(type='str'), login_password=dict(type='str', no_log=True), login_host=dict(type='str', default='localhost'), login_port=dict(type='int', default=3306), login_unix_socket=dict(type='str'), user=dict(type='str', required=True, aliases=['name']), password=dict(type='str', no_log=True), encrypted=dict(type='bool', default=False), host=dict(type='str', default='localhost'), host_all=dict(type='bool', default=False), state=dict(type='str', default='present', choices=['absent', 'present']), priv=dict(type='raw'), append_privs=dict(type='bool', default=False), check_implicit_admin=dict(type='bool', default=False), update_password=dict(type='str', default='always', choices=['always', 'on_create']), connect_timeout=dict(type='int', default=30), config_file=dict(type='path', default='~/.my.cnf'), sql_log_bin=dict(type='bool', default=True), client_cert=dict(type='path', aliases=['ssl_cert']), client_key=dict(type='path', aliases=['ssl_key']), ca_cert=dict(type='path', aliases=['ssl_ca']), plugin=dict(default=None, type='str'), plugin_hash_string=dict(default=None, type='str'), plugin_auth_string=dict(default=None, type='str')), supports_check_mode=True)
    login_user = module.params['login_user']
    login_password = module.params['login_password']
    user = module.params['user']
    password = module.params['password']
    encrypted = module.boolean(module.params['encrypted'])
    host = module.params['host'].lower()
    host_all = module.params['host_all']
    state = module.params['state']
    priv = module.params['priv']
    check_implicit_admin = module.params['check_implicit_admin']
    connect_timeout = module.params['connect_timeout']
    config_file = module.params['config_file']
    append_privs = module.boolean(module.params['append_privs'])
    update_password = module.params['update_password']
    ssl_cert = module.params['client_cert']
    ssl_key = module.params['client_key']
    ssl_ca = module.params['ca_cert']
    db = ''
    sql_log_bin = module.params['sql_log_bin']
    plugin = module.params['plugin']
    plugin_hash_string = module.params['plugin_hash_string']
    plugin_auth_string = module.params['plugin_auth_string']
    if priv and (not (isinstance(priv, str) or isinstance(priv, dict))):
        module.fail_json(msg='priv parameter must be str or dict but %s was passed' % type(priv))
    if priv and isinstance(priv, dict):
        priv = convert_priv_dict_to_str(priv)
    if mysql_driver is None:
        module.fail_json(msg=mysql_driver_fail_msg)
    cursor = None
    try:
        if check_implicit_admin:
            try:
                (cursor, db_conn) = mysql_connect(module, 'root', '', config_file, ssl_cert, ssl_key, ssl_ca, db, connect_timeout=connect_timeout)
            except Exception:
                pass
        if not cursor:
            (cursor, db_conn) = mysql_connect(module, login_user, login_password, config_file, ssl_cert, ssl_key, ssl_ca, db, connect_timeout=connect_timeout)
    except Exception as e:
        module.fail_json(msg='unable to connect to database, check login_user and login_password are correct or %s has the credentials. Exception message: %s' % (config_file, to_native(e)))
    if not sql_log_bin:
        cursor.execute('SET SQL_LOG_BIN=0;')
    if priv is not None:
        try:
            mode = get_mode(cursor)
        except Exception as e:
            module.fail_json(msg=to_native(e))
        try:
            priv = privileges_unpack(priv, mode)
        except Exception as e:
            module.fail_json(msg='invalid privileges string: %s' % to_native(e))
    if state == 'present':
        if user_exists(cursor, user, host, host_all):
            try:
                if update_password == 'always':
                    (changed, msg) = user_mod(cursor, user, host, host_all, password, encrypted, plugin, plugin_hash_string, plugin_auth_string, priv, append_privs, module)
                else:
                    (changed, msg) = user_mod(cursor, user, host, host_all, None, encrypted, plugin, plugin_hash_string, plugin_auth_string, priv, append_privs, module)
            except (SQLParseError, InvalidPrivsError, mysql_driver.Error) as e:
                module.fail_json(msg=to_native(e))
        else:
            if host_all:
                module.fail_json(msg='host_all parameter cannot be used when adding a user')
            try:
                changed = user_add(cursor, user, host, host_all, password, encrypted, plugin, plugin_hash_string, plugin_auth_string, priv, module.check_mode)
                if changed:
                    msg = 'User added'
            except (SQLParseError, InvalidPrivsError, mysql_driver.Error) as e:
                module.fail_json(msg=to_native(e))
    elif state == 'absent':
        if user_exists(cursor, user, host, host_all):
            changed = user_delete(cursor, user, host, host_all, module.check_mode)
            msg = 'User deleted'
        else:
            changed = False
            msg = "User doesn't exist"
    module.exit_json(changed=changed, user=user, msg=msg)
if __name__ == '__main__':
    main()