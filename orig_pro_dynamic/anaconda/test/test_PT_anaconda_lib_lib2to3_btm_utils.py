from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.btm_utils import MinNode
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.btm_utils import reduce_tree
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.btm_utils import get_characteristic_subpattern
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.btm_utils import rec_test

def test_PT_MinNode_leaf_to_root():
    m = MinNode()
    m.leaf_to_root()

def test_PT_MinNode_get_linear_subpattern():
    m = MinNode()
    m.get_linear_subpattern()

def test_PT_MinNode_leaves():
    m = MinNode()
    m.leaves()

def test_PT_reduce_tree():
    reduce_tree()

def test_PT_get_characteristic_subpattern():
    get_characteristic_subpattern()

def test_PT_rec_test():
    rec_test()