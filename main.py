import selenium
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
import os
import re
import requests
from selenium_stealth import stealth

class GetSource():
    source_file = 'demo.txt'
    finalFile = "result.txt"

    def __init__(self):
        self.driver = self.setup_driver()
        self.main()

    def setup_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")
        options.add_argument('--headless')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("blink-settings=imagesEnabled=false")
        driver = webdriver.Chrome(options=options)
        stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        )
        return driver

    def getChannelItems(self):
        # open the source file and read all lines
        with open(self.source_file, 'r', encoding='utf-16') as f:
            lines = f.readlines()

        # create a dictionary to store the channels
        channels = {}
        current_channel = ''
        pattern = r"^(.*?),(?!#genre#)"

        for line in lines:
            line = line.strip()
            if '#genre#' in line:
                # This is a new channel, create a new key in the dictionary
                current_channel = line.split(',')[0]
                channels[current_channel] = []
            else:
                # This is a url, add it to the list of urls for the current channel
                match = re.search(pattern, line)
                if match and match.group(1) not in channels[current_channel]:
                    channels[current_channel].append(match.group(1))
        
        return channels

    def getSpeed(self,url):
        start = time.time()
        try:
            r = requests.get(url,timeout=4)
            resStatus = r.status_code
        except:
            print('request timeout or error')
        end = time.time()
        return end - start

    def compareSpeed(self,pageUrls):
        response_times = []
        for pageUrl in pageUrls:
            response_times.append(self.getSpeed(pageUrl))
        
        sorted_urls = zip(pageUrls, response_times)
        sorted_urls = sorted(sorted_urls, key=lambda x: x[1])

        pageUrls_new =[]
        for url, _ in sorted_urls:
            pageUrls_new.append(url)
            
        return pageUrls_new
    
    def removeFile(self):
        if os.path.exists(self.finalFile):
            os.remove(self.finalFile)

    def outputTxt(self,cate,channelUrls):
        # update the final file
        with open(self.finalFile, 'a', encoding='utf-16') as f:
            f.write('\n' + cate + ',#genre#\n')
            for name, urls in channelUrls.items():
                for url in urls:
                    f.write(name + ',' + url + '\n')

    def visitPage(self,channelItems):
        self.driver.get("https://www.foodieguide.com/iptvsearch/")
        self.removeFile()
        for cate, names in channelItems.items():
            channelUrls = {}
            for name in names:
                element=self.driver.find_element(By.ID, "search")
                element.clear()
                element.send_keys(name)
                self.driver.find_element(By.ID, "form1").find_element(By.NAME,"Submit").click()
                urls=[]
                allRangeElement=self.driver.find_elements(By.CLASS_NAME, "m3u8")
                if len(allRangeElement)<=0:
                    continue
                if len(allRangeElement)>5:
                    allRangeElement=allRangeElement[:5]
                for elem in allRangeElement:
                    urls.append(elem.text)
                # urls=self.compareSpeed(urls)
                channelUrls[name]=urls
            self.outputTxt(cate,channelUrls)
            time.sleep(1)

    def main(self):
        self.visitPage(self.getChannelItems())

GetSource()