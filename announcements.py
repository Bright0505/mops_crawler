import requests
from bs4 import BeautifulSoup
import json
import datetime
from datetime import timedelta
from urllib.parse import urlencode
import time
import json
import env_config

datalist = []
stocks = env_config.stocks
now = datetime.date.today()
this_month_start = datetime.datetime(now.year, now.month, 1)
last_month_end = this_month_start - timedelta(days=1)
last_month_start = datetime.datetime(last_month_end.year, last_month_end.month, 1)
years = int(last_month_start.strftime("%Y")) #帶入當前年分

def announcements(stock, year):
    search_get = {"encodeURIComponent": "1",
               "step": "1",
               "firstin": "1",
               "off": "1",
               "keyword4": "",
               "code1": "",
               "TYPEK2": "",
               "checkbtn": "",
               "queryName": "co_id",
               "inpuType": "co_id",
               "TYPEK": "all",
               "co_id": str(stock),
               "year": str(year - 1911),
               "month": "",
               "b_date": "",
               "e_date": ""}
    url = "https://mops.twse.com.tw/mops/web/t05st01?"+urlencode(search_get)
    page = requests.get(url)
    page.encoding = 'utf-8'
    soup = BeautifulSoup(page.text, "html.parser")
    table = soup.find("table", class_="hasBorder").find_all("tr")[1:]
    for td in table:
        datadic = {"標題": "", "年度": "", "日期": "", "時間": "", "內容": ""}
        datadic["標題"] = td.find("font").text.replace("\xa0", "").replace("\r\n", "")
        datadic["年度"] = int(td.find_all("td")[2].text[:4]) + 1911
        datadic["日期"] = str(int(td.find_all("td")[2].text[:4]) + 1911) + td.find_all("td")[2].text[4:].replace("/","-")
        datadic["時間"] = td.find_all("td")[3].text.replace("\xa0", "")
        ts_value = str(td.find("input")).replace('<input onclick="',"").replace("document.t05st01_fm.","").replace(".value","").replace(";","&").replace("""&openWindow(this.form ,'')&" type="button" value="詳細資料"/>""","").replace("'","")
        ts_url = "https://mops.twse.com.tw/mops/web/ajax_t05st01?encodeURIComponent=1&firstin=true&step=2&"+ts_value
        ts_page = requests.get(ts_url)
        ts_page.encoding = 'utf-8'
        ts_html =  BeautifulSoup(ts_page.text, "html.parser")
        
        # 清掃 HTML 程序
        # datadic["content"] = str(ts_html.find("table",class_="hasBorder")).replace('<pre style="font-family:0�;">','').\
        #     replace('<pre style="text-align:left !important; font-family:細明體 !important;">','').\
        #     replace('\u3000第\n','第\xa0').\
        #     replace('<td class="odd" style="text-align:left !important;">\xa0','<td class="odd" style="text-align:left !important;">').\
        #     replace('<td class="odd">\xa0','<td class="odd">').\
        #     replace('主旨</td>\n<td class="odd" colspan="5" style="text-align:left !important;"><font size="3">\xa0','主旨</td>\n<td class="odd" colspan="5" style="text-align:left !important;"><font size="3">')
        #datadic["content"] = ts_html.find("table",class_="hasBorder").text
        
        datadic["內容"] = ts_html.find("table",class_="hasBorder").text
        datalist.append(datadic)

announcements(stocks,years)


def telegram_bot_sendMessage (token,message,chat_id):
    url ="https://api.telegram.org/bot"+str(token)+"/sendMessage"
    payload = {"chat_id": str(chat_id),"text": str(message),"parse_mode":"HTML"}
    headers = {"Content-Type": "application/json"}
    requests.request("POST", url, headers=headers, data=json.dumps(payload))

token = env_config.token
chat_id = env_config.chat_id
chat_id = '1037459971'
telegram_bot_form = "重大訊息擷取回報\r\n"+str(datalist).replace("[{'","\r\n").replace("', '","\r\n").replace(", '","\r\n").replace("'}, {'","\r\n\r\n").replace("': '",":").replace("': ",":").replace("'}]","") #擷取內容
telegram_bot_sendMessage(token, telegram_bot_form, chat_id)