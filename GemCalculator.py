import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import requests
from tqdm import tqdm
def strip_price(s):
    s = s.strip()
    s = s.replace(',','')
    s= s.replace('NT$','')
    return float(s)
def get_price(list_fn='appid.txt'):
    with open (list_fn,'r') as f :
        appid_l = [i.strip().split(' ')[0] for i in f.readlines()]
    f = open('gem_count.txt','w')
    f.write('appid,card_count,gem_count\n')

    gem_count = 0
    print(appid_l)
    for appid in tqdm(appid_l):
        #Url Setup
        exchange_url  ='https://www.steamcardexchange.net/index.php?gamepage-appid-{appid}'
        ua = UserAgent()
        headers = {'User-Agent': ua.chrome}
        #Requests
        req = requests.get(exchange_url.format(appid=appid),headers=headers)
        #Parse HTML
        card_link_list = []
        #Get All Card link list fomr steamcardexchange
        soup = BeautifulSoup(req.text,'html.parser')
        for showcase in soup.find_all('div',class_='showcase-element-container card'):
            for card in showcase.find_all('div',class_='element-button'):
                for a in card.find_all('a'):
                    card_link_list.append(a.get('href'))
        card_count = len(card_link_list) /2 
        table = {15:400,13:462,11:545,10:600,9:667, 8:750,7:857,6:1000,5:1200}
        f.write(','.join([str(i) for i in [appid,card_count,table[card_count]]])+'\n')
        gem_count += table[card_count]
    print('total gem count : %d '%gem_count)
    f.write('total gem count : %d '%gem_count)
    f.close()
    input('All data save in gem_count.txt, Press Enter to close')


if __name__ =='__main__':
    get_price()
