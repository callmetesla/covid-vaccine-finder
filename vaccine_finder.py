import argparse
import logging
from collections import defaultdict
from datetime import datetime, timedelta

import pytz
import requests

from slack_helper import send_message as slack_send

logging.basicConfig(format='', level=logging.INFO)
log = logging.getLogger(__name__)

API_URL = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/calendarByDistrict"


def _form_date(date):
    return "{:02d}-{:02d}-{}".format(date.day, date.month, date.year)


def get_date():
    date = datetime.now(pytz.timezone('Asia/kolkata'))
    return date


def find_vaccine(district_codes):
    start_date = get_date()
    formatted_dates = list(map(_form_date, [start_date]))
    found_stuff = defaultdict(dict)
    for date in formatted_dates:
        log.info(f"Date: {date}")
        for district in district_codes:
            log.info(f"================= district {district} ======================")
            r = requests.get(API_URL, params={'district_id': district, 'date': date})
            if r.status_code in [200, 201, 202]:
                data = r.json()
                if 'centers' in data:
                    centers = data['centers']
                    if len(centers) == 0:
                        log.info(f"Centers not found in {district}")
                    for center in centers:
                        center_name = center['name']
                        if 'sessions' in center:
                            for session in center['sessions']:
                                if "min_age_limit" in session and session['min_age_limit'] < 45:
                                    log.debug(
                                        f"****************** 18+ {center_name} Cap {session['available_capacity']} *********************")
                                    if session['available_capacity'] > 0:
                                        date = session['date']
                                        unique_key = f"D:{district}:C:{center_name}"
                                        found_stuff[date][unique_key] = session['available_capacity']
                                        log.info(f"****************** {center_name} *********************")
                                else:
                                    pass
        if len(found_stuff) > 0:
            return found_stuff
    return found_stuff


def main(args):
    district_codes = args.district_codes.split(",")
    found_stuff = find_vaccine(district_codes)
    current_date = datetime.now(pytz.timezone('Asia/kolkata')).strftime("%d/%m/%Y, %H:%M:%S")
    log.info(f"Ran on {current_date}")
    if len(found_stuff.keys()) > 0:
        msg = []
        for date in found_stuff:
            msg.append(date)
            for name, cap in found_stuff[date].items():
                msg.extend([f"{name}:{cap}"])
        message = '\n'.join(msg)
        log.info(message)
        if args.send_message:
            slack_send(message)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Find vaccine appointments')
    parser.add_argument('--verbose', required=False, default=False, action="store_true")
    parser.add_argument('--district_codes', required=False, type=str, default="565,571")
    parser.add_argument('--send_message', required=False, default=False, action="store_true")
    parsed_args = parser.parse_args()
    if parsed_args.verbose:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)
    main(parsed_args)
