from __future__ import absolute_import, division, print_function
__metaclass__ = type
ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['preview'], 'supported_by': 'community'}
DOCUMENTATION = '\n---\nmodule: mysql_db\nshort_description: Add or remove MySQL databases from a remote host\ndescription:\n- Add or remove MySQL databases from a remote host.\nversion_added: \'0.6\'\noptions:\n  name:\n    description:\n    - Name of the database to add or remove.\n    - I(name=all) may only be provided if I(state) is C(dump) or C(import).\n    - List of databases is provided with I(state=dump), I(state=present) and I(state=absent).\n    - If I(name=all) it works like --all-databases option for mysqldump (Added in 2.0).\n    required: true\n    type: list\n    elements: str\n    aliases: [db]\n  state:\n    description:\n    - The database state\n    type: str\n    default: present\n    choices: [\'absent\', \'dump\', \'import\', \'present\']\n  collation:\n    description:\n    - Collation mode (sorting). This only applies to new table/databases and\n      does not update existing ones, this is a limitation of MySQL.\n    type: str\n    default: \'\'\n  encoding:\n    description:\n    - Encoding mode to use, examples include C(utf8) or C(latin1_swedish_ci),\n      at creation of database, dump or importation of sql script.\n    type: str\n    default: \'\'\n  target:\n    description:\n    - Location, on the remote host, of the dump file to read from or write to.\n    - Uncompressed SQL files (C(.sql)) as well as bzip2 (C(.bz2)), gzip (C(.gz)) and\n      xz (Added in 2.0) compressed files are supported.\n    type: path\n  single_transaction:\n    description:\n    - Execute the dump in a single transaction.\n    type: bool\n    default: no\n    version_added: \'2.1\'\n  quick:\n    description:\n    - Option used for dumping large tables.\n    type: bool\n    default: yes\n    version_added: \'2.1\'\n  ignore_tables:\n    description:\n    - A list of table names that will be ignored in the dump\n      of the form database_name.table_name.\n    type: list\n    elements: str\n    required: no\n    default: []\n    version_added: \'2.7\'\n  hex_blob:\n    description:\n    - Dump binary columns using hexadecimal notation.\n    required: no\n    default: no\n    type: bool\n    version_added: \'2.10\'\n  force:\n    description:\n    - Continue dump or import even if we get an SQL error.\n    - Used only when I(state) is C(dump) or C(import).\n    required: no\n    type: bool\n    default: no\n    version_added: \'2.10\'\n  master_data:\n    description:\n      - Option to dump a master replication server to produce a dump file\n        that can be used to set up another server as a slave of the master.\n      - C(0) to not include master data.\n      - C(1) to generate a \'CHANGE MASTER TO\' statement\n        required on the slave to start the replication process.\n      - C(2) to generate a commented \'CHANGE MASTER TO\'.\n      - Can be used when I(state=dump).\n    required: no\n    type: int\n    choices: [0, 1, 2]\n    default: 0\n    version_added: \'2.10\'\n  skip_lock_tables:\n    description:\n      - Skip locking tables for read. Used when I(state=dump), ignored otherwise.\n    required: no\n    type: bool\n    default: no\n    version_added: \'2.10\'\n  dump_extra_args:\n    description:\n      - Provide additional arguments for mysqldump.\n        Used when I(state=dump) only, ignored otherwise.\n    required: no\n    type: str\n    version_added: \'2.10\'\nseealso:\n- module: mysql_info\n- module: mysql_variables\n- module: mysql_user\n- module: mysql_replication\n- name: MySQL command-line client reference\n  description: Complete reference of the MySQL command-line client documentation.\n  link: https://dev.mysql.com/doc/refman/8.0/en/mysql.html\n- name: mysqldump reference\n  description: Complete reference of the ``mysqldump`` client utility documentation.\n  link: https://dev.mysql.com/doc/refman/8.0/en/mysqldump.html\n- name: CREATE DATABASE reference\n  description: Complete reference of the CREATE DATABASE command documentation.\n  link: https://dev.mysql.com/doc/refman/8.0/en/create-database.html\n- name: DROP DATABASE reference\n  description: Complete reference of the DROP DATABASE command documentation.\n  link: https://dev.mysql.com/doc/refman/8.0/en/drop-database.html\nauthor: "Ansible Core Team"\nrequirements:\n   - mysql (command line binary)\n   - mysqldump (command line binary)\nnotes:\n   - Requires the mysql and mysqldump binaries on the remote host.\n   - This module is B(not idempotent) when I(state) is C(import),\n     and will import the dump file each time if run more than once.\nextends_documentation_fragment: mysql\n'
EXAMPLES = "\n- name: Create a new database with name 'bobdata'\n  mysql_db:\n    name: bobdata\n    state: present\n\n- name: Create new databases with names 'foo' and 'bar'\n  mysql_db:\n    name:\n      - foo\n      - bar\n    state: present\n\n# Copy database dump file to remote host and restore it to database 'my_db'\n- name: Copy database dump file\n  copy:\n    src: dump.sql.bz2\n    dest: /tmp\n\n- name: Restore database\n  mysql_db:\n    name: my_db\n    state: import\n    target: /tmp/dump.sql.bz2\n\n- name: Restore database ignoring errors\n  mysql_db:\n    name: my_db\n    state: import\n    target: /tmp/dump.sql.bz2\n    force: yes\n\n- name: Dump multiple databases\n  mysql_db:\n    state: dump\n    name: db_1,db_2\n    target: /tmp/dump.sql\n\n- name: Dump multiple databases\n  mysql_db:\n    state: dump\n    name:\n      - db_1\n      - db_2\n    target: /tmp/dump.sql\n\n- name: Dump all databases to hostname.sql\n  mysql_db:\n    state: dump\n    name: all\n    target: /tmp/dump.sql\n\n- name: Dump all databases to hostname.sql including master data\n  mysql_db:\n    state: dump\n    name: all\n    target: /tmp/dump.sql\n    master_data: 1\n\n# Import of sql script with encoding option\n- name: >\n    Import dump.sql with specific latin1 encoding,\n    similar to mysql -u <username> --default-character-set=latin1 -p <password> < dump.sql\n  mysql_db:\n    state: import\n    name: all\n    encoding: latin1\n    target: /tmp/dump.sql\n\n# Dump of database with encoding option\n- name: >\n    Dump of Databse with specific latin1 encoding,\n    similar to mysqldump -u <username> --default-character-set=latin1 -p <password> <database>\n  mysql_db:\n    state: dump\n    name: db_1\n    encoding: latin1\n    target: /tmp/dump.sql\n\n- name: Delete database with name 'bobdata'\n  mysql_db:\n    name: bobdata\n    state: absent\n\n- name: Make sure there is neither a database with name 'foo', nor one with name 'bar'\n  mysql_db:\n    name:\n      - foo\n      - bar\n    state: absent\n\n# Dump database with argument not directly supported by this module\n# using dump_extra_args parameter\n- name: Dump databases without including triggers\n  mysql_db:\n    state: dump\n    name: foo\n    target: /tmp/dump.sql\n    dump_extra_args: --skip-triggers\n"
RETURN = '\ndb:\n  description: Database names in string format delimited by white space.\n  returned: always\n  type: str\n  sample: "foo bar"\ndb_list:\n  description: List of database names.\n  returned: always\n  type: list\n  sample: ["foo", "bar"]\n  version_added: \'2.9\'\nexecuted_commands:\n  description: List of commands which tried to run.\n  returned: if executed\n  type: list\n  sample: ["CREATE DATABASE acme"]\n  version_added: \'2.10\'\n'
import os
import subprocess
import traceback
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.database import mysql_quote_identifier
from ansible.module_utils.mysql import mysql_connect, mysql_driver, mysql_driver_fail_msg
from ansible.module_utils.six.moves import shlex_quote
from ansible.module_utils._text import to_native
executed_commands = []

def db_exists(cursor, db):
    res = 0
    for each_db in db:
        res += cursor.execute('SHOW DATABASES LIKE %s', (each_db.replace('_', '\\_'),))
    return res == len(db)

def db_delete(cursor, db):
    if not db:
        return False
    for each_db in db:
        query = 'DROP DATABASE %s' % mysql_quote_identifier(each_db, 'database')
        executed_commands.append(query)
        cursor.execute(query)
    return True

def db_dump(module, host, user, password, db_name, target, all_databases, port, config_file, socket=None, ssl_cert=None, ssl_key=None, ssl_ca=None, single_transaction=None, quick=None, ignore_tables=None, hex_blob=None, encoding=None, force=False, master_data=0, skip_lock_tables=False, dump_extra_args=None):
    cmd = module.get_bin_path('mysqldump', True)
    if config_file:
        cmd += ' --defaults-extra-file=%s' % shlex_quote(config_file)
    if user is not None:
        cmd += ' --user=%s' % shlex_quote(user)
    if password is not None:
        cmd += ' --password=%s' % shlex_quote(password)
    if ssl_cert is not None:
        cmd += ' --ssl-cert=%s' % shlex_quote(ssl_cert)
    if ssl_key is not None:
        cmd += ' --ssl-key=%s' % shlex_quote(ssl_key)
    if ssl_ca is not None:
        cmd += ' --ssl-ca=%s' % shlex_quote(ssl_ca)
    if force:
        cmd += ' --force'
    if socket is not None:
        cmd += ' --socket=%s' % shlex_quote(socket)
    else:
        cmd += ' --host=%s --port=%i' % (shlex_quote(host), port)
    if all_databases:
        cmd += ' --all-databases'
    elif len(db_name) > 1:
        cmd += ' --databases {0}'.format(' '.join(db_name))
    else:
        cmd += ' %s' % shlex_quote(' '.join(db_name))
    if skip_lock_tables:
        cmd += ' --skip-lock-tables'
    if encoding is not None and encoding != '':
        cmd += ' --default-character-set=%s' % shlex_quote(encoding)
    if single_transaction:
        cmd += ' --single-transaction=true'
    if quick:
        cmd += ' --quick'
    if ignore_tables:
        for an_ignored_table in ignore_tables:
            cmd += ' --ignore-table={0}'.format(an_ignored_table)
    if hex_blob:
        cmd += ' --hex-blob'
    if master_data:
        cmd += ' --master-data=%s' % master_data
    if dump_extra_args is not None:
        cmd += ' ' + dump_extra_args
    path = None
    if os.path.splitext(target)[-1] == '.gz':
        path = module.get_bin_path('gzip', True)
    elif os.path.splitext(target)[-1] == '.bz2':
        path = module.get_bin_path('bzip2', True)
    elif os.path.splitext(target)[-1] == '.xz':
        path = module.get_bin_path('xz', True)
    if path:
        cmd = '%s | %s > %s' % (cmd, path, shlex_quote(target))
    else:
        cmd += ' > %s' % shlex_quote(target)
    executed_commands.append(cmd)
    (rc, stdout, stderr) = module.run_command(cmd, use_unsafe_shell=True)
    return (rc, stdout, stderr)

def db_import(module, host, user, password, db_name, target, all_databases, port, config_file, socket=None, ssl_cert=None, ssl_key=None, ssl_ca=None, encoding=None, force=False):
    if not os.path.exists(target):
        return module.fail_json(msg='target %s does not exist on the host' % target)
    cmd = [module.get_bin_path('mysql', True)]
    if config_file:
        cmd.append('--defaults-extra-file=%s' % shlex_quote(config_file))
    if user:
        cmd.append('--user=%s' % shlex_quote(user))
    if password:
        cmd.append('--password=%s' % shlex_quote(password))
    if ssl_cert is not None:
        cmd.append('--ssl-cert=%s' % shlex_quote(ssl_cert))
    if ssl_key is not None:
        cmd.append('--ssl-key=%s' % shlex_quote(ssl_key))
    if ssl_ca is not None:
        cmd.append('--ssl-ca=%s' % shlex_quote(ssl_ca))
    if force:
        cmd.append('-f')
    if socket is not None:
        cmd.append('--socket=%s' % shlex_quote(socket))
    else:
        cmd.append('--host=%s' % shlex_quote(host))
        cmd.append('--port=%i' % port)
    if encoding is not None and encoding != '':
        cmd.append('--default-character-set=%s' % shlex_quote(encoding))
    if not all_databases:
        cmd.append('--one-database')
        cmd.append(shlex_quote(''.join(db_name)))
    comp_prog_path = None
    if os.path.splitext(target)[-1] == '.gz':
        comp_prog_path = module.get_bin_path('gzip', required=True)
    elif os.path.splitext(target)[-1] == '.bz2':
        comp_prog_path = module.get_bin_path('bzip2', required=True)
    elif os.path.splitext(target)[-1] == '.xz':
        comp_prog_path = module.get_bin_path('xz', required=True)
    if comp_prog_path:
        executed_commands.append('%s -dc %s | %s' % (comp_prog_path, target, ' '.join(cmd)))
        p1 = subprocess.Popen([comp_prog_path, '-dc', target], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p2 = subprocess.Popen(cmd, stdin=p1.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout2, stderr2) = p2.communicate()
        p1.stdout.close()
        p1.wait()
        if p1.returncode != 0:
            stderr1 = p1.stderr.read()
            return (p1.returncode, '', stderr1)
        else:
            return (p2.returncode, stdout2, stderr2)
    else:
        cmd = ' '.join(cmd)
        cmd += ' < %s' % shlex_quote(target)
        executed_commands.append(cmd)
        (rc, stdout, stderr) = module.run_command(cmd, use_unsafe_shell=True)
        return (rc, stdout, stderr)

def db_create(cursor, db, encoding, collation):
    if not db:
        return False
    query_params = dict(enc=encoding, collate=collation)
    res = 0
    for each_db in db:
        query = ['CREATE DATABASE %s' % mysql_quote_identifier(each_db, 'database')]
        if encoding:
            query.append('CHARACTER SET %(enc)s')
        if collation:
            query.append('COLLATE %(collate)s')
        query = ' '.join(query)
        res += cursor.execute(query, query_params)
        try:
            executed_commands.append(cursor.mogrify(query, query_params))
        except AttributeError:
            executed_commands.append(cursor._executed)
        except Exception:
            executed_commands.append(query)
    return res > 0

def main():
    module = AnsibleModule(argument_spec=dict(login_user=dict(type='str'), login_password=dict(type='str', no_log=True), login_host=dict(type='str', default='localhost'), login_port=dict(type='int', default=3306), login_unix_socket=dict(type='str'), name=dict(type='list', required=True, aliases=['db']), encoding=dict(type='str', default=''), collation=dict(type='str', default=''), target=dict(type='path'), state=dict(type='str', default='present', choices=['absent', 'dump', 'import', 'present']), client_cert=dict(type='path', aliases=['ssl_cert']), client_key=dict(type='path', aliases=['ssl_key']), ca_cert=dict(type='path', aliases=['ssl_ca']), connect_timeout=dict(type='int', default=30), config_file=dict(type='path', default='~/.my.cnf'), single_transaction=dict(type='bool', default=False), quick=dict(type='bool', default=True), ignore_tables=dict(type='list', default=[]), hex_blob=dict(default=False, type='bool'), force=dict(type='bool', default=False), master_data=dict(type='int', default=0, choices=[0, 1, 2]), skip_lock_tables=dict(type='bool', default=False), dump_extra_args=dict(type='str')), supports_check_mode=True)
    if mysql_driver is None:
        module.fail_json(msg=mysql_driver_fail_msg)
    db = module.params['name']
    if not db:
        module.exit_json(changed=False, db=db, db_list=[])
    db = [each_db.strip() for each_db in db]
    encoding = module.params['encoding']
    collation = module.params['collation']
    state = module.params['state']
    target = module.params['target']
    socket = module.params['login_unix_socket']
    login_port = module.params['login_port']
    if login_port < 0 or login_port > 65535:
        module.fail_json(msg='login_port must be a valid unix port number (0-65535)')
    ssl_cert = module.params['client_cert']
    ssl_key = module.params['client_key']
    ssl_ca = module.params['ca_cert']
    connect_timeout = module.params['connect_timeout']
    config_file = module.params['config_file']
    login_password = module.params['login_password']
    login_user = module.params['login_user']
    login_host = module.params['login_host']
    ignore_tables = module.params['ignore_tables']
    for a_table in ignore_tables:
        if a_table == '':
            module.fail_json(msg='Name of ignored table cannot be empty')
    single_transaction = module.params['single_transaction']
    quick = module.params['quick']
    hex_blob = module.params['hex_blob']
    force = module.params['force']
    master_data = module.params['master_data']
    skip_lock_tables = module.params['skip_lock_tables']
    dump_extra_args = module.params['dump_extra_args']
    if len(db) > 1 and state == 'import':
        module.fail_json(msg='Multiple databases are not supported with state=import')
    db_name = ' '.join(db)
    all_databases = False
    if state in ['dump', 'import']:
        if target is None:
            module.fail_json(msg='with state=%s target is required' % state)
        if db == ['all']:
            all_databases = True
    elif db == ['all']:
        module.fail_json(msg="name is not allowed to equal 'all' unless state equals import, or dump.")
    try:
        (cursor, db_conn) = mysql_connect(module, login_user, login_password, config_file, ssl_cert, ssl_key, ssl_ca, connect_timeout=connect_timeout)
    except Exception as e:
        if os.path.exists(config_file):
            module.fail_json(msg='unable to connect to database, check login_user and login_password are correct or %s has the credentials. Exception message: %s' % (config_file, to_native(e)))
        else:
            module.fail_json(msg='unable to find %s. Exception message: %s' % (config_file, to_native(e)))
    changed = False
    if not os.path.exists(config_file):
        config_file = None
    existence_list = []
    non_existence_list = []
    if not all_databases:
        for each_database in db:
            if db_exists(cursor, [each_database]):
                existence_list.append(each_database)
            else:
                non_existence_list.append(each_database)
    if state == 'absent':
        if module.check_mode:
            module.exit_json(changed=bool(existence_list), db=db_name, db_list=db)
        try:
            changed = db_delete(cursor, existence_list)
        except Exception as e:
            module.fail_json(msg='error deleting database: %s' % to_native(e))
        module.exit_json(changed=changed, db=db_name, db_list=db, executed_commands=executed_commands)
    elif state == 'present':
        if module.check_mode:
            module.exit_json(changed=bool(non_existence_list), db=db_name, db_list=db)
        changed = False
        if non_existence_list:
            try:
                changed = db_create(cursor, non_existence_list, encoding, collation)
            except Exception as e:
                module.fail_json(msg='error creating database: %s' % to_native(e), exception=traceback.format_exc())
        module.exit_json(changed=changed, db=db_name, db_list=db, executed_commands=executed_commands)
    elif state == 'dump':
        if non_existence_list and (not all_databases):
            module.fail_json(msg='Cannot dump database(s) %r - not found' % ', '.join(non_existence_list))
        if module.check_mode:
            module.exit_json(changed=True, db=db_name, db_list=db)
        (rc, stdout, stderr) = db_dump(module, login_host, login_user, login_password, db, target, all_databases, login_port, config_file, socket, ssl_cert, ssl_key, ssl_ca, single_transaction, quick, ignore_tables, hex_blob, encoding, force, master_data, skip_lock_tables, dump_extra_args)
        if rc != 0:
            module.fail_json(msg='%s' % stderr)
        module.exit_json(changed=True, db=db_name, db_list=db, msg=stdout, executed_commands=executed_commands)
    elif state == 'import':
        if module.check_mode:
            module.exit_json(changed=True, db=db_name, db_list=db)
        if non_existence_list and (not all_databases):
            try:
                db_create(cursor, non_existence_list, encoding, collation)
            except Exception as e:
                module.fail_json(msg='error creating database: %s' % to_native(e), exception=traceback.format_exc())
        (rc, stdout, stderr) = db_import(module, login_host, login_user, login_password, db, target, all_databases, login_port, config_file, socket, ssl_cert, ssl_key, ssl_ca, encoding, force)
        if rc != 0:
            module.fail_json(msg='%s' % stderr)
        module.exit_json(changed=True, db=db_name, db_list=db, msg=stdout, executed_commands=executed_commands)
if __name__ == '__main__':
    main()