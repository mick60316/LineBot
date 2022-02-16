from __future__ import unicode_literals
import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from APITools import CoinClass
import configparser
import random
import json
import logging

from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    SourceUser, SourceGroup, SourceRoom,
    TemplateSendMessage, ConfirmTemplate, MessageAction,
    ButtonsTemplate, ImageCarouselTemplate, ImageCarouselColumn, URIAction,
    PostbackAction, DatetimePickerAction,
    CameraAction, CameraRollAction, LocationAction,
    CarouselTemplate, CarouselColumn, PostbackEvent,
    StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,
    ImageMessage, VideoMessage, AudioMessage, FileMessage,
    UnfollowEvent, FollowEvent, JoinEvent, LeaveEvent, BeaconEvent,
    MemberJoinedEvent, MemberLeftEvent,
    FlexSendMessage, BubbleContainer, ImageComponent, BoxComponent,
    TextComponent, IconComponent, ButtonComponent,
    SeparatorComponent, QuickReply, QuickReplyButton,
    ImageSendMessage)
from APITools import ExchangeTools

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)
channel_secret ='76c48209453f0eef97e43c0fd5c1bfcd'
channel_access_token = 'BoWkdI2WoHJbqjBzFtl14qWtY7eMvXFIWkXbjAcgoUFQpqy0aayFr9r0MhZh3jB7jFmQwhHjdtAUmEYXAVFz6LsAjtKsPK+40F0QYhaBI5dk1IIfFNGFqI4rdkGtxPEkvcjBxriJ+BD8cNhF9VOogAdB04t89/1O/w1cDnyilFU='

#LINE 聊天機器人的基本資料
meanFlexMessageString =""
allExchangeMessageString =""

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

tools = ExchangeTools()
keywordList =[]
fiatList=[]




# 接收 LINE 的資訊
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    
    try:
        print(body, signature)
        handler.handle(body, signature)
        
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def pretty_echo(event):
    global meanFlexMessageString
    global allExchangeMessageString
    if event.source.user_id != "Udeadbeefdeadbeefdeadbeefdeadbeef":
        msg =event.message.text
        msg=msg.upper()
        msgSplit =msg.split(' ')
        if msg =="KEYWORD":
            outputStr ="\n".join(keywordList)
            line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=outputStr))
        elif msg =="FIAT":
            outputStr ="\n".join(fiatList)
            line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=outputStr))
            
            
        elif msg in keywordList:
            price,coinClass,trendviewURL,newsMap=tools.getCoinInfo(msg)
           
            
            jsonStr =json.loads(meanFlexMessageString)

            jsonStr['contents'][0]['hero']['url']=str(coinClass.image)
            jsonStr['contents'][0]['body']["contents" ][0]['text']=msg+"/USDT"            
            jsonStr['contents'][0]['body']["contents" ][1]['contents'][0]['contents'][1]['text']=str(price)
            jsonStr['contents'][0]['body']["contents" ][1]['contents'][1]['contents'][1]['text']=str(coinClass.market_cap)
            jsonStr['contents'][0]['body']["contents" ][1]['contents'][2]['contents'][1]['text']=str(coinClass.market_cap_rank)
            jsonStr['contents'][0]['body']["contents" ][1]['contents'][3]['contents'][1]['text']=str(coinClass.high_24h)
            jsonStr['contents'][0]['body']["contents" ][1]['contents'][4]['contents'][1]['text']=str(coinClass.low_24h)
            jsonStr['contents'][0]['body']["contents" ][1]['contents'][5]['contents'][1]['text']=str(coinClass.price_change_24h)
            jsonStr['contents'][0]['body']["contents" ][1]['contents'][6]['contents'][1]['text']=str(coinClass.price_change_percentage_24h)
            
            
            #jsonStr['contents'][1]['hero']['url']=trendviewURL
            newsIndex =0
            for key in newsMap.keys():
                
                jsonStr['contents'][1]['body']['contents'][0]['contents'][newsIndex]['contents'][0]['text']=key
                jsonStr['contents'][1]['body']['contents'][0]['contents'][newsIndex]['action']['uri']=newsMap[key]
                newsIndex+=1
            
            message = FlexSendMessage(alt_text=msg+"/USDT", contents=json.loads(json.dumps(jsonStr)))
            line_bot_api.reply_message(
                event.reply_token,
                message
            )

        elif ((msgSplit[0] in keywordList) and ( msgSplit[1] in fiatList )):
            outputStr =""
            result,imageUrl =tools.getAllPrice(msgSplit[0],msgSplit[1])
            jsonStr =json.loads(allExchangeMessageString)
            jsonStr['hero']['url']=str(imageUrl)
            jsonStr['body']["contents" ][0]['text']="BTC/USDT"#str(msgSplit[0])+'/'+msgSplit[1]
            index=0
            for key in result.keys():
                jsonStr['contents'][1]['contents'][index]['contents'][0]['text']=str(key)
                jsonStr['contents'][1]['contents'][index]['contents'][1]['text']=str(result[key])
                index=index+1
            message = FlexSendMessage(alt_text=str(msgSplit[0])+'/'+msgSplit[1], contents=json.loads(json.dumps(jsonStr)))
            line_bot_api.reply_message(
                event.reply_token,
                message
            )
        elif msg =='TEST':
            
            jsonStr =json.loads(allExchangeMessageString)
            
            message = FlexSendMessage(alt_text="hello", contents=json.loads(json.dumps(jsonStr)))
            line_bot_api.reply_message(
                event.reply_token,
                message
            )
 

if __name__ == "__main__":

    f = open('MeanFlaxMessageFormatAlpha.txt','r',encoding="utf-8")
    meanFlexMessageString= f.read()
    f.close()
    f =open('AllExchangeMessageFormat.txt','r',encoding="utf-8")
    allExchangeMessageString =f.read()
    f.close()

    keywordList,fiatList= tools.getKeywordList()
    app.run()
