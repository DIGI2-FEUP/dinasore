import unittest
import logging
import sys
import os

sys.path.append(os.path.join(os.path.dirname(sys.path[0])))

from tests import test_resources
from tests import test_fb
from tests import test_xml
from tests import test_opcua


loader = unittest.TestLoader()
suite = unittest.TestSuite()

# add tests to the test suite
suite.addTests(loader.loadTestsFromModule(test_resources))
suite.addTests(loader.loadTestsFromModule(test_fb))
suite.addTests(loader.loadTestsFromModule(test_xml))
suite.addTests(loader.loadTestsFromModule(test_opcua))

logging.disable(logging.CRITICAL)

# initialize a runner, pass it your suite and run it
runner = unittest.TextTestRunner(verbosity=3)
result = runner.run(suite)
