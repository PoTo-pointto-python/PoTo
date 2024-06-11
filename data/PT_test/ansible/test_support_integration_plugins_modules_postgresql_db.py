from __future__ import absolute_import, division, print_function
__metaclass__ = type
ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['stableinterface'], 'supported_by': 'community'}
DOCUMENTATION = '\n---\nmodule: postgresql_db\nshort_description: Add or remove PostgreSQL databases from a remote host.\ndescription:\n   - Add or remove PostgreSQL databases from a remote host.\nversion_added: \'0.6\'\noptions:\n  name:\n    description:\n      - Name of the database to add or remove\n    type: str\n    required: true\n    aliases: [ db ]\n  port:\n    description:\n      - Database port to connect (if needed)\n    type: int\n    default: 5432\n    aliases:\n      - login_port\n  owner:\n    description:\n      - Name of the role to set as owner of the database\n    type: str\n  template:\n    description:\n      - Template used to create the database\n    type: str\n  encoding:\n    description:\n      - Encoding of the database\n    type: str\n  lc_collate:\n    description:\n      - Collation order (LC_COLLATE) to use in the database. Must match collation order of template database unless C(template0) is used as template.\n    type: str\n  lc_ctype:\n    description:\n      - Character classification (LC_CTYPE) to use in the database (e.g. lower, upper, ...) Must match LC_CTYPE of template database unless C(template0)\n        is used as template.\n    type: str\n  session_role:\n    description:\n    - Switch to session_role after connecting. The specified session_role must be a role that the current login_user is a member of.\n    - Permissions checking for SQL commands is carried out as though the session_role were the one that had logged in originally.\n    type: str\n    version_added: \'2.8\'\n  state:\n    description:\n    - The database state.\n    - C(present) implies that the database should be created if necessary.\n    - C(absent) implies that the database should be removed if present.\n    - C(dump) requires a target definition to which the database will be backed up. (Added in Ansible 2.4)\n      Note that in some PostgreSQL versions of pg_dump, which is an embedded PostgreSQL utility and is used by the module,\n      returns rc 0 even when errors occurred (e.g. the connection is forbidden by pg_hba.conf, etc.),\n      so the module returns changed=True but the dump has not actually been done. Please, be sure that your version of\n      pg_dump returns rc 1 in this case.\n    - C(restore) also requires a target definition from which the database will be restored. (Added in Ansible 2.4)\n    - The format of the backup will be detected based on the target name.\n    - Supported compression formats for dump and restore include C(.pgc), C(.bz2), C(.gz) and C(.xz)\n    - Supported formats for dump and restore include C(.sql) and C(.tar)\n    type: str\n    choices: [ absent, dump, present, restore ]\n    default: present\n  target:\n    description:\n    - File to back up or restore from.\n    - Used when I(state) is C(dump) or C(restore).\n    type: path\n    version_added: \'2.4\'\n  target_opts:\n    description:\n    - Further arguments for pg_dump or pg_restore.\n    - Used when I(state) is C(dump) or C(restore).\n    type: str\n    version_added: \'2.4\'\n  maintenance_db:\n    description:\n      - The value specifies the initial database (which is also called as maintenance DB) that Ansible connects to.\n    type: str\n    default: postgres\n    version_added: \'2.5\'\n  conn_limit:\n    description:\n      - Specifies the database connection limit.\n    type: str\n    version_added: \'2.8\'\n  tablespace:\n    description:\n      - The tablespace to set for the database\n        U(https://www.postgresql.org/docs/current/sql-alterdatabase.html).\n      - If you want to move the database back to the default tablespace,\n        explicitly set this to pg_default.\n    type: path\n    version_added: \'2.9\'\n  dump_extra_args:\n    description:\n      - Provides additional arguments when I(state) is C(dump).\n      - Cannot be used with dump-file-format-related arguments like ``--format=d``.\n    type: str\n    version_added: \'2.10\'\nseealso:\n- name: CREATE DATABASE reference\n  description: Complete reference of the CREATE DATABASE command documentation.\n  link: https://www.postgresql.org/docs/current/sql-createdatabase.html\n- name: DROP DATABASE reference\n  description: Complete reference of the DROP DATABASE command documentation.\n  link: https://www.postgresql.org/docs/current/sql-dropdatabase.html\n- name: pg_dump reference\n  description: Complete reference of pg_dump documentation.\n  link: https://www.postgresql.org/docs/current/app-pgdump.html\n- name: pg_restore reference\n  description: Complete reference of pg_restore documentation.\n  link: https://www.postgresql.org/docs/current/app-pgrestore.html\n- module: postgresql_tablespace\n- module: postgresql_info\n- module: postgresql_ping\nnotes:\n- State C(dump) and C(restore) don\'t require I(psycopg2) since version 2.8.\nauthor: "Ansible Core Team"\nextends_documentation_fragment:\n- postgres\n'
EXAMPLES = '\n- name: Create a new database with name "acme"\n  postgresql_db:\n    name: acme\n\n# Note: If a template different from "template0" is specified, encoding and locale settings must match those of the template.\n- name: Create a new database with name "acme" and specific encoding and locale # settings.\n  postgresql_db:\n    name: acme\n    encoding: UTF-8\n    lc_collate: de_DE.UTF-8\n    lc_ctype: de_DE.UTF-8\n    template: template0\n\n# Note: Default limit for the number of concurrent connections to a specific database is "-1", which means "unlimited"\n- name: Create a new database with name "acme" which has a limit of 100 concurrent connections\n  postgresql_db:\n    name: acme\n    conn_limit: "100"\n\n- name: Dump an existing database to a file\n  postgresql_db:\n    name: acme\n    state: dump\n    target: /tmp/acme.sql\n\n- name: Dump an existing database to a file excluding the test table\n  postgresql_db:\n    name: acme\n    state: dump\n    target: /tmp/acme.sql\n    dump_extra_args: --exclude-table=test\n\n- name: Dump an existing database to a file (with compression)\n  postgresql_db:\n    name: acme\n    state: dump\n    target: /tmp/acme.sql.gz\n\n- name: Dump a single schema for an existing database\n  postgresql_db:\n    name: acme\n    state: dump\n    target: /tmp/acme.sql\n    target_opts: "-n public"\n\n# Note: In the example below, if database foo exists and has another tablespace\n# the tablespace will be changed to foo. Access to the database will be locked\n# until the copying of database files is finished.\n- name: Create a new database called foo in tablespace bar\n  postgresql_db:\n    name: foo\n    tablespace: bar\n'
RETURN = '\nexecuted_commands:\n  description: List of commands which tried to run.\n  returned: always\n  type: list\n  sample: ["CREATE DATABASE acme"]\n  version_added: \'2.10\'\n'
import os
import subprocess
import traceback
try:
    import psycopg2
    import psycopg2.extras
except ImportError:
    HAS_PSYCOPG2 = False
else:
    HAS_PSYCOPG2 = True
import ansible.module_utils.postgres as pgutils
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.database import SQLParseError, pg_quote_identifier
from ansible.module_utils.six import iteritems
from ansible.module_utils.six.moves import shlex_quote
from ansible.module_utils._text import to_native
executed_commands = []

class NotSupportedError(Exception):
    pass

def set_owner(cursor, db, owner):
    query = 'ALTER DATABASE %s OWNER TO "%s"' % (pg_quote_identifier(db, 'database'), owner)
    executed_commands.append(query)
    cursor.execute(query)
    return True

def set_conn_limit(cursor, db, conn_limit):
    query = 'ALTER DATABASE %s CONNECTION LIMIT %s' % (pg_quote_identifier(db, 'database'), conn_limit)
    executed_commands.append(query)
    cursor.execute(query)
    return True

def get_encoding_id(cursor, encoding):
    query = 'SELECT pg_char_to_encoding(%(encoding)s) AS encoding_id;'
    cursor.execute(query, {'encoding': encoding})
    return cursor.fetchone()['encoding_id']

def get_db_info(cursor, db):
    query = '\n    SELECT rolname AS owner,\n    pg_encoding_to_char(encoding) AS encoding, encoding AS encoding_id,\n    datcollate AS lc_collate, datctype AS lc_ctype, pg_database.datconnlimit AS conn_limit,\n    spcname AS tablespace\n    FROM pg_database\n    JOIN pg_roles ON pg_roles.oid = pg_database.datdba\n    JOIN pg_tablespace ON pg_tablespace.oid = pg_database.dattablespace\n    WHERE datname = %(db)s\n    '
    cursor.execute(query, {'db': db})
    return cursor.fetchone()

def db_exists(cursor, db):
    query = 'SELECT * FROM pg_database WHERE datname=%(db)s'
    cursor.execute(query, {'db': db})
    return cursor.rowcount == 1

def db_delete(cursor, db):
    if db_exists(cursor, db):
        query = 'DROP DATABASE %s' % pg_quote_identifier(db, 'database')
        executed_commands.append(query)
        cursor.execute(query)
        return True
    else:
        return False

def db_create(cursor, db, owner, template, encoding, lc_collate, lc_ctype, conn_limit, tablespace):
    params = dict(enc=encoding, collate=lc_collate, ctype=lc_ctype, conn_limit=conn_limit, tablespace=tablespace)
    if not db_exists(cursor, db):
        query_fragments = ['CREATE DATABASE %s' % pg_quote_identifier(db, 'database')]
        if owner:
            query_fragments.append('OWNER "%s"' % owner)
        if template:
            query_fragments.append('TEMPLATE %s' % pg_quote_identifier(template, 'database'))
        if encoding:
            query_fragments.append('ENCODING %(enc)s')
        if lc_collate:
            query_fragments.append('LC_COLLATE %(collate)s')
        if lc_ctype:
            query_fragments.append('LC_CTYPE %(ctype)s')
        if tablespace:
            query_fragments.append('TABLESPACE %s' % pg_quote_identifier(tablespace, 'tablespace'))
        if conn_limit:
            query_fragments.append('CONNECTION LIMIT %(conn_limit)s' % {'conn_limit': conn_limit})
        query = ' '.join(query_fragments)
        executed_commands.append(cursor.mogrify(query, params))
        cursor.execute(query, params)
        return True
    else:
        db_info = get_db_info(cursor, db)
        if encoding and get_encoding_id(cursor, encoding) != db_info['encoding_id']:
            raise NotSupportedError('Changing database encoding is not supported. Current encoding: %s' % db_info['encoding'])
        elif lc_collate and lc_collate != db_info['lc_collate']:
            raise NotSupportedError('Changing LC_COLLATE is not supported. Current LC_COLLATE: %s' % db_info['lc_collate'])
        elif lc_ctype and lc_ctype != db_info['lc_ctype']:
            raise NotSupportedError('Changing LC_CTYPE is not supported.Current LC_CTYPE: %s' % db_info['lc_ctype'])
        else:
            changed = False
            if owner and owner != db_info['owner']:
                changed = set_owner(cursor, db, owner)
            if conn_limit and conn_limit != str(db_info['conn_limit']):
                changed = set_conn_limit(cursor, db, conn_limit)
            if tablespace and tablespace != db_info['tablespace']:
                changed = set_tablespace(cursor, db, tablespace)
            return changed

def db_matches(cursor, db, owner, template, encoding, lc_collate, lc_ctype, conn_limit, tablespace):
    if not db_exists(cursor, db):
        return False
    else:
        db_info = get_db_info(cursor, db)
        if encoding and get_encoding_id(cursor, encoding) != db_info['encoding_id']:
            return False
        elif lc_collate and lc_collate != db_info['lc_collate']:
            return False
        elif lc_ctype and lc_ctype != db_info['lc_ctype']:
            return False
        elif owner and owner != db_info['owner']:
            return False
        elif conn_limit and conn_limit != str(db_info['conn_limit']):
            return False
        elif tablespace and tablespace != db_info['tablespace']:
            return False
        else:
            return True

def db_dump(module, target, target_opts='', db=None, dump_extra_args=None, user=None, password=None, host=None, port=None, **kw):
    flags = login_flags(db, host, port, user, db_prefix=False)
    cmd = module.get_bin_path('pg_dump', True)
    comp_prog_path = None
    if os.path.splitext(target)[-1] == '.tar':
        flags.append(' --format=t')
    elif os.path.splitext(target)[-1] == '.pgc':
        flags.append(' --format=c')
    if os.path.splitext(target)[-1] == '.gz':
        if module.get_bin_path('pigz'):
            comp_prog_path = module.get_bin_path('pigz', True)
        else:
            comp_prog_path = module.get_bin_path('gzip', True)
    elif os.path.splitext(target)[-1] == '.bz2':
        comp_prog_path = module.get_bin_path('bzip2', True)
    elif os.path.splitext(target)[-1] == '.xz':
        comp_prog_path = module.get_bin_path('xz', True)
    cmd += ''.join(flags)
    if dump_extra_args:
        cmd += ' {0} '.format(dump_extra_args)
    if target_opts:
        cmd += ' {0} '.format(target_opts)
    if comp_prog_path:
        fifo = os.path.join(module.tmpdir, 'pg_fifo')
        os.mkfifo(fifo)
        cmd = '{1} <{3} > {2} & {0} >{3}'.format(cmd, comp_prog_path, shlex_quote(target), fifo)
    else:
        cmd = '{0} > {1}'.format(cmd, shlex_quote(target))
    return do_with_password(module, cmd, password)

def db_restore(module, target, target_opts='', db=None, user=None, password=None, host=None, port=None, **kw):
    flags = login_flags(db, host, port, user)
    comp_prog_path = None
    cmd = module.get_bin_path('psql', True)
    if os.path.splitext(target)[-1] == '.sql':
        flags.append(' --file={0}'.format(target))
    elif os.path.splitext(target)[-1] == '.tar':
        flags.append(' --format=Tar')
        cmd = module.get_bin_path('pg_restore', True)
    elif os.path.splitext(target)[-1] == '.pgc':
        flags.append(' --format=Custom')
        cmd = module.get_bin_path('pg_restore', True)
    elif os.path.splitext(target)[-1] == '.gz':
        comp_prog_path = module.get_bin_path('zcat', True)
    elif os.path.splitext(target)[-1] == '.bz2':
        comp_prog_path = module.get_bin_path('bzcat', True)
    elif os.path.splitext(target)[-1] == '.xz':
        comp_prog_path = module.get_bin_path('xzcat', True)
    cmd += ''.join(flags)
    if target_opts:
        cmd += ' {0} '.format(target_opts)
    if comp_prog_path:
        env = os.environ.copy()
        if password:
            env = {'PGPASSWORD': password}
        p1 = subprocess.Popen([comp_prog_path, target], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p2 = subprocess.Popen(cmd, stdin=p1.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, env=env)
        (stdout2, stderr2) = p2.communicate()
        p1.stdout.close()
        p1.wait()
        if p1.returncode != 0:
            stderr1 = p1.stderr.read()
            return (p1.returncode, '', stderr1, 'cmd: ****')
        else:
            return (p2.returncode, '', stderr2, 'cmd: ****')
    else:
        cmd = '{0} < {1}'.format(cmd, shlex_quote(target))
    return do_with_password(module, cmd, password)

def login_flags(db, host, port, user, db_prefix=True):
    """
    returns a list of connection argument strings each prefixed
    with a space and quoted where necessary to later be combined
    in a single shell string with `"".join(rv)`

    db_prefix determines if "--dbname" is prefixed to the db argument,
    since the argument was introduced in 9.3.
    """
    flags = []
    if db:
        if db_prefix:
            flags.append(' --dbname={0}'.format(shlex_quote(db)))
        else:
            flags.append(' {0}'.format(shlex_quote(db)))
    if host:
        flags.append(' --host={0}'.format(host))
    if port:
        flags.append(' --port={0}'.format(port))
    if user:
        flags.append(' --username={0}'.format(user))
    return flags

def do_with_password(module, cmd, password):
    env = {}
    if password:
        env = {'PGPASSWORD': password}
    executed_commands.append(cmd)
    (rc, stderr, stdout) = module.run_command(cmd, use_unsafe_shell=True, environ_update=env)
    return (rc, stderr, stdout, cmd)

def set_tablespace(cursor, db, tablespace):
    query = 'ALTER DATABASE %s SET TABLESPACE %s' % (pg_quote_identifier(db, 'database'), pg_quote_identifier(tablespace, 'tablespace'))
    executed_commands.append(query)
    cursor.execute(query)
    return True

def main():
    argument_spec = pgutils.postgres_common_argument_spec()
    argument_spec.update(db=dict(type='str', required=True, aliases=['name']), owner=dict(type='str', default=''), template=dict(type='str', default=''), encoding=dict(type='str', default=''), lc_collate=dict(type='str', default=''), lc_ctype=dict(type='str', default=''), state=dict(type='str', default='present', choices=['absent', 'dump', 'present', 'restore']), target=dict(type='path', default=''), target_opts=dict(type='str', default=''), maintenance_db=dict(type='str', default='postgres'), session_role=dict(type='str'), conn_limit=dict(type='str', default=''), tablespace=dict(type='path', default=''), dump_extra_args=dict(type='str', default=None))
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    db = module.params['db']
    owner = module.params['owner']
    template = module.params['template']
    encoding = module.params['encoding']
    lc_collate = module.params['lc_collate']
    lc_ctype = module.params['lc_ctype']
    target = module.params['target']
    target_opts = module.params['target_opts']
    state = module.params['state']
    changed = False
    maintenance_db = module.params['maintenance_db']
    session_role = module.params['session_role']
    conn_limit = module.params['conn_limit']
    tablespace = module.params['tablespace']
    dump_extra_args = module.params['dump_extra_args']
    raw_connection = state in ('dump', 'restore')
    if not raw_connection:
        pgutils.ensure_required_libs(module)
    params_map = {'login_host': 'host', 'login_user': 'user', 'login_password': 'password', 'port': 'port', 'ssl_mode': 'sslmode', 'ca_cert': 'sslrootcert'}
    kw = dict(((params_map[k], v) for (k, v) in iteritems(module.params) if k in params_map and v != '' and (v is not None)))
    is_localhost = 'host' not in kw or kw['host'] == '' or kw['host'] == 'localhost'
    if is_localhost and module.params['login_unix_socket'] != '':
        kw['host'] = module.params['login_unix_socket']
    if target == '':
        target = '{0}/{1}.sql'.format(os.getcwd(), db)
        target = os.path.expanduser(target)
    if not raw_connection:
        try:
            db_connection = psycopg2.connect(database=maintenance_db, **kw)
            if psycopg2.__version__ >= '2.4.2':
                db_connection.autocommit = True
            else:
                db_connection.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        except TypeError as e:
            if 'sslrootcert' in e.args[0]:
                module.fail_json(msg='Postgresql server must be at least version 8.4 to support sslrootcert. Exception: {0}'.format(to_native(e)), exception=traceback.format_exc())
            module.fail_json(msg='unable to connect to database: %s' % to_native(e), exception=traceback.format_exc())
        except Exception as e:
            module.fail_json(msg='unable to connect to database: %s' % to_native(e), exception=traceback.format_exc())
        if session_role:
            try:
                cursor.execute('SET ROLE "%s"' % session_role)
            except Exception as e:
                module.fail_json(msg='Could not switch role: %s' % to_native(e), exception=traceback.format_exc())
    try:
        if module.check_mode:
            if state == 'absent':
                changed = db_exists(cursor, db)
            elif state == 'present':
                changed = not db_matches(cursor, db, owner, template, encoding, lc_collate, lc_ctype, conn_limit, tablespace)
            module.exit_json(changed=changed, db=db, executed_commands=executed_commands)
        if state == 'absent':
            try:
                changed = db_delete(cursor, db)
            except SQLParseError as e:
                module.fail_json(msg=to_native(e), exception=traceback.format_exc())
        elif state == 'present':
            try:
                changed = db_create(cursor, db, owner, template, encoding, lc_collate, lc_ctype, conn_limit, tablespace)
            except SQLParseError as e:
                module.fail_json(msg=to_native(e), exception=traceback.format_exc())
        elif state in ('dump', 'restore'):
            method = state == 'dump' and db_dump or db_restore
            try:
                if state == 'dump':
                    (rc, stdout, stderr, cmd) = method(module, target, target_opts, db, dump_extra_args, **kw)
                else:
                    (rc, stdout, stderr, cmd) = method(module, target, target_opts, db, **kw)
                if rc != 0:
                    module.fail_json(msg=stderr, stdout=stdout, rc=rc, cmd=cmd)
                else:
                    module.exit_json(changed=True, msg=stdout, stderr=stderr, rc=rc, cmd=cmd, executed_commands=executed_commands)
            except SQLParseError as e:
                module.fail_json(msg=to_native(e), exception=traceback.format_exc())
    except NotSupportedError as e:
        module.fail_json(msg=to_native(e), exception=traceback.format_exc())
    except SystemExit:
        raise
    except Exception as e:
        module.fail_json(msg='Database query failed: %s' % to_native(e), exception=traceback.format_exc())
    module.exit_json(changed=changed, db=db, executed_commands=executed_commands)
if __name__ == '__main__':
    main()