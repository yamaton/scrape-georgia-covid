#!/usr/bin/env python
"""
Fetch JSON from the Georgia DPH COVID-19 daily status report[^1].
Note the website actually displays contents from the SAS institute (sas.com)[^2].

[^1] https://dph.georgia.gov/covid-19-daily-status-report
[^2] https://ga-covid19.ondemand.sas.com/


As of 2020-10-10, 18 JSON strings are embedded in the JavaScript code.

00 ... timestamp of the last update
01 ... history of cases and deaths in GA counties
02 ... total counts in GA and counties
03 ... individual death (age, race, sex, county, chronic condition)
04 ... case and death by race and ethnicity
05 ... case and death totals by race, ethnicity, sex, age group, and county
06 ... lab testing over time ... displayed as "Lab Testing"
07 ... lab testing summary
08 ... current total counts (total_tests, confirmed_covid, icu, hospitalization, death)
09 ... current changes (diff in positives, hospitalizations, deaths, tests, total_tests, confirmed_covid, icu, hospitalization, death)
10 ... history of cases, deaths, hospitalization by age group, race, ethnicity, sex
11 ... history of cases and deaths by age group
12 ... history of cases and deaths by ethnicity, race, and sex
13 ... case and death counts by race, ethnicity, sex, and county
14 ... count by comorbidity and sex
15 ... count by ethnicity, race, sex, and comorbidity
16 ... count by ternary comorbidity (Yes/No/Unknown)
17 ... test counts (tot, pcrtest, abtest, pcrpos, abpos)

"""

import urllib.request
import urllib.parse
import re
import pathlib
from html.parser import HTMLParser
from html.entities import name2codepoint

BASE_URL = "https://ga-covid19.ondemand.sas.com/"
PATTERN = re.compile(r"JSON.parse\('(.*?)'\)")

FILENAME = [
    "timestamp",
    "county_history",
    "county_totals",
    "individual_death",
    "race_ethnicity",
    "lab_testing_history",
    "lab_testing_totals",
    "lab_testing_summary",
    "current_status",
    "current_status_changes",
    "demographics_history",
    "age_history",
    "ethnicity_history",
    "ethnicity_totals",
    "comorbidities_totals",
    "comorbidities_ethnicy_totals",
    "comorbidity_summary",
    "testing_summary",
]

SAVE_DIR = "artifacts"


class MyHTMLParser(HTMLParser):
    """HTML parser that stores <script> tag,
    src attribute, as self.url
    """
    def handle_starttag(self, tag, attrs):
        if tag.lower() == "script":
            for attr in attrs:
                if attr[0].lower() == "src":
                    rel = attr[1].lower()
                    if "main" in rel:
                        self.url = urllib.parse.urljoin(BASE_URL, rel)


def extract_json(text: str):
    """Extract <something> from JSON.parse(<something>) in text
    and return them as a generator."""
    matches = PATTERN.finditer(text)
    for match in matches:
        yield match.group(1)


def extract_js_url(text: str):
    """Extract main.js url
    """
    parser = MyHTMLParser()
    parser.feed(text)
    return parser.url


def run(url=BASE_URL, prefix=""):
    path_root = pathlib.Path(SAVE_DIR)
    path_root.mkdir(exist_ok=True)

    with urllib.request.urlopen(url) as response:
        html = response.read().decode("utf-8")
        url_js = extract_js_url(html)

    with urllib.request.urlopen(url_js) as response:
        js_text = response.read().decode("utf-8")
        gen = extract_json(js_text)
        for i, s in enumerate(gen):
            name = FILENAME[i] if i < len(FILENAME) else f"{i:02d}"
            path = path_root / f"{prefix}{name}.json"
            with open(path, "w") as f:
                print(s, file=f)


if __name__ == "__main__":
    run()
