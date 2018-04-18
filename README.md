# Readme
This python script logs in to your PureGym account and records how many people are currently in your home gym.

**Requirements:** requests, BeautifulSoup

Create a file called `.puregym_credentials` and save it in the same directory as the script. The contents should be your PureGym account and PIN in the format `[username] [PIN]` (e.g. `foo@bar.com 12345678`).

Set up a cron job to run the script periodically e.g.:

```
*/10 * * * * /path/to/puregymon.py > /dev/null
```

Headcounts are recorded in a Comma-Separated Values file (`members.csv`) in the same directory.