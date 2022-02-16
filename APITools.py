import requests
import json
from pycoingecko import CoinGeckoAPI
import time
from datetime import datetime
from datetime import timedelta, date
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import feedparser
from pycoingecko import CoinGeckoAPI
import logging
from threading import Timer
import threading



BinanceCoinList =['WBTC','USDT','USDC','DAI','BUSD','PAX','TUSD','HUSD','SUSD','BTC','ETH'
           ,'BNB','XRP','IDR','EUR','TRX','KRW','AUD','SXP','TRY','LCT','NGN']
HuobiCoinList =['USDT','USDC','DAI','BUSD','PAX','TUSD','HUSD','SUSD','BTC','ETH'
           ,'BNB','XRP','IDR','EUR','TRX','KRW','AUD','SXP','TRY','LCT','NGN','HT']

MaxCoinList =['USDT','TWD']
BitfinexCoinList =['USD','UST','ETH','BTC','LEO','EUT','EUR','JPY','GBP']
ShubaoCoinList=['USDT','USDC','DAI','BUSD','PAX','TUSD','HUSD','SUSD','BTC','ETH'
           ,'BNB','XRP','IDR','EUR','TRX','KRW','AUD','SXP','TRY','LCT','NGN']

ProcessMap ={
"Binance" :BinanceCoinList,
"Huobi":HuobiCoinList,
"Max":MaxCoinList,
"Bitfinex":BitfinexCoinList,
"Shubao":ShubaoCoinList,
    }
NoProcessMap ={
'Bitopro','Okex','FTX'}

ApiUrlMap ={
    'Binance':'https://api1.binance.com/api/v3/ticker/price',
    'Bitopro':'https://api.bitopro.com/v3/tickers',
    'Okex':'https://www.okex.com/api/spot/v3/instruments/ticker',
    'Bitfinex':'https://api.bitfinex.com/v1/symbols',
    'FTX':'https://ftx.com/api/markets',
    'Huobi':'https://api.huobi.pro/market/tickers',
    'Max':'https://max-api.maicoin.com/api/v2/tickers/',
    'Shubao':'https://www.shubaoex.com/api/market/tickers'
}

SearchPriceUrl={
    'Binance':'https://api1.binance.com/api/v3/ticker/price?symbol={0}',
    'Bitopro':'https://api.bitopro.com/v3/tickers/{0}',
    'Okex':'https://www.okex.com/api/spot/v3/instruments/{0}/ticker',
    'Bitfinex':'https://api.bitfinex.com/v1/pubticker/{0}',
    'FTX':'https://ftx.com/api/markets/{0}',
    'Huobi':'https://api.huobi.pro/market/detail/merged?symbol={0}',
    'Max':'https://max-api.maicoin.com/api/v2/tickers/{0}',
    'Shubao':'https://www.shubaoex.com/api/market/detail/merged?symbol={0}',
    
}


BinanceMap ={}
BitoproMap={}
OkexMap ={}
BitfinexMap ={}
FTXMap ={}
HuobiMap={}
MaxMap ={}
ShubaoMap ={}


Maps ={
"Binance":BinanceMap,
"Bitopro":BitoproMap,
"Okex":OkexMap,
"Bitfinex":BitfinexMap,
"FTX":FTXMap,
"Huobi":HuobiMap,
"Max":MaxMap,
"Shubao":ShubaoMap
}


keywordList =[]
fiatList =[]
coingeckoAPI =CoinGeckoAPI()

coinInfoMap ={}
trendviewURLMap ={}


coinMarketCupUrl = "https://coinmarketcap.com/?page={0}"
blocktempoRSSUrl ="https://www.blocktempo.com/feed/"

class CoinClass :
    def __init__(self,id,symbol,name,image,current_price,market_cap,
    market_cap_rank,high_24h,low_24h,price_change_24h,price_change_percentage_24h):
        self.id =id
        self.symbol=symbol
        self.name =name
        self.image=image
        self.current_price=current_price
        self.market_cap=market_cap
        self.market_cap_rank=market_cap_rank
        self.high_24h=high_24h
        self.low_24h=low_24h
        self.price_change_24h=price_change_24h
        self.price_change_percentage_24h=price_change_percentage_24h

def cleanhtml(raw_html):
  cleanr = re.compile('<.*?>')
  cleantext = re.sub(cleanr, '', raw_html)
  return cleantext





class ExchangeTools:
    
    def __init__ (self):
        
        print ("Exchange Tools init")

        for key in ApiUrlMap.keys():
            self.updateAllPair (key,ApiUrlMap[key])
       
        t = threading.Thread(target = self.updateCoinGeckoCoinInfoTimer)
        t.start()
        #self.updateTrendviewUrl()
       
    

    def updateCoinGeckoCoinInfoTimer (self):
        self.updateCoinGeckoCoinInfo()
        while True:
            now = datetime.now()
            timeStamp= now.strftime("%M:%S")
            times =timeStamp.split(':')
            m =int(times[0])
            s = int (times[1])
            if (m%10 ==0 and s ==0 ):
                self.updateCoinGeckoCoinInfo()
      
        
    
    def CoinNormalize(self,inputStr2,Exchange):
        inputStr =inputStr2
        inputStr=inputStr.upper()
        inputStr=inputStr.replace('_','/')
        inputStr=inputStr.replace('-','/')
        startIndex=-1
        coin1 = ""
        coin2 =""
        
        if Exchange in NoProcessMap:
            return inputStr2,inputStr
        
        if Exchange in ProcessMap:
            coinList=[]
            coinList =ProcessMap[Exchange]

            for coin in coinList:
                startIndex=inputStr.find(coin)

                if (startIndex ==0):

                    coin1=coin
                    coin2=inputStr[len(coin):]
                    break
                
                elif startIndex ==-1:
                    coin1=inputStr
                    coin2="NULL"
                else:
                    coin1=inputStr[0:startIndex]
                    coin2=coin
                    break
            if (coin2 =="USDT" and (not(coin1 in keywordList)) ):
                keywordList.append (coin1)
                
            if (not(coin2 in fiatList)):
                fiatList.append(coin2)
                
            return inputStr2,coin1+"/"+coin2
        
    def updateAllPair (self,name,url):
        r= requests.get (url)
        jsonStr =json.loads (r.text)
        if name =='Binance':
            for item in jsonStr:
                a1,a2 =self.CoinNormalize(item['symbol'],name)
                BinanceMap[a2]=a1
                
        elif name =='Okex':
            for item in jsonStr:
                a1,a2 =self.CoinNormalize(item['instrument_id'],name)
                OkexMap[a2]=a1
                
        elif name =='Bitopro':
            totalData =jsonStr ['data']
            for item in totalData:
                a1,a2 =self.CoinNormalize(item ['pair'],name)
                BitoproMap[a2]=a1
                
        elif name =='Shubao':
            dataArray =jsonStr['data']
            for item in dataArray:
                a1,a2 =self.CoinNormalize(item['symbol'],name)
                ShubaoMap[a2]=a1
                
        elif name =='FTX':
            for item in jsonStr['result']:
                a1,a2 =self.CoinNormalize( item['name'],name)
                FTXMap [a2]=a1
                
        elif name =='Huobi':
            dataArray =jsonStr['data']
            for item in dataArray:
                a1,a2 =self.CoinNormalize(item['symbol'],"Huobi")
                HuobiMap [a2]=a1
                
        elif name =='Max':
            for key in jsonStr.keys():
                a1,a2=self.CoinNormalize(key,"Max")
                MaxMap[a2]=a1
                
        elif name =='Bitfinex':
            for coin in jsonStr:
                a1,a2 =self.CoinNormalize(coin,'Bitfinex')
                a2 =a2.replace('UST','USDT')
                BitfinexMap[a2]=a1


    def updateTrendviewUrl (self):
        browser =webdriver.Chrome ("chromedriver.exe")
        pageIndex = 0
        while True :
            if pageIndex >1 :
                break
            pageIndex+=1
            url = "https://coinmarketcap.com/?page={0}".format(pageIndex)
            browser.get (url)
            for i in range(0 ,5):
                js = "var q=document.documentElement.scrollTop={0}".format(i*2000)
                browser.execute_script(js)
                time.sleep(1)
            html_doc =browser.page_source
            soup =BeautifulSoup(html_doc,'html.parser')
            blocks =soup.find_all("tbody")
            if (len (blocks)) <1 :
                break
            blocks=blocks[0].find_all('tr')
            for i in range(0,len(blocks)):
                if i != 10:
                    index =blocks[i].find_all('td')[2].find ('div')
                    symbol = ""
                    imgUrl  = ""
                    if (index !=None):
                        symbol = str (cleanhtml (str(index.find('div').find('div').find('p')))).upper().strip()
                        imgUrl =blocks[i].find_all('td')[9].find('a').find('img').get('src')
                        print (i,cleanhtml (str(index.find('div').find('div').find('p'))),imgUrl)
                    else :
                        symbol = str (cleanhtml (str(blocks[i].find_all('td')[2].find_all('span')[2]))).upper().strip()
                        imgUrl= blocks[i].find_all('td')[3]
                        print (i,cleanhtml (str (blocks[i].find_all('td')[2].find_all('span')[2])),blocks[i].find_all('td')[3])
                    trendviewURLMap[symbol]=imgUrl
        browser.close()
        print (trendviewURLMap['BTC'])

    def updateCoinGeckoCoinInfo(self):
        logging.debug ('Start to UpdateCoinGeckoCoinInfo')
        pageIndex = 1
        isRun =True
        while isRun:
            coins=coingeckoAPI.get_coins_markets(vs_currency='usd',page=pageIndex,pre_page=250)
            pageIndex=pageIndex+1
            for coin in coins:
                if (coin['market_cap_rank']!=None):
                    coinObj=CoinClass (coin['id'],coin['symbol'],coin['name'],coin['image'],coin['current_price'],coin['market_cap'],coin['market_cap_rank'],coin['high_24h'],coin['low_24h'],coin['price_change_24h'],coin['price_change_percentage_24h'])
                    coinInfoMap[coin['symbol'].upper()]=coinObj

                else :
                    isRun =False
                    break
        logging.debug ('UpdateCoinGeckoCoinInfo Finish')
            


    
        


    def getPriceByExchanngePair (self,exchange,pair):


        if (not(pair in Maps[exchange] )):
            return None
        url = SearchPriceUrl[exchange].format (Maps[exchange][pair])
        print ("URL= ",url)
        r= requests.get (url)
        jsonStr =json.loads (r.text)
        price =""
        if exchange=="Binance":
         
            price=jsonStr['price']
        elif exchange =='Okex':
            
            price= jsonStr['last']
            
        elif exchange =='Bitopro':
            
            price= jsonStr['data']['lastPrice']  
                 
        elif exchange =='Shubao':
            price= jsonStr['tick']['close']
        
                
        elif exchange =='FTX':
            price= jsonStr['result']['price']
          
                
        elif exchange =='Huobi':
            price= jsonStr['tick']['close']
        
                
        elif exchange =='Max':
            price= jsonStr['last']
        
                
        elif exchange =='Bitfinex':
            price= jsonStr['last_price']
        return price
        
    def getExchangeKeys(self):
        return Maps

    def getKeywordList (self):
        return keywordList,fiatList 
   
    

    def getCoinInfo (self,coin):
        pair =coin+"/USDT"
        count = 0.0
        n =0
        for exchange in Maps.keys():
            price = self.getPriceByExchanngePair(exchange,pair)
            print (exchange,price)

            if (price!=None):
                count=count +float(price)
                n=n+1

        trendviewURL =""
        if coin in trendviewURLMap:
            trendviewURL = trendviewURLMap[coin]
        print (trendviewURL)
        priceAver  =count/n

        newsMap=self.getNewsMap()

        return priceAver,coinInfoMap[coin],trendviewURL,newsMap

    def getAllPrice (self,coin1,coin2):
        pair =str(coin1)+'/'+coin2
        result = {}
        
        imageUrl =coinInfoMap[str(coin1)].image



        for exchange in Maps.keys():
            price = self.getPriceByExchanngePair (exchange,pair)
            if price == None:
                price ='-'
            result[exchange]=price
        return result,imageUrl
    

    def getNewsMap (self):
        newsMap ={}
        rss = feedparser.parse (blocktempoRSSUrl)
        newsCount = 0
        print ('New count',len (rss.entries))
        for news in rss.entries:
            if newsCount >9:
                break
            newsMap[news['title']]=news['link']
            newsCount+=1
            logging.debug(news ['title'],news['link'])
            #print (news ['title'],news['link'])
        return newsMap







        

    
       
            
            
        


