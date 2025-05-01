# -*- coding: UTF-8 -*-
"""
Author: Linzjian666
Date: 2024-01-13 11:29:53
LastEditors: Linzjian666
LastEditTime: 2025-05-01 09:50:00
"""
import yaml
import json
import urllib.request
import logging
import geoip2.database
import socket
import re
import base64

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
            if("network" in proxy and f"{proxy['network']}" == "ws"):
                # host = proxy['ws-opts']['headers']['host']
                
                try:
                    host = proxy['ws-opts']['headers']['host']
                except KeyError:
                    try:
                        host = proxy['ws-opts']['headers']['Host']
                    except KeyError:
                        host = '' 
                
                if(f"{proxy['server']}:{proxy['port']}-{host}-ws" not in servers_list):
                    location = get_physical_location(proxy['server'])
                    proxy['name'] = f"{location}-{proxy['type']} | {index}-{i+1}"
                    servers_list.append(f"{proxy['server']}:{proxy['port']}-{host}-ws")
                else:
                    continue
            elif(f"{proxy['server']}:{proxy['port']}-{proxy['type']}" not in servers_list):
                location = get_physical_location(proxy['server'])
                proxy['name'] = f"{location}-{proxy['type']} | {index}-{i+1}"
                servers_list.append(f"{proxy['server']}:{proxy['port']}-{proxy['type']}") 
            else:
                continue
            extracted_proxies.append(proxy)
        # extracted_proxies.extend(proxies)
    except Exception as e:
        logging.error(f"处理Clash Meta配置{index}时遇到错误: {e}")
        return

def process_hysteria(data, index):
    try:
        content = json.loads(data)
        # print(content)
        auth = content['auth_str']
        server_ports_slt = content['server'].split(":")
        server = server_ports_slt[0]
        ports = server_ports_slt[1]
        ports_slt = ports.split(',')
        server_port = int(ports_slt[0])
        if(len(ports_slt) > 1):
            mport = ports_slt[1]
        else:
            mport = server_port
        fast_open = content.get('fast_open', True)
        # fast_open = True
        insecure = content['insecure']
        sni = content['server_name']
        alpn = content['alpn']
        protocol = content['protocol']
        location = get_physical_location(server)
        name = f"{location}-Hysteria | {index}-0"

        proxy = {
            "name": name,
            "type": "hysteria",
            "server": server,
            "port": server_port,
            "ports": mport,
            "auth-str": auth,
            "up": 80,
            "down": 100,
            "fast-open": fast_open,
            "protocol": protocol,
            "sni": sni,
            "skip-cert-verify": insecure,
            "alpn": [alpn]
        }
        if(f"{proxy['server']}:{proxy['port']}-hysteria" not in servers_list):
            extracted_proxies.append(proxy)
            servers_list.append(f"{proxy['server']}:{proxy['port']}-hysteria")
        else:
            return
    except Exception as e:
        logging.error(f"处理Hysteria配置{index}时遇到错误: {e}")
        return

def process_hysteria2(data, index):
    try:
        content = json.loads(data)
        auth = content['auth']
        server_ports_slt = content['server'].split(":")
        server = server_ports_slt[0]
        ports = server_ports_slt[1]
        ports_slt = ports.split(',')
        server_port = int(ports_slt[0])
        insecure = content['tls']['insecure']
        sni = content['tls']['sni']
        location = get_physical_location(server)
        name = f"{location}-Hysteria2 | {index}-0"

        proxy = {
            "name": name,
            "type": "hysteria2",
            "server": server,
            "port": server_port,
            "password": auth,
            "sni": sni,
            "skip-cert-verify": insecure
        }
        if(f"{proxy['server']}:{proxy['port']}-hysteria2" not in servers_list):
            extracted_proxies.append(proxy)
            servers_list.append(f"{proxy['server']}:{proxy['port']}-hysteria2")
        else:
            return
    except Exception as e:
        logging.error(f"处理Hysteria2配置{index}时遇到错误: {e}")
        return

def process_xray(data, index):
    try:
        content = json.loads(data)
        outbounds = content['outbounds']
        pending_proxy = outbounds[0]
        type = pending_proxy['protocol']
        if(type == "vmess"):
            server = pending_proxy['settings']['vnext'][0]['address']
            port = pending_proxy['settings']['vnext'][0]['port']
            uuid = pending_proxy['settings']['vnext'][0]['users'][0]['id']
            alterId = pending_proxy['settings']['vnext'][0]['users'][0]['alterId']
            cipher = pending_proxy['settings']['vnext'][0]['users'][0]['security']
            network = pending_proxy['streamSettings']['network']
            security = pending_proxy['streamSettings'].get('security', "none")
            location = get_physical_location(server)
            name = f"{location}-{type} | {index}-0"
            if(security == "none"):
                tls = False
            else:
                tls = True
            sni = pending_proxy['streamSettings'].get('tlsSettings', {}).get('serverName', "")
            allowInsecure = pending_proxy['streamSettings'].get('tlsSettings', {}).get('allowInsecure', False)

            if(network in ['tcp','ws','grpc','h2']):
                ws_path = pending_proxy['streamSettings'].get('wsSettings', {}).get('path', "")
                ws_headers = pending_proxy['streamSettings'].get('wsSettings', {}).get('headers', {})
                grpc_serviceName = pending_proxy['streamSettings'].get('grpcSettings', {}).get('serviceName', "/")
                h2_path = pending_proxy['streamSettings'].get('httpSettings', {}).get('path', "/")
                h2_host = pending_proxy['streamSettings'].get('httpSettings', {}).get('host', [])

                proxy = {
                    "name": name,
                    "type": "vmess",
                    "server": server,
                    "port": port,
                    "uuid": uuid,
                    "alterId": alterId,
                    "cipher": cipher,
                    "tls": tls,
                    "servername": sni,
                    "skip-cert-verify": allowInsecure,
                    "network": network,
                    "ws-opts": {
                        "path": ws_path,
                        "headers": ws_headers
                    },
                    "grpc-opts": {
                        "serviceName": grpc_serviceName
                    },
                    "h2-opts": {
                        "path": h2_path,
                        "host": h2_host
                    }
                }
            else:
                logging.error(f"处理Xray配置{index}时遇到错误: 不支持的VMess传输协议: {network}")
                return
        elif(type == "vless"):
            server = pending_proxy['settings']['vnext'][0]['address']
            port = pending_proxy['settings']['vnext'][0]['port']
            uuid = pending_proxy['settings']['vnext'][0]['users'][0]['id']
            flow = pending_proxy['settings']['vnext'][0]['users'][0].get('flow', "")
            security = pending_proxy['streamSettings'].get('security', "none")
            network = pending_proxy['streamSettings']['network']
            location = get_physical_location(server)
            name = f"{location}-{type} | {index}-0"

            if(security == "none"):
                tls = False
            else:
                tls = True
            if(security == "reality"):
                realitySettings = pending_proxy['streamSettings'].get('realitySettings', {})
                sni = realitySettings.get('serverName', "")
                short_id = realitySettings.get('shortId', "")
                publicKey = realitySettings['publicKey']
                fingerprint = realitySettings['fingerprint']
                
                grpc_serviceName = pending_proxy['streamSettings'].get('grpcSettings', {}).get('serviceName', "/")
                proxy = {
                    "name": name,
                    "type": "vless",
                    "server": server,
                    "port": port,
                    "uuid": uuid,
                    "flow": flow,
                    "tls": tls,
                    "servername": sni,
                    "network": network,
                    "client-fingerprint": fingerprint,
                    "grpc-opts": {
                        "grpc-service-name": grpc_serviceName
                    },
                    "reality-opts": {
                        "public-key": publicKey,
                        "short-id": short_id,
                    }
                }
            else:
                if(network in ['tcp','ws','grpc']):
                    sni = pending_proxy['streamSettings'].get('tlsSettings', {}).get('serverName', "")
                    allowInsecure = pending_proxy['streamSettings'].get('tlsSettings', {}).get('allowInsecure', False)

                    ws_path = pending_proxy['streamSettings'].get('wsSettings', {}).get('path', "")
                    ws_headers = pending_proxy['streamSettings'].get('wsSettings', {}).get('headers', {})
                    grpc_serviceName = pending_proxy['streamSettings'].get('grpcSettings', {}).get('serviceName', "/")

                    proxy = {
                        "name": name,
                        "type": "vless",
                        "server": server,
                        "port": port,
                        "uuid": uuid,
                        "tls": tls,
                        "servername": sni,
                        "skip-cert-verify": allowInsecure,
                        "network": network,
                        "ws-opts": {
                            "path": ws_path,
                            "headers": ws_headers
                        },
                        "grpc-opts": {
                            "serviceName": grpc_serviceName
                        }
                    }
                else:
                    logging.error(f"处理Xray配置{index}时遇到错误: 不支持的VLESS传输协议: {network}")
                    return
        else:
            logging.error(f"处理Xray配置{index}时遇到错误: 不支持的传输协议: {type}")
            return
        if(f"{proxy['server']}:{proxy['port']}-{proxy['type']}" not in servers_list):
            extracted_proxies.append(proxy)
            servers_list.append(f"{proxy['server']}:{proxy['port']}-{proxy['type']}")
        else:
            return
        
        # print(security)
        # if(type == "vmess"):
        #     
        # elif(type == "shadowsocks"):
        #     cipher = pending_proxy['settings']['vnext"][0]['users"][0]['method"]
        # else:
        #     cipher = "none"

    except Exception as e:
        logging.error(f"处理Xray配置{index}时遇到错误: {e}")

def get_physical_location(address):
    address = re.sub(":.*", "", address)  # 用正则表达式去除端口部分
    try:
        ip_address = socket.gethostbyname(address)
    except socket.gaierror:
        ip_address = address

    try:
        reader = geoip2.database.Reader("GeoLite2-City.mmdb")  # 这里的路径需要指向你自己的数据库文件
        response = reader.city(ip_address)
        country = response.country.iso_code
        # city = response.city.name
        flag_emoji = ""
        for i in range(len(country)):
            flag_emoji += chr(ord(country[i]) + ord("🇦") - ord("A"))  # 
        if(flag_emoji == "🇹🇼"):
            flag_emoji = "🇨🇳"
        return f"{flag_emoji} {country}"
    except Exception as e:
        # logging.error(f"区域代码获取失败: {e}")
        return "🏳 Unknown"
    
def write_clash_meta_profile(template_file, output_file, extracted_proxies):
    with open(template_file, 'r', encoding='utf-8') as f:
        profile = yaml.safe_load(f)
    if("proxies" not in profile or not profile['proxies']):
        profile['proxies'] = extracted_proxies
    else:
        profile['proxies'].extend(extracted_proxies)
    for group in profile['proxy-groups']:
        if(group['name'] in ['🚀 节点选择','♻️ 自动选择','⚖ 负载均衡','☁ WARP前置节点','📺 巴哈姆特','📺 哔哩哔哩','🌏 国内媒体','🌍 国外媒体','📲 电报信息','Ⓜ️ 微软云盘','Ⓜ️ 微软服务','🍎 苹果服务','📢 谷歌FCM','🤖 OpenAI','🐟 漏网之鱼']):
            if("proxies" not in group or not group['proxies']):
                group['proxies'] = [proxy['name'] for proxy in extracted_proxies]
            else:
                group['proxies'].extend(proxy['name'] for proxy in extracted_proxies)
    # 写入yaml文件
    with open(output_file, 'w', encoding='utf-8') as f:
        yaml.dump(profile, f, sort_keys=False, allow_unicode=True)

def write_proxy_urls_file(output_file, proxies):
    proxy_urls = []
    for proxy in proxies:
        try:
            if(proxy['type'] == "vless"):
                name = proxy['name']
                server = proxy['server']
                port = proxy['port']
                uuid = proxy['uuid']
                tls = int(proxy.get('tls', 0))
                network = proxy['network']
                flow = proxy.get('flow', "")
                grpc_serviceName = proxy.get('grpc-opts', {}).get('grpc-service-name', "")
                ws_path = proxy.get('ws-opts', {}).get('path', "")
                try:
                    ws_headers_host = proxy.get('ws-opts', {}).get('headers', {}).get('host', "")
                except:
                    ws_headers_host = proxy.get('ws-opts', {}).get('headers', {}).get('Host', "")

                if(tls == 0):
                    proxy_url = f"vless://{uuid}@{server}:{port}?encryption=none&flow={flow}&security=none&type={network}&serviceName={grpc_serviceName}&host={ws_headers_host}&path={ws_path}#{name}"
                else:
                    sni = proxy.get('servername', "")
                    publicKey = proxy.get('reality-opts', {}).get('public-key', "")
                    short_id = proxy.get('reality-opts', {}).get('short-id', "")
                    fingerprint = proxy.get('client-fingerprint', "")
                    if(not publicKey == ""):
                        proxy_url = f"vless://{uuid}@{server}:{port}?encryption=none&flow={flow}&security=reality&sni={sni}&fp={fingerprint}&pbk={publicKey}&sid={short_id}&type={network}&serviceName={grpc_serviceName}&host={ws_headers_host}&path={ws_path}#{name}"
                    else:
                        insecure = int(proxy.get('skip-cert-verify', 0))
                        proxy_url = f"vless://{uuid}@{server}:{port}?encryption=none&flow={flow}&security=tls&sni={sni}&fp={fingerprint}&insecure={insecure}&type={network}&serviceName={grpc_serviceName}&host={ws_headers_host}&path={ws_path}#{name}" 
            
            elif(proxy['type'] == "vmess"):
                name = proxy['name']
                server = proxy['server']
                port = proxy['port']
                uuid = proxy['uuid']
                alterId = proxy['alterId']
                if(int(proxy.get('tls', 0)) == 1):
                    tls = "tls"
                else:
                    tls = ""
                sni = proxy.get('servername', "")
                network = proxy['network']
                if(network == "tcp"):
                    type = "none"
                    path = ""
                    host = ""
                elif(network == "ws"):
                    type = "none"
                    path = proxy.get('ws-opts', {}).get('path', "")
                    try:
                        host = proxy.get('ws-opts', {}).get('headers', {}).get('host', "")
                    except:
                        host = proxy.get('ws-opts', {}).get('headers', {}).get('Host', "")
                elif(network == "grpc"):
                    type = "gun"
                    path = proxy.get('grpc-opts', {}).get('grpc-service-name', "")
                    host = ""
                elif(network == "h2"):
                    type = "none"
                    path = proxy.get('h2-opts', {}).get('path', "")
                    # 获取host并将host列表转换为逗号分隔的字符串
                    host = proxy.get('h2-opts', {}).get('host', [])
                    host = ','.join(host)
                else:
                    continue
                vmess_meta = {
                    "v": "2",
                    "ps": name,
                    "add": server,
                    "port": port,
                    "id": uuid,
                    "aid": alterId,
                    "net": network,
                    "type": type,
                    "host": host,
                    "path": path,
                    "tls": tls,
                    "sni": sni,
                    "alpn": ""
                }
                # 将字典`vmess_meta`转换为 JSON 格式字符串并进行 Base64 编码
                vmess_meta = base64.b64encode(json.dumps(vmess_meta).encode('utf-8')).decode('utf-8')
                # 合并为完整的 `vmess://` URL
                proxy_url = "vmess://" + vmess_meta
            
            elif(proxy['type'] == "ss"):
                name = proxy['name']
                server = proxy['server']
                port = proxy['port']
                password = proxy['password']
                cipher = proxy['cipher']
                ss_meta = base64.b64encode(f"{cipher}:{password}").decode('utf-8')
                ss_meta = f"{ss_meta}@{server}:{port}#{name}"
                proxy_url = "ss://" + ss_meta

            
            elif(proxy['type'] == "hysteria"):
                name = proxy['name']
                server = proxy['server']
                port = proxy['port']
                protocol = proxy.get('protocol', "udp")
                insecure = int(proxy.get('skip-cert-verify', 0))
                peer = proxy.get('sni', "")
                try:
                    auth = proxy['auth-str']
                except:
                    auth = proxy['auth_str']
                upmbps = proxy.get('up', "11")
                downmbps = proxy.get('down', "55")
                alpn = proxy['alpn']
                alpn = ','.join(alpn) # 将 `alpn` 列表转换为逗号分隔的字符串
                obfs = proxy.get('obfs', "")
                proxy_url = f"hysteria://{server}:{port}/?protocol={protocol}&insecure={insecure}&peer={peer}&auth={auth}&upmbps={upmbps}&downmbps={downmbps}&alpn={alpn}&obfs={obfs}#{name}"
            
            elif(proxy['type'] == "hysteria2"):
                name = proxy['name']
                server = proxy['server']
                port = proxy['port']
                auth = proxy['password']
                sni = proxy.get('sni', "")
                insecure = int(proxy.get('skip-cert-verify', 0))
                # 如果`proxy`包含`obfs`字段，且`obfs`字段不为空
                if("obfs" in proxy and proxy['obfs'] != ""):
                    obfs = proxy['obfs']
                    obfs_password = proxy['obfs-password']
                    proxy_url = f"hysteria2://{auth}@{server}:{port}/?sni={sni}&insecure={insecure}&obfs={obfs}&obfs-password={obfs_password}#{name}"
                else:
                    proxy_url = f"hysteria2://{auth}@{server}:{port}/?sni={sni}&insecure={insecure}#{name}"
            
            elif(proxy['type'] == "tuic"):
                name = proxy['name']
                server = proxy['server']
                port = proxy['port']
                uuid = proxy['uuid']
                password = proxy.get('password', "")
                congestion_controller = proxy.get('congestion-controller', "bbr")
                udp_relay_mode = proxy.get('udp-relay-mode', "naive")
                sni = proxy.get('sni', "")
                alpn = proxy.get('alpn', [])
                alpn = ','.join(alpn) # 将 `alpn` 列表转换为逗号分隔的字符串
                allowInsecure = int(proxy.get('skip-cert-verify', 1))
                disable_sni = int(proxy.get('disable-sni', 0))
                proxy_url = f"tuic://{uuid}:{password}@{server}:{port}/?congestion_controller={congestion_controller}&udp_relay_mode={udp_relay_mode}&sni={sni}&alpn={alpn}&allow_insecure={allowInsecure}&disable_sni={disable_sni}#{name}"

            else:
                logging.error(f"处理 {proxy['name']} 时遇到问题: 不支持的协议: {proxy['type']}")
                continue

            # print(proxy_url)
            proxy_urls.append(proxy_url)
        except Exception as e:
            logging.error(f"处理 {proxy['name']} 时遇到问题: {e}")
            continue
    # 将`proxy_urls`写入`output_file`
    with open(output_file, 'w', encoding='utf-8') as f:
        for proxy_url in proxy_urls:
            f.write(proxy_url + "\n")

def write_base64_file(output_file, proxy_urls_file):
    with open(proxy_urls_file, 'r', encoding='utf-8') as f:
        proxy_urls = f.read()
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(base64.b64encode(proxy_urls.encode('utf-8')).decode('utf-8'))

if __name__ == "__main__":
    extracted_proxies = []
    servers_list = []

    # 处理clash meta urls
    process_urls("./urls/clash_meta_urls.txt", process_clash_meta)

    # 处理hysteria urls
    process_urls("./urls/hysteria_urls.txt", process_hysteria)

    # 处理hysteria2 urls
    process_urls("./urls/hysteria2_urls.txt", process_hysteria2)

    # 处理Xray urls
    process_urls("./urls/xray_urls.txt", process_xray)

    # logging.info(servers_list)

    # # 写入clash meta配置
    write_clash_meta_profile("./templates/clash_meta.yaml", "./outputs/clash_meta.yaml", extracted_proxies)
    write_clash_meta_profile("./templates/clash_meta_warp.yaml", "./outputs/clash_meta_warp.yaml", extracted_proxies)

    # 写入代理urls
    write_proxy_urls_file("./outputs/proxy_urls.txt", extracted_proxies)
    
    write_base64_file("./outputs/base64.txt", "./outputs/proxy_urls.txt")
