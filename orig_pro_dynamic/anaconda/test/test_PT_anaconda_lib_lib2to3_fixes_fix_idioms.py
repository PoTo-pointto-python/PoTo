from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_idioms import FixIdioms

def test_PT_FixIdioms_match():
    f = FixIdioms()
    f.match()

def test_PT_FixIdioms_transform():
    f = FixIdioms()
    f.transform()

def test_PT_FixIdioms_transform_isinstance():
    f = FixIdioms()
    f.transform_isinstance()

def test_PT_FixIdioms_transform_while():
    f = FixIdioms()
    f.transform_while()

def test_PT_FixIdioms_transform_sort():
    f = FixIdioms()
    f.transform_sort()