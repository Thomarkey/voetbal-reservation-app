import csv
from datetime import datetime, timedelta, time

import requests
from dateutil import tz

FIELD_NAME = "voetbalveld 6 (1/2"
LOCATION_ID = 96
SPORT_ID = 1053
START_HOUR = 19
DAYS_AHEAD = 30


def get_timestamp(dt):
    return int(dt.timestamp() * 1000)


def check_availability():
    results = []
    for day_offset in range(DAYS_AHEAD):
        date = datetime.now() + timedelta(days=day_offset)
        if date.weekday() in (5, 6):  # 5 = Saturday, 6 = Sunday
            continue
        day_start = datetime.combine(date.date(), time(0, 0)).astimezone(tz.tzlocal())
        day_end = datetime.combine(date.date(), time(23, 59)).astimezone(tz.tzlocal())
        t_ts = get_timestamp(datetime.now())
        from_ts = get_timestamp(day_start)
        until_ts = get_timestamp(day_end)
        url = f"https://www.antwerpen.be/srv/sportinfrastructuur/reservations/availability/locations/{LOCATION_ID}/sports/{SPORT_ID}?t={t_ts}&from={from_ts}&until={until_ts}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            fields = data.get("data", [])
            matching_fields = [f for f in fields if FIELD_NAME.lower() in f["fieldName"].lower()]
            for field in matching_fields:
                for slot in field["slots"]:
                    slot_from = datetime.fromtimestamp(slot["from"] / 1000).astimezone(tz.tzlocal())
                    slot_until = datetime.fromtimestamp(slot["until"] / 1000).astimezone(tz.tzlocal())
                    if slot_from.hour >= START_HOUR and slot["available"]:
                        results.append([
                            date.strftime('%A'),
                            date.strftime('%d-%m-%Y'),
                            field['fieldName'],
                            slot_from.strftime("%H:%M"),
                            slot_until.strftime("%H:%M")
                        ])
        except Exception as e:
            pass  # Optionally log errors

    with open('resultaat.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Weekdag', 'Datum', 'Veldnaam', 'Starttijd', 'Eindtijd'])
        writer.writerows(results)


def main():
    check_availability()


if __name__ == "__main__":
    main()
