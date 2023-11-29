from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import (InvalidSignatureError)
# 載入對應的函式庫
from linebot.models import *
import manager
from database import *
import database,FM
from FM import products_manufacturers_FM,Now_Product_Modification_FM,Pre_Product_Modification_FM,create_now_purchase_product

#-------------------使用者狀態檢查----------------------
message_storage = {}
def inventory_check():
    id = manager.user_id
    state = manager.user_state
    if state[id] in 'adding': #判斷user狀態
        check_text = add_goods()
    if 'Product_Modification' in state[id]:#商品修改
        check_text = product_modification()
    '''if state[id] in 'searching_single': #判斷user狀態
        check_text = search_inf()'''
    '''if state[id] in 'searching_all': #判斷user狀態
        check_text = search_allinf()
    if state[id] in 'end': #判斷user狀態
        check_text = end_stop()'''
    if 'createNowProduct' in state[id]:
        check_text= createNowProduct()
    if state[id] in 'searchingOrderByPhoneNumber':
        check_text = searchingOrderByPhoneNumber()
    if state[id] in 'createPreOrder':
        check_text = createPreOrder()
    return check_text

#-------------------新增商品狀態檢查----------------------
def add_goods():
     # 若使用者已經在等待回覆狀態，則根據回覆進行處理
    id = manager.user_id
    state = manager.user_state
    state1 = manager.user_state1
    message = manager.msg
    product = manager.product
    
    if state1[id] == 'name':
        message_storage[id+'pname'] = '品名：'+ message
        product[id] = message
        check_text = ('您輸入的品名： %s' %(message))
        check_text += '\n=>請接著輸入「進貨數量」'
        check_text = TextSendMessage(text=check_text)
        state1[id] = 'one'
    elif state1[id] == 'one':
        message_storage[id+'num'] = '進貨數量：' + message
        check_text = ('%s\n進貨數量： %s' %(message_storage[id+'pname'],message_storage[id+'num']))
        check_text += '\n=>請接著輸入「進貨成本」'
        check_text = TextSendMessage(text=check_text)
        state1[id] = 'two'
    elif state1[id] == 'two':
        message_storage[id+'cost'] = '進貨成本：' + message
        check_text = ('%s\n%s\n進貨成本：%s' %(message_storage[id+'pname'],message_storage[id+'num'],message_storage[id+'cost']))
        check_text += '\n=>請接著輸入「廠商名」'
        check_text = TextSendMessage(text=check_text)
        state1[id] = 'three'
    elif state1[id] == 'three':
        message_storage[id+'fname'] = '廠商名：' + message
        check_text = ('%s\n%s\n%s\n進貨成本： %s' %(message_storage[id+'pname'],message_storage[id+'num'],message_storage[id+'cost'],message_storage[id+'fname']))
        check_text += '\n=>請接著輸入「商品有效期限」\nex:2023/07/24'
        check_text = TextSendMessage(text=check_text)
        state1[id] = 'four'
    elif state1[id] == 'four':
        message_storage[id+'exp'] = '商品有效期限：' + message
        check_text = ('%s\n%s\n%s\n%s\n%s\n請輸入確認' %(message_storage[id+'pname'],message_storage[id+'num'],message_storage[id+'cost'],message_storage[id+'fname'],message_storage[id+'exp']))
        check_text = TextSendMessage(text=check_text)
        state1[id] = 'end'
    elif state1[id] == 'end':
        state[id] = 'normal'
        state1[id] = 'NaN'
        check_text = ('您的商品：%s\n已新增成功！' %(product[id]))
        check_text = TextSendMessage(text=check_text)
    return check_text

#-------------------廠商商品資訊修改-----------------------
def product_modification():
    id = manager.user_id
    state = manager.user_state
    message = manager.msg
    product = manager.product
    manufacturer_id = product[id + 'Product_Modification_manufacturer_id'] 
    product_status = product[id + 'Product_Modification_Product_status']#現預購狀態
    product_id = product[id + 'Product_Modification_Product_id']
    if state[id] == 'Product_Modification_Product':
        info = message[8:]
        if '商品名稱' == info:
            state[id] == 'Product_Modification_Product_Pname'
            flex_message = TextSendMessage(text='修改商品名稱')
        elif '商品簡介' == info:
            #state[id] == 'Product_Modification_Product_Pintroduction'
            flex_message = TextSendMessage(text='修改商品簡介')
        elif '商品售出單價' == info:
            flex_message = TextSendMessage(text='修改商品售出單價')
    
    elif state[id] == 'Product_Modification_Product_Pname':#修改商品名稱
        if message != '取消':
            result = MP_information(message)#接收使用者打的內容
            if result == 'ok':
                if product_status == '現購':
                    flex_message = Now_Product_Modification_FM(product_id)
                elif product_status == '預購':
                    flex_message = Pre_Product_Modification_FM(product_id)
                elif product_status == '查無':
                    flex_message = TextSendMessage(text='商品有誤！')
            else:
                flex_message = TextSendMessage(text=f"修改失敗請稍後再試")
            state[id] = 'normal'#恢復使用者狀態
        else:
            state[id] = 'normal'#恢復使用者狀態
    elif state[id] == 'Product_Modification_Pintroduction':
        flex_message = ''
    else:#取消修改動作
        state[id] = 'normal'#恢復使用者狀態
    return flex_message 

'''def search_inf():
    id = manager.user_id
    state = manager.user_state
    state2 = manager.user_state1
    message = manager.msg
    product = manager.product[id+'product']
    if state[id] == 'searching_oneinf':
            if state2[id] == 'name':
                message_storage[id+'pname'] = '品名：'+ message
                check_text = ('您輸入的品名： %s' %(message))
                check_text += '\n=>請接著輸入「進貨數量」'
                check_text = TextSendMessage(text=check_text)
                state1[id] = 'checking_one'

    return check_text
     
def search_allinf():
     return check_text

def end_stop():
     return check_text'''
def createNowProduct():
    id = manager.user_id
    state = manager.user_state
    state1 = manager.user_state1
    message = manager.msg
    global_Storage = manager.global_Storage
    options = ['frozen', 'dailyuse', 'dessert', 'local', 'staplefood', 'generally', 'beauty', 'snack', 'healthy', 'drinks','test']
    units=['個','包','盒','桶','公克','公斤','組','箱','帶']
    returnoptions = ['可退','可換','退換','空白']
    if state1[id] == 'first':
        if len(message) > 50:
            check_text = ('您輸入的品名超過50字，請重新輸入')
            check_text = TextSendMessage(text=check_text)
            return check_text
        global_Storage[id+'pname'] = '品名：'+ message
        check_text = ('您輸入的品名： %s' %(message))
        check_text += '\n=>請接著輸入「商品類別」'
        
        actions=[]
        for option in options:
           actions.append(QuickReplyButton(action=MessageAction(label=option, text=option)))
        check_text=TextSendMessage(text=check_text, quick_reply=QuickReply(items=actions))
        state1[id] = 'one'
    elif state1[id] == 'one':
        if message not in options:
            check_text = ('您輸入的類別錯誤，請重新輸入')
            actions=[]
            for option in options:
                actions.append(QuickReplyButton(action=MessageAction(label=option, text=option)))
            check_text=TextSendMessage(text=check_text, quick_reply=QuickReply(items=actions))
            return check_text
        global_Storage[id+'category'] = '商品類別:' + message
        check_text = ('%s\n %s' %(global_Storage[id+'pname'],global_Storage[id+'category']))
        check_text += '\n=>請接著選擇「商品單位'
        actions=[]
        for option in units:
           actions.append(QuickReplyButton(action=MessageAction(label=option, text=option)))
        check_text=TextSendMessage(text=check_text, quick_reply=QuickReply(items=actions))
        state1[id] = 'two'
    elif state1[id] == 'two':
        if message not in units :
            check_text = ('您輸入的單位錯誤，請重新輸入')
            actions=[]
            for option in units:
                actions.append(QuickReplyButton(action=MessageAction(label=option, text=option)))
            check_text=TextSendMessage(text=check_text, quick_reply=QuickReply(items=actions))
            return check_text
        global_Storage[id+'unit'] = '商品單位：' + message
        check_text = ('%s\n%s\n%s' %(global_Storage[id+'pname'],global_Storage[id+'category'],global_Storage[id+'unit']))
        check_text += '\n=>請接著輸入「商品簡介」(小於150字)'
        check_text = TextSendMessage(text=check_text)
        state1[id] = 'three'
    elif state1[id] == 'three':
        if len(message) > 150:
            check_text = ('您輸入的商品簡介超過50字，請重新輸入')
            check_text = TextSendMessage(text=check_text)
            return check_text
        global_Storage[id+'introduction'] = '商品簡介：' + message
        check_text = ('%s\n%s\n%s\n %s' %(global_Storage[id+'pname'],global_Storage[id+'category'],global_Storage[id+'unit'],global_Storage[id+'introduction']))
        check_text += '\n=>請接著輸入「商品售出單價」'
        check_text = TextSendMessage(text=check_text)
        state1[id] = 'four'
    elif state1[id] == 'four':
        if not message.isdigit():
            check_text = ('您輸入的商品售出單價不是數字，請重新輸入')
            check_text = TextSendMessage(text=check_text)
            return check_text
        global_Storage[id+'unitPrice'] = '商品售出單價：' + message
        check_text = ('%s\n%s\n%s\n%s\n%s' %(global_Storage[id+'pname'],global_Storage[id+'category'],global_Storage[id+'unit'],global_Storage[id+'introduction'],global_Storage[id+'unitPrice']))
        check_text += '\n=>請接著輸入「商品售出單價2」'
        check_text = TextSendMessage(text=check_text)
        state1[id] = 'five'
    elif state1[id] == 'five':
        if not message.isdigit():
            check_text = ('您輸入的商品售出單價2不是數字，請重新輸入')
            check_text = TextSendMessage(text=check_text)
            return check_text        
        global_Storage[id+'unitPrice2'] = '商品售出單價2：' + message
        check_text = ('%s\n%s\n%s\n%s\n%s\n %s' %(global_Storage[id+'pname'],global_Storage[id+'category'],global_Storage[id+'unit'],global_Storage[id+'introduction'],global_Storage[id+'unitPrice'],global_Storage[id+'unitPrice2']))
        check_text += '\n=>請接著輸入「商品圖片」'
        check_text = TextSendMessage(text=check_text)
        state1[id] = 'six'
    elif state1[id] == 'six':
        global_Storage[id+'picture'] = '商品圖片：' + message
        check_text = ('%s\n%s\n%s\n%s\n%s\n%s\n%s' %(global_Storage[id+'pname'],global_Storage[id+'category'],global_Storage[id+'unit'],global_Storage[id+'introduction'],global_Storage[id+'unitPrice'],global_Storage[id+'unitPrice2'],global_Storage[id+'picture']))
        check_text += '\n=>請接著選擇「可否退換貨」'
        actions=[]
        for option in returnoptions:
           actions.append(QuickReplyButton(action=MessageAction(label=option, text=option)))
        check_text=TextSendMessage(text=check_text, quick_reply=QuickReply(items=actions))
        state1[id] = 'seven'
    elif state1[id] == 'seven':
        if message not in returnoptions:
            check_text = ('您輸入的可否退換貨錯誤，請重新輸入')
            actions=[]
            for option in returnoptions:
                actions.append(QuickReplyButton(action=MessageAction(label=option, text=option)))
            check_text=TextSendMessage(text=check_text, quick_reply=QuickReply(items=actions))
            return check_text
        global_Storage[id+'returnProduct'] = '可否退換貨：' + message
        check_text = ('%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s' %(global_Storage[id+'pname'],global_Storage[id+'category'],global_Storage[id+'unit'],global_Storage[id+'introduction'],global_Storage[id+'unitPrice'],global_Storage[id+'unitPrice2'],global_Storage[id+'picture'],global_Storage[id+'returnProduct']))
        state1[id] = 'ShowFM'
    elif state1[id] == 'changePname':
        if len(message) > 50:
            check_text = ('您輸入的品名超過50字，請重新輸入')
            check_text = TextSendMessage(text=check_text)
            return check_text
        state1[id] = 'ShowFM' 
        global_Storage[id+'pname'] ='品名:'+ message

    elif state1[id] == 'changeCategory':
         if message not in options:
            check_text = ('您輸入的類別錯誤，請重新輸入')
            actions=[]
            for option in options:
                actions.append(QuickReplyButton(action=MessageAction(label=option, text=option)))
            check_text=TextSendMessage(text=check_text, quick_reply=QuickReply(items=actions))
            return check_text
         state1[id] = 'ShowFM'
         global_Storage[id+'category'] ='商品類別:'+ message        
    elif state1[id] == 'changeUnit':
        if message not in units :
            check_text = ('您輸入的單位錯誤，請重新輸入')
            actions=[]
            for option in units:
                actions.append(QuickReplyButton(action=MessageAction(label=option, text=option)))
            check_text=TextSendMessage(text=check_text, quick_reply=QuickReply(items=actions))
            return check_text
        state1[id] = 'ShowFM'
        global_Storage[id+'unit'] ='商品單位:'+ message
    elif state1[id] == 'changeIntroduction':
        if len(message) > 150:
            check_text = ('您輸入的商品簡介超過50字，請重新輸入')
            check_text = TextSendMessage(text=check_text)
            return check_text
        state1[id] = 'ShowFM'
        global_Storage[id+'introduction'] ='商品簡介:'+ message
    elif state1[id] == 'changeUnitPrice':
        if not message.isdigit():
            check_text = ('您輸入的商品售出單價不是數字，請重新輸入')
            check_text = TextSendMessage(text=check_text)
            return check_text
        state1[id] = 'ShowFM'
        global_Storage[id+'unitPrice'] = '商品售出單價:'+message
    elif state1[id] == 'changeUnitPrice2':
        if not message.isdigit():
            check_text = ('您輸入的商品售出單價2不是數字，請重新輸入')
            check_text = TextSendMessage(text=check_text)
            return check_text  
        state1[id] = 'ShowFM'
        global_Storage[id+'unitPrice2'] = '商品售出單價2:'+message
    elif state1[id] == 'changePicture':
        state1[id] = 'ShowFM'
        global_Storage[id+'picture'] = '商品圖片'+message
    elif state1[id] == 'changeReturnProduct':
        if message not in returnoptions:
            check_text = ('您輸入的可否退換貨錯誤，請重新輸入')
            actions=[]
            for option in returnoptions:
                actions.append(QuickReplyButton(action=MessageAction(label=option, text=option)))
            check_text=TextSendMessage(text=check_text, quick_reply=QuickReply(items=actions))
            return check_text
        state1[id] = 'ShowFM'
        global_Storage[id+'returnProduct'] = '可否退換貨:'+message
    if state1[id] == 'ShowFM':
        if(message=='修改品名'):
            check_text = '請輸入品名(少於50字)'
            state1[id] = 'changePname'
            check_text = TextSendMessage(text=check_text)
        if(message=='修改商品類別'):
            check_text = '請選擇商品類別'
            actions=[]
            for option in options:
                actions.append(QuickReplyButton(action=MessageAction(label=option, text=option)))
            check_text=TextSendMessage(text=check_text, quick_reply=QuickReply(items=actions))
            state1[id] = 'changeCategory'
        if(message=='修改商品單位'):
            check_text = '請選擇商品單位'
            state1[id] = 'changeUnit'
            actions=[]
            for option in units:
                actions.append(QuickReplyButton(action=MessageAction(label=option, text=option)))
            check_text=TextSendMessage(text=check_text, quick_reply=QuickReply(items=actions))
        if(message=='修改商品簡介'):
            check_text = '請輸入商品簡介(少於150字)'
            state1[id] = 'changeIntroduction'
            check_text = TextSendMessage(text=check_text)
        if(message=='修改商品售出單價'):
            check_text = '請輸入商品售出單價'
            state1[id] = 'changeUnitPrice'
            check_text = TextSendMessage(text=check_text)
        if(message=='修改商品售出單價2'):
            check_text = '請輸入商品售出單價2'
            state1[id] = 'changeUnitPrice2'
            check_text = TextSendMessage(text=check_text)
        if(message=='修改商品圖片'):
            check_text = '請輸入商品圖片'
            state1[id] = 'changePicture'
            check_text = TextSendMessage(text=check_text)
        if(message=='修改可否退換貨'):
            check_text = '請選擇可否退換貨'
            state1[id] = 'changeReturnProduct'
            check_text = ('您輸入的單位錯誤，請重新輸入')
            actions=[]
            for option in returnoptions:
                actions.append(QuickReplyButton(action=MessageAction(label=option, text=option)))
            check_text=TextSendMessage(text=check_text, quick_reply=QuickReply(items=actions))
            return check_text
        if(message == '建立商品'):
            database.createProduct(id)
            check_text = TextSendMessage(text='商品建立成功')
            state[id]= 'normal'
        elif(state1[id] == 'ShowFM'):
            check_text = FM.create_now_purchase_product(id)
        
    

    return check_text
def createPreOrder():
    id = manager.user_id    
    state = manager.user_state
    state1 = manager.user_state1
    message = manager.msg
    global_Storage = manager.global_Storage
    options = ['frozen', 'dailyuse', 'dessert', 'local', 'staplefood', 'generally', 'beauty', 'snack', 'healthy', 'drinks','test']
    units=['個','包','盒','桶','公克','公斤','組','箱','帶']
    if state1[id] == 'first':
        if len(message) > 50:
            check_text = ('您輸入的品名超過50字，請重新輸入')
            check_text = TextSendMessage(text=check_text)
            return check_text
        global_Storage[id+'pname'] = '品名：'+ message
        check_text = ('您輸入的品名： %s' %(message))
        check_text += '\n=>請接著選擇「商品類別」'
        
        actions=[]
        for option in options:
           actions.append(QuickReplyButton(action=MessageAction(label=option, text=option)))
        check_text=TextSendMessage(text=check_text, quick_reply=QuickReply(items=actions))
        state1[id] = 'one'
    elif state1[id] == 'one':
        if message not in options:
            check_text = ('您輸入的類別錯誤，請重新輸入')
            actions=[]
            for option in options:
                actions.append(QuickReplyButton(action=MessageAction(label=option, text=option)))
            check_text=TextSendMessage(text=check_text, quick_reply=QuickReply(items=actions))
            return check_text
        global_Storage[id+'category'] = '商品類別:' + message
        check_text = ('%s\n %s' %(global_Storage[id+'pname'],global_Storage[id+'category']))
        check_text += '\n=>請接著選擇「商品單位」'
        actions=[]
        for option in units:
           actions.append(QuickReplyButton(action=MessageAction(label=option, text=option)))
        check_text=TextSendMessage(text=check_text, quick_reply=QuickReply(items=actions))
        state1[id] = 'two'
    elif state1[id] == 'two':
        if message not in units :
            check_text = ('您輸入的單位錯誤，請重新輸入')
            actions=[]
            for option in units:
                actions.append(QuickReplyButton(action=MessageAction(label=option, text=option)))
            check_text=TextSendMessage(text=check_text, quick_reply=QuickReply(items=actions))
            return check_text
        global_Storage[id+'unit'] = '商品單位：' + message
        check_text = ('%s\n%s\n%s' %(global_Storage[id+'pname'],global_Storage[id+'category'],global_Storage[id+'unit']))
        check_text += '\n=>請接著輸入「商品簡介」(少於150字)'
        check_text = TextSendMessage(text=check_text)
        state1[id] = 'three'
    elif state1[id] == 'three':
        if len(message) > 150:
            check_text = ('您輸入的商品簡介超過50字，請重新輸入')
            check_text = TextSendMessage(text=check_text)
            return check_text
        global_Storage[id+'introduction'] = '商品簡介：' + message
        check_text = ('%s\n%s\n%s\n %s' %(global_Storage[id+'pname'],global_Storage[id+'category'],global_Storage[id+'unit'],global_Storage[id+'introduction']))
        check_text += '\n=>請接著輸入「商品售出單價」'
        check_text = TextSendMessage(text=check_text)
        state1[id] = 'four'
    elif state1[id] == 'four':
        if not message.isdigit():
            check_text = ('您輸入的商品售出單價不是數字，請重新輸入')
            check_text = TextSendMessage(text=check_text)
            return check_text
        global_Storage[id+'unitPrice'] = '商品售出單價：' + message
        check_text = ('%s\n%s\n%s\n%s\n%s' %(global_Storage[id+'pname'],global_Storage[id+'category'],global_Storage[id+'unit'],global_Storage[id+'introduction'],global_Storage[id+'unitPrice']))
        check_text += '\n=>請接著輸入「商品售出單價2」'
        check_text = TextSendMessage(text=check_text)
        state1[id] = 'five'
    elif state1[id] == 'five':
        if not message.isdigit():
            check_text = ('您輸入的商品售出單價2不是數字，請重新輸入')
            check_text = TextSendMessage(text=check_text)
            return check_text
        global_Storage[id+'unitPrice2'] = '商品售出單價2：' + message
        check_text = ('%s\n%s\n%s\n%s\n%s\n %s' %(global_Storage[id+'pname'],global_Storage[id+'category'],global_Storage[id+'unit'],global_Storage[id+'introduction'],global_Storage[id+'unitPrice'],global_Storage[id+'unitPrice2']))
        check_text += '\n=>請接著輸入「商品圖片」'
        check_text = TextSendMessage(text=check_text)
        state1[id] = 'six'
    elif state1[id] == 'six':
        global_Storage[id+'picture'] = '商品圖片：' + message
        check_text = ('%s\n%s\n%s\n%s\n%s\n%s\n%s' %(global_Storage[id+'pname'],global_Storage[id+'category'],global_Storage[id+'unit'],global_Storage[id+'introduction'],global_Storage[id+'unitPrice'],global_Storage[id+'unitPrice2'],global_Storage[id+'picture']))
        check_text += '\n=>請接著輸入「商品預購截止時間」'
        timeget = gettime()
        datetime = timeget['formatted_datetime2']#2023-10-18T21:00 用於LINE的格式
        check_text = FM.template_message(check_text,datetime)
        state1[id] = 'seven'
    elif state1[id] == 'seven':
        # 加上判斷
        global_Storage[id+'deadline'] = '商品預購截止時間：' + message
        check_text = ('%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s' %(global_Storage[id+'pname'],global_Storage[id+'category'],global_Storage[id+'unit'],global_Storage[id+'introduction'],global_Storage[id+'unitPrice'],global_Storage[id+'unitPrice2'],global_Storage[id+'picture'],global_Storage[id+'deadline']))
        check_text += '\n=>請接著輸入「商品預購倍數」'
        check_text = TextSendMessage(text=check_text)
        state1[id] = 'eight'
    elif state1[id] == 'eight':
        if not message.isdigit():
            check_text = ('您輸入的商品預購倍數不是數字，請重新輸入')
            check_text = TextSendMessage(text=check_text)
            return check_text
        global_Storage[id+'multiple'] = '商品預購倍數：' + message
        check_text = ('%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s' %(global_Storage[id+'pname'],global_Storage[id+'category'],global_Storage[id+'unit'],global_Storage[id+'introduction'],global_Storage[id+'unitPrice'],global_Storage[id+'unitPrice2'],global_Storage[id+'picture'],global_Storage[id+'deadline'],global_Storage[id+'multiple']))
        check_text = TextSendMessage(text=check_text)
        global_Storage[id+'tag'] = 'nil'
        state1[id] = 'ShowFM'
    elif state1[id] == 'changePname':
        if len(message) > 50:
            check_text = ('您輸入的品名超過50字，請重新輸入')
            check_text = TextSendMessage(text=check_text)
            return check_text
        state1[id] = 'ShowFM' 
        global_Storage[id+'pname'] ='品名:'+ message
    elif state1[id] == 'changeCategory':
         if message not in options:
            check_text = ('您輸入的類別錯誤，請重新輸入')
            actions=[]
            for option in options:
                actions.append(QuickReplyButton(action=MessageAction(label=option, text=option)))
            check_text=TextSendMessage(text=check_text, quick_reply=QuickReply(items=actions))
            return check_text
         state1[id] = 'ShowFM'
         global_Storage[id+'category'] ='商品類別:'+ message        
    elif state1[id] == 'changeUnit':
        if message not in units :
            check_text = ('您輸入的單位錯誤，請重新輸入')
            actions=[]
            for option in units:
                actions.append(QuickReplyButton(action=MessageAction(label=option, text=option)))
            check_text=TextSendMessage(text=check_text, quick_reply=QuickReply(items=actions))
            return check_text
        state1[id] = 'ShowFM'
        global_Storage[id+'unit'] ='商品單位:'+ message
    elif state1[id] == 'changeIntroduction':
        if len(message) > 150:
            check_text = ('您輸入的商品簡介超過50字，請重新輸入')
            check_text = TextSendMessage(text=check_text)
            return check_text
        state1[id] = 'ShowFM'
        global_Storage[id+'introduction'] ='商品簡介:'+ message
    elif state1[id] == 'changeUnitPrice':
        if not message.isdigit():
            check_text = ('您輸入的商品售出單價不是數字，請重新輸入')
            check_text = TextSendMessage(text=check_text)
            return check_text
        state1[id] = 'ShowFM'
        global_Storage[id+'unitPrice'] = '商品售出單價:'+message
    elif state1[id] == 'changeUnitPrice2':
        if not message.isdigit():
            check_text = ('您輸入的商品售出單價2不是數字，請重新輸入')
            check_text = TextSendMessage(text=check_text)
            return check_text
        state1[id] = 'ShowFM'
        global_Storage[id+'unitPrice2'] = '商品售出單價2:'+message
    elif state1[id] == 'changePicture':
        state1[id] = 'ShowFM'
        global_Storage[id+'picture'] = '商品圖片'+message
    elif state1[id] == 'changeDeadline':
        state1[id] = 'ShowFM'
        global_Storage[id+'deadline'] = '商品預購截止時間:'+message
    elif state1[id] == 'changeMultiple':
        if not message.isdigit():
            check_text = ('您輸入的商品預購倍數不是數字，請重新輸入')
            check_text = TextSendMessage(text=check_text)
            return check_text
        state1[id] = 'ShowFM'
        global_Storage[id+'multiple'] = '商品預購倍數:'+message
    if state1[id] == 'ShowFM':
        if(message=='修改品名'):
            check_text = '請輸入品名(少於50字)'
            state1[id] = 'changePname'
            check_text = TextSendMessage(text=check_text)
        if(message=='修改商品類別'):
            check_text = '請選擇商品類別'
            actions=[]
            for option in options:
                actions.append(QuickReplyButton(action=MessageAction(label=option, text=option)))
            check_text=TextSendMessage(text=check_text, quick_reply=QuickReply(items=actions))
            state1[id] = 'changeCategory'
        if(message=='修改商品單位'):
            check_text = '請選擇商品單位'
            state1[id] = 'changeUnit'
            actions=[]
            for option in units:
                actions.append(QuickReplyButton(action=MessageAction(label=option, text=option)))
            check_text=TextSendMessage(text=check_text, quick_reply=QuickReply(items=actions))
        if(message=='修改商品簡介'):
            check_text = '請輸入商品簡介(少於150字)'
            state1[id] = 'changeIntroduction'
            check_text = TextSendMessage(text=check_text)
        if(message=='修改商品售出單價'):
            check_text = '請輸入商品售出單價'
            state1[id] = 'changeUnitPrice'
            check_text = TextSendMessage(text=check_text)
        if(message=='修改商品售出單價2'):
            check_text = '請輸入商品售出單價2'
            state1[id] = 'changeUnitPrice2'
            check_text = TextSendMessage(text=check_text)
        if(message=='修改商品圖片'):
            check_text = '請輸入商品圖片'
            state1[id] = 'changePicture'
            check_text = TextSendMessage(text=check_text)
        if(message=='修改商品預購截止時間'):
            check_text = '請輸入商品預購截止時間'
            state1[id] = 'changeDeadline'
            timeget = gettime()
            datetime = timeget['formatted_datetime2']#2023-10-18T21:00 用於LINE的格式
            check_text = FM.template_message(check_text,datetime)
        if(message=='修改商品預購倍數'):
            check_text = '請輸入商品預購倍數'
            state1[id] = 'changeMultiple'
            check_text = TextSendMessage(text=check_text)
        if(message == '建立商品'):
            database.createProduct(id)
            check_text = TextSendMessage(text='商品建立成功')
            state[id]= 'normal'
        elif(state1[id] == 'ShowFM'):
            check_text = FM.create_preorder(id)

    return check_text

def searchingOrderByPhoneNumber():
     # 若使用者已經在等待回覆狀態，則根據回覆進行處理
    id = manager.user_id
    message = manager.msg
    state = manager.user_state
    state1 = manager.user_state1
    global_Storage = manager.global_Storage
    
    if state1[id] =='first':
        global_Storage[id+'base'] = 0
        actions = []
        global_Storage[id+'orders'] = database.getPhoneNumberByPhoneNumberLastThreeYard(message)
        # global_Storage[id+'orders'] = a
        if global_Storage[id+'orders'] == []:
            check_text = TextSendMessage(text='找不到符合條件的資料')
            state[id] = 'normal'
        else:            
            for option in global_Storage[id+'orders'][global_Storage[id+'base']:global_Storage[id+'base']+10]:
                actions.append(QuickReplyButton(action=MessageAction(label=option, text=option)))
            if len(global_Storage[id+'orders'])>global_Storage[id+'base']+10:
                actions.append(QuickReplyButton(action=MessageAction(label='下一頁', text='下一頁')))
            check_text=TextSendMessage(text='請選擇電話', quick_reply=QuickReply(items=actions))
            state1[id] = 'second'
    elif state1[id] == 'second':
        if message == '下一頁':
            actions = []
            global_Storage[id+'base']+=10
            for option in global_Storage[id+'orders'][global_Storage[id+'base']:global_Storage[id+'base']+10]:
                actions.append(QuickReplyButton(action=MessageAction(label=option, text=option)))
            if len(global_Storage[id+'orders'])>global_Storage[id+'base']+10:
                actions.append(QuickReplyButton(action=MessageAction(label='下一頁', text='下一頁')))
            check_text=TextSendMessage(text='請選擇電話', quick_reply=QuickReply(items=actions))
        else:
            global_Storage[id+'base'] = 0
            check_text = TemplateSendMessage(
                    alt_text='取貨選擇',
                    template=ConfirmTemplate(
                        text='請選擇取貨方式：\n【全部領取】或是【分開領】',
                        actions=[
                            MessageAction(
                                label='【全部領取】',
                                text='全部領取'+message,
                            ),
                            MessageAction(
                                label='【分開領】',
                                text='分開領'+message
                            )
                        ]
                    )
                )
            state1[id]='third'
    elif state1[id] == 'third':
        if message[:3] == '分開領':
            actions = []
            global_Storage[id+'orders'] = database.getOrderByPhoneNumber(message[3:])
            for option in global_Storage[id+'orders'][global_Storage[id+'base']:global_Storage[id+'base']+10]:
                actions.append(QuickReplyButton(action=MessageAction(label=option, text=option)))
            if len(global_Storage[id+'orders'])>global_Storage[id+'base']+10:
                actions.append(QuickReplyButton(action=MessageAction(label='下一頁', text='下一頁')))
            check_text=TextSendMessage(text='請選擇訂單', quick_reply=QuickReply(items=actions))

        else:
            if message == '下一頁':
                actions = []
                global_Storage[id+'base']+=10
                for option in global_Storage[id+'orders'][global_Storage[id+'base']:global_Storage[id+'base']+10]:
                    actions.append(QuickReplyButton(action=MessageAction(label=option, text=option)))
                if len(global_Storage[id+'orders'])>global_Storage[id+'base']+10:
                    actions.append(QuickReplyButton(action=MessageAction(label='下一頁', text='下一頁')))
                return TextSendMessage(text='請選擇訂單', quick_reply=QuickReply(items=actions))
            elif message[:4]== '全部領取':
                
                global_Storage[id+'orders'] = database.getOrderDetailByPhoneNumber(message[4:])
                global_Storage[id+'order'] = message[4:]
            else:
                global_Storage[id+'base']=0
                global_Storage[id+'orders'] = database.getOrderDetailByOrder(message)
                global_Storage[id+'order'] = message
            check_text = FM.showOrder()
            state1[id] = 'end'
    elif state1[id] == 'end':
        if message == '下一頁':
            global_Storage[id+'base']+=10
            check_text = FM.showOrder()
            return check_text
        elif '【確認】' in message:
            result = database.updateOrder(id)
            check_text = TextSendMessage(text='取貨成功')
        else:
            check_text = TextSendMessage(text='取貨取消')
        state[id] = 'normal'
        global_Storage[id+'base'] = 0
    return check_text
