# Automatic Vaccination Availability Check for Saarland, Germany


<img src="./imgs/vaccination_homepage.jpg" height="400" />

Vaccinations appointments in [Saarland](https://en.wikipedia.org/wiki/Saarland), Germany can be scheduled [online](https://www.impfen-saarland.de/).
However, since there is no information on when new appointments will be open to the public, I built this small tool to check the current availability.

**Note** that the website is under active development (e.g. there was no `back` button during the time of development). Dialogues might change over time and thus, compatibility cannot be guarantied.

## Installation
Install necessary packages for Python3 with
```shell script
pip install -r requirements.txt
```
Also, download the [chrome driver](https://chromedriver.chromium.org/downloads) (must match your installed Chrome version) and adjust `DRIVER_PATH`.

## Usage
### General
Adjust the configuration:
- `SLEEP_TIME_BETWEEN_QUERIES_*`: configure the frequency in which the availability is checked.

Run the function
```shell script
python check_availability.py
```


## Disclaimer
This was a small and quick project, so don't except the code to be too clean ;)
I hope it helps someone and feedback is always welcome!