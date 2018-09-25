#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from pyquery import PyQuery as pq
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from lagou_config import *

client = MongoClient(MONGO_URL)
db = client[MONGO_DB]

browser = webdriver.Chrome()
wait = WebDriverWait(browser, 4)


def get_index():
    """根据传入的地址,得到首页的相关信息"""
    browser.get("https://www.lagou.com/")
    # 选择相关城市
    switch = browser.find_element_by_css_selector('#changeCityBox > ul > li:nth-child(7) > a')
    switch.click()
    # 等待输入框被加载
    input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#search_input')))
    # 等待确定按钮被加载
    submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#search_button')))
    input.send_keys(KEYWORD)
    submit.click()
    total = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#order > li > div.item.page > '
                                                                        'div.page-number > span.span.totalNum')))
    get_info()
    return total.text
    print(total.text)


def get_next_page():
    """根据传入的值开始翻页
    """
    # 跳转浏览器到最后
    browser.execute_script('window.scrollTo(0, document.body.scrollHeight);')
    next_page = browser.find_element_by_css_selector('.next_disabled')
    # 取到当前页面
    time.sleep(3)
    next_page.click()
    get_info()
    # print('')


def get_info():
    """解析页面
    """
    doc = pq(browser.page_source.replace("xmlns", "other"))
    items = doc('#s_position_list > ul >li').items()
    for item in items:
        info = {}
        info['position'] = item.find('h3').text()
        # print(item.find('h3').text())
        info['locate'] = item('.add').find('em').text()
        # print(item('.add').find('em').text())
        info['money'] = item('.p_bot .li_b_l').children('span').text()
        # print(item('.p_bot .li_b_l').children('span').text())
        info['industry'] = item('.industry').text()
        # print(item('.industry').text())
        info['summary'] = item('.list_item_bot .li_b_l').find('span').text()
        # print(item('.list_item_bot .li_b_l').find('span').text())
        info['welfare'] = item('.list_item_bot .li_b_r').text()
        # print(item('.list_item_bot .li_b_r').text())
        some = item('.p_bot .li_b_l').remove(':nth-child(n)').text()
        info['experience'] = some.split('/')[0].strip()
        info['education'] = some.split("/")[1].strip()
        print(info)
        save_to_mongo(info)


def save_to_mongo(result):
    try:
        if db[MONGO_TABLE].insert(result):
            print("保存数据到MongoDB中成功")
        else:
            print("保存数据到MongoDB中失败!!!", result)
    except DuplicateKeyError:
        print("id重复,存在冲突ToT")


def get_all_language():
    """得到首页的所有语言"""
    browser.get("https://www.lagou.com/")
    # 选择相关城市
    switch = browser.find_element_by_css_selector('#changeCityBox > ul > li:nth-child(7) > a')
    switch.click()
    jobs = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#sideper .mainNavs .menu_box ')))
    print(jobs)
    # for job in jobs:
    #     print(job)


def main():
    page_num = int(get_index())
    for i in range(2, page_num + 2):
        print('开始第{}页'.format(i))
        get_next_page()
    browser.close()
    # get_all_language()


if __name__ == '__main__':
    main()