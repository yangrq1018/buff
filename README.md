# Buff脚本


CMD终端

```
pip install -r requirements.txt
```

1. Buff收益脚本

浏览器打开[Buff](https://buff.163.com/)，登陆。

Chrome安装**EditThisCookie**插件，方便复制网页Cookie。
点击地址栏右边的饼干图标，“导出Cookies”按钮，Cookie被复制到剪贴板上，把项目里的`cookie.json`替换为剪贴板里的内容。

Python运行`buff_pnl.py`，在当前目录下生产一个`profit.xlsx`工作表。