import requests
from flask import render_template, request
from flask import Flask
import urllib.request
import json
import ssl
import time
import hashlib
site = ['', 'https://anime1.me']

from bs4 import BeautifulSoup

""" adding multiple users
import firebase_admin
from firebase_admin import credentials, firestore

#Firebase Api Fetch the service account key JSON file contents
FIREBASE_TOKEN = "Line-notify-50374a349fbb.json"
cred = credentials.Certificate(FIREBASE_TOKEN)
default_app = firebase_admin.initialize_app(cred)

# conncect to cloud firestore database
db = firestore.client()  # conncect to cloud firestore database
"""

message = ''
access_token = ''


from apscheduler.schedulers.background import BackgroundScheduler

def runprogram() :
# 檢查json檔案是否存在，若沒有則建立一個


    global access_token
    print("Already work " )
    try:
        my_file = open('sitechange.json')
    except IOError:
        data = {}
        with open('sitechange.json', 'w') as outfile:
            json.dump(data, outfile, ensure_ascii=False)

    # 開啟json檔案，讀入資料
    with open("sitechange.json") as infile:
        data = infile.read()
        local_data = json.loads(data)

    # 檢查json檔中是否有相關網址紀錄，若沒有則建立一個
    for i in range(len(site)):
        if site[i] not in local_data:
            local_data[site[i]] = ""

    # 若用戶刪除網址紀錄，則更新json檔
    temp = local_data.copy()
    for i in local_data.keys():
        if i not in site:
            temp.pop(i)

    local_data = temp

    # 讀入相關網址，並找出其雜湊值，與已儲存的雜湊值進行對比
    for i in range(len(site)):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
        req = urllib.request.Request(url=site[i], headers=headers)
        remote_data = urllib.request.urlopen(req).read()
        remote_hash = hashlib.md5(remote_data).hexdigest()
        print("check" +  site[i] )

        if remote_hash == local_data[site[i]]:
            #lineNotifyMessage(access_token, 'findding')
            print("check")

        else:
            if site[i] == 'https://anime1.me' :
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}
                res = requests.get(site[i], headers=headers)
                res.encoding = 'utf-8'
                soup = BeautifulSoup(res.text, 'lxml')

                paragraphs = []
                for x in soup.find_all("a", string=soup.find('td', {'class': 'column-1'}).text):
                    paragraphs.append(str(x))
                str1 = ''.join(paragraphs)
                url = 'https://anime1.me' + str1.split("\"", 2)[1]
                msg = soup.find('td', {'class': 'column-1'}).get_text() + "剛剛更新了 " + url
                lineNotifyMessage(access_token, msg)

            else :
                msg = site[i] + ' has been updated.'
                print(access_token)
                lineNotifyMessage(access_token, msg)

            local_data[site[i]] = remote_hash

    # 把更新的雜湊值寫回json檔
    with open('sitechange.json', 'w') as outfile:
        json.dump(local_data, outfile, ensure_ascii=False)

sched = BackgroundScheduler(daemon=True)
sched.add_job(runprogram,'interval',seconds=10)
sched.start()

app = Flask(__name__)
ssl._create_default_https_context = ssl._create_unverified_context

# 輸入想要追蹤的網址，可以增加或刪除

#pretend heroku sleep
#@app.route( '/not-stop', methods=['POST'])

@app.route('/', methods=['GET'])
def run():
  global access_token
  code = request.args.get('code')
  print(code)
  if code is None :
    return render_template('index.html')
  else :
    url = 'https://notify-bot.line.me/oauth/token' ;
    params = {'grant_type' : 'authorization_code',
              'code' : code,
              'redirect_uri':'https://website-line-notify.herokuapp.com',
              'client_id' : 'zj06EeRm09yneWM35OqLGU',
              'client_secret' : 'KL2ajPTxQo3vwGtoWOHB3jL78hhazkgmadHemrWbxjr'
    }
    r = requests.post(url, data=params)
    data = r.json()
    token = data['access_token'];
    access_token = token
    print(data)
    msg = "Success registered"
    lineNotifyMessage(token, msg)
    return render_template('success.html')

def lineNotifyMessage(access_token, msg):
    headers = {
        "Authorization": "Bearer " + access_token,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    payload = {'message': msg}
    r = requests.post("https://notify-api.line.me/api/notify", headers=headers, params=payload)
    return r.status_code


if __name__ == "__main__":
    app.run()

