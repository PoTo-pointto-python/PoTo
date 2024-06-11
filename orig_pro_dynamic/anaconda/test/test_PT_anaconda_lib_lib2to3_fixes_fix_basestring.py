from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_basestring import FixBasestring

def test_PT_FixBasestring_transform():
    f = FixBasestring()
    f.transform()
