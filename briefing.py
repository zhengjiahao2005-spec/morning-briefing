"""晨间简报 - GitHub Actions v4"""
import json, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime

FEISHU_HOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/343babb3-dd3a-4c92-8ae2-d41e0917a2a3"
CITY = "Guangzhou"

def send_feishu(title, content):
    text = f"{title}\n\n{content}"
    body = json.dumps({"msg_type": "text", "content": {"text": text}}).encode()
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
            f"        {desc}  {c.get('temp_C','?')}C",
            f"        {t.get('mintempC','?')}~{t.get('maxtempC','?')}C  湿度{c.get('humidity','?')}%  {c.get('windspeedKmph','?')}km/h",
        ]
    except Exception as e:
        print(f"[天气] {e}")
        return ["        暂不可用"]

def fetch_rss(url, max_n, label):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            tree = ET.fromstring(resp.read().decode("utf-8"))
        items = []
        for item in tree.iter("item"):
            t = (item.find("title").text or "").strip()
            if t and len(t) > 3:
                items.append(t)
            if len(items) >= max_n:
                break
        return items
    except Exception as e:
        print(f"[{label}] {e}")
        return []

def get_netease():
    try:
        url = "https://c.m.163.com/nc/article/headline/T1348647853363/0-20.html"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        items = []
        for article in data.get("T1348647853363", [])[:8]:
            title = article.get("title", "").strip()
            if title:
                items.append(title)
        return items
    except Exception as e:
        print(f"[网易] {e}")
        return []

def main():
    now = datetime.now()
    weekdays = ["星期一","星期二","星期三","星期四","星期五","星期六","星期日"]
    wd = weekdays[now.weekday()]
    is_weekend = now.weekday() >= 5

    print(f"[{now:%Y-%m-%d %H:%M}] generating...")

    weather = get_weather()
    netease = get_netease()
    google_news = fetch_rss("https://news.google.com/rss?hl=zh-CN&gl=CN&ceid=CN:zh-Hans", 6, "GoogleNews")
    kr36 = fetch_rss("https://36kr.com/feed", 6, "36kr")
    hn = fetch_rss("https://hnrss.org/frontpage?count=5", 5, "HN")
    bbc = fetch_rss("https://feeds.bbci.co.uk/news/world/rss.xml", 5, "BBC")

    L = []
    L.append("=" * 44)
    L.append(f"  ☀️  晨 间 简 报")
    L.append(f"  {now:%Y年%m月%d日} {wd}")
    L.append("=" * 44)
    L.append("")

    L.append("🌤 广州今日天气")
    L.extend(weather)

    if netease:
        L.append(f"\n📋 网易新闻 · 头条")
        for i, n in enumerate(netease, 1):
            L.append(f"  {i}. {n}")

    if google_news:
        L.append(f"\n🗞️  Google News · 中国")
        for i, g in enumerate(google_news, 1):
            L.append(f"  {i}. {g}")

    if kr36:
        L.append(f"\n📰 36氪 · 科技商业")
        for i, k in enumerate(kr36, 1):
            L.append(f"  {i}. {k}")

    if hn:
        L.append(f"\n💻 Hacker News")
        for i, h in enumerate(hn, 1):
            L.append(f"  {i}. {h}")

    if bbc:
        L.append(f"\n🌍 BBC World")
        for i, b in enumerate(bbc, 1):
            L.append(f"  {i}. {b}")

    L.append("")
    if is_weekend:
        L.append("🎉 周末愉快！")
    else:
        L.append("📋 今日提醒：检查日历邮件 · 确认待办优先级 · 保持专注")
    L.append("")
    L.append("═" * 44)
    L.append("Have a great day! 🎯")

    report = "\n".join(L)
    print(report)

    title = f"[晨间简报] {now:%m/%d} {wd}"
    ok, msg = send_feishu(title, report)
    if ok:
        print(f"\n✅ 飞书推送成功!")
    else:
        print(f"\n❌ 飞书推送失败: {msg}")
        exit(1)

if __name__ == "__main__":
    main()