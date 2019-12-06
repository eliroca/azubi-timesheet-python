# SUSE Apprentices Timesheets made easy

## Contributions are welcome:
   + [ ] Subcommand `export` should accept date without day, like this `-d 10.2019`
   + [ ] Possibility to add more days with one command for vacation, etc.
   + [ ] Raise exceptions in `timesheet.py` and catch them in main, instead of exiting the program
   + [ ] Reformat code with black: https://pypi.org/project/black
   + [ ] Implement working hours carryover(Stundenübertrag)
   + Update: early implementation does the job, but it can't extract the value from previous month unless:
      you exported the previous month already AND opened the previous xlsx file AND Ctrl+S to save it,
      so that the calculated values of all formulas are saved. Not quite ideal.
   + [x] Better separate the main script (azubi-timesheet.py) from a module (timesheet.py)
   + [x] Adding "special" days like: vacation, school; only date and comment needed for that
   + [x] Method to fill in records from json file to xlsx exported file
   + [x] Method to create file names like `timesheet_2019_10.json` `timesheet_2019_10.xlsx` and implement where needed
   + [x] Method to load specific json files of the given date's month and year

## Structure
+ Data is saved internally as `json` strings
+ Exports to `xlsx`, therefore: `pip install -r requirements.txt`

## How it looks like
### Main help message
```
./azubi-timesheet.py --help
usage: azubi-timesheet.py [-V] [-n] <SUBCOMMAND> ...

Keep track of your work hours. Add, delete, update records. Export and print
at the end of the month!

global arguments:
  -V, --version         show program's version number and exit
  -n, --non-interactive
                        do not ask anything, use default answers automatically

available subcommands:
  <SUBCOMMAND>
    add                 add a new record
    update              update an existing record
    delete              delete an existing record
    export              export records as .xlsx file

Type <SUBCOMMAND> --help for more info.
```
### Subcommand help message
```
./azubi-timesheet.py add --help
usage: azubi-timesheet.py add [-d DD.MM.YYYY] [-w HH:MM-HH:MM]
                              [-b HH:MM-HH:MM] [-c COMMENT] [-s]

Add a new record.

subcommand arguments:
  -d DD.MM.YYYY, --date DD.MM.YYYY
                        date of the record
  -w HH:MM-HH:MM, --work-hours HH:MM-HH:MM
                        begin and end time of the work day
  -b HH:MM-HH:MM, --break-time HH:MM-HH:MM
                        begin and end time of the break
  -c COMMENT, --comment COMMENT
                        comment of the record, if needed
  -s, --special-record  special records only need a date and a comment
```
### Subcommands
+ `add` creates a new json string and appends it to the list
```
./azubi-timesheet.py add --date 07.10.2019 --work-hours 09:00-17:30 --break-time 12:00-12:30
```
+ `add -s` adds special records like school, vacation, sick leave, where `--work-hours` or `--break_time` are **not** necessary
```
./azubi-timesheet.py --non-interactive add --date 09.10.2019 --comment "Berufsschule" --special-record
```
+ `update` finds record, updates it with the given data
```
./azubi-timesheet.py update --date 07.10.2019 --work-hours 10:00-18:30 --break-time 13:00-13:30
```
+ `delete` removes record with given date
```
./azubi-timesheet.py delete --date 07.10.2019
```
+ `export` creates an `xlsx` document from the given date's **month** and **year**, day is not relevant
```
./azubi-timesheet.py export --date 01.12.2019
```
