from pycoingecko import CoinGeckoAPI
import json

class coin :
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



cg=CoinGeckoAPI()
total = 0
pageIndex = 1
isRun =True
coins=cg.get_coins_markets(vs_currency='usd',page=1,pre_page =1)

c =coins[0]
coinObj  =coin (c['id'],c['symbol'],c['name'],c['image'],c['current_price'],c['market_cap'],c['market_cap_rank'],c['high_24h'],c['low_24h'],c['price_change_24h'],c['price_change_percentage_24h'])
print (coinObj.id,coinObj.symbol,coinObj.high_24h,coinObj.low_24h)



    

#cc=cg.get_coins_list()
#print (len(cc))
#print (a)