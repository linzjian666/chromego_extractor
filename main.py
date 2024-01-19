# -*- coding: UTF-8 -*-
'''
Author: Linzjian666
Date: 2024-01-13 11:29:53
LastEditors: Linzjian666
LastEditTime: 2024-01-19 18:46:22
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
    try:
        content = yaml.safe_load(data)
        try:
            proxies = content['proxies']
        except:
            proxies = []
        for i, proxy in enumerate(proxies):
            if(f"{proxy['server']}:{proxy['port']}" not in servers_list):
                location = get_physical_location(proxy['server'])
                proxy['name'] = f"{location}-{proxy['type']} | {index}-{i+1}"
                servers_list.append(f"{proxy['server']}:{proxy['port']}") # 将已处理的代理添加到列表中
            else:
                continue
        extracted_proxies.extend(proxies)
    except Exception as e:
        logging.error(f"处理Clash Meta配置{index}时遇到错误: {e}")
        return

def process_hysteria(data, index):
    try:
        content = json.loads(data)
        # print(content)
        auth = content["auth_str"]
        server_ports_slt = content["server"].split(":")
        server = server_ports_slt[0]
        ports = server_ports_slt[1]
        ports_slt = ports.split(",")
        server_port = int(ports_slt[0])
        if len(ports_slt) > 1:
            mport = ports_slt[1]
        else:
            mport = server_port
        # fast_open = content["fast_open"]
        fast_open = True
        insecure = content["insecure"]
        server_name = content["server_name"]
        alpn = content["alpn"]
        protocol = content["protocol"]
        location = get_physical_location(server)
        name = f"{location}-Hysteria | {index}-0"

        proxy = {
            "name": name,
            "type": "hysteria",
            "server": server,
            "port": server_port,
            "ports": mport,
            "auth_str": auth,
            "up": 80,
            "down": 100,
            "fast-open": fast_open,
            "protocol": protocol,
            "sni": server_name,
            "skip-cert-verify": insecure,
            "alpn": [alpn]
        }
        if(f"{proxy['server']}:{proxy['port']}" not in servers_list):
            extracted_proxies.append(proxy)
            servers_list.append(f"{proxy['server']}:{proxy['port']}")
        else:
            return
    except Exception as e:
        logging.error(f"处理Hysteria配置{index}时遇到错误: {e}")
        return

def process_hysteria2(data, index):
    try:
        content = json.loads(data)
        auth = content["auth"]
        server_ports_slt = content["server"].split(":")
        server = server_ports_slt[0]
        ports = server_ports_slt[1]
        ports_slt = ports.split(",")
        server_port = int(ports_slt[0])
        # fast_open = content["fast_open"]
        fast_open = True
        insecure = content["tls"]["insecure"]
        sni = content["tls"]["sni"]
        location = get_physical_location(server)
        name = f"{location}-Hysteria2 | {index}-0"

        proxy = {
            "name": name,
            "type": "hysteria2",
            "server": server,
            "port": server_port,
            "password": auth,
            "fast-open": fast_open,
            "sni": sni,
            "skip-cert-verify": insecure
        }
        if(f"{proxy['server']}:{proxy['port']}" not in servers_list):
            extracted_proxies.append(proxy)
            servers_list.append(f"{proxy['server']}:{proxy['port']}")
        else:
            return
    except Exception as e:
        logging.error(f"处理Hysteria2配置{index}时遇到错误: {e}")
        return

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
    except Exception as e:
        print(f"Error: {e}")
        return "🏳 Unknown"
    
def write_clash_profile(template_file, output_file, extracted_proxies):
    with open(template_file, 'r', encoding='utf-8') as f:
        profile = yaml.safe_load(f)
    if 'proxies' not in profile or not profile['proxies']:
        profile['proxies'] = extracted_proxies
    else:
        profile['proxies'].extend(extracted_proxies)
    for group in profile['proxy-groups']:
        if group['name'] in ['🚀 节点选择','♻️ 自动选择','⚖ 负载均衡','☁ WARP前置节点','📺 巴哈姆特','📺 哔哩哔哩','🌏 国内媒体','🌍 国外媒体','📲 电报信息','Ⓜ️ 微软云盘','Ⓜ️ 微软服务','🍎 苹果服务','📢 谷歌FCM','🤖 OpenAI','🐟 漏网之鱼']:
            if 'proxies' not in group or not group['proxies']:
                group['proxies'] = [proxy['name'] for proxy in extracted_proxies]
            else:
                group['proxies'].extend(proxy['name'] for proxy in extracted_proxies)
    # 写入yaml文件
    with open(output_file, 'w', encoding='utf-8') as f:
        yaml.dump(profile, f, sort_keys=False, allow_unicode=True)

if __name__ == "__main__":
    extracted_proxies = []
    servers_list = []

    # 处理clash urls
    process_urls('./urls/clash_meta_urls.txt', process_clash_meta)

    # 处理hysteria urls
    process_urls('./urls/hysteria_urls.txt', process_hysteria)

    # 处理hysteria2 urls
    process_urls('./urls/hysteria2_urls.txt', process_hysteria2)

    # logging.info(servers_list)

    # 写入clash meta配置
    write_clash_profile('./templates/clash_meta.yaml', './outputs/clash_meta.yaml', extracted_proxies)
    write_clash_profile('./templates/clash_meta_warp.yaml', './outputs/clash_meta_warp.yaml', extracted_proxies)