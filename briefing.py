"""晨间简报 - GitHub Actions 云版本"""
import json, urllib.request, urllib.parse, xml.etree.ElementTree as ET
from datetime import datetime

FEISHU_HOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/343babb3-dd3a-4c92-8ae2-d41e0917a2a3"
CITY = "Guangzhou"

def send_feishu(title, content):
    text = f"{title}\n\n{content}"
    body = json.dumps({"msg_type": "text", "content": {"text": text}}).encode("utf-8")
    req = urllib.request.Request(FEISHU_HOOK, data=body, method="POST",
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        r = json.loads(resp.read().decode("utf-8"))
        return r.get("code") == 0, r.get("msg", "")

def get_weather():
    try:
        url = f"https://wttr.in/{CITY}?format=j1"
        req = urllib.request.Request(url, headers={"User-Agent": "curl/8.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        c = data.get("current_condition", [{}])[0]
        t = data.get("weather", [{}])[0]
        desc = c.get("weatherDesc", [{}])[0].get("value","?").split(",")[0].strip()
        return [
            f"📍 广州",
            f"🌡 {desc}  {c.get('temp_C','?')}°C（体感 {c.get('FeelsLikeC','?')}°C）",
            f"📊 {t.get('mintempC','?')}°C ~ {t.get('maxtempC','?')}°C  |  湿度 {c.get('humidity','?')}%  |  风力 {c.get('windspeedKmph','?')}km/h",
            f"🌅 {t.get('astronomy',[{}])[0].get('sunrise','?')}  🌇 {t.get('astronomy',[{}])[0].get('sunset','?')}",
        ]
    except Exception as e:
        print(f"[天气] {e}")
        return ["🌡 天气暂不可用"]

def get_36kr():
    try:
        req = urllib.request.Request("https://36kr.com/feed",
            headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            tree = ET.fromstring(resp.read().decode("utf-8"))
        items = []
        for item in tree.iter("item"):
            title = item.find("title").text or ""
            if title:
                items.append(title)
            if len(items) >= 8:
                break
        return items
    except Exception as e:
        print(f"[36kr] {e}")
        return []

def get_weibo():
    urls = [
        "https://tenapi.cn/v2/weibohot",
        "https://api.vvhan.com/api/hotlist/wbHot",
        "https://api.uomg.com/api/weibo.hots",
    ]
    for url in urls:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            items = []
            for item in data.get("data", [])[:8]:
                name = item.get("name", "") or item.get("title", "") or item.get("word", "")
                hot = item.get("hot", "") or str(item.get("hotnum", ""))
                if name:
                    items.append(f"{name}  🔥{hot}" if hot else name)
            if items:
                return items
        except Exception:
            continue
    return []

def get_sspai():
    try:
        req = urllib.request.Request("https://sspai.com/feed",
            headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            tree = ET.fromstring(resp.read().decode("utf-8"))
        items = []
        for item in tree.iter("item"):
            title = item.find("title").text or ""
            if title:
                items.append(title)
            if len(items) >= 5:
                break
        return items
    except Exception as e:
        print(f"[少数派] {e}")
        return []

def main():
    now = datetime.now()
    weekdays = ["星期一","星期二","星期三","星期四","星期五","星期六","星期日"]
    wd = weekdays[now.weekday()]
    is_weekend = now.weekday() >= 5

    print(f"正在生成 {now:%Y-%m-%d} {wd} 简报...")

    weather = get_weather()
    kr36 = get_36kr()
    weibo = get_weibo()
    sspai = get_sspai()

    L = []
    L.append("=" * 40)
    L.append(f"  ☀️  晨 间 简 报")
    L.append(f"  {now:%Y年%m月%d日} {wd}")
    L.append("=" * 40)
    L.append("")

    L.append("--- 🌤 今日天气 ---")
    L.extend(weather)
    L.append("")

    if weibo:
        L.append("--- 🔥 微博热搜 ---")
        for i, w in enumerate(weibo, 1):
            L.append(f"  {i}. {w}")
        L.append("")

    if kr36:
        L.append("--- 📰 36氪快讯 ---")
        for i, k in enumerate(kr36, 1):
            L.append(f"  {i}. {k}")
        L.append("")

    if sspai:
        L.append("--- 💻 少数派 ---")
        for i, s in enumerate(sspai, 1):
            L.append(f"  {i}. {s}")
        L.append("")

    if is_weekend:
        L.append("🎉 周末愉快！")
    else:
        L.append("📋 今日提醒：检查日历邮件 · 确认待办优先级")
    L.append("")
    L.append("💡 每日习惯：专注 · 起身活动 · 8杯水 💧")
    L.append("")
    L.append("-" * 40)
    L.append("Have a great day! 🎯")

    report = "\n".join(L)
    print(report)
    print()

    title = f"[晨间简报] {now:%m/%d} {wd}"
    ok, msg = send_feishu(title, report)
    if ok:
        print("✅ 飞书推送成功!")
    else:
        print(f"❌ 飞书推送失败: {msg}")
        exit(1)

if __name__ == "__main__":
    main()
