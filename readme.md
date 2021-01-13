# Automatic Vaccination Availability Check for Saarland, Germany

<p align="center">
    <img src="./imgs/vaccination_homepage.jpg" height="400" />
</p>

Vaccinations appointments in [Saarland](https://en.wikipedia.org/wiki/Saarland), Germany can be scheduled [online](https://www.impfen-saarland.de/).
However, since there is no information on when new appointments will be open to the public, I built this small tool to check the current availability.
In addition to that, also direct booking of an appointment is possible.

This script sends an automatic message with the current status to a group in [Element](https://element.io/blog/welcome-to-element/) I created and triggers a computer sound when an appointment is available.

**Note** that the website is under active development (e.g. there was no `back` button during the time of development). Dialogues might change over time and thus, compatibility cannot be guaranteed.

**UPDATE**: The system for booking vaccination appointments has [changed](https://www.rtl.de/cms/impftermine-leichter-buchen-saarland-fuehrt-impfliste-ein-4681030.html), thus booking appointments with this tool is no longer possible as of 11.01.2020.

## Installation
Install necessary packages for Python3 with
```shell script
pip install -r requirements.txt
```
Also, download the [chrome driver](https://chromedriver.chromium.org/downloads) (must match your installed Chrome version) and adjust `DRIVER_PATH`.

## Usage
### General
Adjust the configuration in [config.py](config.py):
- `DRIVER_PATH`: adjust your chrome driver path.
- `DESIRED_VACCINATION_CENTERS`: Select the vaccination centers you want to book at (0: SLS, 1: SB, 2: NK).
- `SEND_MSG_RIOT `: `boolean` whether or not messages should be send. Note that a [token](https://webapps.stackexchange.com/a/138497) is needed and `MATRIX_ROOM_ID` must be changed.
- `MATRIX_ROOM_ID `: set matrix room id, if you want to send messages via Riot/Element.
- `SLEEP_TIME_BETWEEN_QUERIES_*`: configure the frequency with which the availability is checked.
- `SLEEP_TIME_BETWEEN_CLICKS_*`: configure the frequency with which buttons are clicked.

Add personal data for booking in [personal_data.json](personal_data.json). Gender can be `female`, `male`, `diverse` or `unkown`.
If no booking should be performed, simply do not pass the path to the main method of [check_availability.py](check_availability.py).

Run the function
```shell script
python check_availability.py
```

### Using Elements to send messages
I used the [matrix-python-sdk](https://github.com/matrix-org/matrix-python-sdk), but also the [API](https://matrix.org/docs/api/client-server/#/Send45to45Device32messaging) can be used (check this [gist](https://gist.github.com/RickCogley/69f430d4418ae5498e8febab44d241c9)).
To find the room ID go the room `Settings` and select `Advanced`.


## Disclaimer
This was a small and quick project, so don't expect the code to be too clean ;)

I hope it helps someone and feedback is always welcome!