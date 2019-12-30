from selenium import webdriver
from selenium.webdriver.support.ui import Select
import os 
from time import sleep

def load_driver():
    options = webdriver.ChromeOptions()
    #options.add_extension('./extensions/Better-Buy-Orders_v1.6.2.crx')
    #prefs = {"profile.managed_default_content_settings.images": 2}
    #options.add_experimental_option("prefs", prefs)
    options.add_argument("user-data-dir=selenium")
    driver = webdriver.Chrome(options=options)
    driver.get('https://steamcommunity.com/tradingcards/boostercreator')
    print('='*50)
    input('Please Login in the automated Chrome, make sure you see create booster pack page\nAfter Login, press Enter to continue\nor alt+F4 to quit\n')
    print('='*50)
    return driver


def makepack(list_fn='./appid.txt'):
	sleep_time= 0.5
    driver = load_driver()
    if not os.path.isfile(list_fn):
        print ('%s is not existed'%list_fn)
        exit()
    with open (list_fn,'r') as f :
        appid_l = [i.strip().split(' ')[0] for i in f.readlines()]

    #Print Appids
    print('All APPS that would make booster pack')
    for appid in appid_l:
        print(appid)
    print('='*50)

    select = Select(driver.find_element_by_id('booster_game_selector'))
    skip_flag=False
    for appid in appid_l:
        select.select_by_value(appid)
        print (select.first_selected_option.text)
        available =  select.first_selected_option.get_attribute("class") == 'available'
        if  not available :
            print (appid, " : ", select.first_selected_option.text, ' is not available to make pack, may because of time limit\n')
            if not skip_flag:
                skip_text = input('Press Enter to Continue\nOr key in "y" in console to SKIP all confirmation\nor just alt+f4 to quit\n')
                if skip_text.strip().lower() == 'y':
                    skip_flag = True
            continue
        if not skip_flag:
            skip_text = input('Press Enter to make pack \nOr key in "y" in console to SKIP all confirmation\nor just alt+f4 to quit\n')
            if skip_text.strip().lower() == 'y':
                skip_flag = True
        radio_name = 'booster_tradability_preference_%s_%s'
        #Click Nottradable first 
        driver.find_element_by_id(radio_name%('nottradable',appid)).click()
        #If tradable make tradable card pack
        driver.find_element_by_id(radio_name%('tradable',appid)).click()
        driver.find_element_by_class_name("btn_makepack").click()
        sleep(sleep_time)
        driver.find_element_by_class_name("newmodal_buttons").find_element_by_class_name("btn_green_white_innerfade").click()
        sleep(sleep_time)
        driver.find_element_by_class_name("newmodal_close").click()
        sleep(sleep_time)
        print('='*50)

    input('Make sure every actions is done! \nThen Press enter to quit')
if __name__ == '__main__':
    makepack()
