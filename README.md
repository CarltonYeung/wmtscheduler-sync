# wmtscheduler-sync
One-way sync from WMT Scheduler to Google Calendar using the PDF you export from WMT Scheduler.

## How it works
This app does NOT ask you for your login credentials and does NOT connect to WMT Scheduler. It simply reads the PDF you export from WMT Scheduler and makes your Google Calendar look exactly like the schedule in the PDF. That's it.

> ❕ The script is idempotent, so you can run it as many times as you like and it won't add duplicate events; although if you manually edit an event on your Calendar and re-run the script, it WILL override your edits.

> ❕ The Google Calendar events are created with NO notifications enabled, 30-minute early flex, and 8-hour shifts.

## Quickstart

![Screenshot 2023-06-12 180818](https://github.com/CarltonYeung/wmtscheduler-sync/assets/19213290/f2a42162-60ff-4676-8880-aed910afb291)


## Step-by-step

1. Learn to code
2. Log in to [WMT Scheduler](https://wmtscheduler.faa.gov/gatekeeper)
3. Go to `Views` > `My Schedule`
4. Click `Print` and `Save as PDF`
5. In bash, run
```
$ poetry install
$ poetry run python3.10 sync.py
```
6. Modify the newly generated `settings.ini` file
7. A webpage will open where Google will ask you to click `Continue` to give this app permission to modify your Google Calendar
