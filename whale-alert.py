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
from telegram import ParseMode
bot = telegram.Bot(token='6361430672:AAG2qr7zuFQkcQb13Xtud2q8KksonuTNVN4')
api_key='I38poa9dJRyy8qK8fG2KmSGicjXLjlLU'
s = 0
df = pd.DataFrame()
# transfer，mint
while True:
    time.sleep(1)
    s += 1
    print(s)
    if s%180 == 0:
        hash_data = pd.read_csv('/root/whale-alert/hash_data.csv')
        hash_list = list(hash_data['hash'])
        #print(hash_list)
        start_time=int(time.time()-600)
        success,transactions,status=whale.get_transactions(start_time,api_key=api_key,min_value = 5000000)
        if success:
            #print(transactions)
            if len(transactions) == 0:
                continue
            else:
                for i in range(len(transactions)):
                    data = transactions[i]
                    blockchain = data['blockchain']
                    currecy = data['symbol']
                    transaction_type = data['transaction_type']
                    if blockchain in ('bitcoin','ethereum','tron') and currecy in ('BTC','USDT','USDC') and transaction_type == 'transfer':
                        hash_value = data['hash']
                        from_address = data['from']['address']
                        from_address_owner = data['from']['owner']
                        to_address = data['to']['address']
                        to_address_owner = data['to']['owner']
                        to_address_owner_type = data['to']['owner_type']
                        timestamp = data['timestamp']
                        time_local = time.localtime(timestamp)
                        dt = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
                        amount = data['amount']
                        amount_usd = data['amount_usd']
                        df = pd.concat([df,pd.DataFrame({'flag':s,'blockchain':blockchain,'currecy':currecy,'hash_value':hash_value,'from_address':from_address,'from_address_owner':from_address_owner,'to_address':to_address,'to_address_owner':to_address_owner,'to_address_owner_type':to_address_owner_type,'timestamp':dt,'amount':amount,'amount_usd':amount_usd},index=[0])])
                if len(df) == 0:
                    continue
                else:
                    logo = np.max(df['flag'])
                    sub_df = df[df.flag==logo]
                    sub_df = sub_df.reset_index(drop=True)
                    print(sub_df)
                    if len(sub_df) == 0:
                        continue
                    else:
                        sub_hash = []
                        for j in range(len(sub_df)):
                            if sub_df['from_address_owner'][j] == '' and sub_df['to_address_owner'][j] != '' and sub_df['to_address_owner_type'][j] == 'exchange':
                                #向telegram进行报警
                                blockchain = sub_df['blockchain'][j]
                                currecy_now = sub_df['currecy'][j]
                                if currecy_now in ('BTC'):
                                    alert = '%s砸盘风险'%(currecy_now)
                                    from_address_now = sub_df['from_address'][j]
                                    to_address_now = sub_df['to_address'][j]
                                    to_address_owner_now = sub_df['to_address_owner'][j]
                                    localtime_now = str(sub_df['timestamp'][j])
                                    amount_now = str(round(sub_df['amount'][j],2))
                                    amount_usd_now = str(round(sub_df['amount_usd'][j]/10000,1))
                                    hash_v = sub_df['hash_value'][j]
                                    if hash_v in hash_list:
                                        continue 
                                    else:
                                        sub_hash.append(hash_v)
                                        hash_now = str(sub_df['hash_value'][j])
                                        msg_url = 'https://www.oklink.com/cn/btc/tx/' + hash_now
                                        content_2 =  "<a href='%s'>点击链接查看转账详情</a>"%(msg_url)
                                        content_1 = '\n \
                                        【警报 — %s】 \n \
%s链上地址%s在北京时间%s向%s交易所地址%s转入了%s万个%s,目前市值为%s万美元,警惕砸盘风险。'%(alert,blockchain,from_address_now,localtime_now,to_address_owner_now,to_address_now,amount_now,currecy_now,amount_usd_now)
                                        #推送tele
                                        bot.sendMessage(chat_id='-1001920263299', text=content_1,message_thread_id=2)
                                        #bot.sendMessage(chat_id='-1001920263299', text=content_2, parse_mode = ParseMode.HTML,message_thread_id=2)
                                else:
                                    alert = '稳定币入场'
                                    from_address_now = sub_df['from_address'][j]
                                    to_address_now = sub_df['to_address'][j]
                                    to_address_owner_now = sub_df['to_address_owner'][j]
                                    localtime_now = str(sub_df['timestamp'][j])
                                    amount_now = str(round(sub_df['amount'][j]/10000,1))
                                    amount_usd_now = str(round(sub_df['amount_usd'][j]/10000,1))
                                    hash_v = sub_df['hash_value'][j]
                                    if hash_v in hash_list:
                                        continue 
                                    else:
                                        sub_hash.append(hash_v)
                                        hash_now = str(sub_df['hash_value'][j])
                                        if blockchain == 'ethereum':
                                            msg_url = 'https://www.oklink.com/cn/eth/tx/' + hash_now
                                        else:
                                            msg_url = 'https://www.oklink.com/cn/trx/tx/' + hash_now

                                        content_2 =  "<a href='%s'>点击链接查看转账详情</a>"%(msg_url)
                                        content_1 = '\n \
                                        【警报 — %s】 \n \
%s链上地址%s在北京时间%s向%s交易所地址%s转入了%s万个%s,目前市值为%s万美元。'%(alert,blockchain,from_address_now,localtime_now,to_address_owner_now,to_address_now,amount_now,currecy_now,amount_usd_now)
                                        #推送tele
                                        bot.sendMessage(chat_id='-1001920263299', text=content_1,message_thread_id=2)
                                        #bot.sendMessage(chat_id='-1001920263299', text=content_2, parse_mode = ParseMode.HTML,message_thread_id=2)
                            else:
                                continue
                        #print(sub_hash)        
                        if len(sub_hash) > 0:
                            sub_hash_df = pd.DataFrame({'hash':sub_hash})
                            hash_data = pd.concat([hash_data,sub_hash_df])
                            #print(hash_data)
                            hash_data.to_csv('/root/whale-alert/hash_data.csv',index=False)
                                
                            
    else:
        continue;