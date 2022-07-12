# Buff脚本


## 前置步骤
安装依赖，CMD终端
```
pip install -r requirements.txt
```

安装浏览器插件：  
Chrome安装**EditThisCookie**插件，方便复制网页Cookie。
> 国内用户无法打开Chrome官方商店，镜像站EditThisCookie[下载地址](https://www.crx4chrome.com/crx/1148/)
> 下载`crx`文件后，打开Chrome的扩展管理页面，拖进去安装

1. Buff收益脚本

浏览器打开[Buff](https://buff.163.com/)，登陆。点击地址栏右边的饼干图标，“导出Cookies”按钮，Cookie被复制到剪贴板上，把项目里的`cookie.json`替换为剪贴板里的内容。

Python运行`buff_pnl.py`（或者双击`generate.bat`），等待爬取完毕，给出Raw PnL，在当前目录下产生一个`profit.xlsx`工作表。

`profit.xlsx`的Sheets分别为买、卖、匹配买和匹配卖。

注意：
- Buff登陆Cookie的有效期是10天，10天后需要再次登陆和替换`cookie.json`。

2. 渐变大理石大红头扫描