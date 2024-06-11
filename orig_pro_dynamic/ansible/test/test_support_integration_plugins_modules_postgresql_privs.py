from __future__ import absolute_import, division, print_function
__metaclass__ = type
ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['stableinterface'], 'supported_by': 'community'}
DOCUMENTATION = '\n---\nmodule: postgresql_privs\nversion_added: \'1.2\'\nshort_description: Grant or revoke privileges on PostgreSQL database objects\ndescription:\n- Grant or revoke privileges on PostgreSQL database objects.\n- This module is basically a wrapper around most of the functionality of\n  PostgreSQL\'s GRANT and REVOKE statements with detection of changes\n  (GRANT/REVOKE I(privs) ON I(type) I(objs) TO/FROM I(roles)).\noptions:\n  database:\n    description:\n    - Name of database to connect to.\n    required: yes\n    type: str\n    aliases:\n    - db\n    - login_db\n  state:\n    description:\n    - If C(present), the specified privileges are granted, if C(absent) they are revoked.\n    type: str\n    default: present\n    choices: [ absent, present ]\n  privs:\n    description:\n    - Comma separated list of privileges to grant/revoke.\n    type: str\n    aliases:\n    - priv\n  type:\n    description:\n    - Type of database object to set privileges on.\n    - The C(default_privs) choice is available starting at version 2.7.\n    - The C(foreign_data_wrapper) and C(foreign_server) object types are available from Ansible version \'2.8\'.\n    - The C(type) choice is available from Ansible version \'2.10\'.\n    type: str\n    default: table\n    choices: [ database, default_privs, foreign_data_wrapper, foreign_server, function,\n               group, language, table, tablespace, schema, sequence, type ]\n  objs:\n    description:\n    - Comma separated list of database objects to set privileges on.\n    - If I(type) is C(table), C(partition table), C(sequence) or C(function),\n      the special valueC(ALL_IN_SCHEMA) can be provided instead to specify all\n      database objects of type I(type) in the schema specified via I(schema).\n      (This also works with PostgreSQL < 9.0.) (C(ALL_IN_SCHEMA) is available\n       for C(function) and C(partition table) from version 2.8)\n    - If I(type) is C(database), this parameter can be omitted, in which case\n      privileges are set for the database specified via I(database).\n    - \'If I(type) is I(function), colons (":") in object names will be\n      replaced with commas (needed to specify function signatures, see examples)\'\n    type: str\n    aliases:\n    - obj\n  schema:\n    description:\n    - Schema that contains the database objects specified via I(objs).\n    - May only be provided if I(type) is C(table), C(sequence), C(function), C(type),\n      or C(default_privs). Defaults to C(public) in these cases.\n    - Pay attention, for embedded types when I(type=type)\n      I(schema) can be C(pg_catalog) or C(information_schema) respectively.\n    type: str\n  roles:\n    description:\n    - Comma separated list of role (user/group) names to set permissions for.\n    - The special value C(PUBLIC) can be provided instead to set permissions\n      for the implicitly defined PUBLIC group.\n    type: str\n    required: yes\n    aliases:\n    - role\n  fail_on_role:\n    version_added: \'2.8\'\n    description:\n    - If C(yes), fail when target role (for whom privs need to be granted) does not exist.\n      Otherwise just warn and continue.\n    default: yes\n    type: bool\n  session_role:\n    version_added: \'2.8\'\n    description:\n    - Switch to session_role after connecting.\n    - The specified session_role must be a role that the current login_user is a member of.\n    - Permissions checking for SQL commands is carried out as though the session_role were the one that had logged in originally.\n    type: str\n  target_roles:\n    description:\n    - A list of existing role (user/group) names to set as the\n      default permissions for database objects subsequently created by them.\n    - Parameter I(target_roles) is only available with C(type=default_privs).\n    type: str\n    version_added: \'2.8\'\n  grant_option:\n    description:\n    - Whether C(role) may grant/revoke the specified privileges/group memberships to others.\n    - Set to C(no) to revoke GRANT OPTION, leave unspecified to make no changes.\n    - I(grant_option) only has an effect if I(state) is C(present).\n    type: bool\n    aliases:\n    - admin_option\n  host:\n    description:\n    - Database host address. If unspecified, connect via Unix socket.\n    type: str\n    aliases:\n    - login_host\n  port:\n    description:\n    - Database port to connect to.\n    type: int\n    default: 5432\n    aliases:\n    - login_port\n  unix_socket:\n    description:\n    - Path to a Unix domain socket for local connections.\n    type: str\n    aliases:\n    - login_unix_socket\n  login:\n    description:\n    - The username to authenticate with.\n    type: str\n    default: postgres\n    aliases:\n    - login_user\n  password:\n    description:\n    - The password to authenticate with.\n    type: str\n    aliases:\n    - login_password\n  ssl_mode:\n    description:\n    - Determines whether or with what priority a secure SSL TCP/IP connection will be negotiated with the server.\n    - See https://www.postgresql.org/docs/current/static/libpq-ssl.html for more information on the modes.\n    - Default of C(prefer) matches libpq default.\n    type: str\n    default: prefer\n    choices: [ allow, disable, prefer, require, verify-ca, verify-full ]\n    version_added: \'2.3\'\n  ca_cert:\n    description:\n    - Specifies the name of a file containing SSL certificate authority (CA) certificate(s).\n    - If the file exists, the server\'s certificate will be verified to be signed by one of these authorities.\n    version_added: \'2.3\'\n    type: str\n    aliases:\n    - ssl_rootcert\n\nnotes:\n- Parameters that accept comma separated lists (I(privs), I(objs), I(roles))\n  have singular alias names (I(priv), I(obj), I(role)).\n- To revoke only C(GRANT OPTION) for a specific object, set I(state) to\n  C(present) and I(grant_option) to C(no) (see examples).\n- Note that when revoking privileges from a role R, this role  may still have\n  access via privileges granted to any role R is a member of including C(PUBLIC).\n- Note that when revoking privileges from a role R, you do so as the user\n  specified via I(login). If R has been granted the same privileges by\n  another user also, R can still access database objects via these privileges.\n- When revoking privileges, C(RESTRICT) is assumed (see PostgreSQL docs).\n\nseealso:\n- module: postgresql_user\n- module: postgresql_owner\n- module: postgresql_membership\n- name: PostgreSQL privileges\n  description: General information about PostgreSQL privileges.\n  link: https://www.postgresql.org/docs/current/ddl-priv.html\n- name: PostgreSQL GRANT command reference\n  description: Complete reference of the PostgreSQL GRANT command documentation.\n  link: https://www.postgresql.org/docs/current/sql-grant.html\n- name: PostgreSQL REVOKE command reference\n  description: Complete reference of the PostgreSQL REVOKE command documentation.\n  link: https://www.postgresql.org/docs/current/sql-revoke.html\n\nextends_documentation_fragment:\n- postgres\n\nauthor:\n- Bernhard Weitzhofer (@b6d)\n- Tobias Birkefeld (@tcraxs)\n'
EXAMPLES = '\n# On database "library":\n# GRANT SELECT, INSERT, UPDATE ON TABLE public.books, public.authors\n# TO librarian, reader WITH GRANT OPTION\n- name: Grant privs to librarian and reader on database library\n  postgresql_privs:\n    database: library\n    state: present\n    privs: SELECT,INSERT,UPDATE\n    type: table\n    objs: books,authors\n    schema: public\n    roles: librarian,reader\n    grant_option: yes\n\n- name: Same as above leveraging default values\n  postgresql_privs:\n    db: library\n    privs: SELECT,INSERT,UPDATE\n    objs: books,authors\n    roles: librarian,reader\n    grant_option: yes\n\n# REVOKE GRANT OPTION FOR INSERT ON TABLE books FROM reader\n# Note that role "reader" will be *granted* INSERT privilege itself if this\n# isn\'t already the case (since state: present).\n- name: Revoke privs from reader\n  postgresql_privs:\n    db: library\n    state: present\n    priv: INSERT\n    obj: books\n    role: reader\n    grant_option: no\n\n# "public" is the default schema. This also works for PostgreSQL 8.x.\n- name: REVOKE INSERT, UPDATE ON ALL TABLES IN SCHEMA public FROM reader\n  postgresql_privs:\n    db: library\n    state: absent\n    privs: INSERT,UPDATE\n    objs: ALL_IN_SCHEMA\n    role: reader\n\n- name: GRANT ALL PRIVILEGES ON SCHEMA public, math TO librarian\n  postgresql_privs:\n    db: library\n    privs: ALL\n    type: schema\n    objs: public,math\n    role: librarian\n\n# Note the separation of arguments with colons.\n- name: GRANT ALL PRIVILEGES ON FUNCTION math.add(int, int) TO librarian, reader\n  postgresql_privs:\n    db: library\n    privs: ALL\n    type: function\n    obj: add(int:int)\n    schema: math\n    roles: librarian,reader\n\n# Note that group role memberships apply cluster-wide and therefore are not\n# restricted to database "library" here.\n- name: GRANT librarian, reader TO alice, bob WITH ADMIN OPTION\n  postgresql_privs:\n    db: library\n    type: group\n    objs: librarian,reader\n    roles: alice,bob\n    admin_option: yes\n\n# Note that here "db: postgres" specifies the database to connect to, not the\n# database to grant privileges on (which is specified via the "objs" param)\n- name: GRANT ALL PRIVILEGES ON DATABASE library TO librarian\n  postgresql_privs:\n    db: postgres\n    privs: ALL\n    type: database\n    obj: library\n    role: librarian\n\n# If objs is omitted for type "database", it defaults to the database\n# to which the connection is established\n- name: GRANT ALL PRIVILEGES ON DATABASE library TO librarian\n  postgresql_privs:\n    db: library\n    privs: ALL\n    type: database\n    role: librarian\n\n# Available since version 2.7\n# Objs must be set, ALL_DEFAULT to TABLES/SEQUENCES/TYPES/FUNCTIONS\n# ALL_DEFAULT works only with privs=ALL\n# For specific\n- name: ALTER DEFAULT PRIVILEGES ON DATABASE library TO librarian\n  postgresql_privs:\n    db: library\n    objs: ALL_DEFAULT\n    privs: ALL\n    type: default_privs\n    role: librarian\n    grant_option: yes\n\n# Available since version 2.7\n# Objs must be set, ALL_DEFAULT to TABLES/SEQUENCES/TYPES/FUNCTIONS\n# ALL_DEFAULT works only with privs=ALL\n# For specific\n- name: ALTER DEFAULT PRIVILEGES ON DATABASE library TO reader, step 1\n  postgresql_privs:\n    db: library\n    objs: TABLES,SEQUENCES\n    privs: SELECT\n    type: default_privs\n    role: reader\n\n- name: ALTER DEFAULT PRIVILEGES ON DATABASE library TO reader, step 2\n  postgresql_privs:\n    db: library\n    objs: TYPES\n    privs: USAGE\n    type: default_privs\n    role: reader\n\n# Available since version 2.8\n- name: GRANT ALL PRIVILEGES ON FOREIGN DATA WRAPPER fdw TO reader\n  postgresql_privs:\n    db: test\n    objs: fdw\n    privs: ALL\n    type: foreign_data_wrapper\n    role: reader\n\n# Available since version 2.10\n- name: GRANT ALL PRIVILEGES ON TYPE customtype TO reader\n  postgresql_privs:\n    db: test\n    objs: customtype\n    privs: ALL\n    type: type\n    role: reader\n\n# Available since version 2.8\n- name: GRANT ALL PRIVILEGES ON FOREIGN SERVER fdw_server TO reader\n  postgresql_privs:\n    db: test\n    objs: fdw_server\n    privs: ALL\n    type: foreign_server\n    role: reader\n\n# Available since version 2.8\n# Grant \'execute\' permissions on all functions in schema \'common\' to role \'caller\'\n- name: GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA common TO caller\n  postgresql_privs:\n    type: function\n    state: present\n    privs: EXECUTE\n    roles: caller\n    objs: ALL_IN_SCHEMA\n    schema: common\n\n# Available since version 2.8\n# ALTER DEFAULT PRIVILEGES FOR ROLE librarian IN SCHEMA library GRANT SELECT ON TABLES TO reader\n# GRANT SELECT privileges for new TABLES objects created by librarian as\n# default to the role reader.\n# For specific\n- name: ALTER privs\n  postgresql_privs:\n    db: library\n    schema: library\n    objs: TABLES\n    privs: SELECT\n    type: default_privs\n    role: reader\n    target_roles: librarian\n\n# Available since version 2.8\n# ALTER DEFAULT PRIVILEGES FOR ROLE librarian IN SCHEMA library REVOKE SELECT ON TABLES FROM reader\n# REVOKE SELECT privileges for new TABLES objects created by librarian as\n# default from the role reader.\n# For specific\n- name: ALTER privs\n  postgresql_privs:\n    db: library\n    state: absent\n    schema: library\n    objs: TABLES\n    privs: SELECT\n    type: default_privs\n    role: reader\n    target_roles: librarian\n\n# Available since version 2.10\n- name: Grant type privileges for pg_catalog.numeric type to alice\n  postgresql_privs:\n    type: type\n    roles: alice\n    privs: ALL\n    objs: numeric\n    schema: pg_catalog\n    db: acme\n'
RETURN = '\nqueries:\n  description: List of executed queries.\n  returned: always\n  type: list\n  sample: [\'REVOKE GRANT OPTION FOR INSERT ON TABLE "books" FROM "reader";\']\n  version_added: \'2.8\'\n'
import traceback
PSYCOPG2_IMP_ERR = None
try:
    import psycopg2
    import psycopg2.extensions
except ImportError:
    PSYCOPG2_IMP_ERR = traceback.format_exc()
    psycopg2 = None
from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils.database import pg_quote_identifier
from ansible.module_utils.postgres import postgres_common_argument_spec
from ansible.module_utils._text import to_native
VALID_PRIVS = frozenset(('SELECT', 'INSERT', 'UPDATE', 'DELETE', 'TRUNCATE', 'REFERENCES', 'TRIGGER', 'CREATE', 'CONNECT', 'TEMPORARY', 'TEMP', 'EXECUTE', 'USAGE', 'ALL', 'USAGE'))
VALID_DEFAULT_OBJS = {'TABLES': ('ALL', 'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'TRUNCATE', 'REFERENCES', 'TRIGGER'), 'SEQUENCES': ('ALL', 'SELECT', 'UPDATE', 'USAGE'), 'FUNCTIONS': ('ALL', 'EXECUTE'), 'TYPES': ('ALL', 'USAGE')}
executed_queries = []

class Error(Exception):
    pass

def role_exists(module, cursor, rolname):
    """Check user exists or not"""
    query = "SELECT 1 FROM pg_roles WHERE rolname = '%s'" % rolname
    try:
        cursor.execute(query)
        return cursor.rowcount > 0
    except Exception as e:
        module.fail_json(msg="Cannot execute SQL '%s': %s" % (query, to_native(e)))
    return False

def partial(f, *args, **kwargs):
    """Partial function application"""

    def g(*g_args, **g_kwargs):
        new_kwargs = kwargs.copy()
        new_kwargs.update(g_kwargs)
        return f(*args + g_args, **g_kwargs)
    g.f = f
    g.args = args
    g.kwargs = kwargs
    return g

class Connection(object):
    """Wrapper around a psycopg2 connection with some convenience methods"""

    def __init__(self, params, module):
        self.database = params.database
        self.module = module
        params_map = {'host': 'host', 'login': 'user', 'password': 'password', 'port': 'port', 'database': 'database', 'ssl_mode': 'sslmode', 'ca_cert': 'sslrootcert'}
        kw = dict(((params_map[k], getattr(params, k)) for k in params_map if getattr(params, k) != '' and getattr(params, k) is not None))
        is_localhost = 'host' not in kw or kw['host'] == '' or kw['host'] == 'localhost'
        if is_localhost and params.unix_socket != '':
            kw['host'] = params.unix_socket
        sslrootcert = params.ca_cert
        if psycopg2.__version__ < '2.4.3' and sslrootcert is not None:
            raise ValueError('psycopg2 must be at least 2.4.3 in order to user the ca_cert parameter')
        self.connection = psycopg2.connect(**kw)
        self.cursor = self.connection.cursor()

    def commit(self):
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()

    @property
    def encoding(self):
        """Connection encoding in Python-compatible form"""
        return psycopg2.extensions.encodings[self.connection.encoding]

    def schema_exists(self, schema):
        query = 'SELECT count(*)\n                   FROM pg_catalog.pg_namespace WHERE nspname = %s'
        self.cursor.execute(query, (schema,))
        return self.cursor.fetchone()[0] > 0

    def get_all_tables_in_schema(self, schema):
        if not self.schema_exists(schema):
            raise Error('Schema "%s" does not exist.' % schema)
        query = "SELECT relname\n                   FROM pg_catalog.pg_class c\n                   JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace\n                   WHERE nspname = %s AND relkind in ('r', 'v', 'm', 'p')"
        self.cursor.execute(query, (schema,))
        return [t[0] for t in self.cursor.fetchall()]

    def get_all_sequences_in_schema(self, schema):
        if not self.schema_exists(schema):
            raise Error('Schema "%s" does not exist.' % schema)
        query = "SELECT relname\n                   FROM pg_catalog.pg_class c\n                   JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace\n                   WHERE nspname = %s AND relkind = 'S'"
        self.cursor.execute(query, (schema,))
        return [t[0] for t in self.cursor.fetchall()]

    def get_all_functions_in_schema(self, schema):
        if not self.schema_exists(schema):
            raise Error('Schema "%s" does not exist.' % schema)
        query = 'SELECT p.proname, oidvectortypes(p.proargtypes)\n                    FROM pg_catalog.pg_proc p\n                    JOIN pg_namespace n ON n.oid = p.pronamespace\n                    WHERE nspname = %s'
        self.cursor.execute(query, (schema,))
        return ['%s(%s)' % (t[0], t[1]) for t in self.cursor.fetchall()]

    def get_table_acls(self, schema, tables):
        query = "SELECT relacl\n                   FROM pg_catalog.pg_class c\n                   JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace\n                   WHERE nspname = %s AND relkind in ('r','p','v','m') AND relname = ANY (%s)\n                   ORDER BY relname"
        self.cursor.execute(query, (schema, tables))
        return [t[0] for t in self.cursor.fetchall()]

    def get_sequence_acls(self, schema, sequences):
        query = "SELECT relacl\n                   FROM pg_catalog.pg_class c\n                   JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace\n                   WHERE nspname = %s AND relkind = 'S' AND relname = ANY (%s)\n                   ORDER BY relname"
        self.cursor.execute(query, (schema, sequences))
        return [t[0] for t in self.cursor.fetchall()]

    def get_function_acls(self, schema, function_signatures):
        funcnames = [f.split('(', 1)[0] for f in function_signatures]
        query = 'SELECT proacl\n                   FROM pg_catalog.pg_proc p\n                   JOIN pg_catalog.pg_namespace n ON n.oid = p.pronamespace\n                   WHERE nspname = %s AND proname = ANY (%s)\n                   ORDER BY proname, proargtypes'
        self.cursor.execute(query, (schema, funcnames))
        return [t[0] for t in self.cursor.fetchall()]

    def get_schema_acls(self, schemas):
        query = 'SELECT nspacl FROM pg_catalog.pg_namespace\n                   WHERE nspname = ANY (%s) ORDER BY nspname'
        self.cursor.execute(query, (schemas,))
        return [t[0] for t in self.cursor.fetchall()]

    def get_language_acls(self, languages):
        query = 'SELECT lanacl FROM pg_catalog.pg_language\n                   WHERE lanname = ANY (%s) ORDER BY lanname'
        self.cursor.execute(query, (languages,))
        return [t[0] for t in self.cursor.fetchall()]

    def get_tablespace_acls(self, tablespaces):
        query = 'SELECT spcacl FROM pg_catalog.pg_tablespace\n                   WHERE spcname = ANY (%s) ORDER BY spcname'
        self.cursor.execute(query, (tablespaces,))
        return [t[0] for t in self.cursor.fetchall()]

    def get_database_acls(self, databases):
        query = 'SELECT datacl FROM pg_catalog.pg_database\n                   WHERE datname = ANY (%s) ORDER BY datname'
        self.cursor.execute(query, (databases,))
        return [t[0] for t in self.cursor.fetchall()]

    def get_group_memberships(self, groups):
        query = 'SELECT roleid, grantor, member, admin_option\n                   FROM pg_catalog.pg_auth_members am\n                   JOIN pg_catalog.pg_roles r ON r.oid = am.roleid\n                   WHERE r.rolname = ANY(%s)\n                   ORDER BY roleid, grantor, member'
        self.cursor.execute(query, (groups,))
        return self.cursor.fetchall()

    def get_default_privs(self, schema, *args):
        query = 'SELECT defaclacl\n                   FROM pg_default_acl a\n                   JOIN pg_namespace b ON a.defaclnamespace=b.oid\n                   WHERE b.nspname = %s;'
        self.cursor.execute(query, (schema,))
        return [t[0] for t in self.cursor.fetchall()]

    def get_foreign_data_wrapper_acls(self, fdws):
        query = 'SELECT fdwacl FROM pg_catalog.pg_foreign_data_wrapper\n                   WHERE fdwname = ANY (%s) ORDER BY fdwname'
        self.cursor.execute(query, (fdws,))
        return [t[0] for t in self.cursor.fetchall()]

    def get_foreign_server_acls(self, fs):
        query = 'SELECT srvacl FROM pg_catalog.pg_foreign_server\n                   WHERE srvname = ANY (%s) ORDER BY srvname'
        self.cursor.execute(query, (fs,))
        return [t[0] for t in self.cursor.fetchall()]

    def get_type_acls(self, schema, types):
        query = 'SELECT t.typacl FROM pg_catalog.pg_type t\n                   JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace\n                   WHERE n.nspname = %s AND t.typname = ANY (%s) ORDER BY typname'
        self.cursor.execute(query, (schema, types))
        return [t[0] for t in self.cursor.fetchall()]

    def manipulate_privs(self, obj_type, privs, objs, roles, target_roles, state, grant_option, schema_qualifier=None, fail_on_role=True):
        """Manipulate database object privileges.

        :param obj_type: Type of database object to grant/revoke
                         privileges for.
        :param privs: Either a list of privileges to grant/revoke
                      or None if type is "group".
        :param objs: List of database objects to grant/revoke
                     privileges for.
        :param roles: Either a list of role names or "PUBLIC"
                      for the implicitly defined "PUBLIC" group
        :param target_roles: List of role names to grant/revoke
                             default privileges as.
        :param state: "present" to grant privileges, "absent" to revoke.
        :param grant_option: Only for state "present": If True, set
                             grant/admin option. If False, revoke it.
                             If None, don't change grant option.
        :param schema_qualifier: Some object types ("TABLE", "SEQUENCE",
                                 "FUNCTION") must be qualified by schema.
                                 Ignored for other Types.
        """
        if obj_type == 'table':
            get_status = partial(self.get_table_acls, schema_qualifier)
        elif obj_type == 'sequence':
            get_status = partial(self.get_sequence_acls, schema_qualifier)
        elif obj_type == 'function':
            get_status = partial(self.get_function_acls, schema_qualifier)
        elif obj_type == 'schema':
            get_status = self.get_schema_acls
        elif obj_type == 'language':
            get_status = self.get_language_acls
        elif obj_type == 'tablespace':
            get_status = self.get_tablespace_acls
        elif obj_type == 'database':
            get_status = self.get_database_acls
        elif obj_type == 'group':
            get_status = self.get_group_memberships
        elif obj_type == 'default_privs':
            get_status = partial(self.get_default_privs, schema_qualifier)
        elif obj_type == 'foreign_data_wrapper':
            get_status = self.get_foreign_data_wrapper_acls
        elif obj_type == 'foreign_server':
            get_status = self.get_foreign_server_acls
        elif obj_type == 'type':
            get_status = partial(self.get_type_acls, schema_qualifier)
        else:
            raise Error('Unsupported database object type "%s".' % obj_type)
        if not objs:
            return False
        if obj_type == 'function':
            obj_ids = []
            for obj in objs:
                try:
                    (f, args) = obj.split('(', 1)
                except Exception:
                    raise Error('Illegal function signature: "%s".' % obj)
                obj_ids.append('"%s"."%s"(%s' % (schema_qualifier, f, args))
        elif obj_type in ['table', 'sequence', 'type']:
            obj_ids = ['"%s"."%s"' % (schema_qualifier, o) for o in objs]
        else:
            obj_ids = ['"%s"' % o for o in objs]
        if obj_type == 'group':
            set_what = ','.join(('"%s"' % i for i in obj_ids))
        elif obj_type == 'default_privs':
            set_what = ','.join(privs)
        else:
            if obj_type != 'function':
                obj_ids = [pg_quote_identifier(i, 'table') for i in obj_ids]
            set_what = '%s ON %s %s' % (','.join(privs), obj_type.replace('_', ' '), ','.join(obj_ids))
        if roles == 'PUBLIC':
            for_whom = 'PUBLIC'
        else:
            for_whom = []
            for r in roles:
                if not role_exists(self.module, self.cursor, r):
                    if fail_on_role:
                        self.module.fail_json(msg="Role '%s' does not exist" % r.strip())
                    else:
                        self.module.warn("Role '%s' does not exist, pass it" % r.strip())
                else:
                    for_whom.append('"%s"' % r)
            if not for_whom:
                return False
            for_whom = ','.join(for_whom)
        as_who = None
        if target_roles:
            as_who = ','.join(('"%s"' % r for r in target_roles))
        status_before = get_status(objs)
        query = QueryBuilder(state).for_objtype(obj_type).with_grant_option(grant_option).for_whom(for_whom).as_who(as_who).for_schema(schema_qualifier).set_what(set_what).for_objs(objs).build()
        executed_queries.append(query)
        self.cursor.execute(query)
        status_after = get_status(objs)

        def nonesorted(e):
            if e is None:
                return ''
            return e
        status_before.sort(key=nonesorted)
        status_after.sort(key=nonesorted)
        return status_before != status_after

class QueryBuilder(object):

    def __init__(self, state):
        self._grant_option = None
        self._for_whom = None
        self._as_who = None
        self._set_what = None
        self._obj_type = None
        self._state = state
        self._schema = None
        self._objs = None
        self.query = []

    def for_objs(self, objs):
        self._objs = objs
        return self

    def for_schema(self, schema):
        self._schema = schema
        return self

    def with_grant_option(self, option):
        self._grant_option = option
        return self

    def for_whom(self, who):
        self._for_whom = who
        return self

    def as_who(self, target_roles):
        self._as_who = target_roles
        return self

    def set_what(self, what):
        self._set_what = what
        return self

    def for_objtype(self, objtype):
        self._obj_type = objtype
        return self

    def build(self):
        if self._state == 'present':
            self.build_present()
        elif self._state == 'absent':
            self.build_absent()
        else:
            self.build_absent()
        return '\n'.join(self.query)

    def add_default_revoke(self):
        for obj in self._objs:
            if self._as_who:
                self.query.append('ALTER DEFAULT PRIVILEGES FOR ROLE {0} IN SCHEMA {1} REVOKE ALL ON {2} FROM {3};'.format(self._as_who, self._schema, obj, self._for_whom))
            else:
                self.query.append('ALTER DEFAULT PRIVILEGES IN SCHEMA {0} REVOKE ALL ON {1} FROM {2};'.format(self._schema, obj, self._for_whom))

    def add_grant_option(self):
        if self._grant_option:
            if self._obj_type == 'group':
                self.query[-1] += ' WITH ADMIN OPTION;'
            else:
                self.query[-1] += ' WITH GRANT OPTION;'
        else:
            self.query[-1] += ';'
            if self._obj_type == 'group':
                self.query.append('REVOKE ADMIN OPTION FOR {0} FROM {1};'.format(self._set_what, self._for_whom))
            elif not self._obj_type == 'default_privs':
                self.query.append('REVOKE GRANT OPTION FOR {0} FROM {1};'.format(self._set_what, self._for_whom))

    def add_default_priv(self):
        for obj in self._objs:
            if self._as_who:
                self.query.append('ALTER DEFAULT PRIVILEGES FOR ROLE {0} IN SCHEMA {1} GRANT {2} ON {3} TO {4}'.format(self._as_who, self._schema, self._set_what, obj, self._for_whom))
            else:
                self.query.append('ALTER DEFAULT PRIVILEGES IN SCHEMA {0} GRANT {1} ON {2} TO {3}'.format(self._schema, self._set_what, obj, self._for_whom))
            self.add_grant_option()
        if self._as_who:
            self.query.append('ALTER DEFAULT PRIVILEGES FOR ROLE {0} IN SCHEMA {1} GRANT USAGE ON TYPES TO {2}'.format(self._as_who, self._schema, self._for_whom))
        else:
            self.query.append('ALTER DEFAULT PRIVILEGES IN SCHEMA {0} GRANT USAGE ON TYPES TO {1}'.format(self._schema, self._for_whom))
        self.add_grant_option()

    def build_present(self):
        if self._obj_type == 'default_privs':
            self.add_default_revoke()
            self.add_default_priv()
        else:
            self.query.append('GRANT {0} TO {1}'.format(self._set_what, self._for_whom))
            self.add_grant_option()

    def build_absent(self):
        if self._obj_type == 'default_privs':
            self.query = []
            for obj in ['TABLES', 'SEQUENCES', 'TYPES']:
                if self._as_who:
                    self.query.append('ALTER DEFAULT PRIVILEGES FOR ROLE {0} IN SCHEMA {1} REVOKE ALL ON {2} FROM {3};'.format(self._as_who, self._schema, obj, self._for_whom))
                else:
                    self.query.append('ALTER DEFAULT PRIVILEGES IN SCHEMA {0} REVOKE ALL ON {1} FROM {2};'.format(self._schema, obj, self._for_whom))
        else:
            self.query.append('REVOKE {0} FROM {1};'.format(self._set_what, self._for_whom))

def main():
    argument_spec = postgres_common_argument_spec()
    argument_spec.update(database=dict(required=True, aliases=['db', 'login_db']), state=dict(default='present', choices=['present', 'absent']), privs=dict(required=False, aliases=['priv']), type=dict(default='table', choices=['table', 'sequence', 'function', 'database', 'schema', 'language', 'tablespace', 'group', 'default_privs', 'foreign_data_wrapper', 'foreign_server', 'type']), objs=dict(required=False, aliases=['obj']), schema=dict(required=False), roles=dict(required=True, aliases=['role']), session_role=dict(required=False), target_roles=dict(required=False), grant_option=dict(required=False, type='bool', aliases=['admin_option']), host=dict(default='', aliases=['login_host']), unix_socket=dict(default='', aliases=['login_unix_socket']), login=dict(default='postgres', aliases=['login_user']), password=dict(default='', aliases=['login_password'], no_log=True), fail_on_role=dict(type='bool', default=True))
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    fail_on_role = module.params['fail_on_role']
    p = type('Params', (), module.params)
    if p.type in ['table', 'sequence', 'function', 'type', 'default_privs']:
        p.schema = p.schema or 'public'
    elif p.schema:
        module.fail_json(msg='Argument "schema" is not allowed for type "%s".' % p.type)
    if p.type == 'database':
        p.objs = p.objs or p.database
    elif not p.objs:
        module.fail_json(msg='Argument "objs" is required for type "%s".' % p.type)
    if p.type == 'group':
        if p.privs:
            module.fail_json(msg='Argument "privs" is not allowed for type "group".')
    elif not p.privs:
        module.fail_json(msg='Argument "privs" is required for type "%s".' % p.type)
    if not psycopg2:
        module.fail_json(msg=missing_required_lib('psycopg2'), exception=PSYCOPG2_IMP_ERR)
    try:
        conn = Connection(p, module)
    except psycopg2.Error as e:
        module.fail_json(msg='Could not connect to database: %s' % to_native(e), exception=traceback.format_exc())
    except TypeError as e:
        if 'sslrootcert' in e.args[0]:
            module.fail_json(msg='Postgresql server must be at least version 8.4 to support sslrootcert')
        module.fail_json(msg='unable to connect to database: %s' % to_native(e), exception=traceback.format_exc())
    except ValueError as e:
        module.fail_json(msg=to_native(e))
    if p.session_role:
        try:
            conn.cursor.execute('SET ROLE "%s"' % p.session_role)
        except Exception as e:
            module.fail_json(msg='Could not switch to role %s: %s' % (p.session_role, to_native(e)), exception=traceback.format_exc())
    try:
        if p.privs:
            privs = frozenset((pr.upper() for pr in p.privs.split(',')))
            if not privs.issubset(VALID_PRIVS):
                module.fail_json(msg='Invalid privileges specified: %s' % privs.difference(VALID_PRIVS))
        else:
            privs = None
        if p.type == 'table' and p.objs == 'ALL_IN_SCHEMA':
            objs = conn.get_all_tables_in_schema(p.schema)
        elif p.type == 'sequence' and p.objs == 'ALL_IN_SCHEMA':
            objs = conn.get_all_sequences_in_schema(p.schema)
        elif p.type == 'function' and p.objs == 'ALL_IN_SCHEMA':
            objs = conn.get_all_functions_in_schema(p.schema)
        elif p.type == 'default_privs':
            if p.objs == 'ALL_DEFAULT':
                objs = frozenset(VALID_DEFAULT_OBJS.keys())
            else:
                objs = frozenset((obj.upper() for obj in p.objs.split(',')))
                if not objs.issubset(VALID_DEFAULT_OBJS):
                    module.fail_json(msg='Invalid Object set specified: %s' % objs.difference(VALID_DEFAULT_OBJS.keys()))
            valid_objects_for_priv = frozenset((obj for obj in objs if privs.issubset(VALID_DEFAULT_OBJS[obj])))
            if not valid_objects_for_priv == objs:
                module.fail_json(msg='Invalid priv specified. Valid object for priv: {0}. Objects: {1}'.format(valid_objects_for_priv, objs))
        else:
            objs = p.objs.split(',')
            if p.type == 'function':
                objs = [obj.replace(':', ',') for obj in objs]
        if p.roles == 'PUBLIC':
            roles = 'PUBLIC'
        else:
            roles = p.roles.split(',')
            if len(roles) == 1 and (not role_exists(module, conn.cursor, roles[0])):
                module.exit_json(changed=False)
                if fail_on_role:
                    module.fail_json(msg="Role '%s' does not exist" % roles[0].strip())
                else:
                    module.warn("Role '%s' does not exist, nothing to do" % roles[0].strip())
        if p.target_roles and (not p.type == 'default_privs'):
            module.warn('"target_roles" will be ignored Argument "type: default_privs" is required for usage of "target_roles".')
        if p.target_roles:
            target_roles = p.target_roles.split(',')
        else:
            target_roles = None
        changed = conn.manipulate_privs(obj_type=p.type, privs=privs, objs=objs, roles=roles, target_roles=target_roles, state=p.state, grant_option=p.grant_option, schema_qualifier=p.schema, fail_on_role=fail_on_role)
    except Error as e:
        conn.rollback()
        module.fail_json(msg=e.message, exception=traceback.format_exc())
    except psycopg2.Error as e:
        conn.rollback()
        module.fail_json(msg=to_native(e.message))
    if module.check_mode:
        conn.rollback()
    else:
        conn.commit()
    module.exit_json(changed=changed, queries=executed_queries)
if __name__ == '__main__':
    main()

def test_Connection_commit():
    ret = Connection().commit()

def test_Connection_rollback():
    ret = Connection().rollback()

def test_Connection_encoding():
    ret = Connection().encoding()

def test_Connection_schema_exists():
    ret = Connection().schema_exists()

def test_Connection_get_all_tables_in_schema():
    ret = Connection().get_all_tables_in_schema()

def test_Connection_get_all_sequences_in_schema():
    ret = Connection().get_all_sequences_in_schema()

def test_Connection_get_all_functions_in_schema():
    ret = Connection().get_all_functions_in_schema()

def test_Connection_get_table_acls():
    ret = Connection().get_table_acls()

def test_Connection_get_sequence_acls():
    ret = Connection().get_sequence_acls()

def test_Connection_get_function_acls():
    ret = Connection().get_function_acls()

def test_Connection_get_schema_acls():
    ret = Connection().get_schema_acls()

def test_Connection_get_language_acls():
    ret = Connection().get_language_acls()

def test_Connection_get_tablespace_acls():
    ret = Connection().get_tablespace_acls()

def test_Connection_get_database_acls():
    ret = Connection().get_database_acls()

def test_Connection_get_group_memberships():
    ret = Connection().get_group_memberships()

def test_Connection_get_default_privs():
    ret = Connection().get_default_privs()

def test_Connection_get_foreign_data_wrapper_acls():
    ret = Connection().get_foreign_data_wrapper_acls()

def test_Connection_get_foreign_server_acls():
    ret = Connection().get_foreign_server_acls()

def test_Connection_get_type_acls():
    ret = Connection().get_type_acls()

def test_Connection_nonesorted():
    ret = Connection().nonesorted()

def test_Connection_manipulate_privs():
    ret = Connection().manipulate_privs()

def test_QueryBuilder_for_objs():
    ret = QueryBuilder().for_objs()

def test_QueryBuilder_for_schema():
    ret = QueryBuilder().for_schema()

def test_QueryBuilder_with_grant_option():
    ret = QueryBuilder().with_grant_option()

def test_QueryBuilder_for_whom():
    ret = QueryBuilder().for_whom()

def test_QueryBuilder_as_who():
    ret = QueryBuilder().as_who()

def test_QueryBuilder_set_what():
    ret = QueryBuilder().set_what()

def test_QueryBuilder_for_objtype():
    ret = QueryBuilder().for_objtype()

def test_QueryBuilder_build():
    ret = QueryBuilder().build()

def test_QueryBuilder_add_default_revoke():
    ret = QueryBuilder().add_default_revoke()

def test_QueryBuilder_add_grant_option():
    ret = QueryBuilder().add_grant_option()

def test_QueryBuilder_add_default_priv():
    ret = QueryBuilder().add_default_priv()

def test_QueryBuilder_build_present():
    ret = QueryBuilder().build_present()

def test_QueryBuilder_build_absent():
    ret = QueryBuilder().build_absent()