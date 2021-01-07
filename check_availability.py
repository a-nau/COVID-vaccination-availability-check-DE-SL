import os
import datetime
import random
import beepy
import time
import json
from selenium import webdriver
from matrix_client.api import MatrixHttpApi

from config import DRIVER_PATH, SLEEP_TIME_BETWEEN_QUERIES_MIN, SLEEP_TIME_BETWEEN_QUERIES_MAX, \
    DESIRED_VACCINATION_CENTERS, SEND_MSG_RIOT, MATRIX_ROOM_ID, SLEEP_TIME_BETWEEN_CLICKS_MIN, \
    SLEEP_TIME_BETWEEN_CLICKS_MAX, ZENTREN


def run_continuous_availability_check_and_book_date(personal_data_file_name=None):
    if personal_data_file_name is not None:
        with open('./personal_data.json') as f:
            personal_data = json.load(f)
    else:
        personal_data = None
    if SEND_MSG_RIOT:
        token = os.getenv('RIOT_TOKEN')  # riot token can be specified as an environment variable
    responses = []
    booked = False
    with webdriver.Chrome(executable_path=DRIVER_PATH) as wd:
        while True:
            sleep_time = 60 * (SLEEP_TIME_BETWEEN_QUERIES_MIN + random.random() * (
                    SLEEP_TIME_BETWEEN_QUERIES_MAX - SLEEP_TIME_BETWEEN_QUERIES_MIN))
            if check_availability(wd, responses):
                beepy.beep(sound='coin')
                msg = f"**NOW AVAILABLE!** ({responses[-1]})"
                print(f"[{datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')}] -- {msg}")
                if SEND_MSG_RIOT:
                    send_message_riot(msg, token=token, room=MATRIX_ROOM_ID)
                try:
                    success = select_appointment(wd)
                    if success and personal_data is not None and not booked:
                        fill_out_form(wd, personal_data)
                        booked = True
                        msg += f"\n Succesfully booked appointment for {personal_data['firstname']}"
                except Exception as e:
                    msg += f"\n Failed booking appointment: {e}"
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
        answer = get_text_of_first_class_instance(wd, 'heading-5')
        if answer is None:
            answer = f"Could not find result text!"
            responses.append(answer)
            return False
        else:
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


def get_text_of_first_class_instance(wd, class_name):
    result_texts = retry(wd.find_elements_by_class_name, [class_name])
    if len(result_texts) == 0:
        return None
    else:
        answer = result_texts[0].text
        return answer


def click_through_website(wd, vaccination_center):
    def click_above_80(wd):
        btn_above80 = retry(wd.find_elements_by_class_name, ['fEMWDd'])
        btn_above80[0].click()
        sleep()

    def click_vaccination_center(wd, vaccination_center):
        btns_impfzentrum = retry(wd.find_elements_by_class_name, ['fEMWDd'])
        btns_impfzentrum[vaccination_center].click()
        sleep()

    click_above_80(wd)
    click_submit(wd)
    click_vaccination_center(wd, vaccination_center)
    click_submit(wd)


def click_submit(wd):
    submit = retry(wd.find_elements_by_class_name, ['fPsgMr'])
    if len(submit) > 0:
        submit[0].click()
        sleep()
        return


def select_appointment(wd, save_page=True):
    if save_page:  # save page to know where changes occurred
        save_html_page(wd, 'appointments')

    for element in ['iotktz', 'hqpCsy']:
        dates = retry(wd.find_elements_by_class_name, [element])
        if len(dates) > 1:
            dates[-1].click()  # choose last, because first is often taken
        else:
            dates[0].click()
        click_submit(wd)

        headline = get_text_of_first_class_instance(wd, 'heading-5')
        if headline is None:
            pass
        elif headline.lower() == 'patient data':
            return True
        elif headline.lower() == 'select vaccination appointments':
            # check if no available anymore
            error = get_text_of_first_class_instance(wd, 'error')
            if error is not None and error[:13] == 'Unfortunately':
                print(f"[{datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')}] -- Try again: {error}")
                select_appointment(wd, save_page=True)  # try to book new appointment
    # time.sleep(1200)  # sleep only if couldn't reach patient data site
    return False


def fill_out_form(wd, data, save_page=False):
    time.sleep(2.5)  # wait for page load

    if save_page:  # save page to know where changes occurred
        save_html_page(wd, 'enter_data')

    headline = get_text_of_first_class_instance(wd, 'heading-5')
    if headline is not None and headline.lower() != 'patient data':
        time.sleep(1200)  # sleep to manually interrupt
    try:
        # Enter all personal data
        for element in ['firstName', 'lastName', 'street', 'zip', 'city', 'email', 'mobile']:
            el = wd.find_element_by_name(element)
            el.send_keys(data[element.lower()])
        gender = wd.find_element_by_name('gender')
        for option in gender.find_elements_by_tag_name('option'):
            if option.text.lower() == data['gender']:
                option.click()
                break
        wd.execute_script(f"document.getElementsByTagName('input')[2].setAttribute('value', '{data['bday']}')")

        # Confirm everything
        for element in ['confirmEntitledForVaccination', 'acceptPrivacyPolicy', 'allowDataTransferToInstitution',
                        'allowNotificationViaEmailOrSMS']:
            confirm = wd.find_element_by_name(element)
            confirm.click()
    except Exception as e:
        print(f'Error during filling out form: {e}')
        return

    # Submit form
    if save_page:  # save page to know where changes occurred
        save_html_page(wd, 'final_data')
    click_submit(wd)
    time.sleep(1200)  # allow time to fill out manually if error occurred


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


def send_message_riot(message, token, room, server='https://matrix.org'):
    matrix = MatrixHttpApi(server, token=token)
    response = matrix.send_message(room, message)


def save_html_page(wd, identifier):
    if not os.path.exists('./misc'):
        os.mkdir('./misc')
    content = wd.page_source
    with open(os.path.join('./misc', f"{identifier}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"),
              "w") as f:
        f.write(content)
    wd.get_screenshot_as_file(
        os.path.join("./misc", f"{identifier}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"))


if __name__ == '__main__':
    run_continuous_availability_check_and_book_date('./personal_data.json')
