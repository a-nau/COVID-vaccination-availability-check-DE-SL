import datetime
import random
import beepy
import time
from selenium import webdriver

DRIVER_PATH = 'C:\dev\chromedriver\chromedriver_87.exe'  # download chrome drivers and adjust path
SLEEP_TIME_BETWEEN_QUERIES_MIN = 0.8  # minutes
SLEEP_TIME_BETWEEN_QUERIES_MAX = 1.5  # minutes
DESIRED_VACCINATION_CENTERS = [0, 1, 2]  # add or remove wanted locations (0: SLS, 1: SB, 2: NK)
SLEEP_TIME_BETWEEN_CLICKS_MIN = 0.5  # seconds (Note: Increase when getting many errors)
SLEEP_TIME_BETWEEN_CLICKS_MAX = 1  # seconds
ZENTREN = ['SLS', 'SB', 'NK']


def run_continous_availability_check_and_book_date(personal_data=None):
    responses = []
    with webdriver.Chrome(executable_path=DRIVER_PATH) as wd:
        while True:
            sleep_time = 60 * (SLEEP_TIME_BETWEEN_QUERIES_MIN + random.random() * (
                    SLEEP_TIME_BETWEEN_QUERIES_MAX - SLEEP_TIME_BETWEEN_QUERIES_MIN))
            if check_availability(wd, responses):
                beepy.beep(sound='coin')
                msg = f"**NOW AVAILABLE!** ({responses[-1]})"
            else:
                msg = f"{responses[-1]}, wait {round(sleep_time)} secs"
            print(f"[{datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')}] -- {msg}")
            time.sleep(sleep_time)


def check_availability(wd, responses):
    try:  # load website and click through
        wd.get('https://www.impfen-saarland.de')
        vaccination_center = random.sample(DESIRED_VACCINATION_CENTERS, 1)[0]
        click_through_website(wd, vaccination_center)
    except Exception as e:
        responses.append(f"Error occurred reaching result site: {e}")
        return False

    try:  # check if appointments are available
        time.sleep(1.5)  # finish loading site
        result_texts = retry(wd.find_elements_by_class_name, ['heading-5'])
        if len(result_texts) == 0:
            answer = f"Could not find result text!"
            responses.append(answer)
            return False
        else:
            answer = result_texts[0].text
            if answer in ['Select vaccination center', 'Contraindications', 'To a vaccination center in Saarland']:
                responses.append(f"Error occurred reaching result site: Got stuck on {answer}")
                return False
            else:
                responses.append(f"Zentrum {ZENTREN[vaccination_center]}: {answer}")
                return not (answer == 'No appointments available')
    except Exception as e:
        responses.append(
            f"Error retrieving result for Zentrum {ZENTREN[vaccination_center]}: {e}")
        return False


'''
Page interaction
'''


def click_through_website(wd, vaccination_center):
    def click_above_80(wd):
        btn_above80 = retry(wd.find_elements_by_class_name, ['fEMWDd'])
        btn_above80[0].click()
        sleep()

    def click_not_pregnant(wd):
        # class name works better than using 3rd css_selector 'button'
        btns_pregnant = retry(wd.find_elements_by_class_name, ['iGemVH'])
        btns_pregnant[1].click()
        sleep()

    def click_vaccination_center(wd, vaccination_center):
        btns_impfzentrum = retry(wd.find_elements_by_class_name, ['fEMWDd'])
        btns_impfzentrum[vaccination_center].click()
        sleep()

    click_above_80(wd)
    click_submit(wd)
    click_not_pregnant(wd)
    click_submit(wd)
    click_vaccination_center(wd, vaccination_center)
    click_submit(wd)


def click_submit(wd):
    for submit in [
        retry(wd.find_elements_by_class_name, ['fPsgMr']),
        # retry(wd.find_elements_by_class_name, ['form-submit-button']),
    ]:
        if len(submit) > 0:
            submit[0].click()
            sleep()
            return


''' 
Utilities 
'''


def sleep():
    time.sleep(SLEEP_TIME_BETWEEN_CLICKS_MIN + random.random() * (
            SLEEP_TIME_BETWEEN_CLICKS_MAX - SLEEP_TIME_BETWEEN_CLICKS_MIN))


def retry(fct, args, max_attempts=5):
    retries = 0
    while retries < max_attempts:
        try:
            res = fct(*args)
            if isinstance(res, list):
                if len(res) > 0:
                    break
            else:
                break
        except:
            pass
        time.sleep(1.5)
        print(f"[{datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')}] -- "
              f"sleep & retry ({retries + 1}/{max_attempts}) (args: {args})")
        retries += 1
    return res


if __name__ == '__main__':
    run_continous_availability_check_and_book_date()
