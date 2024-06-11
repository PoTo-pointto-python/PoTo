from ansible.module_utils.connection import Connection

def get(module, path=None, content=None, fields=None, output='json'):
    if path is None:
        raise ValueError('path value must be provided')
    if content:
        path += '?' + 'content=%s' % content
    if fields:
        path += '?' + 'field=%s' % fields
    accept = None
    if output == 'xml':
        accept = 'application/yang-data+xml'
    connection = Connection(module._socket_path)
    return connection.send_request(None, path=path, method='GET', accept=accept)

def edit_config(module, path=None, content=None, method='GET', format='json'):
    if path is None:
        raise ValueError('path value must be provided')
    content_type = None
    if format == 'xml':
        content_type = 'application/yang-data+xml'
    connection = Connection(module._socket_path)
    return connection.send_request(content, path=path, method=method, content_type=content_type)