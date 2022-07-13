import requests
import bs4
import pandas as pd
import re
from tqdm import tqdm
import browser_cookie3


def read_buy_page(page, status=None):
    url = "https://buff.163.com/market/buy_order/history?game=csgo&page_num={page}"
    if status:
        url = url + "&state=" + status
    return read_page(url.format(page=page), "buy")


def read_sell_page(page, status=None):
    url = "https://buff.163.com/market/sell_order/history?game=csgo&page_num={page}"
    if status:
        url = url + "&state=" + status
    return read_page(url.format(page=page), "sell")


def bargain(x):
    items = x.split()
    if len(items) == 1:
        return x
    try:
        return float(items[1])
    except:
        return x


session = requests.session()
session.cookies = browser_cookie3.edge()


def read_page(url, direction):
    res = session.get(url)
    soup = bs4.BeautifulSoup(res.content, features="lxml")
    if soup.select_one(".nodata") is not None:
        return None
    table = soup.select_one(".detail-tab-cont .list_tb")

    goods_link = table.select("div.name-cont a")
    goods_link = [x.attrs["href"] for x in goods_link]

    df = pd.read_html(str(table))[0]
    df = df.drop(columns=df.columns[:2], axis=1)
    df.columns = ["饰品"] + list(df.columns[1:])
    order_snos = [tr.attrs["id"]
                  for tr in table.select("tr") if "id" in tr.attrs]
    if direction == "buy":
        df['sno'] = order_snos

    # 替换全角标点符号，方便匹配
    df["饰品"] = df["饰品"].map(lambda x: x.replace(": ", ":"))

    if "售价" in df.columns:
        # 去掉人民币符合，方便转换成float
        df["售价"] = df["售价"].map(lambda x: re.sub(
            "[()¥]", "", x).strip()).map(bargain)
    else:
        df["价格"] = df["价格"].map(lambda x: re.sub("[()¥]", "", x).strip())

    df["状态"] = df["状态"].map(lambda x: x.strip().replace("查看详情", ""))
    df["商品链接"] = goods_link
    return df


def read_pages(dir, successful=False):
    dfs = []
    if dir == "sell":
        f = read_sell_page
    else:
        f = read_buy_page

    def gen():
        i = 1
        while True:
            df = f(i, status="success" if successful else None)
            if df is None:
                return
            i += 1
            yield df

    for df in tqdm(gen(), desc="read {} pages".format(dir)):
        dfs.append(df)

    df = pd.concat(dfs)
    return df.reset_index(drop=True)


def analyse(buy: pd.DataFrame, sell: pd.DataFrame, writer: pd.ExcelWriter):
    inter = pd.Index(set(buy.index).intersection(sell.index))
    buy = buy.loc[inter]
    sell = sell.loc[inter]

    # add an e
    buy['id'] = buy.groupby('饰品').cumcount()
    sell['id'] = sell.groupby('饰品').cumcount()
    paired = buy. \
        merge(sell, on=['id', '饰品'], how='outer',  suffixes=['_buy', '_sell']). \
        drop(['id', '商品链接_buy', '商品链接_sell'], axis=1)
    paired.dropna(axis=0, how='any', subset=['价格', '售价'], inplace=True)
    paired['收益'] = paired['售价'] - paired['价格']
    paired['手续费'] = paired['售价'] * 2.5 / 100
    paired['手续费'] = paired['手续费'].round(2)
    paired['费后收益'] = paired['收益'] - paired['手续费']

    paired.sort_values('费后收益', inplace=True)
    paired.to_excel(writer, sheet_name="配对交易")
    print("raw pnl",  paired['收益'].sum())
    print("after fee pnl",  paired['费后收益'].sum())


if __name__ == '__main__':
    buy = read_pages("buy", successful=True)
    sell = read_pages("sell", successful=True)
    # 处理还价
    buy['价格'] = buy['价格'].map(lambda x: x.split(' ')[0])
    buy['价格'] = buy['价格'].astype(float)
    sell['售价'] = sell['售价'].astype(float)
    writer = pd.ExcelWriter('profit.xlsx', engine='xlsxwriter')
    buy.to_excel(writer, sheet_name="买入")
    sell.to_excel(writer, sheet_name="卖出")
    analyse(buy, sell, writer)
    writer.save()
