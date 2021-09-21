from flask import flash
from datetime import datetime
from dateutil import tz

def flash_form_errors(form):
    for _, errors in form.errors.items():
        for e in errors:
            flash(e)

# https://stackoverflow.com/questions/4770297/convert-utc-datetime-string-to-local-datetime 참조
def from_utc_to_local(utc_time):
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    utc_datetime_object = datetime.strptime(utc_time, '%Y-%m-%d %H:%M:%S')
    utc_datetime_object = utc_datetime_object.replace(tzinfo=from_zone)
    return utc_datetime_object.astimezone(to_zone).strftime('%Y-%m-%d %H:%M:%S')