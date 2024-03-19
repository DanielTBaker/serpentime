import datetime
import mechanize
import numpy as np
from bs4 import BeautifulSoup
import configparser
import argparse
import re
from serpentime import *
from getpass import getpass

## Load Configuration
config = configparser.ConfigParser()
config.read('config.ini')
## Username
if config['Authorization']['user']:
    user = config['Authorization']['user']
else:
    user = input('Username : ')
## Password
if config['Authorization']['password']:
    pwd  = config['Authorization']['password']
else:
    pwd = getpass()
## Clock in time (hours)
clockIn = int(config['Clock Settings']['clockIn'])
## Clock out time (hours)
clockOut = int(config['Clock Settings']['clockOut'])

## Prepare URLs:
## Root URL for internal site
baseURL = "https://www.asiaa.sinica.edu.tw/internal_site/"
## URL for personnel system
personnelURL = baseURL + "personnel_system/"
##URL for clock in/out page
clockURL = personnelURL + "WorkHour.php"

## Flag used to distiguish clocking in from out in records
inFlag = 10

## Load holidaynames from config file
holidayNames = np.array(config['Holidays']['holidayNames'].splitlines())

parser=argparse.ArgumentParser(description='CYGNSS analysis.')
parser.add_argument('-r',type=str, help='Revert to date')
parser.add_argument('-d',type=str, default = datetime.datetime.now().isoformat(), help='Date to fill to')
args=parser.parse_args()

## Prepare browser
br = mechanize.Browser()
br.set_handle_robots(False)
br.set_handle_refresh(False) 
br.add_password(baseURL, user, pwd)

dateFormat = re.compile('[0-9]{4}-[0-9]{2}-[0-9]{2}')
if args.r:
    assert dateFormat.match(args.r), "Reversion date must be in the format yyyy-mm-dd"
    reversionDate = datetime.datetime.fromisoformat(args.r)
    br.open(clockURL)
    br.select_form(nr=1)
    log = br.form["s2g"].split(", ")
    date = log[0].split(" ")[0]
    time = log[0].split(" ")[1]
    lastLog = datetime.datetime.fromisoformat(date+'T'+time)
    while lastLog>reversionDate:
        print(f'Removing Log from {lastLog.isoformat()}')
        br.submit("bt_remove")
        br.open(clockURL)
        br.select_form(nr=1)
        log = br.form["s2g"].split(", ")
        date = log[0].split(" ")[0]
        time = log[0].split(" ")[1]
        lastLog = datetime.datetime.fromisoformat(date+'T'+time)
    
assert dateFormat.match(args.d), "Final date must be in the format yyyy-mm-dd"

## Final date to update to (Default is current date)
endDate = datetime.datetime.fromisoformat(args.d)

## Get starting date from last log
startDate, startTime, startFlag, startUser = get_last_log(br,clockURL)
startDate = datetime.datetime(*[int(n) for n in startDate.split("-")])
currentDate = startDate

## Get all between start and end dates
starts, ends = get_leaves(br, startDate, endDate,baseURL,user)

##Load the last log and check if it was clocking in or out
print("Last log:")
if startFlag == inFlag:
    clockedIn = True
    print(
        f"Clocked in at {(currentDate+datetime.timedelta(hours=clockIn)).isoformat()}"
    )
    currentDate += datetime.timedelta(hours=clockOut)

else:
    clockedIn = False
    print(
        f"Clocked out at {(currentDate+datetime.timedelta(hours=clockOut)).isoformat()}"
    )
    currentDate += datetime.timedelta(days=1,hours=clockIn)

## If there are logs to update print a message
if currentDate < endDate:
    print("Updated Logs:")


## Get monthly holiday data for starting date
holidayURL = (
            personnelURL
            + f"attendance_record.php?smn={currentDate.isoformat()[:7]}&acc={user}"
        )
month = BeautifulSoup(br.open(holidayURL).get_data(), "html.parser")
br.open(clockURL)
## Update records until you reach the current time
while currentDate < endDate:
    ## If this is the first record on the 1st day of a month, get the holidays
    if currentDate.day == 1 and not clockedIn:
        holidayURL = (
            personnelURL
            + f"attendance_record.php?smn={currentDate.isoformat()[:7]}&acc={user}"
        )
        month = BeautifulSoup(br.open(holidayURL).get_data(), "html.parser")
        br.open(clockURL)

    ## Check for holiday on date
    workday, holiday, typhoon = check_holiday(currentDate.isoformat()[:10], month,holidayNames)
    ## Check if weekday
    weekday = check_weekday(currentDate)
    ## Check if day is during any leave
    leave = np.any([(currentDate>starts[id]) and (currentDate<ends[id]) for id in range(len(starts))])

    ## Check if it's a normal workday
    normalWork = weekday and not (leave or holiday or typhoon)
    ## Check for adjusted workday
    adjustedWork = workday and not (leave or holiday or typhoon)
    ## only care about leave if you would otherwise work
    leave = (leave and (weekday or workday))

    ## Only clock if it's a weekday or an adjusted workday but not a holiday,typhoon day, or leave day
    doClock = (weekday or workday) and not (holiday or typhoon or leave)

    ## Clock out if clocked in on a workday
    if clockedIn:
        if doClock:
            clock_out(br, clockURL, currentDate)
            print(f"Clocked out at {currentDate.isoformat()}")
        currentDate += datetime.timedelta(days=1, hours=clockIn - clockOut)
        clockedIn = False
    ## Clock in if clocked out on a workday
    else:
        if doClock:
            clock_in(br, clockURL, currentDate)
            print(f"Clocked in at {currentDate.isoformat()}")
            currentDate += datetime.timedelta(hours=clockOut - clockIn)
            clockedIn = True
        else:
            currentDate += datetime.timedelta(days=1)

print("Records are current!")
