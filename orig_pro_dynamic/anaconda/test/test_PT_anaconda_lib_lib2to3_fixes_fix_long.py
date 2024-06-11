from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_long import FixLong

def test_PT_FixLong_transform():
    f = FixLong()
    f.transform()