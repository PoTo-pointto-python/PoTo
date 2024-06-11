from __future__ import absolute_import, division, print_function
__metaclass__ = type
from ansible.module_utils.common.sys_info import get_all_subclasses

class TestGetAllSubclasses:

    class Base:
        pass

    class BranchI(Base):
        pass

    class BranchII(Base):
        pass

    class BranchIA(BranchI):
        pass

    class BranchIB(BranchI):
        pass

    class BranchIIA(BranchII):
        pass

    class BranchIIB(BranchII):
        pass

    def test_bottom_level(self):
        assert get_all_subclasses(self.BranchIIB) == set()

    def test_one_inheritance(self):
        assert set(get_all_subclasses(self.BranchII)) == set([self.BranchIIA, self.BranchIIB])

    def test_toplevel(self):
        assert set(get_all_subclasses(self.Base)) == set([self.BranchI, self.BranchII, self.BranchIA, self.BranchIB, self.BranchIIA, self.BranchIIB])

def test_TestGetAllSubclasses_test_bottom_level():
    ret = TestGetAllSubclasses().test_bottom_level()

def test_TestGetAllSubclasses_test_one_inheritance():
    ret = TestGetAllSubclasses().test_one_inheritance()

def test_TestGetAllSubclasses_test_toplevel():
    ret = TestGetAllSubclasses().test_toplevel()