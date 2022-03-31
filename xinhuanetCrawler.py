from datetime import datetime
import json
import time
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
            'images': 2,
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


class xinhuanet_crawl_text:
    def __init__(self):
        self.driver = connectchrome()
        self.url_list = []
        self.get_url()

    def get_url(self):
        driver = self.driver
        driver.get(url='http://www.xinhuanet.com/milpro/')
        scroll_to_bottom(driver)
        urls = driver.find_elements_by_xpath('//ul[@class="army_list"]/li/a')
        data_list = []
        for _url in urls:
            url = _url.get_attribute('href')
            self.url_list.append(url)
        urls_lunbo =  driver.find_elements_by_xpath('//div[@class="picTitle"]/p[@class="img"]/a')
        for _url in urls_lunbo:
            url = _url.get_attribute('href')
            self.url_list.append(url)
        for url in self.url_list:
            driver.get(url)
            print(url)
            scroll_to_bottom(driver)
            # 文章
            if url.find('news.cn/mil') >= 0:
                dic = {}
                # 情报源
                dic["source"] = "新华网"
                # 情报源注册时长（空）
                dic["register_time"] = ""
                # 情报源关注者数目(空)
                dic["follower"] = ""
                # 文章标题
                dic["title"] = driver.find_element_by_xpath("//div[@class='head-line clearfix']/h1/span").text
                # 文章作者
                author = driver.find_element_by_xpath("//div[@id='articleEdit']/span[@class='editor']").text
                author = str(author).split(':')[1]
                dic["author"] = author.split('】')[0]
                # 转自何处
                source_from = driver.find_element_by_xpath('//div[@class="source"]').text
                dic["source_from"] = str(source_from).split('：')[1]
                # 文章发布时间
                year = driver.find_element_by_xpath('//span[@class="year"]').text
                year = str(year).strip() + "-"
                day = driver.find_element_by_xpath('//span[@class="day"]').text
                day = str(day).split('/')[0] + "-" + str(day).split('/')[1]
                dic["publish_time"] = year + day + " " + driver.find_element_by_xpath('//span[@class="time"]').text
                # 爬取时间
                now = datetime.now()
                dic["crawl_time"] = now.strftime('%Y-%m-%d %H:%M:%S')
                # 文章正文
                content = ""
                temp = driver.find_elements_by_xpath("//div[@id='detail']/p[not(font)]")
                for t in temp:
                    content += t.text
                dic["content"] = content
                # 阅读数
                dic["page_views"] = ""
                # 转发数
                dic["forword"] = ""
                # 链接
                dic["url"] = url
                data_list.append(dic)
            # 公众号
            else:
                dic = {}
                # 情报源
                dic["source"] = "新华网"
                # 情报源注册时长（空）
                dic["register_time"] = ""
                # 情报源关注者数目(空)
                dic["follower"] = ""
                # 文章标题
                title = driver.find_element_by_xpath('//header[@class="news-basic"]/h1').text
                dic["title"] = title
                # 文章作者
                dic["author"] = "新华网"
                # 转自何处
                source_from = driver.find_element_by_xpath(
                    '//header[@class="news-basic"]/div/p[@class="hender-info-source-v7"]/span').text
                dic["source_from"] = str(source_from).split('：')[1]
                # 文章发布时间
                dic["publish_time"] = driver.find_element_by_xpath(
                    '//header[@class="news-basic"]/div/span[@class="hender-info-over"]/span[1]').text
                # 爬取时间
                now = datetime.now()
                dic["crawl_time"] = now.strftime('%Y-%m-%d %H:%M:%S')
                # 文章正文
                content = ""
                temp = driver.find_elements_by_xpath("//section[@class='main-text-container']/p[not(a)]")
                for t in temp:
                    content += t.text
                dic["content"] = content
                # 阅读数
                page_views = driver.find_element_by_xpath(
                    '//header[@class="news-basic"]/div/span[@class="hender-info-over"]/span[2]').text
                dic["page_views"] = str(page_views).split("：")[1]
                # 转发数
                dic["forword"] = ""
                # 链接
                dic["url"] = url
                data_list.append(dic)
        self.save_data(data_list)

    def save_data(self, data_list):
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')[:-3]
        text_name = "xinhuanet_" + str(timestamp) + ".json"
        with open(text_name, 'a', encoding='utf-8') as f:
            f.write(json.dumps(data_list, indent=2, ensure_ascii=False))


if __name__=="__main__":
    xinhuanet_crawl = xinhuanet_crawl_text()
