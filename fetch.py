#!/usr/bin/env python
"""
Fetch JSON from the Georgia DPH COVID-19 daily status report[^1].
Note the website actually displays contents by the SAS institute[^2].

[^1] https://dph.georgia.gov/covid-19-daily-status-report
[^2] https://ga-covid19.ondemand.sas.com/


As of 2020-09-15, 23 JSON strings are embedded in the JavaScript code.

00 ... county geometry
01 ... datetime of the last update
02 ... sequence of positives and death counts in GA and counties
03 ... sequence of positives and death counts in GA and counties (same keys, different numbers)  ... Displayed as "COVID-19 By County" and "COVID-19 Over Time"
04 ... sequence of PCR test counts in GA and counties
05 ... county-wise summary (subset of #07)
06 ... individual death (age, race, sex, county, chronic condition)
07 ... county-wise summary
08 ... IQR (interquartile range) summary
09 ... case and death by race and ethnicity
10 ... case and death totals by race, ethnicity, sex, age group, and county
11 ... lab testing over time ... displayed as "Lab Testing"
12 ... lab testing summary
13 ... current total counts
14 ... increments in total counts
15 ... positives and hospitalizations by test date, age group, race, ethnicity, sex, county, positive patient data (35070 out of 296833 as of 2020-09-15)
16 ... sequence of positives and death by age group
17 ... sequence of positives, death, and hospitalization by ethnicity, race, and sex
18 ... current totals by ethnicity, race, and sex
19 ... current totals by comorbidity and sex
20 ... current totals by ethnicity, race, sex, and comorbidity
21 ... current case count by binary comorbidity (Yes/No/Unknown)
22 ... current test counts (pcr and antibody)
23 ... lab testing summary (added since 2020-09-22)
"""

import urllib.request
import re
import pathlib

URL = "https://ga-covid19.ondemand.sas.com/static/js/main.js"
PATTERN = re.compile(r"JSON.parse\('(.*?)'\)")

FILENAME = [
    "geometry_county",
    "last_updated",
    "cases_county_over_time0",
    "cases_county_over_time",
    "tests_over_time",
    "summary_county0",
    "deaths",
    "summary_county",
    "iqr",
    "cases_by_race_ethnicity",
    "cases_totals",
    "lab_testing",
    "lab_testing_totals",
    "current_status",
    "current_status_changes",
    "positive_cases",
    "demographics",
    "comorbidities",
    "comorbidities_by_sex",
    "comorbidities_by_race_and_sex",
    "cases_tally",
    "comorbidity_total",
    "current_status_tests",
    "lab_testing_summary",
]

SAVE_DIR = "artifacts"


def extract_json(text: str):
    """Extract <something> from JSON.parse(<something>) in text
    and return them as a generator."""
    matches = PATTERN.finditer(text)
    for match in matches:
        yield match.group(1)


def run(url=URL, prefix=""):
    path_root = pathlib.Path(SAVE_DIR)
    path_root.mkdir(exist_ok=True)

    with urllib.request.urlopen(url) as response:
        js_text = response.read().decode("utf-8")
        gen = extract_json(js_text)
        for i, s in enumerate(gen):
            name = FILENAME[i] if i < len(FILENAME) else f"{i:02d}"
            path = path_root / f"{prefix}{name}.json"
            with open(path, "w") as f:
                print(s, file=f)


if __name__ == "__main__":
    run()
