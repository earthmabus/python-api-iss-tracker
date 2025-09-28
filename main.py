import datetime

import requests
import datetime as dt
import time

from email_account import EmailAccount

MY_EMAIL = "earthmabus@gmail.com"
PASSWORD_FILE = "./password.txt"
POLL_TIME_IN_SECONDS = 60

def load_password():
    '''loads the password for the email account from PASSWORD_FILE'''
    retval = ""
    with open(PASSWORD_FILE, "r") as file_password:
        retval = file_password.readline().strip()
    return retval

def is_iss_viewable(iss_lat, iss_long, my_lat, my_long, sunrise_hour, sunset_hour, current_hour):
    '''returns true if the ISS is viewable overhead -- must be dark and within +/- 5 degrees of my location'''
    in_view_range = abs(iss_lat - my_lat) <= 5 and abs(iss_long - my_long) <= 5
    is_dark_outside = sunset_hour < current_hour < sunrise_hour
    if in_view_range and not is_dark_outside:
        print("ISS is above, but it's not dark outside")
    return in_view_range and is_dark_outside

# my current location
LAT_ORLANDO = 28.538336
LONG_ORLANDO = -81.379234

# if it's dark outside and the iss is near my current position, then send email to notify me to look up to see it
password = load_password()
account = EmailAccount(MY_EMAIL, password)
while True:
    # get the current time
    time_now = dt.datetime.now()
    time_now_hour = time_now.hour
    print(f"{time_now}: checking if ISS is above...")

    try:
        # get the current location of the ISS
        response_iss_loc = requests.get(url="http://api.open-notify.org/iss-now.json")
        response_iss_loc.raise_for_status()
        iss_lat = float(response_iss_loc.json()['iss_position']['latitude'])
        iss_long = float(response_iss_loc.json()['iss_position']['longitude'])

        # get the sunrise/sunset for my location
        parameters = {"lat": LAT_ORLANDO, "lng": LONG_ORLANDO, "formatted": 0}
        response_sunrise = requests.get("https://api.sunrise-sunset.org/json", params=parameters)
        response_sunrise.raise_for_status()
        sunrise_sunset_data = response_sunrise.json()
        time_sunrise_hour = int(sunrise_sunset_data['results']['sunrise'].split("T")[1].split(":")[0])
        time_sunset_hour = int(sunrise_sunset_data['results']['sunset'].split("T")[1].split(":")[0])

        # if the ISS is above and it is dark outside, send email
        if is_iss_viewable(iss_lat, iss_long, LAT_ORLANDO, LONG_ORLANDO, time_sunset_hour, time_sunset_hour, time_now_hour):
            message = "The ISS is viewable right now!\n"
            message += f"- Your location ({LAT_ORLANDO}, {LONG_ORLANDO})\n"
            message += f"- ISS location ({iss_lat}, {iss_long})\n"
            message += f"- sunset ({time_sunset_hour}) < current hour ({time_now_hour}) < sunrise ({time_sunrise_hour})\n"
            print(f"{time_now}: sending email\n{message}")
            account.send_email("earthmabus@hotmail.com", "The ISS is above you!", message)
    except requests.exceptions.ConnectTimeout:
        print(requests.exceptions.ConnectTimeout)
    except Exception:
        print(Exception)

    # sleep until the next time to check for the ISS
    time.sleep(POLL_TIME_IN_SECONDS)
