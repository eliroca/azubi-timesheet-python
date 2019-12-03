#!/usr/bin/env python3
#
# Copyright (c) 2019 Elisei Roca
#
"""
Keep track of your work hours. Add, delete, update records.
Export and print at the end of the month!
"""

import os
import re
import sys
import argparse
import datetime
from timesheet import Timesheet

__author__ = "Elisei Roca"
__version__ = "0.9"
__prog__ = os.path.basename(sys.argv[0])


def execute(args):
    """Checks which subcommand was given and executes it.

    :param args: The namespace containing the scripts arguments
    :type args: :class:`argparse.Namespace`
    """
    timesheet = Timesheet(args, config_file="config.json")
    # toms: you can avoid this if...elif.. cascade with a function map,
    # see FUNC_MAP below.
    if args.subcommand == "add":
        if not timesheet.add_record():
            print("Exiting. Record already exists.")
            sys.exit(1)
    elif args.subcommand == "update":
        if not timesheet.update_record():
            print("Exiting. Record with given date not found.")
            sys.exit(1)
    elif args.subcommand == "delete":
        if not timesheet.delete_record():
            print("Exiting. Record with given date not found.")
            sys.exit(1)
    elif args.subcommand == "export":
        if not timesheet.export():
            print("Exiting. No idea why yet.")
            sys.exit(1)

def check_date(date, non_interactive, message, attempts=3):
    """Check that date respects format 'DD.MM.YYYY'.

    :param str date: The date supplied from the command line
    :param bool non_interactive: Tells the function if asking for user input is ok
    :param str message: Message to print when asking for date input
    :param int attempts: Allowed number of attempts to specify a valid date
    :return: Validated date object: date(year, month, day)
    :rtype: datetime.date
    """

    if non_interactive:
        attempts = 1
    while attempts:
        if not date and not non_interactive:
            date = input(message)
        try:
            date = datetime.datetime.strptime(date, "%d.%m.%Y")
            return date
        except ValueError as error:
            print("Expected date of following format: 'DD.MM.YYYY'",
                  error,
                  file=sys.stderr)
        attempts -= 1
        date = ""

    # toms: I'd recommend to raise an exception here and catch it in main.
    # Then you don't need to exit the script here, main would be responsible
    # for example:
    # raise RuntimeError(...)
    # raise SystemExit(...)
    # or create your own exception:
    # class TimesheetError(ValueError):
    #    pass
    # raise TimesheetError(...)
    print("Exiting. You entered invalid date or didn't enter any input.",
          file=sys.stderr)
    sys.exit(1)

def check_time_interval(time_interval, non_interactive, name="", attempts=3):
    """Check that time interval respects format 'HH:MM-HH:MM'.

    :param str time_interval: The time interval supplied from the command line
    :param bool non_interactive: Tells the function if asking for user input is ok
    :param str name: Name of time interval, used when printing to stdout
    :param int attempts: Allowed number of attempts to specify a valid time interval
    :return: Two validated time objects: time(hour, minute)
    :rtype: tuple(datetime.time, datetime.time)
    """

    if non_interactive:
        attempts = 1
    while attempts:
        if not time_interval and not non_interactive:
            time_interval = input("- Enter the BEGIN and END {}: ".format(name))

        # toms: Acutally, you don't need this regex. You can replace it
        # with: datetime.datetime.strptime(date_string, "%H:%M")
        # If you pass an invalid date/time, you get a ValueError exception
        # But better check my code. ;-)

        try:
            start, end = time_interval.split("-")
            start = datetime.datetime.strptime(start, "%H:%M")
            end = datetime.datetime.strptime(end, "%H:%M")
            return start.time(), end.time()
        except ValueError:
            print("Expected {} of following format: 'HH:MM-HH:MM'".format(name),
                  file=sys.stderr)
        attempts -= 1
        time_interval = ""

    # toms: I'd recommend to raise an exception here and catch it in main.
    # Then you don't need to exit the script here, main would be responsible
    # for example:
    # raise RuntimeError(...)
    # raise SystemExit(...)
    # or create your own exception:
    # class TimesheetError(ValueError):
    #    pass
    # raise TimesheetError(...)
    print("Exiting. You entered invalid {} or didn't enter any input.".format(name),
          file=sys.stderr)
    sys.exit(1)

def check_args(args):
    """Checks if no arguments were given when running the script and asks for them.

    :param args: The namespace containing the scripts arguments
    :type args: :class:`argparse.Namespace`
    """
    # checking date
    args.date = check_date(args.date, args.non_interactive, "- Enter the DATE of record: ")

    # toms: This special check may not be necessary, if you use subparsers
    # see below
    if not args.subcommand in ("delete", "export"):
        # checking comment
        if not args.comment and not args.non_interactive:
            args.comment=input("- Enter the COMMENT of record, if needed: ")
        if not args.special:
            # checking work hours
            args.work_hours = check_time_interval(args.work_hours, args.non_interactive, "WORK HOURS")
            # checking break
            args.break_time = check_time_interval(args.break_time, args.non_interactive, "BREAK TIME")
        else:
            args.work_hours = (datetime.time(0, 0), datetime.time(0, 0))
            args.break_time = (datetime.time(0, 0), datetime.time(0, 0))

def parse_cli(args=None):
    """Parse CLI with :class:`argparse.ArgumentParser` and return parsed result.

    :param list args: Arguments to parse or None (=use sys.argv)
    :return: parsed CLI result
    :rtype: :class:`argparse.Namespace`
    """
    parser=argparse.ArgumentParser(description=__doc__,
                                     prog=__prog__,
                                     add_help=False)
    parser.add_argument("-v", "--version",
                        action="version",
                        version="%(prog)s {}".format(__version__),
                        help="Show program's version number and exit."
                        )
    # toms: Maybe better create subparsers for this.
    # For an example, look at:
    # https://gist.github.com/tomschr/8bfb228b68c52e8b6686213d89c842d5
    # Python doc:
    # https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.add_subparsers
    #
    # If you still would like to use this approach, I would propose this
    # alternative:
    #
    # 1. Define your subcommand functions, for example:
    #    def func_add(args):  # args would be :class:`argparse.Namespace`
    #
    # 2. Create function map like with keys as command names and keys as functions
    #    like this:
    #    FUNC_MAP = { 'add': func_add, 'delete': func_delete, ...}
    #    parser.add_argument(action="store", dest="subcommand", nargs="?", help="...",
    #                        choices=FUNC_MAP.keys(), )
    #
    # To call the requested subcommand, use:
    #
    #   func = FUNC_MAP[args.command]
    #   func()
    parser.add_argument(action="store",
                        dest="subcommand",
                        metavar="add | delete | update | export",
                        choices=["add", "delete", "update", "export"],
                        nargs="?",
                        help="Choose one of these subcommands.",
                        )
    parser.add_argument("-n", "--non-interactive",
                        action="store_true",
                        dest="non_interactive",
                        help="Do not ask anything, use default answers automatically.",
                        )
    parser.add_argument("-s", "--special-record",
                        action="store_true",
                        dest="special",
                        help="Special records only need a date and a comment.",
                        )
    parser.add_argument("-d", "--date",
                        dest="date",
                        metavar="DD.MM.YYYY",
                        default="",
                        help="Date of the record.",
                        )
    parser.add_argument("-w", "--work-hours",
                        dest="work_hours",
                        metavar="HH:MM-HH:MM",
                        default="",
                        help="Begin and end time of the work day.",
                        )
    parser.add_argument("-b", "--break-time",
                        dest="break_time",
                        metavar="HH:MM-HH:MM",
                        default="",
                        help="Begin and end time of the break.",
                        )
    parser.add_argument("-c", "--comment",
                        dest="comment",
                        default="",
                        help="Comment of the record, if needed.",
                        )
    parser.add_argument("-h", "--help",
                        action="help",
                        default=argparse.SUPPRESS,
                        help="Show this help message and exit.",
                        )
    args = parser.parse_args(args)
    args.parser = parser
    # If no argument is given, print help info:
    if not sys.argv[1:]:
        parser.print_help()
        sys.exit(0)
    return args

def main(args=None):
    """Main function of the script.

    :param list args: a list of arguments (sys.argv[:1])
    """
    args = parse_cli(args)
    check_args(args)
    execute(args)
    return 0

if __name__ == "__main__":
    sys.exit(main())
