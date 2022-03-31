import os
import urllib.request
from datetime import datetime
import json
import time

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
import csv


def connectchrome():
    options = Options()
    options.add_argument('log-level=3')
    options.add_argument('--incognito')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_experimental_option('useAutomationExtension', False)
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    prefs = {
        'profile.default_content_setting_values': {
            # 'images': 2,
        }
    }
    options.add_experimental_option('prefs', prefs)
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'")  # 进行UA伪装
    # 不显示窗口
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
              get: () => undefined
            })
          """
    })
    driver.maximize_window()
    time.sleep(2)
    return driver


def scroll_to_bottom(driver):     # 将页面滑动到最底端
    js = "return action=document.body.scrollHeight" # 获取页面总高度
    last_height = driver.execute_script(js)
    while True:
        driver.execute_script("window.scrollBy(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script(js)
        if new_height == last_height:
            break
        last_height = new_height


def isElementExist(driver, path):
    try:
        ele = driver.find_element_by_xpath(path)
        return True
    except:
        return False


def create_dirs():
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')[:-3]
    file_name = "./xinhuanet_video_" + str(timestamp)
    folder = os.path.exists(file_name)
    if not folder:  # 判断是否存在文件夹如果不存在则创建为文件夹
        os.makedirs(file_name)  # makedirs 创建文件时如果路径不存在会创建这个路径
    return file_name


class xinhuanet_crawl_video:
    def __init__(self):
        self.driver = connectchrome()
        self.url_list = []
        self.get_url()

    def get_url(self):
        driver = self.driver
        driver.get(url='http://www.xinhuanet.com/milpro/')
        scroll_to_bottom(driver)
        urls = driver.find_elements_by_xpath('//ul[@class="army_list"]/li/a')
        for _url in urls:
            url = _url.get_attribute('href')
            self.url_list.append(url)
        urls_lunbo = driver.find_elements_by_xpath('//div[@class="picTitle"]/p[@class="img"]/a')
        for _url in urls_lunbo:
            url = _url.get_attribute('href')
            self.url_list.append(url)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'
        }
        dir = create_dirs()
        # self.url_list = ['http://www.news.cn/mil/2022-03/15/c_1211608754.htm']
        for url in self.url_list:
            cnt = 1
            driver.get(url)
            print(url)
            scroll_to_bottom(driver)
            # 文章
            if url.find('news.cn/mil') >= 0:
                continue
            # 公众号
            else:
                # 标题
                title = driver.find_element_by_xpath('//header[@class="news-basic"]/h1').text
                try:
                    # 视频url
                    video_urls = driver.find_elements_by_xpath('//div[@class="video-container link-video"]/video')
                except:
                    continue
                for video_url in video_urls:
                    tit = title + "(" + str(cnt) + ")"
                    cnt = cnt + 1
                    video_url = video_url.get_attribute('src')
                    downsize = 0
                    print('开始下载')
                    startTime = time.time()
                    req = requests.get(video_url, headers=headers, stream=True, verify=False)
                    # 保存视频路径
                    path = dir + '/' + tit + '.mp4'
                    with(open(path, 'wb')) as f:
                        for chunk in req.iter_content(chunk_size=10000):
                            if chunk:
                                f.write(chunk)
                    print('over')


if __name__=="__main__":
    xinhuanet_crawl = xinhuanet_crawl_video()
