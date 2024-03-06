import datetime
import mechanize
import numpy as np
from bs4 import BeautifulSoup

def check_holiday(date, month,holidayNames):
    """
    Test if a day is holiday in a given monnth

    params
    ------
    data datetime.datetime : The date to test
    month : parsed html data for a given month to check for holidays in
    """
    ## find all lines with correct format
    lines = [line for line in month.find_all("tr") if line.td]
    ## find specific line for date
    line = [line for line in lines if line.td.text == date][0]
    ## Read the office note for that day
    note = line.find_all("td")[4].text.lower()
    ## Preset all holiday types to false
    adjustedWorkday = False
    holiday = False
    typhoon = False
    if len(note) > 2:
        ## Check if day is an adjusted workday
        if note.count("adjusted workday") > 0:
            adjustedWorkday = True
        ## Check if day is an adjusted holiday
        elif note.count("adjusted holiday") > 0:
            holiday = True
        ## Check if day is a typhoon day
        elif note.count("typhoon") > 0:
            typhoon = True
        ## Check if day is a named holiday
        elif np.array([note.count(name) for name in holidayNames]).max() > 0:
            holiday = True
    return (adjustedWorkday, holiday, typhoon)


def clock_in(br, url, date):
    """
    Submits clock-in request at url for date

    params
    ------
    br : the browser
    url : the url to submit the form
    date : the date and time to clock in
    """
    # br.open(url)
    br.select_form(nr=0)
    br["d"] = date.isoformat()[:10]
    br["t"] = date.isoformat()[11:16]
    br.submit("bt_in")


def clock_out(br, url, date):
    """
    Submits clock-out request at url for date

    params
    ------
    br : the browser
    url : the url to submit the form
    date : the date and time to clock out
    """
    # br.open(url)
    br.select_form(nr=0)
    br["d"] = date.isoformat()[:10]
    br["t"] = date.isoformat()[11:16]
    br.submit("bt_out")


def get_last_log(br,url):
    """
    Checks last log from a given url

    params
    ------
    br : the browser
    url : the url to get the log from
    """
    br.open(url)
    br.select_form(nr=1)
    log = br.form["s2g"].split(", ")
    date = log[0].split(" ")[0]
    time = log[0].split(" ")[1]
    flag = int(log[1])
    name = log[2]
    return (date, time, flag, name)

def check_weekday(date):
    """
    Checks if a given date is a weekday

    params
    ------
    date : the date to check
    """
    return date.weekday() < 5


def get_leaves(br, searchStart, searchEnd,baseURL,user):
    """
    Generate lists of start and end dates for booked leave

    params
    ------
    br : the browser
    searchStart : the first day of the leave search
    searchEnd : the last day of the leave search
    baseURL : the root url of the clock system
    user : Username to check leaves for
    """
    leaveURL = baseURL + "leave_system/LeaveSchedule.php?"
    leaveAguments = f"ss={searchStart.isoformat()[:10]}&se={searchEnd.isoformat()[:10]}&sa={user}&bt_search=+++Search+++"
    leave = BeautifulSoup(br.open(leaveURL + leaveAguments).get_data(), "html.parser")
    lines = [
        line
        for line in leave.find_all("tr")
        if line.td and str(line).lower().count("leaverequest") > 0
    ]
    starts = list()
    ends = list()
    for line in lines:
        start, end = extract_leave_data(line)
        starts.append(start)
        ends.append(end)
        
    return (starts, ends)


def extract_leave_data(line):
    """
    Extract start and end dates from a single leave request

    params
    ------
    line : parsed url for the leave request
    """
    count, name, type, length, start, end, processed = [
        child.text for child in line.children if len(child.text) > 1
    ]
    start = datetime.datetime.fromisoformat(start)
    end = datetime.datetime.fromisoformat(end)
    return (start, end)


def remove_log(br,url,comparisonDate=None,logNumber=1):
    br.open(url)
    if comparisonDate:
      pass  
    else:
        br.select_form(nr=logNumber)
        br.submit("bt_remove")