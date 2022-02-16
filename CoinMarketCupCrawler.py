import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import sys
import re
from threading import Timer
import time


trendviewMap ={}
def cleanhtml(raw_html):
  cleanr = re.compile('<.*?>')
  cleantext = re.sub(cleanr, '', raw_html)
  return cleantext


if __name__=='__main__':
  browser =webdriver.Chrome ("chromedriver.exe")
  browser.close()
  pageIndex = 0
  while False :
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
        
        trendviewMap[symbol]=imgUrl

    


  """
  for i in range (0,10):
    js = "var q=document.documentElement.scrollTop={0}".format(i*1000)
    browser.execute_script(js)
    #time.sleep(5)
    html_doc =browser.page_source
    soup =BeautifulSoup(html_doc,'html.parser')
    symbols =soup.find_all("p",class_=re.compile("sc-1eb5slv-0 gGIpIK coin-item-symbol"))
    imgUrl = soup.find_all("img",class_=re.compile("tableGraph___c_IY- graphDown___2-1G6"))
    print (len (symbols),len (imgUrl))
  
    
    #print (imgUrl)
    for i in range(0,len(symbols)):
      a[str (symbols[i])]=str(imgUrl)
     # print ( cleanhtml (str (symbols[i])),cleanhtml (imgUrl[i].get('src')))

  print (a)
  
  
  #for symbol in symbols :
  """
    
  

