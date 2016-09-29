import unittest

def run():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    from . import datasets, managers
    suite.addTest(load_tests(loader, datasets))
    suite.addTest(load_tests(loader, managers))

    unittest.TextTestRunner().run(suite)


def load_tests(loader, m):
    suite = unittest.TestSuite()
    for k, v in m.__dict__.items():
        if isinstance(v, type) and issubclass(v, unittest.TestCase):
            tests = loader.loadTestsFromTestCase(v)
            suite.addTests(tests)
    return suite

