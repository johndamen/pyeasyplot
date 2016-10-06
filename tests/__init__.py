import unittest
import importlib
import os


def run():

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # load tests from this directory
    root = os.path.split(__file__)[0]
    for f in os.listdir(root):
        # skip private modules
        if f.startswith('_'):
            continue

        # get module name from filename
        if os.path.isdir(os.path.join(root, f)):
            name = f
        else:
            name, ext = os.path.splitext(f)
            if ext != '.py':
                continue

        # import module
        m = importlib.import_module('.'+name, package=__name__)

        # add tests from module
        module_suite = loader.loadTestsFromModule(m)
        print('{:20s} {} tests'.format(
            m.__name__, module_suite.countTestCases()))
        suite.addTest(module_suite)

    # run tests
    unittest.TextTestRunner().run(suite)

