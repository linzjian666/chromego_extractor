<div align="center">

# ChromeGo Extractor

A python script to extract ChromeGo Proxies

一个用来提取ChromeGo代理节点的Python脚本

**中文** | [English](README_EN.md)

</div>

> 鸣谢
> - 感谢[ChromeGo](https://github.com/bannedbook/fanqiang)项目
> - 感谢[Alvin9999](https://github.com/Alvin9999/)大佬
> - 感谢[chromegopacs](https://github.com/markbang/chromegopacs)提供的区域代码设置思路

## 使用说明
### 订阅链接：
> 本项目已配置Github Actions自动运行，最近提取于：`UTC 2025-03-19 12:14:19`

- Clash Meta (不带WARP):
  
  [https://raw.githubusercontent.com/linzjian666/chromego_extractor/main/outputs/clash_meta.yaml](https://raw.githubusercontent.com/linzjian666/chromego_extractor/main/outputs/clash_meta.yaml)

- Clash Meta (带WARP):
  
  [https://raw.githubusercontent.com/linzjian666/chromego_extractor/main/outputs/clash_meta_warp.yaml](https://raw.githubusercontent.com/linzjian666/chromego_extractor/main/outputs/clash_meta_warp.yaml)

- Base64:

  [https://raw.githubusercontent.com/linzjian666/chrome_extractor/main/outputs/base64.txt](https://raw.githubusercontent.com/linzjian666/chrome_extractor/main/outputs/base64.txt)

- Proxy urls:

  [https://raw.githubusercontent.com/linzjian666/chromego_extractor/main/outputs/proxy_urls.txt](https://raw.githubusercontent.com/linzjian666/chromego_extractor/main/outputs/proxy_urls.txt)

<details>

<summary>(备用)</summary>

- Clash Meta (不带WARP):
  
  [https://gcore.jsdelivr.net/gh/linzjian666/chromego_extractor@main/outputs/clash_meta.yaml](https://gcore.jsdelivr.net/gh/linzjian666/chromego_extractor@main/outputs/clash_meta.yaml)

- Clash Meta (带WARP):
  
  [https://gcore.jsdelivr.net/gh/linzjian666/chromego_extractor@main/outputs/clash_meta_warp.yaml](https://gcore.jsdelivr.net/gh/linzjian666/chromego_extractor@main/outputs/clash_meta_warp.yaml)
  
- Base64:

  [https://gcore.jsdelivr.net/gh/linzjian666/chromego_extractor@main/outputs/base64.txt](https://gcore.jsdelivr.net/gh/linzjian666/chromego_extractor@main/outputs/base64.txt)

- Proxy urls:

  [https://gcore.jsdelivr.net/gh/linzjian666/chromego_extractor@main/outputs/proxy_urls.txt](https://gcore.jsdelivr.net/gh/linzjian666/chromego_extractor@main/outputs/proxy_urls.txt)

</details>

### 本地运行：
<details>

#### 1. 环境要求
确保你的环境满足以下要求：
- Python 3.x
- 安装所需的依赖：`pip install requests`

#### 2. 下载脚本
克隆本项目到本地：
```bash
git clone https://github.com/linzjian666/chromego-extractor.git
```

#### 3. 运行脚本
1. 进入项目目录：
```bash
cd chromego-extractor
```
2. 运行脚本：
```bash
python main.py
```

#### 4. 获取代理信息
脚本将提取 ChromeGo 代理节点信息，并保存到`outputs`目录中。

#### 5. 其他
根据需要，你可以自行修改脚本的一些配置，比如保存文件的路径等。

</details>

## 免责声明

**本项目仅供学习交流使用，作者不对其在实际使用中产生的任何后果负任何法律或技术责任。**

1. **使用风险**：用户在使用本项目时需自行承担风险。作者无法保证生成的配置信息适用于所有使用情境，因此可能会导致潜在的问题或错误。

2. **合规性和法律遵守**：用户使用本项目必须遵守部署服务器所在地、所在国家和用户所在国家的法律法规及云服务提供商的政策。作者不对使用者任何不当行为负责。

3. **无担保**：作者不提供关于本项目的任何担保或保证。本项目可能会受到外部因素的影响，如云服务提供商政策变更、网络故障等。用户需自行评估和处理这些风险。

4. **技术支持**：作者不承诺提供关于本项目的技术支持。用户需自行解决配置信息可能出现的问题。

5. **数据隐私**：用户需谨慎处理配置信息中可能包含的个人数据或敏感信息。作者不对因配置信息泄漏或不当使用而导致的数据隐私问题负责。

**服务对象限定为非中国大陆地区用户。在使用本项目前，请仔细阅读并理解免责声明。如果不同意免责声明中的任何条款，请勿使用本项目！**

## 许可协议

本项目遵循 MIT 许可协议。有关详细信息，请参阅 [LICENSE](LICENSE) 文件。

---
**欢迎提出问题或为本项目的开发做出贡献！**

<!--
## 统计
![Star History Chart](https://api.star-history.com/svg?repos=linzjian666/chromego_extractor&type=Date)
-->
