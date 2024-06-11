from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.pytree import type_repr
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.pytree import Base
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.pytree import Node
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.pytree import Leaf
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.pytree import convert
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.pytree import BasePattern
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.pytree import LeafPattern
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.pytree import NodePattern
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.pytree import WildcardPattern
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.pytree import NegatedPattern
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.pytree import generate_matches
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.pytree import xxx
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.pytree import xxx

def test_PT_type_repr():
    type_repr()

def test_PT_Base_clone():
    b = Base()
    b.clone()

def test_PT_Base_post_order():
    b = Base()
    b.post_order()

def test_PT_Base_pre_order():
    b = Base()
    b.pre_order()

def test_PT_Base_set_prefix():
    b = Base()
    b.set_prefix("testprefix")

def test_PT_Base_get_prefix():
    b = Base()
    b.get_prefix()

def test_PT_Base_replace():
    b = Base()
    b.replace()

def test_PT_Base_get_lineno():
    b = Base()
    b.get_lineno()

def test_PT_Base_changed():
    b = Base()
    b.changed()

def test_PT_Base_remove():
    b = Base()
    b.remove()

def test_PT_Base_next_sibling():
    b = Base()
    b.next_sibling()

def test_PT_Base_prev_sibling():
    b = Base()
    b.prev_sibling()

def test_PT_Base_leaves():
    b = Base()
    b.leaves()

def test_PT_Base_depth():
    b = Base()
    b.depth()

def test_PT_Base_get_suffix():
    b = Base()
    b.get_suffix()

def test_PT_Node_clone():
    n = Node()
    n.clone()

def test_PT_Node_post_order():
    n = Node()
    n.post_order()

def test_PT_Node_pre_order():
    n = Node()
    n.pre_order()

def test_PT_Node_set_child():
    n = Node()
    n.set_child(1,child)

def test_PT_Node_insert_child():
    n = Node()
    n.insert_child(1,child)

def test_PT_Node_append_child():
    n = Node()
    n.append_child()

def test_PT_Leaf_clone():
    l = Leaf()
    l.clone()

def test_PT_Leaf_leaves():
    l = Leaf()
    l.leaves()

def test_PT_Leaf_post_order():
    l = Leaf()
    l.post_order()

def test_PT_Leaf_pre_order():
    l = Leaf()
    l.pre_order()

def test_PT_convert():
    convert()

def test_PT_BasePattern_optimize():
    b = BasePattern()
    b.optimize()

def test_PT_BasePattern_match():
    b = BasePattern()
    b.match()

def test_PT_BasePattern_match_seq():
    b = BasePattern()
    b.match_seq()

def test_PT_BasePattern_generate_matches():
    b = BasePattern()
    b.generate_matches()

def test_PT_LeafPattern_match():
    l = LeafPattern()
    l.match()

def test_PT_WildcardPattern_optimize():
    w = WildcardPattern()
    w.optimize()

def test_PT_WildcardPattern_match():
    w = WildcardPattern()
    w.match()

def test_PT_WildcardPattern_match_seq():
    w = WildcardPattern()
    w.match_seq()

def test_PT_WildcardPattern_generate_matches():
    w = WildcardPattern()
    w.generate_matches()

def test_PT_NegatedPattern_match():
    n = NegatedPattern()
    n.match()

def test_PT_NegatedPattern_match_seq():
    n = NegatedPattern()
    n.match_seq()

def test_PT_NegatedPattern_generate_matches():
    n = NegatedPattern()
    n.generate_matches()

def test_PT_generate_matches():
    generate_matches()