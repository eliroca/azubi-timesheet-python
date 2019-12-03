import os
import sys
import json
import locale
from datetime import datetime
from datetime import timedelta
from openpyxl import load_workbook

class Timesheet(object):
    """Object for managing a timesheet.
    Saves records in a JSON file.
    """
    def __init__(self, args, config_file):
        """Constructor,  initializes the instance attributes.

        :param args: argparse.Namespace object
        :param str config_file: Name of configuration file
        """
        # toms: This is unneccessary as object doesn't initalize anything:
        # super(Timesheet, self).__init__()
        # toms: I also removed configure_attr as it isn't called from anywhere
        self.args = args
        self.config = self.load_json_file(config_file)
        if self.config == None:
            sys.exit("Exiting. Configuration file '{}' not found.".format(config_file))

        self.date_str = self.args.date.strftime("%d.%m.%Y")
        self.month_str = self.args.date.strftime("%m")
        self.year = self.args.date.year

        # toms: can you absolutely be sure, that self.config contains the key
        # 'records_dir'? If not, it will easily raise a KeyError exception. ;)
        self.records_file = os.path.join(self.config["records_dir"], "timesheet_{}_{}.json".format(self.year, self.month_str))
        self.records = self.load_json_file(self.records_file, [])

    def netto_workdays(self, start_date, end_date, holidays=[], weekend_days=[5,6]):
        """Calculates number of workdays between two given dates, subtracting weekends.

        :param date start_date: Date from where to start counting
        :param date end_date: Date where to stop counting
        :param list holidays: List of holidays, date objects
        :param list weekend_days: List of days included in weekend; 5=sat, 6=sun
                as specified in :func:`datetime.datetime.weekday`
        :return: Integer number of workdays
        """
        delta_days = (end_date - start_date).days + 1
        full_weeks, extra_days = divmod(delta_days, 7)
        # num_workdays = how many days/week you work * total number of weeks
        num_workdays = (full_weeks + 1) * (7 - len(weekend_days))
        # subtract out any working days that fall in the 'shortened week'
        for d in range(1, 8 - extra_days):
            if (end_date + timedelta(d)).weekday() not in weekend_days:
                 num_workdays -= 1
        # skip holidays that fall on weekend_days
        holidays =  [x for x in holidays if x.weekday() not in weekend_days]
        # subtract out any holidays
        for d in holidays:
            if start_date <= d <= end_date:
                num_workdays -= 1
        return num_workdays

    def add_record(self):
        """Add a new record in timesheet.
        """
        if not self.record_exists(self.args.date):
            record = self.create_record()
            self.records.append(record)
            self.write_json_file(self.records_file, self.records)
            return True
        return False

    def delete_record(self):
        """Delete a record from timesheet.
        """
        for record in self.records:
            if self.date_str == record["date"]:
                self.records.remove(record)
                if len(self.records) > 0:
                    self.write_json_file(self.records_file, self.records)
                else:
                    os.remove(self.records_file)
                return True
        return False

    def update_record(self):
        """Replace a record in timesheet.
        """
        new_record = self.create_record()
        for record in self.records:
            if self.date_str == record["date"] and not record == new_record:
                record.update(new_record)
                self.write_json_file(self.records_file, self.records)
                return True
        return False

    def create_record(self):
        """Create a record as dictionary.

        :param args: argparse.Namespace object
        :return: a dictionary with record data from argparse.Namespace object
        :rtype: dict
        """
        return {
            "date": self.date_str,
            "start_day": self.args.work_hours[0].strftime("%H:%M"),
            "end_day": self.args.work_hours[1].strftime("%H:%M"),
            "start_break": self.args.break_time[0].strftime("%H:%M"),
            "end_break": self.args.break_time[1].strftime("%H:%M"),
            "comment": self.args.comment,
            "special": str(self.args.special)
        }

    def write_json_file(self, file, content):
        """Write list of records to JSON file.

        :param str file: name of file to write
        :param content: content to write in file
        """
        with open(file, "w", encoding="utf-8") as f:
            json.dump(content, f, indent=2)

    def load_json_file(self, file, default_content=None):
        """Load JSON file, return content.

        :param str file: name of file to load
        :param default_content: default content to return as loaded content
        :return: content from file
        """
        if os.path.isfile(file) and os.path.getsize(file):
            with open(file, "r", encoding="utf-8") as f:
                return json.load(f)
        return default_content

    def record_exists(self, date):
        """Check if record exists already.

        :param date: datetime.date object
        return: a bool with the result
        """
        for record in self.records:
            if self.date_str == record["date"]:
                return True
        return False

    def export(self):
        """Export timesheet as .xlsx file
        """
        # toms: IMHO, a class or library should only raise an exception here 
        # and NOT exit the script; that is the responsibility of the caller.
        # In your case, you should raise an exception and catch it in main
        # (or wherever it is useful)
        if len(self.records) == 0:
            exit_message = "Exiting. There are no records for {} {} to export.".format(self.args.date.strftime("%B"), self.year)
            sys.exit(exit_message)

        total_days = (self.args.date.replace(month = self.args.date.month % 12 +1, day = 1)-timedelta(days=1)).day
        start_month = self.args.date.replace(day = 1)
        end_month = self.args.date.replace(day = total_days)
        workdays = self.netto_workdays(start_month, end_month, weekend_days=(5,6))

        # toms: again, are you really sure, self.config contains ALWAYS the keys
        # "templates_dir" and "exports_dir"? If not, you get an KeyError exception.
        #
        # Actually, after looking into "config.json", if you only need to access
        # directories relative to this script, why not use this:
        #
        # DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
        # template_file = os.path.join(DATA_DIR, "template_timesheet_{}_days.xlsx".format(workdays))
        #
        # You could use it for the other directories too to define this as
        # "default behaviour". That makes this config.json file obsolete and you
        # could simplify your code. ;)
        template_file = os.path.join(self.config["templates_dir"], "template_timesheet_{}_days.xlsx".format(workdays))

        export_file = os.path.join(self.config["exports_dir"], "timesheet_{}_{}.xlsx".format(self.year, self.month_str))

        # set locale to use weekdays, months full name in german
        locale.setlocale(locale.LC_TIME, 'de_DE.UTF-8')
        wb = load_workbook(template_file)
        ws = wb.active
        ws.cell(row=7, column=4).value = self.config["name"]
        month_year_str = "{} {}".format(self.args.date.strftime("%B"), self.year)
        ws.cell(row=8, column=4).value = month_year_str
        row = 12
        for record in self.records:
            col = 2
            date =  datetime.strptime(record["date"], "%d.%m.%Y")
            ws.cell(row=row, column=col).value = date.strftime("%A")
            col += 1
            ws.cell(row=row, column=col).value = date
            col += 1
            if "special" in record.keys() and record["special"] == "true":
                ws.cell(row=row, column=9).value = 8.00
                col += 4
            else:
                ws.cell(row=row, column=col).value = datetime.strptime(record["start_day"], "%H:%M").time()
                col += 1
                ws.cell(row=row, column=col).value = datetime.strptime(record["end_day"], "%H:%M").time()
                col += 1
                ws.cell(row=row, column=col).value = datetime.strptime(record["start_break"], "%H:%M").time()
                col += 1
                ws.cell(row=row, column=col).value = datetime.strptime(record["end_break"], "%H:%M").time()
            col += 4
            ws.cell(row=row, column=col).value = record["comment"]
            row += 1
        wb.save(export_file)
        return True
