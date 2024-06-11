from __future__ import absolute_import, division, print_function
__metaclass__ = type
DOCUMENTATION = '\n    name: docker_swarm\n    plugin_type: inventory\n    version_added: \'2.8\'\n    author:\n      - Stefan Heitmüller (@morph027) <stefan.heitmueller@gmx.com>\n    short_description: Ansible dynamic inventory plugin for Docker swarm nodes.\n    requirements:\n        - python >= 2.7\n        - L(Docker SDK for Python,https://docker-py.readthedocs.io/en/stable/) >= 1.10.0\n    extends_documentation_fragment:\n        - constructed\n    description:\n        - Reads inventories from the Docker swarm API.\n        - Uses a YAML configuration file docker_swarm.[yml|yaml].\n        - "The plugin returns following groups of swarm nodes:  I(all) - all hosts; I(workers) - all worker nodes;\n          I(managers) - all manager nodes; I(leader) - the swarm leader node;\n          I(nonleaders) - all nodes except the swarm leader."\n    options:\n        plugin:\n            description: The name of this plugin, it should always be set to C(docker_swarm) for this plugin to\n                         recognize it as it\'s own.\n            type: str\n            required: true\n            choices: docker_swarm\n        docker_host:\n            description:\n                - Socket of a Docker swarm manager node (C(tcp), C(unix)).\n                - "Use C(unix://var/run/docker.sock) to connect via local socket."\n            type: str\n            required: true\n            aliases: [ docker_url ]\n        verbose_output:\n            description: Toggle to (not) include all available nodes metadata (e.g. C(Platform), C(Architecture), C(OS),\n                         C(EngineVersion))\n            type: bool\n            default: yes\n        tls:\n            description: Connect using TLS without verifying the authenticity of the Docker host server.\n            type: bool\n            default: no\n        validate_certs:\n            description: Toggle if connecting using TLS with or without verifying the authenticity of the Docker\n                         host server.\n            type: bool\n            default: no\n            aliases: [ tls_verify ]\n        client_key:\n            description: Path to the client\'s TLS key file.\n            type: path\n            aliases: [ tls_client_key, key_path ]\n        ca_cert:\n            description: Use a CA certificate when performing server verification by providing the path to a CA\n                         certificate file.\n            type: path\n            aliases: [ tls_ca_cert, cacert_path ]\n        client_cert:\n            description: Path to the client\'s TLS certificate file.\n            type: path\n            aliases: [ tls_client_cert, cert_path ]\n        tls_hostname:\n            description: When verifying the authenticity of the Docker host server, provide the expected name of\n                         the server.\n            type: str\n        ssl_version:\n            description: Provide a valid SSL version number. Default value determined by ssl.py module.\n            type: str\n        api_version:\n            description:\n                - The version of the Docker API running on the Docker Host.\n                - Defaults to the latest version of the API supported by docker-py.\n            type: str\n            aliases: [ docker_api_version ]\n        timeout:\n            description:\n                - The maximum amount of time in seconds to wait on a response from the API.\n                - If the value is not specified in the task, the value of environment variable C(DOCKER_TIMEOUT)\n                  will be used instead. If the environment variable is not set, the default value will be used.\n            type: int\n            default: 60\n            aliases: [ time_out ]\n        include_host_uri:\n            description: Toggle to return the additional attribute C(ansible_host_uri) which contains the URI of the\n                         swarm leader in format of C(tcp://172.16.0.1:2376). This value may be used without additional\n                         modification as value of option I(docker_host) in Docker Swarm modules when connecting via API.\n                         The port always defaults to C(2376).\n            type: bool\n            default: no\n        include_host_uri_port:\n            description: Override the detected port number included in I(ansible_host_uri)\n            type: int\n'
EXAMPLES = '\n# Minimal example using local docker\nplugin: docker_swarm\ndocker_host: unix://var/run/docker.sock\n\n# Minimal example using remote docker\nplugin: docker_swarm\ndocker_host: tcp://my-docker-host:2375\n\n# Example using remote docker with unverified TLS\nplugin: docker_swarm\ndocker_host: tcp://my-docker-host:2376\ntls: yes\n\n# Example using remote docker with verified TLS and client certificate verification\nplugin: docker_swarm\ndocker_host: tcp://my-docker-host:2376\nvalidate_certs: yes\nca_cert: /somewhere/ca.pem\nclient_key: /somewhere/key.pem\nclient_cert: /somewhere/cert.pem\n\n# Example using constructed features to create groups and set ansible_host\nplugin: docker_swarm\ndocker_host: tcp://my-docker-host:2375\nstrict: False\nkeyed_groups:\n  # add e.g. x86_64 hosts to an arch_x86_64 group\n  - prefix: arch\n    key: \'Description.Platform.Architecture\'\n  # add e.g. linux hosts to an os_linux group\n  - prefix: os\n    key: \'Description.Platform.OS\'\n  # create a group per node label\n  # e.g. a node labeled w/ "production" ends up in group "label_production"\n  # hint: labels containing special characters will be converted to safe names\n  - key: \'Spec.Labels\'\n    prefix: label\n'
from ansible.errors import AnsibleError
from ansible.module_utils._text import to_native
from ansible.module_utils.six.moves.urllib.parse import urlparse
from ansible.plugins.inventory import BaseInventoryPlugin, Constructable
from ansible.parsing.utils.addresses import parse_address
try:
    import docker
    from docker.errors import TLSParameterError
    from docker.tls import TLSConfig
    HAS_DOCKER = True
except ImportError:
    HAS_DOCKER = False

def update_tls_hostname(result):
    if result['tls_hostname'] is None:
        parsed_url = urlparse(result['docker_host'])
        if ':' in parsed_url.netloc:
            result['tls_hostname'] = parsed_url.netloc[:parsed_url.netloc.rindex(':')]
        else:
            result['tls_hostname'] = parsed_url

def _get_tls_config(fail_function, **kwargs):
    try:
        tls_config = TLSConfig(**kwargs)
        return tls_config
    except TLSParameterError as exc:
        fail_function('TLS config error: %s' % exc)

def get_connect_params(auth, fail_function):
    if auth['tls'] or auth['tls_verify']:
        auth['docker_host'] = auth['docker_host'].replace('tcp://', 'https://')
    if auth['tls_verify'] and auth['cert_path'] and auth['key_path']:
        if auth['cacert_path']:
            tls_config = _get_tls_config(client_cert=(auth['cert_path'], auth['key_path']), ca_cert=auth['cacert_path'], verify=True, assert_hostname=auth['tls_hostname'], ssl_version=auth['ssl_version'], fail_function=fail_function)
        else:
            tls_config = _get_tls_config(client_cert=(auth['cert_path'], auth['key_path']), verify=True, assert_hostname=auth['tls_hostname'], ssl_version=auth['ssl_version'], fail_function=fail_function)
        return dict(base_url=auth['docker_host'], tls=tls_config, version=auth['api_version'], timeout=auth['timeout'])
    if auth['tls_verify'] and auth['cacert_path']:
        tls_config = _get_tls_config(ca_cert=auth['cacert_path'], assert_hostname=auth['tls_hostname'], verify=True, ssl_version=auth['ssl_version'], fail_function=fail_function)
        return dict(base_url=auth['docker_host'], tls=tls_config, version=auth['api_version'], timeout=auth['timeout'])
    if auth['tls_verify']:
        tls_config = _get_tls_config(verify=True, assert_hostname=auth['tls_hostname'], ssl_version=auth['ssl_version'], fail_function=fail_function)
        return dict(base_url=auth['docker_host'], tls=tls_config, version=auth['api_version'], timeout=auth['timeout'])
    if auth['tls'] and auth['cert_path'] and auth['key_path']:
        tls_config = _get_tls_config(client_cert=(auth['cert_path'], auth['key_path']), verify=False, ssl_version=auth['ssl_version'], fail_function=fail_function)
        return dict(base_url=auth['docker_host'], tls=tls_config, version=auth['api_version'], timeout=auth['timeout'])
    if auth['tls']:
        tls_config = _get_tls_config(verify=False, ssl_version=auth['ssl_version'], fail_function=fail_function)
        return dict(base_url=auth['docker_host'], tls=tls_config, version=auth['api_version'], timeout=auth['timeout'])
    return dict(base_url=auth['docker_host'], version=auth['api_version'], timeout=auth['timeout'])

class InventoryModule(BaseInventoryPlugin, Constructable):
    """ Host inventory parser for ansible using Docker swarm as source. """
    NAME = 'docker_swarm'

    def _fail(self, msg):
        raise AnsibleError(msg)

    def _populate(self):
        raw_params = dict(docker_host=self.get_option('docker_host'), tls=self.get_option('tls'), tls_verify=self.get_option('validate_certs'), key_path=self.get_option('client_key'), cacert_path=self.get_option('ca_cert'), cert_path=self.get_option('client_cert'), tls_hostname=self.get_option('tls_hostname'), api_version=self.get_option('api_version'), timeout=self.get_option('timeout'), ssl_version=self.get_option('ssl_version'), debug=None)
        update_tls_hostname(raw_params)
        connect_params = get_connect_params(raw_params, fail_function=self._fail)
        self.client = docker.DockerClient(**connect_params)
        self.inventory.add_group('all')
        self.inventory.add_group('manager')
        self.inventory.add_group('worker')
        self.inventory.add_group('leader')
        self.inventory.add_group('nonleaders')
        if self.get_option('include_host_uri'):
            if self.get_option('include_host_uri_port'):
                host_uri_port = str(self.get_option('include_host_uri_port'))
            elif self.get_option('tls') or self.get_option('validate_certs'):
                host_uri_port = '2376'
            else:
                host_uri_port = '2375'
        try:
            self.nodes = self.client.nodes.list()
            for self.node in self.nodes:
                self.node_attrs = self.client.nodes.get(self.node.id).attrs
                self.inventory.add_host(self.node_attrs['ID'])
                self.inventory.add_host(self.node_attrs['ID'], group=self.node_attrs['Spec']['Role'])
                self.inventory.set_variable(self.node_attrs['ID'], 'ansible_host', self.node_attrs['Status']['Addr'])
                if self.get_option('include_host_uri'):
                    self.inventory.set_variable(self.node_attrs['ID'], 'ansible_host_uri', 'tcp://' + self.node_attrs['Status']['Addr'] + ':' + host_uri_port)
                if self.get_option('verbose_output'):
                    self.inventory.set_variable(self.node_attrs['ID'], 'docker_swarm_node_attributes', self.node_attrs)
                if 'ManagerStatus' in self.node_attrs:
                    if self.node_attrs['ManagerStatus'].get('Leader'):
                        swarm_leader_ip = parse_address(self.node_attrs['ManagerStatus']['Addr'])[0] or self.node_attrs['Status']['Addr']
                        if self.get_option('include_host_uri'):
                            self.inventory.set_variable(self.node_attrs['ID'], 'ansible_host_uri', 'tcp://' + swarm_leader_ip + ':' + host_uri_port)
                        self.inventory.set_variable(self.node_attrs['ID'], 'ansible_host', swarm_leader_ip)
                        self.inventory.add_host(self.node_attrs['ID'], group='leader')
                    else:
                        self.inventory.add_host(self.node_attrs['ID'], group='nonleaders')
                else:
                    self.inventory.add_host(self.node_attrs['ID'], group='nonleaders')
                strict = self.get_option('strict')
                self._set_composite_vars(self.get_option('compose'), self.node_attrs, self.node_attrs['ID'], strict=strict)
                self._add_host_to_composed_groups(self.get_option('groups'), self.node_attrs, self.node_attrs['ID'], strict=strict)
                self._add_host_to_keyed_groups(self.get_option('keyed_groups'), self.node_attrs, self.node_attrs['ID'], strict=strict)
        except Exception as e:
            raise AnsibleError('Unable to fetch hosts from Docker swarm API, this was the original exception: %s' % to_native(e))

    def verify_file(self, path):
        """Return the possibly of a file being consumable by this plugin."""
        return super(InventoryModule, self).verify_file(path) and path.endswith((self.NAME + '.yaml', self.NAME + '.yml'))

    def parse(self, inventory, loader, path, cache=True):
        if not HAS_DOCKER:
            raise AnsibleError('The Docker swarm dynamic inventory plugin requires the Docker SDK for Python: https://github.com/docker/docker-py.')
        super(InventoryModule, self).parse(inventory, loader, path, cache)
        self._read_config_data(path)
        self._populate()

def test_InventoryModule__fail():
    ret = InventoryModule()._fail()

def test_InventoryModule__populate():
    ret = InventoryModule()._populate()

def test_InventoryModule_verify_file():
    ret = InventoryModule().verify_file()

def test_InventoryModule_parse():
    ret = InventoryModule().parse()