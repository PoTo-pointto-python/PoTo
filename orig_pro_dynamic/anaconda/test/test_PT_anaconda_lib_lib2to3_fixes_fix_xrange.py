from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_xrange import FixXrange

def test_PT_FixXrange_start_tree():
    f = FixXrange()
    f.start_tree()

def test_PT_FixXrange_finish_tree():
    f = FixXrange()
    f.finish_tree()

def test_PT_FixXrange_transform():
    f = FixXrange()
    f.transform()

def test_PT_FixXrange_transform_xrange():
    f = FixXrange()
    f.transform_xrange()

def test_PT_FixXrange_transform_range():
    f = FixXrange()
    f.transform_range()

def test_PT_FixXrange_in_special_context():
    f = FixXrange()
    f.in_special_context()
