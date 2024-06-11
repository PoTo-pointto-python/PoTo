from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_future import FixFuture

def test_PT_FixFuture_transform():
    f = FixFuture()
    f.transform()
