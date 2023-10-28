import sys

from tests import TestRunner


def main():
    test_runner = TestRunner()
    test_names = sys.argv[1:]
    if len(test_names) < 1:
        print('pass test name(s) as script argument(s)')
        print('eg.: py test.py mytestname')
        print()
        test_runner.print_info()
        return
    test_runner.run(test_names)


if __name__ == '__main__':
    main()
