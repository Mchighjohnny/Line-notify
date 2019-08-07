
import os
import hashlib
import urllib.request
import json
import codecs
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

# 輸入想要追蹤的網址，可以增加或刪除
site = ['https://onejav.com/new']

# 檢查json檔案是否存在，若沒有則建立一個
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
    remote_data = urllib.request.urlopen(site[i]).read()
    remote_hash = hashlib.md5(remote_data).hexdigest()

    if remote_hash == local_data[site[i]]:
        print(site[i] + ' has no update')
    else:
        print(site[i] + ' is modified')
        local_data[site[i]] = remote_hash

# 把更新的雜湊值寫回json檔
with open('sitechange.json', 'w') as outfile:
    json.dump(local_data, outfile, ensure_ascii=False)


