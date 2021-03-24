import requests
from bs4 import BeautifulSoup
import calendar
import json
import datetime
from datetime import timedelta

datalist = {"標題":"","年度": "" ,"月份": "", "增減百分比": "", "本月": "", "去年同期": ""}
stocks = 0000 #公司代號
now = datetime.date.today()
this_month_start = datetime.datetime(now.year, now.month, 1)
last_month_end = this_month_start - timedelta(days=1)
last_month_start = datetime.datetime(last_month_end.year, last_month_end.month, 1)
years = int(last_month_start.strftime("%Y")) #帶入當前年分
months = int(last_month_start.strftime("%m")) #帶入當前月分

def financials(stock,year,month):
    url= "https://mops.twse.com.tw/mops/web/ajax_t05st10_ifrs?encodeURIComponent=1&run=Y&co_id="+str(stock)+"&colorchg=&TYPEK=rotc&off=1&year="+str(year-1911)+"&month="+str(month).zfill(2)+"&firstin=true"
    page = requests.get(url)
    page.encoding = "utf-8"
    soup = BeautifulSoup(page.text,"html.parser")
    try:
        datalist["增減百分比"] = soup.find_all("td", style="text-align:right !important;")[4].text.replace("\xa0","").replace(" ","")
        datalist["本月"] = soup.find_all("td", style="text-align:right !important;")[1].text.replace("\xa0","").replace(" ","")
        datalist["去年同期"] = soup.find_all("td", style="text-align:right !important;")[2].text.replace("\xa0","").replace(" ","")
        datalist["標題"] = str(year)+"-"+str(month).zfill(2)
        datalist["年度"] = year
        datalist["月份"] = calendar.month_abbr[month]
    except:
        datalist["標題"] = "無資料"
        pass

financials(stocks,years,months)


def telegram_bot_sendMessage (token,message,member):
    url ="https://api.telegram.org/bot"+str(token)+"/sendMessage"
    payload = {"chat_id": str(member),"text": str(message)}
    headers = {"Content-Type": "application/json"}
    requests.request("POST", url, headers=headers, data=json.dumps(payload))

token = "XXXXXXXXXXXXXXXXXXXXXXX" #telegram bot token
member = "0000000000" # member ID
telegram_bot_form = "財報擷取回報:\r\n"+str(datalist).replace("{'","").replace("', '","\r\n").replace(", '","\r\n").replace("': '",":").replace("'}","").replace("'","")
telegram_bot_sendMessage(token,telegram_bot_form,member)
