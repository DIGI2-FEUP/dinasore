import unittest
import logging
import sys
import os

sys.path.append(os.path.join(os.path.dirname(sys.path[0])))

from communication import marketplace_bridge

from tests import test_resources
from tests import test_fb
from tests import test_xml
from tests import test_opcua
from tests import test_data_model

marketplace_bridge.MarketplaceBridge.initializeGenericRequester('d_api',3000,'d_ftp',21)
loader = unittest.TestLoader()
suite = unittest.TestSuite()

# add tests to the test suite
suite.addTests(loader.loadTestsFromModule(test_resources))
suite.addTests(loader.loadTestsFromModule(test_fb))
suite.addTests(loader.loadTestsFromModule(test_xml))
suite.addTests(loader.loadTestsFromModule(test_opcua))
suite.addTests(loader.loadTestsFromModule(test_data_model))

logging.disable(logging.CRITICAL)

# initialize a runner, pass it your suite and run it
runner = unittest.TextTestRunner(verbosity=3)
result = runner.run(suite)
