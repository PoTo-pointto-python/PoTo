from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_urllib import build_pattern
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_urllib import FixUrllib

def test_PT_build_pattern():
    build_pattern()

def test_PT_FixUrllib_build_pattern():
    f = FixUrllib()
    f.build_pattern()

def test_PT_FixUrllib_transform_import():
    f = FixUrllib()
    f.transform_import()

def test_PT_FixUrllib_transform_member():
    f = FixUrllib()
    f.transform_member()

def test_PT_FixUrllib_transform_dot():
    f = FixUrllib()
    f.transform_dot()

def test_PT_FixUrllib_transform():
    f = FixUrllib()
    f.transform()