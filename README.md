# wmtscheduler-sync
One-way sync from WMT Scheduler to Google Calendar using the PDF exported from WMT Scheduler. This app does not require access to your login credentials!

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
