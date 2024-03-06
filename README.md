Python code for updating your ASIAA timesheet.

# File Descriptions

config.ini : Configuration file. Includes holiday names, clock times, and account info

clock.py : Python script. The script that actually updates your time sheet

serpentime.py : Python Script. Contains all the functions used by clock.py



# Configuration

Install requirements using ```pip install -r requirements.txt```

The code automatically scrapes the internal website for holidays and vacation days, so all you need to add is your account information.
In the config.ini file find the authorization section
```
[Authorizaion]
user = user.name
password = password
```

and insert your username and password.

# Using the autoclocker

The default usage is ```python clock.py``` which will read the most recent record in your time sheet and will fill in all days between that record and the current time. The code accounts for weekends, holidays, typhoon days, and full vacation days; but not half days.

If you need to corrrect a record you can use the revert function to remove all records back to a given date with ```python clock.py -r yyy-mm-dd```. For example to delete all records back to January 1st 2024 use ```python clock.py 2024-01-01```

You can also tell the code to stop before the current date using the ```-d``` argument. For example if you only want to update your records up to Februrary 1st 2024 you use ```python clock.py -d 2024-02-01```. Combining this option with reversion is currently the only way to allow you to correct a previous record by hand.

