# Readme

This python script logs in to your PureGym account and records:
* your activity; and
* how many people are currently in your home gym

**Requirements:** Python 3, requests, BeautifulSoup4.

Create a file called `.puregym_credentials` and save it in the same directory as the script. The contents should be your PureGym account and PIN in the format `[username] [PIN]` (for example: `foo@bar.com 12345678`).

Set up a cron job to run the script periodically, for example:

```bash
*/10 * * * * /path/to/puregymon.py
```

Activity is recorded in a [CSV](https://en.m.wikipedia.org/wiki/Comma-separated_values "Comma-Separated Values") file named `activity.csv` in the same directory.

Headcounts are recorded in a [CSV](https://en.m.wikipedia.org/wiki/Comma-separated_values "Comma-Separated Values") file named `headcount.csv` in the same directory.

Note that when headcount drops below a certain value (currently 20), PureGym reports "fewer than 20 people" rather than the precise number. In this case, 20 will be recorded.