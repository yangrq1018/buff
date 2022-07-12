import pyperclip
import json
from http.cookies import SimpleCookie

# 从Chrome的Cookie插件里导出到剪贴板
def get_cookie(where=None):
    cookie_json_string = ""
    if where is None or where == "clipboard":
        cookie_json_string = pyperclip.paste()
    else:
        cookie_json_string = open(where).read()

    try:
        cookie = json.loads(cookie_json_string)
    except json.JSONDecodeError as e:
        print("cannot parse json, copy your cookie to clipboard", e)
        raise e
        
    buff_cookies = {c["name"]:c["value"] for c in cookie if c["domain"] == "buff.163.com"}
    buff_cookies_simple = SimpleCookie(";".join([k + "=" + v for k, v in buff_cookies.items()]))
    return  {i.key:i.value for i in buff_cookies_simple.values()}