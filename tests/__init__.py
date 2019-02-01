import unittest
import logging

from tests import test_resources
from tests import test_fb


loader = unittest.TestLoader()
suite = unittest.TestSuite()

# add tests to the test suite
suite.addTests(loader.loadTestsFromModule(test_resources))
suite.addTests(loader.loadTestsFromModule(test_fb))

logging.disable(logging.CRITICAL)

# initialize a runner, pass it your suite and run it
runner = unittest.TextTestRunner(verbosity=3)
result = runner.run(suite)
