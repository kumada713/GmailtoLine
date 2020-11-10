from datetime import datetime, timedelta, timezone


def fetch_today():
    JST = timezone(timedelta(hours=+9), "JST")
    TODAY = datetime.now(JST).date()
    return str(TODAY)


def format_string_date(string_date):
    return string_date.replace("+0000", "").replace("(UTC)", "")
