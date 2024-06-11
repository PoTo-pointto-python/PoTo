from __future__ import absolute_import, division, print_function
__metaclass__ = type
from units.compat import unittest
from units.compat.mock import patch, MagicMock
from ansible.executor.task_result import TaskResult

class TestTaskResult(unittest.TestCase):

    def test_task_result_basic(self):
        mock_host = MagicMock()
        mock_task = MagicMock()
        tr = TaskResult(mock_host, mock_task, dict())
        with patch('ansible.parsing.dataloader.DataLoader.load') as p:
            tr = TaskResult(mock_host, mock_task, '{}')

    def test_task_result_is_changed(self):
        mock_host = MagicMock()
        mock_task = MagicMock()
        tr = TaskResult(mock_host, mock_task, dict())
        self.assertFalse(tr.is_changed())
        tr = TaskResult(mock_host, mock_task, dict(changed=True))
        self.assertTrue(tr.is_changed())
        mock_task.loop = 'foo'
        tr = TaskResult(mock_host, mock_task, dict(results=[dict(foo='bar'), dict(bam='baz'), True]))
        self.assertFalse(tr.is_changed())
        mock_task.loop = 'foo'
        tr = TaskResult(mock_host, mock_task, dict(results=[dict(changed=False), dict(changed=True), dict(some_key=False)]))
        self.assertTrue(tr.is_changed())

    def test_task_result_is_skipped(self):
        mock_host = MagicMock()
        mock_task = MagicMock()
        tr = TaskResult(mock_host, mock_task, dict())
        self.assertFalse(tr.is_skipped())
        tr = TaskResult(mock_host, mock_task, dict(skipped=True))
        self.assertTrue(tr.is_skipped())
        mock_task.loop = 'foo'
        tr = TaskResult(mock_host, mock_task, dict(results=[dict(foo='bar'), dict(bam='baz'), True]))
        self.assertFalse(tr.is_skipped())
        mock_task.loop = 'foo'
        tr = TaskResult(mock_host, mock_task, dict(results=[dict(skipped=False), dict(skipped=True), dict(some_key=False)]))
        self.assertFalse(tr.is_skipped())
        mock_task.loop = 'foo'
        tr = TaskResult(mock_host, mock_task, dict(results=[dict(skipped=True), dict(skipped=True), dict(skipped=True)]))
        self.assertTrue(tr.is_skipped())
        mock_task.loop = 'foo'
        tr = TaskResult(mock_host, mock_task, dict(results=['a', 'b', 'c'], skipped=False))
        self.assertFalse(tr.is_skipped())
        tr = TaskResult(mock_host, mock_task, dict(results=['a', 'b', 'c'], skipped=True))
        self.assertTrue(tr.is_skipped())

    def test_task_result_is_unreachable(self):
        mock_host = MagicMock()
        mock_task = MagicMock()
        tr = TaskResult(mock_host, mock_task, dict())
        self.assertFalse(tr.is_unreachable())
        tr = TaskResult(mock_host, mock_task, dict(unreachable=True))
        self.assertTrue(tr.is_unreachable())
        mock_task.loop = 'foo'
        tr = TaskResult(mock_host, mock_task, dict(results=[dict(foo='bar'), dict(bam='baz'), True]))
        self.assertFalse(tr.is_unreachable())
        mock_task.loop = 'foo'
        tr = TaskResult(mock_host, mock_task, dict(results=[dict(unreachable=False), dict(unreachable=True), dict(some_key=False)]))
        self.assertTrue(tr.is_unreachable())

    def test_task_result_is_failed(self):
        mock_host = MagicMock()
        mock_task = MagicMock()
        tr = TaskResult(mock_host, mock_task, dict())
        self.assertFalse(tr.is_failed())
        tr = TaskResult(mock_host, mock_task, dict(rc=0))
        self.assertFalse(tr.is_failed())
        tr = TaskResult(mock_host, mock_task, dict(rc=1))
        self.assertFalse(tr.is_failed())
        tr = TaskResult(mock_host, mock_task, dict(failed=True))
        self.assertTrue(tr.is_failed())
        tr = TaskResult(mock_host, mock_task, dict(failed_when_result=True))
        self.assertTrue(tr.is_failed())

    def test_task_result_no_log(self):
        mock_host = MagicMock()
        mock_task = MagicMock()
        tr = TaskResult(mock_host, mock_task, dict(_ansible_no_log=True, secret='DONTSHOWME'))
        clean = tr.clean_copy()
        self.assertTrue('secret' not in clean._result)

    def test_task_result_no_log_preserve(self):
        mock_host = MagicMock()
        mock_task = MagicMock()
        tr = TaskResult(mock_host, mock_task, dict(_ansible_no_log=True, retries=5, attempts=5, changed=False, foo='bar'))
        clean = tr.clean_copy()
        self.assertTrue('retries' in clean._result)
        self.assertTrue('attempts' in clean._result)
        self.assertTrue('changed' in clean._result)
        self.assertTrue('foo' not in clean._result)

def test_TestTaskResult_test_task_result_basic():
    ret = TestTaskResult().test_task_result_basic()

def test_TestTaskResult_test_task_result_is_changed():
    ret = TestTaskResult().test_task_result_is_changed()

def test_TestTaskResult_test_task_result_is_skipped():
    ret = TestTaskResult().test_task_result_is_skipped()

def test_TestTaskResult_test_task_result_is_unreachable():
    ret = TestTaskResult().test_task_result_is_unreachable()

def test_TestTaskResult_test_task_result_is_failed():
    ret = TestTaskResult().test_task_result_is_failed()

def test_TestTaskResult_test_task_result_no_log():
    ret = TestTaskResult().test_task_result_no_log()

def test_TestTaskResult_test_task_result_no_log_preserve():
    ret = TestTaskResult().test_task_result_no_log_preserve()