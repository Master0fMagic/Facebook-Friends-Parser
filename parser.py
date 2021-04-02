import config as cfg
import time
import sys
from getpass import getpass

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

config = None
driver = None


def is_element_exists(xpath):
    try:
        elements = WebDriverWait(driver, 2.5).until(EC.presence_of_all_elements_located((By.XPATH, xpath)))
        if len(elements) == 0:
            return False
        return True
    except TimeoutException as ex:
        return False


def fill_field( xpath, value):
    element = get_element(xpath)
    element.send_keys(value)   


def get_element(xpath):
    try:
        return  WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, xpath))
    )
    except TimeoutException as ex:
        print(ex)
        driver.quit()
        sys.exit()


def get_elements(xpath):
    try:
        return  WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, xpath))
    )
    except TimeoutException as ex:
        print(ex)
        driver.quit()
        sys.exit()


def go_to_page_without_redirecting(url):
    driver.get(url)
    return url


def go_to_page(url:str) -> str: 
    cur_url = driver.current_url
    driver.get(url)
    WebDriverWait(driver, 10).until(EC.url_changes(cur_url))
    return driver.current_url


def setup():
    global config
    global driver
    try:
        options = webdriver.ChromeOptions()
        prefs = {"profile.default_content_setting_values.notifications" : 2}
        options.add_experimental_option("prefs",prefs)
        config = cfg.Config('config.cfg')
        driver = webdriver.Chrome(options=options, executable_path=config['path_to_chromedriver'])
    except Exception as ex:
        print(ex)
        sys.exit()


def press_button(xpath):
    driver.find_element_by_xpath(xpath).click()


def login_to_facebook(login, password):
    url = go_to_page("https://www.facebook.com")
    fill_field('//form/descendant::*/input[@type="text"]', login)
    fill_field('//form/descendant::*/input[@type="password"]', password)
    press_button('//form/descendant::*/button[@type="submit"]')
    return url


def get_friends():
    elements = get_elements('//div/div[2]/div[1]/a/span/parent::*')
    friends = []
    for element in elements:
        name = element.text
        if name == '':
            continue 
        link = element.get_attribute('href')
        friends.append([name, link])
    return friends


def scroll_down():
    while not is_element_exists(r'//div[@data-pagelet="ProfileAppSection_{n}"]'):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        #time.sleep(1)


def write_friends_to_file(friends):
    try:
        file = open(config['file'], 'w', encoding='utf-8')
        file.write(f'Friends amount: {len(friends)}\n\n')
        for friend in friends:
            file.write(f'{friend[0]}: {friend[1]}\n')
        file.close()
    except Exception as ex:
        print(ex)


def input_data():
    login = input("Input login: \n")
    password = getpass("Input password: \n")
    return login, password

def main():
    login, password = input_data()
    setup() 
    url = login_to_facebook(login, password)
    url = go_to_page(url + 'profile.php')
    url = go_to_page(url + '&sk=friends')
    #time.sleep(5)
    scroll_down()
    friends = get_friends()
    write_friends_to_file(friends)
    print("Finished")
    driver.quit()


if __name__ == "__main__":
    try:
        main()
    except Exception as ex:
        print(ex)
        driver.quit()
        sys.exit()