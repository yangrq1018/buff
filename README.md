# Buff脚本


## 安装依赖
解压zip文件，点开文件夹，右键“终端打开”，运行以下命令
```
pip install -r requirements.txt
```


1. Buff收益脚本
    **Edge浏览器**打开[Buff](https://buff.163.com/)，登陆，关闭浏览器即可。

    Python运行`buff_pnl.py`（或者双击`generate.bat`），等待爬取完毕，给出Raw PnL，在当前目录下产生一个`profit.xlsx`工作表。
    `profit.xlsx`的Sheets分别为买、卖、配对交易的收益。

    > Buff登陆Cookie的有效期是10天，10天后需要再次在浏览器登陆。

2. 渐变大理石大红头扫描