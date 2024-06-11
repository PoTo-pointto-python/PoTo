from __future__ import absolute_import, division, print_function
__metaclass__ = type
ANSIBLE_METADATA = {'metadata_version': '1.1', 'supported_by': 'community', 'status': ['preview']}
DOCUMENTATION = "\n---\nmodule: postgresql_query\nshort_description: Run PostgreSQL queries\ndescription:\n- Runs arbitrary PostgreSQL queries.\n- Can run queries from SQL script files.\n- Does not run against backup files. Use M(postgresql_db) with I(state=restore)\n  to run queries on files made by pg_dump/pg_dumpall utilities.\nversion_added: '2.8'\noptions:\n  query:\n    description:\n    - SQL query to run. Variables can be escaped with psycopg2 syntax\n      U(http://initd.org/psycopg/docs/usage.html).\n    type: str\n  positional_args:\n    description:\n    - List of values to be passed as positional arguments to the query.\n      When the value is a list, it will be converted to PostgreSQL array.\n    - Mutually exclusive with I(named_args).\n    type: list\n    elements: raw\n  named_args:\n    description:\n    - Dictionary of key-value arguments to pass to the query.\n      When the value is a list, it will be converted to PostgreSQL array.\n    - Mutually exclusive with I(positional_args).\n    type: dict\n  path_to_script:\n    description:\n    - Path to SQL script on the remote host.\n    - Returns result of the last query in the script.\n    - Mutually exclusive with I(query).\n    type: path\n  session_role:\n    description:\n    - Switch to session_role after connecting. The specified session_role must\n      be a role that the current login_user is a member of.\n    - Permissions checking for SQL commands is carried out as though\n      the session_role were the one that had logged in originally.\n    type: str\n  db:\n    description:\n    - Name of database to connect to and run queries against.\n    type: str\n    aliases:\n    - login_db\n  autocommit:\n    description:\n    - Execute in autocommit mode when the query can't be run inside a transaction block\n      (e.g., VACUUM).\n    - Mutually exclusive with I(check_mode).\n    type: bool\n    default: no\n    version_added: '2.9'\n  encoding:\n    description:\n    - Set the client encoding for the current session (e.g. C(UTF-8)).\n    - The default is the encoding defined by the database.\n    type: str\n    version_added: '2.10'\nseealso:\n- module: postgresql_db\nauthor:\n- Felix Archambault (@archf)\n- Andrew Klychkov (@Andersson007)\n- Will Rouesnel (@wrouesnel)\nextends_documentation_fragment: postgres\n"
EXAMPLES = "\n- name: Simple select query to acme db\n  postgresql_query:\n    db: acme\n    query: SELECT version()\n\n- name: Select query to db acme with positional arguments and non-default credentials\n  postgresql_query:\n    db: acme\n    login_user: django\n    login_password: mysecretpass\n    query: SELECT * FROM acme WHERE id = %s AND story = %s\n    positional_args:\n    - 1\n    - test\n\n- name: Select query to test_db with named_args\n  postgresql_query:\n    db: test_db\n    query: SELECT * FROM test WHERE id = %(id_val)s AND story = %(story_val)s\n    named_args:\n      id_val: 1\n      story_val: test\n\n- name: Insert query to test_table in db test_db\n  postgresql_query:\n    db: test_db\n    query: INSERT INTO test_table (id, story) VALUES (2, 'my_long_story')\n\n- name: Run queries from SQL script using UTF-8 client encoding for session\n  postgresql_query:\n    db: test_db\n    path_to_script: /var/lib/pgsql/test.sql\n    positional_args:\n    - 1\n    encoding: UTF-8\n\n- name: Example of using autocommit parameter\n  postgresql_query:\n    db: test_db\n    query: VACUUM\n    autocommit: yes\n\n- name: >\n    Insert data to the column of array type using positional_args.\n    Note that we use quotes here, the same as for passing JSON, etc.\n  postgresql_query:\n    query: INSERT INTO test_table (array_column) VALUES (%s)\n    positional_args:\n    - '{1,2,3}'\n\n# Pass list and string vars as positional_args\n- name: Set vars\n  set_fact:\n    my_list:\n    - 1\n    - 2\n    - 3\n    my_arr: '{1, 2, 3}'\n\n- name: Select from test table by passing positional_args as arrays\n  postgresql_query:\n    query: SELECT * FROM test_array_table WHERE arr_col1 = %s AND arr_col2 = %s\n    positional_args:\n    - '{{ my_list }}'\n    - '{{ my_arr|string }}'\n"
RETURN = '\nquery:\n    description: Query that was tried to be executed.\n    returned: always\n    type: str\n    sample: \'SELECT * FROM bar\'\nstatusmessage:\n    description: Attribute containing the message returned by the command.\n    returned: always\n    type: str\n    sample: \'INSERT 0 1\'\nquery_result:\n    description:\n    - List of dictionaries in column:value form representing returned rows.\n    returned: changed\n    type: list\n    sample: [{"Column": "Value1"},{"Column": "Value2"}]\nrowcount:\n    description: Number of affected rows.\n    returned: changed\n    type: int\n    sample: 5\n'
try:
    from psycopg2 import ProgrammingError as Psycopg2ProgrammingError
    from psycopg2.extras import DictCursor
except ImportError:
    pass
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.postgres import connect_to_db, get_conn_params, postgres_common_argument_spec
from ansible.module_utils._text import to_native
from ansible.module_utils.six import iteritems

def list_to_pg_array(elem):
    """Convert the passed list to PostgreSQL array
    represented as a string.

    Args:
        elem (list): List that needs to be converted.

    Returns:
        elem (str): String representation of PostgreSQL array.
    """
    elem = str(elem).strip('[]')
    elem = '{' + elem + '}'
    return elem

def convert_elements_to_pg_arrays(obj):
    """Convert list elements of the passed object
    to PostgreSQL arrays represented as strings.

    Args:
        obj (dict or list): Object whose elements need to be converted.

    Returns:
        obj (dict or list): Object with converted elements.
    """
    if isinstance(obj, dict):
        for (key, elem) in iteritems(obj):
            if isinstance(elem, list):
                obj[key] = list_to_pg_array(elem)
    elif isinstance(obj, list):
        for (i, elem) in enumerate(obj):
            if isinstance(elem, list):
                obj[i] = list_to_pg_array(elem)
    return obj

def main():
    argument_spec = postgres_common_argument_spec()
    argument_spec.update(query=dict(type='str'), db=dict(type='str', aliases=['login_db']), positional_args=dict(type='list', elements='raw'), named_args=dict(type='dict'), session_role=dict(type='str'), path_to_script=dict(type='path'), autocommit=dict(type='bool', default=False), encoding=dict(type='str'))
    module = AnsibleModule(argument_spec=argument_spec, mutually_exclusive=(('positional_args', 'named_args'),), supports_check_mode=True)
    query = module.params['query']
    positional_args = module.params['positional_args']
    named_args = module.params['named_args']
    path_to_script = module.params['path_to_script']
    autocommit = module.params['autocommit']
    encoding = module.params['encoding']
    if autocommit and module.check_mode:
        module.fail_json(msg='Using autocommit is mutually exclusive with check_mode')
    if path_to_script and query:
        module.fail_json(msg='path_to_script is mutually exclusive with query')
    if positional_args:
        positional_args = convert_elements_to_pg_arrays(positional_args)
    elif named_args:
        named_args = convert_elements_to_pg_arrays(named_args)
    if path_to_script:
        try:
            with open(path_to_script, 'rb') as f:
                query = to_native(f.read())
        except Exception as e:
            module.fail_json(msg="Cannot read file '%s' : %s" % (path_to_script, to_native(e)))
    conn_params = get_conn_params(module, module.params)
    db_connection = connect_to_db(module, conn_params, autocommit=autocommit)
    if encoding is not None:
        db_connection.set_client_encoding(encoding)
    cursor = db_connection.cursor(cursor_factory=DictCursor)
    if module.params.get('positional_args'):
        arguments = module.params['positional_args']
    elif module.params.get('named_args'):
        arguments = module.params['named_args']
    else:
        arguments = None
    changed = False
    try:
        cursor.execute(query, arguments)
    except Exception as e:
        if not autocommit:
            db_connection.rollback()
        cursor.close()
        db_connection.close()
        module.fail_json(msg="Cannot execute SQL '%s' %s: %s" % (query, arguments, to_native(e)))
    statusmessage = cursor.statusmessage
    rowcount = cursor.rowcount
    try:
        query_result = [dict(row) for row in cursor.fetchall()]
    except Psycopg2ProgrammingError as e:
        if to_native(e) == 'no results to fetch':
            query_result = {}
    except Exception as e:
        module.fail_json(msg='Cannot fetch rows from cursor: %s' % to_native(e))
    if 'SELECT' not in statusmessage:
        if 'UPDATE' in statusmessage or 'INSERT' in statusmessage or 'DELETE' in statusmessage:
            s = statusmessage.split()
            if len(s) == 3:
                if statusmessage.split()[2] != '0':
                    changed = True
            elif len(s) == 2:
                if statusmessage.split()[1] != '0':
                    changed = True
            else:
                changed = True
        else:
            changed = True
    if module.check_mode:
        db_connection.rollback()
    elif not autocommit:
        db_connection.commit()
    kw = dict(changed=changed, query=cursor.query, statusmessage=statusmessage, query_result=query_result, rowcount=rowcount if rowcount >= 0 else 0)
    cursor.close()
    db_connection.close()
    module.exit_json(**kw)
if __name__ == '__main__':
    main()