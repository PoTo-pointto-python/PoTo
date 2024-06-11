from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_tuple_params import is_docstring
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_tuple_params import FixTupleParams
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_tuple_params import simplify_args
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_tuple_params import find_params
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_tuple_params import map_to_index
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_tuple_params import tuple_name

def test_PT_is_docstring():
    is_docstring()

def test_PT_FixTupleParams_transform():
    f = FixTupleParams()
    f.transform()

def test_PT_FixTupleParams_transform_lambda():
    f = FixTupleParams()
    f.transform_lambda()

def test_PT_simplify_args():
    simplify_args()

def test_PT_find_params():
    find_params()

def test_PT_map_to_index():
    map_to_index()

def test_PT_tuple_name():
    tuple_name()