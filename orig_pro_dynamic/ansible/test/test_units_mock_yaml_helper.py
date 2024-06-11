from __future__ import absolute_import, division, print_function
__metaclass__ = type
import io
import yaml
from ansible.module_utils.six import PY3
from ansible.parsing.yaml.loader import AnsibleLoader
from ansible.parsing.yaml.dumper import AnsibleDumper

class YamlTestUtils(object):
    """Mixin class to combine with a unittest.TestCase subclass."""

    def _loader(self, stream):
        """Vault related tests will want to override this.

        Vault cases should setup a AnsibleLoader that has the vault password."""
        return AnsibleLoader(stream)

    def _dump_stream(self, obj, stream, dumper=None):
        """Dump to a py2-unicode or py3-string stream."""
        if PY3:
            return yaml.dump(obj, stream, Dumper=dumper)
        else:
            return yaml.dump(obj, stream, Dumper=dumper, encoding=None)

    def _dump_string(self, obj, dumper=None):
        """Dump to a py2-unicode or py3-string"""
        if PY3:
            return yaml.dump(obj, Dumper=dumper)
        else:
            return yaml.dump(obj, Dumper=dumper, encoding=None)

    def _dump_load_cycle(self, obj):
        string_from_object_dump = self._dump_string(obj, dumper=AnsibleDumper)
        stream_from_object_dump = io.StringIO(string_from_object_dump)
        loader = self._loader(stream_from_object_dump)
        obj_2 = loader.get_data()
        string_from_object_dump_2 = self._dump_string(obj_2, dumper=AnsibleDumper)
        self.assertEqual(string_from_object_dump, string_from_object_dump_2)
        self.assertEqual(obj, obj_2)
        stream_3 = io.StringIO(string_from_object_dump_2)
        loader_3 = self._loader(stream_3)
        obj_3 = loader_3.get_data()
        string_from_object_dump_3 = self._dump_string(obj_3, dumper=AnsibleDumper)
        self.assertEqual(obj, obj_3)
        self.assertEqual(obj_2, obj_3)
        self.assertEqual(string_from_object_dump, string_from_object_dump_3)

    def _old_dump_load_cycle(self, obj):
        """Dump the passed in object to yaml, load it back up, dump again, compare."""
        stream = io.StringIO()
        yaml_string = self._dump_string(obj, dumper=AnsibleDumper)
        self._dump_stream(obj, stream, dumper=AnsibleDumper)
        yaml_string_from_stream = stream.getvalue()
        stream.seek(0)
        loader = self._loader(stream)
        obj_from_stream = loader.get_data()
        stream_from_string = io.StringIO(yaml_string)
        loader2 = self._loader(stream_from_string)
        obj_from_string = loader2.get_data()
        stream_obj_from_stream = io.StringIO()
        stream_obj_from_string = io.StringIO()
        if PY3:
            yaml.dump(obj_from_stream, stream_obj_from_stream, Dumper=AnsibleDumper)
            yaml.dump(obj_from_stream, stream_obj_from_string, Dumper=AnsibleDumper)
        else:
            yaml.dump(obj_from_stream, stream_obj_from_stream, Dumper=AnsibleDumper, encoding=None)
            yaml.dump(obj_from_stream, stream_obj_from_string, Dumper=AnsibleDumper, encoding=None)
        yaml_string_stream_obj_from_stream = stream_obj_from_stream.getvalue()
        yaml_string_stream_obj_from_string = stream_obj_from_string.getvalue()
        stream_obj_from_stream.seek(0)
        stream_obj_from_string.seek(0)
        if PY3:
            yaml_string_obj_from_stream = yaml.dump(obj_from_stream, Dumper=AnsibleDumper)
            yaml_string_obj_from_string = yaml.dump(obj_from_string, Dumper=AnsibleDumper)
        else:
            yaml_string_obj_from_stream = yaml.dump(obj_from_stream, Dumper=AnsibleDumper, encoding=None)
            yaml_string_obj_from_string = yaml.dump(obj_from_string, Dumper=AnsibleDumper, encoding=None)
        assert yaml_string == yaml_string_obj_from_stream
        assert yaml_string == yaml_string_obj_from_stream == yaml_string_obj_from_string
        assert yaml_string == yaml_string_obj_from_stream == yaml_string_obj_from_string == yaml_string_stream_obj_from_stream == yaml_string_stream_obj_from_string
        assert obj == obj_from_stream
        assert obj == obj_from_string
        assert obj == yaml_string_obj_from_stream
        assert obj == yaml_string_obj_from_string
        assert obj == obj_from_stream == obj_from_string == yaml_string_obj_from_stream == yaml_string_obj_from_string
        return {'obj': obj, 'yaml_string': yaml_string, 'yaml_string_from_stream': yaml_string_from_stream, 'obj_from_stream': obj_from_stream, 'obj_from_string': obj_from_string, 'yaml_string_obj_from_string': yaml_string_obj_from_string}

def test_YamlTestUtils__loader():
    ret = YamlTestUtils()._loader()

def test_YamlTestUtils__dump_stream():
    ret = YamlTestUtils()._dump_stream()

def test_YamlTestUtils__dump_string():
    ret = YamlTestUtils()._dump_string()

def test_YamlTestUtils__dump_load_cycle():
    ret = YamlTestUtils()._dump_load_cycle()

def test_YamlTestUtils__old_dump_load_cycle():
    ret = YamlTestUtils()._old_dump_load_cycle()