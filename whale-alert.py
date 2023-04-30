#鲸鱼异动报警
import time
from pprint import pprint
import pandas as pd
import numpy as np
import datetime,time
# For formatted dictionary printing>>>
from whalealert.whalealert import WhaleAlert
whale=WhaleAlert()# Specify a single transaction from the last 10 minutes>>>
import telegram
bot = telegram.Bot(token='6219784883:AAE3YXlXvxNArWJu-0qKpKlhm4KaTSHcqpw')
api_key='I38poa9dJRyy8qK8fG2KmSGicjXLjlLU'
s = 0
df = pd.DataFrame()
# transfer，mint
while True:
    time.sleep(1)
    s += 1
    print(s)
    if s%180 == 0:
        start_time=int(time.time()-180)
        success,transactions,status=whale.get_transactions(start_time,api_key=api_key,min_value = 500000)
        if success:
            print(transactions)
            if len(transactions) == 0:
                continue
            else:
                for i in range(len(transactions)):
                    data = transactions[i]
                    blockchain = data['blockchain']
                    currecy = data['symbol']
                    transaction_type = data['transaction_type']
                    if blockchain in ('bitcoin','ethereum','tron') and currecy in ('BTC','ETH','USDT','USDC') and transaction_type == 'transfer':
                        hash_value = data['hash']
                        from_address = data['from']['address']
                        from_address_owner = data['from']['owner']
                        to_address = data['to']['address']
                        to_address_owner = data['to']['owner']
                        timestamp = data['timestamp']
                        time_local = time.localtime(timestamp)
                        dt = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
                        amount = data['amount']
                        amount_usd = data['amount_usd']
                        df = pd.concat([df,pd.DataFrame({'flag':s,'blockchain':blockchain,'currecy':currecy,'hash_value':hash_value,'from_address':from_address,'from_address_owner':from_address_owner,'to_address':to_address,'to_address_owner':to_address_owner,'timestamp':dt,'amount':amount,'amount_usd':amount_usd},index=[0])])
                logo = np.max(df['flag'])
                sub_df = df[df.flag==logo]
                if len(sub_df) == 0:
                    continue
                else:
                    #sub_df = sub_df.fillna('unknow')
                    sub_df = sub_df.reset_index(drop=True)
                    print(sub_df)
                    for j in range(len(sub_df)):
                        if sub_df['from_address_owner'][j] == '' and sub_df['to_address_owner'][j] != '':
                            #向telegram进行报警
                            currecy_now = sub_df['currecy'][j]
                            if currecy_now in ('BTC','ETH'):
                                alert = '%s砸盘风险'%(currecy_now)
                                from_address_now = sub_df['from_address'][j]
                                to_address_now = sub_df['to_address'][j]
                                to_address_owner_now = sub_df['to_address_owner'][j]
                                localtime_now = str(sub_df['timestamp'][j])
                                amount_now = str(sub_df['amount'][j])
                                amount_usd_now = str(sub_df['amount_usd'][j])
                                hash_now = str(sub_df['hash_value'][j])
                                content = '\n \
                                【警报 —— %s】 \n \
                                一未知地址%s在北京时间%s向%s地址%s转入了%s个%s,目前市值为%s,警惕砸盘风险 \n \
                                具体交易哈希：%s'%(alert,from_address_now,localtime_now,to_address_owner_now,to_address_now,amount_now,currecy_now,amount_usd_now,hash_now)
                                bot.sendMessage(chat_id='-840309715', text=content)
                            else:
                                alert = '稳定币入场'
                                from_address_now = sub_df['from_address'][j]
                                to_address_now = sub_df['to_address'][j]
                                to_address_owner_now = sub_df['to_address_owner'][j]
                                localtime_now = str(sub_df['timestamp'][j])
                                amount_now = str(sub_df['amount'][j])
                                amount_usd_now = str(sub_df['amount_usd'][j])
                                hash_now = str(sub_df['hash_value'][j])
                                content = '\n \
                                【警报 —— %s】 \n \
                                一未知地址%s在北京时间%s向%s地址%s转入了%s个%s,目前市值为%s。 \n \
                                具体交易哈希：%s'%(alert,from_address_now,localtime_now,to_address_owner_now,to_address_now,amount_now,currecy_now,amount_usd_now,hash_now)
                                bot.sendMessage(chat_id='-840309715', text=content)


                        else:
                            continue
                            
    else:
        continue;