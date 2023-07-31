from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import (InvalidSignatureError)
# 載入對應的函式庫
from linebot.models import *
import lineboterp
from database  import *

#-------------------未取列表----------------------
def ordernottaken_list():
    db_nottaken = ordertoplist()
    if db_nottaken=='找不到符合條件的資料。':
        ordernottaken_show = TextSendMessage(text='您尚未有未取資料')
    else:
        ordernottaken_show = []#發送全部
        ordernottaken_handlelist = []#處理切割db_nottaken資料10筆一組

        # 迴圈每次取出10個元素，並將這兩個元素作為一個子陣列存入結果陣列中，直到取完為止
        while len(db_nottaken) > 0:
            two_elements = db_nottaken[:10]  # 取得10個元素
            ordernottaken_handlelist.append(two_elements)  # 將10個元素作為一個子陣列加入結果陣列
            db_nottaken = db_nottaken[10:]  # 移除已取得的元素

        for totallist in ordernottaken_handlelist:
            buttons = []  # #模塊中10筆資料
            for i in range(len(totallist)):
                lumpsum = totallist[i][1]
                if lumpsum is not None:
                    lumpsum_formatted = '{:,}'.format(lumpsum)
                dtime = totallist[i][2].strftime('%Y-%m-%d %H:%M')
                button = {
                    "type": "button",
                    "action": {
                        "type": "message",
                        "label": f"[{dtime}] NT${lumpsum_formatted}",
                        "text": f"【訂單詳細】{dtime}\n{totallist[i][0]}"
                    }
                }
                buttons.append(button)

            ordernottaken_show.append({
                    "type": "bubble",
                    "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                        "type": "text",
                        "text": "高逸嚴選",
                        "weight": "bold",
                        "color": "#1DB446",
                        "size": "sm"
                        },
                        {
                        "type": "text",
                        "text": "未取訂單查詢",
                        "weight": "bold",
                        "size": "xxl",
                        "margin": "md"
                        },
                        {
                        "type": "separator",
                        "margin": "xxl"
                        },
                        {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "md",
                        "contents": buttons
                        }
                    ]
                    },
                    "styles": {
                    "footer": {
                        "separator": True
                    }
                    }
                })
        
        ordernottaken_show = FlexSendMessage(
            alt_text="未取訂單查詢",
            contents={
                "type": "carousel",
                "contents": ordernottaken_show      
                } 
            )
    return ordernottaken_show

#-------------------已取列表----------------------
def orderhastaken_list():
    db_hastaken = ordertopalllist()
    if db_hastaken=='找不到符合條件的資料。':
        orderhastaken_show = TextSendMessage(text='您尚未有完成歷史資料')
    else:
        orderhastaken_show = []#發送全部
        orderhastaken_handlelist = []#處理切割db_nottaken資料10筆一組

        # 迴圈每次取出10個元素，並將這兩個元素作為一個子陣列存入結果陣列中，直到取完為止
        while len(db_hastaken) > 0:
            two_elements = db_hastaken[:10]  # 取得10個元素
            orderhastaken_handlelist.append(two_elements)  # 將10個元素作為一個子陣列加入結果陣列
            db_hastaken = db_hastaken[10:]  # 移除已取得的元素

        for totallist in orderhastaken_handlelist:
            buttons = []  # #模塊中10筆資料
            for i in range(len(totallist)):
                lumpsum = totallist[i][1]
                if lumpsum is not None:
                    lumpsum_formatted = '{:,}'.format(lumpsum)
                dtime = totallist[i][2].strftime('%Y-%m-%d %H:%M')
                button = {
                    "type": "button",
                    "action": {
                        "type": "message",
                        "label": f"[{dtime}] NT${lumpsum_formatted}",
                        "text": f"【訂單詳細】{dtime}\n{totallist[i][0]}"
                    }
                }
                buttons.append(button)

            orderhastaken_show.append({
                    "type": "bubble",
                    "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                        "type": "text",
                        "text": "高逸嚴選",
                        "weight": "bold",
                        "color": "#1DB446",
                        "size": "sm"
                        },
                        {
                        "type": "text",
                        "text": "已完成訂單列表",
                        "weight": "bold",
                        "size": "xxl",
                        "margin": "md"
                        },
                        {
                        "type": "separator",
                        "margin": "xxl"
                        },
                        {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "md",
                        "contents": buttons
                        }
                    ]
                    },
                    "styles": {
                    "footer": {
                        "separator": True
                    }
                    }
                })
        
        orderhastaken_show = FlexSendMessage(
            alt_text="已完成訂單列表",
            contents={
                "type": "carousel",
                "contents": orderhastaken_show      
                } 
            )
    return orderhastaken_show