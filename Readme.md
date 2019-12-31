# SteamAutoBoosterPack
Easy automate browser to make boostercard

## Requirements  
 - Chrome 
 - Selenium webdriver that match your chrome version 
 - python3 

## How to use 
#### Installation Requirements
`pip3 install -r requirements.txt  `  
Install Chrome and put Correspond  `Chromedirver` in same folder  
#### Run Applications
- `python makepack.py` : Auto craft booster pack based on `appid.txt`
- `python GemCalculator.py` : Calculate all gem you need based on `appid.txt`
- `python DailyReport.py` : Calculate your daily profit if you craft all booster pack in `appid.txt`  

#### Appid.txt 
Key one steam appid in each line.  
You can also add game name or comments after appid, seperate by one space .
example :  
    883710 Biohazzard 2
    960170 DJMAX RESPECT V
    385800 
    333600 
