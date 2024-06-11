from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_filter import FixFilter

def test_PT_FixFilter_transform():
    f = FixFilter()
    f.transform()
