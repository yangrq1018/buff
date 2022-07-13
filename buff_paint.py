from buff_cookie import get_cookie_from_clipboard
import requests
import pandas as pd
from tqdm import tqdm
import time
import simplejson
import random
from requests.adapters import HTTPAdapter, Retry
from pyecharts.charts import Boxplot
import pyecharts.options as opts

session = requests.Session()
retries = Retry(total=10,
                backoff_factor=3,
                status_forcelist=[429])
session.mount('https://buff.163.com/api', HTTPAdapter(max_retries=retries))

sell_order_url = "https://buff.163.com/api/market/goods/sell_order?" + \
    "game=csgo&goods_id={goods_id}&page_num=1&sort_by=default&mode=&allow_tradable_cooldown=1&paintseed={paint_seed}&_=1648797763879"

BUFF_COOKIE = get_cookie_from_clipboard()


def get_sell_orders(goods_id, paint_seed):
    url = sell_order_url.format(
        goods_id=goods_id,
        paint_seed=paint_seed,
    )
    res = session.get(url, cookies=BUFF_COOKIE)
    if res.status_code != 200:
        raise ValueError("buff api returns status " + str(res.status_code))
    try:
        data = res.json()["data"]["items"]
    except KeyError as err:
        print(res.json())
        raise err
    except simplejson.JSONDecodeError as err:
        print("json decode failed (seed {}), content: {}".format(
            paint_seed, res.content))
        raise err
    return data


sleep_factor = 1
min_sleep = 1


def get_comparison_df(goods_id, seeds):
    with tqdm(seeds) as bar:
        items = []
        for paint_seed in bar:
            paint_seed = paint_seed.strip()
            bar.set_description("paint seed "+str(paint_seed))
            orders = get_sell_orders(goods_id, paint_seed)
            try:
                items.extend(
                    [{
                        "asset_id": o["asset_info"]["assetid"],
                        "class_id": o["asset_info"]["classid"],
                        "instance_id": o["asset_info"]["instanceid"],
                        "price": float(o["price"]),
                        "lowest_bargain_price": o["lowest_bargain_price"],
                        "can_bargain": o["can_bargain"],
                        # nametag
                        "name_tag": o["asset_info"]["info"]["fraudwarnings"],
                        # 检视图片链接
                        "inspect_image": o["asset_info"]["info"].get("inspect_url", ""),
                        # 皮肤编号
                        "paintindex": int(o["asset_info"]["info"]["paintindex"]),
                        # 模板编号
                        "paintseed": int(o["asset_info"]["info"]["paintseed"]),
                        "paintwear": float(o["asset_info"]["paintwear"]),
                    } for o in orders]
                )
            except KeyError as err:
                print(paint_seed)
                print(err)
                raise err
            time.sleep(sleep_factor * random.random() + min_sleep)
    df = pd.DataFrame(items)
    return df


def load_groups(file):
    with open(file) as fp:
        j = simplejson.load(fp)
    return {k: v.split(",") for k, v in j["groups"].items()}, j["sorted_keys"]

groups, keys = load_groups("fn_marble_tiers.json")
    

# 崭新大理石蝴蝶
fn_marble = "42563"

df_dict = {}
for tier_name, seeds in groups.items():
    df_dict[tier_name] = get_comparison_df(fn_marble, seeds)


box_plot = Boxplot()
(
    box_plot
    .add_xaxis(sorted(groups.keys()))
    .add_yaxis(series_name="", y_axis=box_plot.prepare_data(
        [
            df_dict[key].query("price <= 20000")["price"].values
            for key in keys
        ]
    ))
    .set_global_opts(
        yaxis_opts=opts.AxisOpts(
            min_=8000,
            type_="value",
            name="元",
            splitarea_opts=opts.SplitAreaOpts(
                 is_show=True, areastyle_opts=opts.AreaStyleOpts(opacity=1)
            ),
        ),
        title_opts=opts.TitleOpts(
            title="渐变大理石蝴蝶刀Tier价格"
        )
    )
)
box_plot.render_notebook()

writer = pd.ExcelWriter('fn_marble.xlsx', engine='xlsxwriter')
for k in keys:
    df_dict[k].to_excel(writer, sheet_name=k, index=False)
writer.save()
