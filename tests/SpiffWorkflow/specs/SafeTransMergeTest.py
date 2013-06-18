import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from tests.SpiffWorkflow.util import run_workflow
from TaskSpecTest import TaskSpecTest
from SpiffWorkflow.specs import Transform, Simple, SafeTransMerge
from SpiffWorkflow.util import merge_dictionary


class SafeTransMergeTest(TaskSpecTest):
    def create_instance(self):
        if 'testtask' in self.wf_spec.task_specs:
            del self.wf_spec.task_specs['testtask']

        return SafeTransMerge(self.wf_spec,
                       'testtask',
                       description='foo',
                       transforms=[''])

    def testWaitOnInputs(self):
        """
        Tests that we can make the transform wait on its inputs and then
        continue.
        """
        # Any task that writes 'foo' as an output
        taskA1 = Transform(self.wf_spec, 'A1', transforms=[
            "my_task.set_attribute(foo=1)"])
        self.wf_spec.start.connect(taskA1)
        # Any task that writes 'bar' as an output after a wait
        taskA2 = Transform(self.wf_spec, 'A2', transforms=[
            "self.bar = getattr(self, 'bar', 0) + 1",
            "my_task.set_attribute(bar=self.bar)",
            "return self.bar == 4",
            ])
        self.wf_spec.start.connect(taskA2)

        function_name = "tests.SpiffWorkflow.specs.SafeTransMergeTest." \
                        "SomeClass.my_code"
        taskB = SafeTransMerge(self.wf_spec, 'B', function_name=function_name)
        taskB.follow(taskA1)
        taskB.follow(taskA2)
        task3 = Simple(self.wf_spec, 'Last')
        taskB.connect(task3)

        expected = 'Start\n  A1\n  A2\n    B\n      Last\n'
        workflow = run_workflow(self, self.wf_spec, expected, '', max_tries=3)
        last = [t for t in workflow.get_tasks() if t.get_name() == 'Last'][0]
        self.assertEqual(last.attributes.get('my_foo'), 1)
        self.assertEqual(last.attributes.get('my_bar'), 4)
        self.assertEqual(last.attributes.get('foo'), 1)
        self.assertEqual(last.attributes.get('bar'), 4)


class SomeClass:
    @staticmethod
    def my_code(self, my_task):
        fields = ['foo', 'bar']
        # Get fields from task and store them in spec
        for key in fields:
            if key in my_task.attributes:
                merge_dictionary(self.properties, dict(collect={
                        'my_%s' % key: my_task.attributes[key],
                        key: my_task.attributes[key]}))
        # Check if we have all fields
        collected = self.get_property('collect', {})
        if any(key for key in fields if key not in collected):
            return False
        my_task.set_attribute(**collected)
        return True


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(SafeTransMergeTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
