"""晨间简报 - GitHub Actions 云版本 v3"""
import json, urllib.request, urllib.parse, xml.etree.ElementTree as ET
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
            f"📍 广州",
            f"🌡 {desc}  {c.get('temp_C','?')}°C（体感 {c.get('FeelsLikeC','?')}°C）",
            f"📊 {t.get('mintempC','?')}°C ~ {t.get('maxtempC','?')}°C  |  湿度 {c.get('humidity','?')}%  |  风力 {c.get('windspeedKmph','?')}km/h",
            f"🌅 {t.get('astronomy',[{}])[0].get('sunrise','?')}  🌇 {t.get('astronomy',[{}])[0].get('sunset','?')}",
        ]
    except Exception as e:
        print(f"[天气] {e}")
        return ["🌡 天气暂不可用"]

def fetch_rss(url, max_items, label):
    """通用 RSS 抓取"""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            tree = ET.fromstring(resp.read().decode("utf-8"))
        items = []
        for item in tree.iter("item"):
            title = (item.find("title").text or "").strip()
            if title and len(title) > 3:
                items.append(title)
            if len(items) >= max_items:
                break
        return items
    except Exception as e:
        print(f"[{label}] {e}")
        return []

def get_36kr():
    return fetch_rss("https://36kr.com/feed", 8, "36kr")

def get_hn():
    """Hacker News - 国外科技前沿"""
    return fetch_rss("https://hnrss.org/frontpage?count=6", 6, "HN")

def get_bbc():
    """BBC World News"""
    items = fetch_rss("https://feeds.bbci.co.uk/news/world/rss.xml", 6, "BBC")
    # translate or prefix emoji
    return items

def get_wallstreetcn():
    """华尔街见闻 - 财经快讯"""
    return fetch_rss("https://wallstreetcn.com/rss", 6, "华尔街见闻")

def get_thepaper():
    """澎湃新闻 - 要闻"""
    items = fetch_rss("https://www.thepaper.cn/rss_www.xml", 6, "澎湃")
    return items

def main():
    now = datetime.now()
    weekdays = ["星期一","星期二","星期三","星期四","星期五","星期六","星期日"]
    wd = weekdays[now.weekday()]
    is_weekend = now.weekday() >= 5

    print(f"[{now:%Y-%m-%d %H:%M}] 生成中...")

    weather = get_weather()
    kr36 = get_36kr()
    hn = get_hn()
    bbc = get_bbc()
    wscn = get_wallstreetcn()
    paper = get_thepaper()

    L = []
    L.append("=" * 44)
    L.append(f"  ☀️  晨 间 简 报")
    L.append(f"  {now:%Y年%m月%d日} {wd}")
    L.append("=" * 44)
    L.append("")

    L.append("── 🌤 今日天气 ──")
    L.extend(weather)
    L.append("")

    if wscn:
        L.append(f"── 💰 华尔街见闻 · 财经 ({len(wscn)}条) ──")
        for i, s in enumerate(wscn, 1):
            L.append(f"  {i}. {s}")
        L.append("")

    if kr36:
        L.append(f"── 📰 36氪 · 科技商业 ({len(kr36)}条) ──")
        for i, k in enumerate(kr36, 1):
            L.append(f"  {i}. {k}")
        L.append("")

    if paper:
        L.append(f"── 📋 澎湃新闻 · 要闻 ({len(paper)}条) ──")
        for i, p in enumerate(paper, 1):
            L.append(f"  {i}. {p}")
        L.append("")

    if hn:
        L.append(f"── 💻 Hacker News · 科技前沿 ({len(hn)}条) ──")
        for i, h in enumerate(hn, 1):
            L.append(f"  {i}. {h}")
        L.append("")

    if bbc:
        L.append(f"── 🌍 BBC World News ({len(bbc)}条) ──")
        for i, b in enumerate(bbc, 1):
            L.append(f"  {i}. {b}")
        L.append("")

    if is_weekend:
        L.append("🎉 周末愉快！")
    else:
        L.append("📋 今日提醒：检查日历邮件 · 确认待办优先级")
    L.append("")
    L.append("💡 每日习惯：专注 · 起身活动 · 8杯水 💧")
    L.append("")
    L.append("─" * 44)
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
