import sys

if sys.argv[1] == 'test':
    from . import tests
    tests.run()
