# -*- coding: UTF-8 -*-
'''
Author: Linzjian666
Date: 2024-01-13 11:29:53
LastEditors: Linzjian666
LastEditTime: 2024-01-13 21:27:29
'''
import yaml
import json
import urllib.request
import logging
import geoip2.database
import socket
import re

def process_urls(urls_file, method):
    try:
        with open(urls_file, 'r') as f:
            urls = f.read().splitlines()

        for index, url in enumerate(urls):
        # for url in urls:
            try:
                response = urllib.request.urlopen(url)
                data = response.read().decode('utf-8')
                # index += 1
                method(data, index)
            except Exception as e:
                logging.error(f"处理{url}时遇到错误: {e}")
    except Exception as e:
        logging.error(f"读取{urls_file}时遇到错误: {e}")
        return

def process_clash_meta(data, index):
    content = yaml.safe_load(data)
    try:
        proxies = content['proxies']
    except:
        proxies = []
    for i, proxy in enumerate(proxies):
        if(f"{proxy['server']}:{proxy['port']}" not in servers_list):
            location = get_physical_location(proxy['server'])
            proxy['name'] = f"{location}-{proxy['type']} | {index}-{i+1}"
            servers_list.extend(f"{proxy['server']}:{proxy['port']}") # 将已处理的代理添加到列表中
        else:
            continue
    extracted_proxies.extend(proxies)

def get_physical_location(address):
    address = re.sub(':.*', '', address)  # 用正则表达式去除端口部分
    try:
        ip_address = socket.gethostbyname(address)
    except socket.gaierror:
        ip_address = address

    try:
        reader = geoip2.database.Reader('GeoLite2-City.mmdb')  # 这里的路径需要指向你自己的数据库文件
        response = reader.city(ip_address)
        country = response.country.iso_code
        # city = response.city.name
        flag_emoji = ''
        for i in range(len(country)):
            flag_emoji += chr(ord(country[i]) + ord('🇦') - ord('A'))  # 
        if flag_emoji == '🇹🇼':
            flag_emoji = '🇨🇳'
        return f"{flag_emoji} {country}"
    except geoip2.errors.AddressNotFoundError as e:
        print(f"Error: {e}")
        return "🏳 Unknown"
    
def write_clash_profile(template_file, extracted_proxies):
    with open(template_file, 'r', encoding='utf-8') as f:
        profile = yaml.safe_load(f)
    if 'proxies' not in profile or not profile['proxies']:
        profile['proxies'] = extracted_proxies
    else:
        profile['proxies'].extend(extracted_proxies)
    for group in profile['proxy-groups']:
        if group['name'] in ['🚀 节点选择','♻️ 自动选择','📺 巴哈姆特','📺 哔哩哔哩','🌏 国内媒体','🌍 国外媒体','📲 电报信息','Ⓜ️ 微软云盘','Ⓜ️ 微软服务','🍎 苹果服务','📢 谷歌FCM','🤖 OpenAI','🐟 漏网之鱼']:
            if 'proxies' not in group or not group['proxies']:
                group['proxies'] = [proxy['name'] for proxy in extracted_proxies]
            else:
                group['proxies'].extend(proxy['name'] for proxy in extracted_proxies)
    # 写入yaml文件
    with open('./output/clash_meta.yml', 'w', encoding='utf-8') as f:
        yaml.dump(profile, f, sort_keys=False, allow_unicode=True)

    # with open('clash.yml', 'w') as f:
    #     f.write(template.format(json.dumps(extracted_proxies)))

if __name__ == "__main__":
    extracted_proxies = []
    servers_list = []

    # 处理clash urls
    process_urls('./urls/clash_urls.txt', process_clash_meta)

    # 写入clash meta配置
    write_clash_profile('./templates/clash_meta.yaml', extracted_proxies)