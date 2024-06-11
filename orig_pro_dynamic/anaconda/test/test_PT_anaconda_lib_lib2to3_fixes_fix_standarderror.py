from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_standarderror import FixStandarderror

def test_PT_FixStandarderror_transform():
    f = FixStandarderror()
    f.transform()
