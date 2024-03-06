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

