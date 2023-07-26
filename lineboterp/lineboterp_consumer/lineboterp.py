from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

#======這裡是呼叫的檔案內容=====
from product.product_preorder import *
from product.buy_now import *
from product.check import *
from database import *
from ask_wishes.ask import *
from ask_wishes.wishes import *
from relevant_information import linebotinfo
from product.cartlist import *
from product.orderlist import *
#======python的函數庫==========
import tempfile, os
import datetime
import time
import requests

#======python的函數庫==========

app = Flask(__name__)
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')
linebotdata = linebotinfo()
# Channel Access Token
line_bot_api = LineBotApi(linebotdata['LineBotApidata'])
# Channel Secret
handler = WebhookHandler(linebotdata['WebhookHandlerdata'])


# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


#-------------------儲存使用者狀態----------------------
global user_state
user_state = {}
global member
member = {}
global product
product = {}
global list_page
list_page = {}
global product_order_preorder
product_order_preorder = {}
global duplicate_save
duplicate_save = {}
global storage
storage = {}
global orderall
orderall = {}
# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global user_id
    global msg
    msg = event.message.text
    user_id = event.source.user_id
    #-------------------檢查是否有在會員名單並且有自己的購物車----------------------
    if user_id not in member:
        member_profile(user_id)#執行會員資料確認
    #-------------------確認及給予初始使用者狀態----------------------
    if user_id not in user_state:
        user_state[user_id] = 'normal'
    #-------------------確認使用者狀態進行處理----------------------
    #使用者狀態不屬於normal，不允許進行其他動作
    if user_state[user_id] != 'normal':
        check_text = product_check()
        line_bot_api.reply_message(event.reply_token, check_text)
    else:
        #-------------------團購商品及2種商品列表----------------------
        if '團購商品' in msg:
            line_bot_api.reply_message(event.reply_token, TemplateSendMessage(
            alt_text='商品狀態選擇',
            template=ConfirmTemplate(
                    text='請選擇商品狀態：\n【預購商品】或是【現購商品】',
                    actions=[
                        MessageAction(
                            label='【預購商品】',
                            text='【預購商品】列表'
                        ),
                        MessageAction(
                            label='【現購商品】',
                            text='【現購商品】列表'
                        )
                    ]
                )
            ))
        elif '【預購商品】列表' in msg:
            list_page[user_id+'預購min'] = 0
            list_page[user_id+'預購max'] = 9
            product_show = product_preorder_list()
            line_bot_api.reply_message(event.reply_token, FlexSendMessage(
            alt_text='【預購商品】列表',
            contents={
                "type": "carousel",
                "contents": product_show      
                } 
            ))
        elif '【現購商品】列表' in msg:
            list_page[user_id+'現購min'] = 0
            list_page[user_id+'現購max'] = 9
            product_show = product_buynow_list()
            line_bot_api.reply_message(event.reply_token, FlexSendMessage(
            alt_text='【現購商品】列表',
            contents={
                "type": "carousel",
                "contents": product_show      
                } 
            ))
        #-------------------查詢、訂單、購物車----------------------
        elif '訂單/購物車查詢' in msg:
            line_bot_api.reply_message(event.reply_token, TemplateSendMessage(
            alt_text='訂單/購物車查詢選擇',
            template=ConfirmTemplate(
                    text='請選擇查詢項目：\n【訂單列表】或是【購物車】',
                    actions=[
                        MessageAction(
                            label='【訂單列表】',
                            text='訂單查詢'
                        ),
                        MessageAction(
                            label='【購物車】',
                            text='查看購物車'
                        )
                    ]
                )
            ))
        elif '訂單查詢' in msg:
            order = order_list()
            line_bot_api.reply_message(event.reply_token, FlexSendMessage(
            alt_text='訂單查詢',
            contents={
                "type": "carousel",
                "contents": order      
                } 
            ))
        elif '營業資訊' in msg:
            business_detail = business_information()
            line_bot_api.reply_message(event.reply_token, business_detail)
        elif '【加入購物車】' in msg:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='【加入購物車】'))
        elif '查看購物車' in msg:
            cart = cart_list()
            line_bot_api.reply_message(event.reply_token, FlexSendMessage(
            alt_text='我的購物車',
            contents={
                "type": "carousel",
                "contents": cart      
                } 
            ))
        elif '【送出購物車訂單】' in msg:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='送出購物車訂單'))
        elif '【修改購物車清單】' in msg:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='修改購物車清單'))
        #-------------------提問及許願----------------------
        elif '問題提問' in msg:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='問題提問'))  
        elif '許願商品' in msg:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='許願商品'))
        #-------------------執行購買或預購----------------------
        elif '【立即購買】' in msg:
            original_string = msg
            # 找到"【立即購買】"的位置
            start_index = original_string.find("【立即購買】")
            if start_index != -1:
                # 從"【現購列表下一頁】"後面開始切割字串
                substr = original_string[start_index + len("【立即購買】"):]
                # 切割取得前後文字
                product_id = substr.split("_")[0].strip() # 取出～前面的字並去除空白字元
                product_name = substr.split("_")[1].strip() # 取出～後面的字並去除空白字元
            product[user_id+'product_id'] = product_id
            product[user_id+'product'] = product_name
            Order_buynow_text = Order_buynow()
            line_bot_api.reply_message(event.reply_token, Order_buynow_text)
        elif '【手刀預購】' in msg:
            original_string = msg
            # 找到"【手刀預購】"的位置
            start_index = original_string.find("【手刀預購】")
            if start_index != -1:
                # 從"【現購列表下一頁】"後面開始切割字串
                substr = original_string[start_index + len("【手刀預購】"):]
                # 切割取得前後文字
                product_id = substr.split("_")[0].strip() # 取出～前面的字並去除空白字元
                product_name = substr.split("_")[1].strip() # 取出～後面的字並去除空白字元
            product[user_id+'product_id'] = product_id
            product[user_id+'product'] = product_name
            Order_preorder_text = Order_preorder()
            line_bot_api.reply_message(event.reply_token, Order_preorder_text)
        #-------------------現購、預購下一頁----------------------
        elif '【現購列表下一頁】' in msg:
            original_string = msg
            # 找到"【現購列表下一頁】"的位置
            start_index = original_string.find("【現購列表下一頁】")
            if start_index != -1:
                # 從"【現購列表下一頁】"後面開始切割字串
                substr = original_string[start_index + len("【現購列表下一頁】"):]
                # 切割取得前後文字
                min = int(substr.split("～")[0].strip()) # 取出～前面的字並去除空白字元
                max = int(substr.split("～")[1].strip()) # 取出～後面的字並去除空白字元
            list_page[user_id+'現購min'] = min-1
            list_page[user_id+'現購max'] = max
            buynowpage = product_buynow_list()
            if 'TextSendMessage' in buynowpage:
                line_bot_api.reply_message(event.reply_token,buynowpage)
            else:
                line_bot_api.reply_message(event.reply_token, FlexSendMessage(
                alt_text='【現購商品】列表',
                contents={
                    "type": "carousel",
                    "contents": buynowpage      
                    } 
                ))
        elif '【預購列表下一頁】' in msg:
            original_string = msg
            # 找到"【預購列表下一頁】"的位置
            start_index = original_string.find("【預購列表下一頁】")
            if start_index != -1:
                # 從"【預購列表下一頁】"後面開始切割字串
                substr = original_string[start_index + len("【預購列表下一頁】"):]
                # 切割取得前後文字
                min = int(substr.split("～")[0].strip()) # 取出～前面的字並去除空白字元
                max = int(substr.split("～")[1].strip()) # 取出～後面的字並去除空白字元
            list_page[user_id+'預購min'] = min-1
            list_page[user_id+'預購max'] = max
            preorderpage = product_preorder_list()
            if 'TextSendMessage' in preorderpage:
                line_bot_api.reply_message(event.reply_token,buynowpage)
            else:
                line_bot_api.reply_message(event.reply_token, FlexSendMessage(
                alt_text='【現購商品】列表',
                contents={
                    "type": "carousel",
                    "contents": preorderpage      
                    } 
                ))
        #-------------------資料庫連線測試----------------------
        elif '資料庫' in msg:
            databasetest_msg = databasetest()['databasetest_msg']
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='【資料庫連線測試】\n結果：%s' %(databasetest_msg)))
        elif '測試' in msg:
            datasearch = test_datasearch()
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='【資料庫測試】提取資料測試：\n%s' %(datasearch)))
        #資料庫圖片測試
        elif '圖片' in msg:
            imgsend = imagesent()
            line_bot_api.reply_message(event.reply_token, imgsend)
        #-------------------非上方功能的所有回覆----------------------
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text= '您的問題：\n「'+msg+'」\n無法立即回覆！\n已將問題發送至客服人員，請稍後！'))
        #return user_id,user_state


@handler.add(PostbackEvent)
def handle_message(event):
    print(event.postback.data)

@handler.add(MemberJoinedEvent)
def welcome(event):
    uid = event.joined.members[0].user_id
    profile = line_bot_api.get_group_member_profile(uid)
    name = profile.display_name
    message = TextSendMessage(text=f'{name}歡迎加入')
    line_bot_api.reply_message(event.reply_token, message)
    member_profile(uid)#執行會員資料確認
        
        
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
