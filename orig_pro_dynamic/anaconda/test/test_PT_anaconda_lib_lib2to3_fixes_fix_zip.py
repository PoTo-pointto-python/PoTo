from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_zip import FixZip

def test_PT_FixZip_transform():
    f = FixZip()
    f.transform()
