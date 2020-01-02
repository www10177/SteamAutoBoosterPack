from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import re
from urllib.parse import unquote
import requests
from time import sleep
import pandas as pd 
from tqdm import tqdm
from sys import argv
def load_driver():
    options = webdriver.ChromeOptions()
    options.add_extension('./extensions/Better-Buy-Orders_v1.6.2.crx')
    options.add_extension('./extensions/Augmented Steam1.3.crx')
    options.add_argument("user-data-dir=selenium")
    prefs = {"profile.managed_default_content_settings.images": 0}
    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(chrome_options=options)
    driver.get('https://steamcommunity.com')
    if len(argv) == 1 :
        input('Make sure you have login STEAM and press ENTER to continue')
    return driver

def get_price_tuple(link,driver):
    driver.get(link)
    try :
        select = Select(driver.find_element_by_id('currency_buyorder'))	
    except Exception as e :
        print(e)
        print('Cannot Get Steam Store Page, Try Again...')
        return ((-99,-99),(-99,-99))

    select = Select(driver.find_element_by_id('currency_buyorder'))
    select.select_by_value('30')
    sell_ele = driver.find_element_by_id('market_commodity_forsale')
    buy_ele = driver.find_element_by_id('market_commodity_buyrequests')
    reg = r'(\d*).*NT\$ (\d*.\d*) .*'
    try_count = 0
    while 'NT' not in sell_ele.text and 'NT' not in buy_ele.text:
    	try :
    		sleep(0.2)
    	except: 
    		try_count +=1
    	if try_count >50:
    		print('break from NT check')
    		break
    sell_re = re.search(reg,sell_ele.text)
    buy_re = re.search(reg,buy_ele.text)
    sell_group = sell_re.groups() if sell_re is not None else  (-99,-99)
    buy_group  = buy_re.groups() if buy_re is not None else (-99,-99)
    return (sell_group,buy_group)
def get_sell_vol(driver):
    sleep_time=0.5
    #Try 3 times to make sure sold_amount appear
    for i in range(1):
        try :
            div = driver.find_element_by_class_name('es_sold_amount')
            amount = div.find_element_by_css_selector('span').text
            return int(amount.replace(',',''))
        except Exception as e:
            print(e)
            sleep(sleep_time)
    return -99

def get_info(appid,driver):
    sleep_time=0.5
    return_dict = {}
    #Url Setup
    exchange_url  ='https://www.steamcardexchange.net/index.php?gamepage-appid-{appid}'

    #Requests
    req=requests.get(exchange_url.format(appid=appid))

    #Parse HTML
    card_link_list = []
    #Get All Card link list fomr steamcardexchange
    soup = BeautifulSoup(req.text,'html.parser')
    for showcase in soup.find_all('div',class_='showcase-element-container card'):
        for card in showcase.find_all('div',class_='element-button'):
            for a in card.find_all('a'):
                card_link_list.append(a.get('href'))
    #Get Game Name
    return_dict['game_name']= soup.find('div',class_='game-title').find('h1').getText()

    #Get Card Price from steam market
    price_list = []
    #print(card_link_list)

    for link in card_link_list:
        marketname = unquote(link.split('/')[-1])
        d = {'name':marketname,'link':link}
        if 'Foil' in marketname:
            d['sell_price'] = -99
            d['sell_vol'] = -99
            d['buy_price']=-99
            d['buy_vol']=-99
            d['sell_vol']=-99
        else:
            price_tuple = get_price_tuple(link,driver)
            #sleep(sleep_time)
            d['sell_vol'] = int(price_tuple[0][0])
            d['sell_price'] = float(price_tuple[0][1])
            d['buy_vol']=int(price_tuple[1][0])
            d['buy_price']=float(price_tuple[1][1])
            d['24hr_sell_vol']=get_sell_vol(driver)
        price_list.append(d)
    return_dict['price_list']=price_list
    return return_dict
def cal_avg(price_list) :
    #Input: price_list from get_price
    #Return:price_tuple(with fee,without fee) (Sum of not foil card only)
    price_list = [i for i in price_list if i['sell_price'] > 0]
    sell_price= 0.0
    for item in price_list:
        sell_price+= item['sell_price']
    l = len(price_list)
    return sell_price/l

def get_gem_price(driver):
    #Return Gem price(float)
    url = r'https://steamcommunity.com/market/listings/753/753-Sack%20of%20Gems'
    price_t = get_price_tuple(url,driver)
    return float(price_t[0][1])
def get_gem_count(length):
    # card_len : gem_count
    table = {15:400,13:462,11:545,10:600,9:667, 8:750,7:857,6:1000,5:1200}
    try : 
        return table[length]
    except Exception as e:
        print(e)
        return 100000000

def results():
    appid=request.values['appid']
    info_dict= get_info(appid,driver)
    price_list = info_dict['price_list']
    price_list = [i for i in price_list if i['sell_price'] > 0]
    game_name = info_dict['game_name']
    card_avg = tax_rate*cal_avg(price_list) ## Cal price after tax
    gem_price = get_gem_price(driver)
    gem_count = get_gem_count(len(price_list))
    return render_template('result.html',appid=appid, game_name = game_name,
        price_list = price_list, card_avg = card_avg, gem_price = gem_price,gem_count=gem_count, tax_rate = tax_rate)

if __name__ == '__main__':
    tax_rate = 0.85
    with open ('../Daily_appid.txt','r') as f :
        appid_l = [i.strip().split(' ')[0] for i in f.readlines()]
    df_allcard = pd.DataFrame(columns = ['card_name','link','24hr_sell_vol','sell_price(before tax)',
        'sell_price(after tax)','sell_amount','buy_price','buy_amount'])
    df_game = pd.DataFrame(columns = ['game_name','link','gem_price','required_gem_amount','gem_cost','avg_card_price(after_tax)',
        'avg_pack_income','avg_pack_revenue'])
    
    driver = load_driver()
    gem_price = get_gem_price(driver)
    for appid in tqdm(appid_l):
        try :
            info_dict= get_info(appid,driver)
            price_list = info_dict['price_list']
            price_list = [i for i in price_list if i['sell_price'] > 0]
            game_name = info_dict['game_name']
            game_link = 'https://www.steamcardexchange.net/index.php?gamepage-appid-%s'%appid
            card_avg = tax_rate*cal_avg(price_list) ## Cal price after tax
            gem_count = get_gem_count(len(price_list))
            for priced in price_list:
                #Each Card
                df_allcard = df_allcard.append(pd.DataFrame([{'card_name':priced['name'],
                    'link':priced['link'],'24hr_sell_vol':priced['24hr_sell_vol'],'sell_price(before tax)':priced['sell_price'],
                'sell_price(after tax)':priced['sell_price']*tax_rate,'sell_amount':priced['sell_vol'],
                'buy_price':priced['buy_price'],'buy_amount':priced['buy_vol']}]))
            game_dict = {'game_name':game_name,'link':game_link,'gem_price':gem_price,'required_gem_amount':gem_count,
            'gem_cost':gem_price*gem_count/1000,'avg_card_price(after_tax)':card_avg,
            'avg_pack_income':card_avg*3,'avg_pack_revenue':card_avg*3-gem_price*gem_count/1000}
            df_game = df_game.append(pd.DataFrame([game_dict]))
        except Exception as e:
            print(e)
            print(appid)
    writer = pd.ExcelWriter('DailyReport.xlsx', engine='xlsxwriter')
    df_game.to_excel(writer,sheet_name='Game_report',index=False)
    df_allcard.to_excel(writer,sheet_name='Card_report',index=False)
    writer.save()
    input('Already write Daily Report to dailly_report.xlsx...\nPress enter to close')

