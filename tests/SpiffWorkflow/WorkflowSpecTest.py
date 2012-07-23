import os
import sys
import unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from SpiffWorkflow.specs import Join, WorkflowSpec


class WorkflowSpecTest(unittest.TestCase):
    def setUp(self):
        self.wf_spec = WorkflowSpec()

    def test_cyclic_wait(self):
        """
        Tests that we can detect when two wait taks are witing on each other.
        """
        task1 = Join(self.wf_spec, 'First')
        self.wf_spec.start.connect(task1)
        task2 = Join(self.wf_spec, 'Second')
        task1.connect(task2)

        task2.follow(task1)
        task1.follow(task2)

        results = self.wf_spec.validate()
        self.assertIn("Found loop with 'Second': Second->First then 'Second' "
                "again", results)
        self.assertIn("Found loop with 'First': First->Second then 'First' "
                "again", results)


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(
            WorkflowSpecTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
