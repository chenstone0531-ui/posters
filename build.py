#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""掃描海報資料夾，產生縮圖、壓縮大圖與 images.js 清單（依片名分組、年份排序）。"""
import os, re, json, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "網站")
THUMBS = os.path.join(SITE, "thumbs")
FULL = os.path.join(SITE, "full")
os.makedirs(THUMBS, exist_ok=True)
os.makedirs(FULL, exist_ok=True)

EXTS = (".jpg", ".jpeg", ".png")

# ── 片名對照表：檔名只要包含「關鍵字」就歸入該片 ──
# (關鍵字, 片名, 年份)  年份 None = 不確定，改用檔案日期估計
PATTERNS = [
    ("濁水漂流", "濁水漂流", 2021),
    ("11A3特典", "一一（4K修復版）", 2025),
    ("11台灣4K", "一一（4K修復版）", 2025),
    ("11誠品劇照", "一一（4K修復版）", 2025),
    ("台北爵士音樂節", "台北爵士音樂節", 2022),
    ("22個男人", "22個男人", None),
    ("3DNA", "五月天3DNA", 2011),
    ("3D台灣", "美力台灣3D", 2017),
    ("美力台灣", "美力台灣3D", 2017),
    ("96分鐘", "96分鐘", 2025),
    ("Miss Andy", "迷失安狄 Miss Andy", 2021),
    ("一千個晚安", "一千個晚安", 2019),
    ("一秒拳王", "一秒拳王", 2021),
    ("三好海報", "三好", None),
    ("中韓夢之隊", "中韓夢之隊", None),
    ("五個姊姊", "有五個姊姊的我就註定單身了啊", 2018),
    ("五個姐姐", "有五個姊姊的我就註定單身了啊", 2018),
    ("五月天2023跨年", "五月天跨年演唱會視覺", 2023),
    ("五月天幕後花絮", "五月天跨年演唱會視覺", 2023),
    ("灼人秘密", "灼人秘密", 2019),
    ("他們創業的那些鳥事", "他們創業的那些鳥事", 2021),
    ("但願人長久", "但願人長久", 2024),
    ("你在我心上", "你在我心上", None),
    ("做工的人", "做工的人", 2020),
    ("傻瓜向錢衝", "傻瓜向錢衝", None),
    ("六弄", "六弄咖啡館", 2016),
    ("再見瓦城", "再見瓦城", 2016),
    ("最後防線", "最後防線", None),
    ("切小金", "切小金家的旅館", 2019),
    ("午餐爭霸戰", "午餐爭霸戰", None),
    ("叫我林彩香", "叫我林彩香！婆婆前傳", 2023),
    ("哭悲", "哭悲", 2021),
    ("售命", "售命", 2022),
    ("回家海報", "回家", None),
    ("大稻埕", "大稻埕", 2014),
    ("大三元", "大三元", 2019),
    ("大尾鱸鰻2", "大尾鱸鰻2", 2016),
    ("大債時代", "大債時代", 2021),
    ("大囍臨門", "大囍臨門", 2015),
    ("大釣哥", "大釣哥", 2017),
    ("天使之卵", "天使之卵（數位修復版）", 2025),
    ("失魂", "失魂", 2013),
    ("奇人密碼", "奇人密碼：古羅布之謎", 2015),
    ("女優摔吧", "女優摔吧", None),
    ("女朋友男朋友", "女朋友。男朋友", 2012),
    ("女追擊者", "女追擊者", None),
    ("女鬼橋2", "女鬼橋2：怨鬼樓", 2023),
    ("女鬼橋", "女鬼橋", 2020),
    ("如果愛", "如果愛", 2005),
    ("痞子英雄", "痞子英雄系列", 2012),
    ("孤味", "孤味", 2020),
    ("孩子你好嗎", "孩子你好嗎", None),
    ("萌學園", "萌學園：尋找磐古", 2015),
    ("宮崎駿紀錄片", "宮崎駿紀錄片", None),
    ("富貴發", "富貴發", None),
    ("寒蟬", "寒蟬效應", 2014),
    ("幸福之路", "幸福之路", None),
    ("幻影", "幻影", None),
    ("引爆點", "引爆點", 2018),
    ("志氣", "志氣", 2013),
    ("快一秒", "快一秒的他", 2023),
    ("怎麼可能我家的祖先", "怎麼可能我家的祖先是你家的鬼", None),
    ("報告老師", "報告老師！怪怪怪怪物！", 2017),
    ("怪物", "怪物", 2023),
    ("悲傷影集", "比悲傷更悲傷的故事（影集版）", 2021),
    ("比悲傷", "比悲傷更悲傷的故事", 2018),
    ("愛情無全順", "愛情無全順", 2013),
    ("愛情發生在三天後", "愛情發生在三天後", None),
    ("愛情算不算", "愛情算不算", None),
    ("愛的混混", "愛的混混", None),
    ("愛的迫降", "愛的迫降（舞台劇）", 2024),
    ("愛的麵包魂", "愛的麵包魂", 2012),
    ("我們全家不太熟", "我們全家不太熟", 2015),
    ("我們全班卡到卡陰", "我們全班卡到卡陰", None),
    ("我們的那時此刻", "我們的那時此刻", 2016),
    ("去月球", "帶我去月球", 2017),
    ("我和我的賽車老爸", "我和我的賽車老爸", 2021),
    ("我是誰", "我是誰", None),
    ("我的麻吉", "我的麻吉4個鬼", None),
    ("打噴嚏", "打噴嚏", 2020),
    ("詭扯", "詭扯", 2021),
    ("投名狀", "投名狀", 2007),
    ("普拉嘉造星計劃", "普拉嘉造星計劃", None),
    ("桃蛙源記", "桃蛙源記", 2014),
    ("森林戰士", "森林戰士", 2013),
    ("極樂宿舍", "極樂宿舍", None),
    ("榮耀之路", "榮耀之路", None),
    ("樓下的房客", "樓下的房客", 2016),
    ("殘影空間", "殘影空間", None),
    ("決味廚神", "決味廚神", None),
    ("沒有名字的甜點店", "沒有名字的甜點店", 2013),
    ("法鼓山除夕撞鐘", "法鼓山除夕撞鐘", None),
    ("浪我在你身邊", "浪我在你身邊", None),
    ("海上焰火", "海上焰火 Fire at Sea", 2016),
    ("海霧", "海霧", None),
    ("深夜食堂", "深夜食堂（華語版）", 2017),
    ("火力全開", "火力全開", None),
    ("狂徒", "狂徒", 2018),
    ("万王之王", "萬王之王", None),
    ("王牌教師", "王牌教師 麻辣出擊", 2017),
    ("生命捕手", "生命捕手", None),
    ("當男人戀愛時", "當男人戀愛時", 2021),
    ("瘋狂電視台", "瘋狂電視台瘋電影", 2019),
    ("盜命師", "盜命師", 2017),
    ("目擊者", "目擊者", 2017),
    ("真愛BJ4", "真愛BJ4", None),
    ("神之鄉", "神之鄉", 2021),
    ("神廚", "神廚", None),
    ("科學少女", "科學少女", 2022),
    ("穿越人海", "穿越人海擁抱你", 2021),
    ("童話世界", "童話世界", 2022),
    ("第一次离别", "第一次的離別", 2020),
    ("素還真", "素還真", 2022),
    ("謎絲", "謎絲", None),
    ("練愛iNG", "練愛iNG", 2020),
    ("美食無間", "美食無間", None),
    ("老師你會不會回來", "老師，你會不會回來", 2017),
    ("老鷹想飛", "老鷹想飛", 2015),
    ("聽見下", "聽見下雨的聲音", 2013),
    ("聽見歌", "聽見歌 再唱", 2021),
    ("花甲", "花甲大人轉男孩", 2018),
    ("蒼鷺與少年", "蒼鷺與少年", 2023),
    ("血滴子", "血滴子", 2012),
    ("複身犯", "複身犯", 2021),
    ("謝謝你", "謝謝你，在世界的角落找到我", 2017),
    ("變身", "變身", 2013),
    ("貓的報恩", "貓的報恩（重映）", None),
    ("賽德克", "賽德克·巴萊", 2011),
    ("跟你老婆去旅行", "跟你老婆去旅行", None),
    ("輝煌年代", "輝煌年代", 2016),
    ("逆光飛翔", "逆光飛翔", 2012),
    ("逆局", "逆局", 2021),
    ("逐風少年", "逐風少年", None),
    ("速命道", "速命道", None),
    ("進行曲", "進行曲", None),
    ("那些年", "那些年，我們一起追的女孩", 2011),
    ("粽邪3", "粽邪3", None),
    ("粽邪2", "馗降：粽邪2", 2020),
    ("粽邪", "粽邪", 2018),
    ("銷售奇姬", "銷售奇姬", None),
    ("鐵獅玉玲瓏", "鐵獅玉玲瓏", 2014),
    ("鑑識英雄", "鑑識英雄", 2017),
    ("逗陣ㄟ", "逗陣ㄟ", None),
    ("陣頭", "陣頭", 2012),
    ("雖然媽媽說", "雖然媽媽說我不可以嫁去日本", 2017),
    ("霍爾的移動城堡", "霍爾的移動城堡（重映）", None),
    ("青狗2", "青狗2不一樣的煙火", None),
    ("韓版風聲", "風聲（韓國版）", None),
    ("風聲", "風聲", 2009),
    ("順雲", "順雲", 2017),
    ("風中家族", "風中家族", 2015),
    ("風雲高手", "風雲高手", 2015),
    ("驚夢49天", "驚夢49天", None),
    ("高跟鞋先生", "高跟鞋先生", 2016),
    ("鬥魚", "鬥魚", 2018),
    ("鬼才之道", "鬼才之道", 2024),
    ("魔法公主", "魔法公主（4K修復版）", 2024),
    ("魚腸劍客", "魚腸劍客", None),
    ("鴕鳥騎士", "鴕鳥騎士", None),
    ("麻辣學園", "麻辣學園", None),
    ("麻煩家族", "麻煩家族", 2016),
    ("黑熊來了", "黑熊來了", 2019),
    ("黑白", "黑白原來是真的", None),
    ("媽祖", "媽祖", None),
    # ── 2026-06 新增 ──
    ("人生海海", "人生海海", None),
    ("我們六個", "我們六個", 2025),
    ("催眠麥克風", "催眠麥克風", None),
    ("世外", "世外", 2025),
    ("凶宅", "凶宅", None),
    ("極樂", "極樂", None),
    ("心之谷", "心之谷（重映）", None),
    ("看看你有多愛我", "看看你有多愛我", None),
    ("贖夢", "贖夢", None),
    ("小孩才做選擇", "小孩才做選擇", None),
    ("無形", "無形", None),
    ("NO GOOD", "NO GOOD歐吉桑", None),
    ("偷生", "偷生", None),
    ("星與翼的悖論", "星與翼的悖論", None),
    ("好孩子", "好孩子", None),
    ("月老", "月老", 2021),
    ("須菩提的眼淚", "須菩提的眼淚", None),
    # ── 資料夾攤平後改用檔名判斷 ──
    ("富都青年", "富都青年", 2023),
    ("靈語", "靈語", 2021),
    ("地獄里長", "地獄里長", None),
    ("廢柴英雄聯盟", "廢柴英雄聯盟", None),
    ("痞子", "痞子英雄系列", 2012),
    ("個人版立牌", "痞子英雄系列", 2012),
    ("個人版小立牌", "痞子英雄系列", 2012),
    ("大尾2", "大尾鱸鰻2", 2016),
    ("奇人", "奇人密碼：古羅布之謎", 2015),
]

# ── 子資料夾對照表 ──
FOLDER_MAP = {
    "痞子英雄1.2": ("痞子英雄系列", 2012),
    "近期的影視電影作品跟近1.2年賣座的電影": ("近期作品精選", None),
    "樓下的房客": ("樓下的房客", 2016),
    "六弄咖啡館": ("六弄咖啡館", 2016),
    "鑑識英雄II主視覺海報": ("鑑識英雄", 2017),
    "靈語前導＋人物款夾": ("靈語", 2021),
    "奇人密碼": ("奇人密碼：古羅布之謎", 2015),
    "大稻埕": ("大稻埕", 2014),
    "陣頭海報": ("陣頭", 2012),
    "變身": ("變身", 2013),
    "孤味": ("孤味", 2020),
    "大釣哥": ("大釣哥", 2017),
    "大囍臨門海報": ("大囍臨門", 2015),
    "帶我去月球": ("帶我去月球", 2017),
    "女鬼橋": ("女鬼橋", 2020),
    "大三元": ("大三元", 2019),
    "賽德克巴萊": ("賽德克·巴萊", 2011),
    "深夜食堂華劇": ("深夜食堂（華語版）", 2017),
    "富都青年海報": ("富都青年", 2023),
    "投名狀": ("投名狀", 2007),
    "廢柴英雄聯盟": ("廢柴英雄聯盟", None),
    "地獄里長正式海報確定直版": ("地獄里長", None),
    "地獄里長小檔": ("地獄里長", None),
    "Miss Andy-海報": ("迷失安狄 Miss Andy", 2021),
    "粽邪1.2海報": ("粽邪", 2018),       # 檔名先比對，比不到才用這個
    "血滴子": ("血滴子", 2012),
    "萌學園電影版": ("萌學園：尋找磐古", 2015),
    "報告老師怪怪怪怪物海報": ("報告老師！怪怪怪怪物！", 2017),
    "切小金的旅館海報": ("切小金家的旅館", 2019),
    "麻煩家族海報": ("麻煩家族", 2016),
    "比悲傷更悲傷的故事": ("比悲傷更悲傷的故事", 2018),
    "有五個姊姊的我就註定單身了啊": ("有五個姊姊的我就註定單身了啊", 2018),
    "打噴嚏海報": ("打噴嚏", 2020),
    "寒蟬效應": ("寒蟬效應", 2014),
    "快一秒海報21X23": ("快一秒的他", 2023),
    "女朋友.男朋友前": ("女朋友。男朋友", 2012),
    "大尾鱸鰻2": ("大尾鱸鰻2", 2016),
    "地表撐霸海報媒體特映券ok": ("地表撐霸", None),
    "回家": ("回家", None),
    "新增海報": ("其他設計作品", None),
}
# 這些資料夾混了不同作品，優先用檔名比對
FOLDER_PREFER_FILENAME = {"粽邪1.2海報", "痞子英雄1.2", "近期的影視電影作品跟近1.2年賣座的電影", "新增海報"}

OTHER = "其他設計作品"

# 不放上網站的作品（其他設計作品 = 認不出片名的雜項，全部不放）
EXCLUDE_FILMS = {"鬼才之道", "小孩才做選擇", OTHER}

def match_patterns(name):
    for key, film, year in PATTERNS:
        if key.lower() in name.lower():
            return film, year
    return None

def classify(filename, folder):
    """回傳 (片名, 年份或None)"""
    if folder:
        if folder in FOLDER_PREFER_FILENAME:
            hit = match_patterns(filename)
            if hit:
                return hit
        if folder in FOLDER_MAP:
            return FOLDER_MAP[folder]
        hit = match_patterns(filename) or match_patterns(folder)
        if hit:
            return hit
        return folder, None
    hit = match_patterns(filename)
    return hit if hit else (OTHER, None)

def clean_title(name):
    t = os.path.splitext(name)[0]
    t = re.sub(r"[_-]?(画板|工作區域)\s*\d*", "", t)
    t = re.sub(r"(?i)\bok\b", "", t)
    t = t.replace("ok-", "-").replace("OK-", "-")
    t = re.sub(r"[-_]+", " ", t).strip()
    return t or os.path.splitext(name)[0]

entries = []  # (src_path, folder, title)
for f in sorted(os.listdir(ROOT)):
    p = os.path.join(ROOT, f)
    if os.path.isfile(p) and f.lower().endswith(EXTS) and not f.startswith("."):
        entries.append((p, "", clean_title(f)))
for d in sorted(os.listdir(ROOT)):
    dp = os.path.join(ROOT, d)
    if os.path.isdir(dp) and d != "網站" and not d.startswith("."):
        for base, _, files in os.walk(dp):
            for f in sorted(files):
                if f.lower().endswith(EXTS) and not f.startswith("."):
                    entries.append((os.path.join(base, f), d, clean_title(f)))

print(f"共 {len(entries)} 張圖片", flush=True)

def sips_size(path):
    out = subprocess.run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", path],
                         capture_output=True, text=True).stdout
    w = h = 0
    for line in out.splitlines():
        if "pixelWidth" in line: w = int(line.split(":")[1])
        if "pixelHeight" in line: h = int(line.split(":")[1])
    return w, h

import datetime, hashlib
# 固定檔名對照表：來源路徑 -> 輸出檔名（確保新增圖片不會打亂既有檔名）
NAMES_PATH = os.path.join(SITE, "names.json")
NAMES = {}
if os.path.exists(NAMES_PATH):
    with open(NAMES_PATH, encoding="utf-8") as fh:
        NAMES = json.load(fh)

manifest = []
group_years = {}     # 片名 -> 確定年份
group_guess = {}     # 片名 -> 檔案日期推估
for i, (src, folder, title) in enumerate(entries, 1):
    film, year = classify(os.path.basename(src), folder)
    if film in EXCLUDE_FILMS:
        continue
    rel = os.path.relpath(src, ROOT)
    name = NAMES.get(rel)
    if not name:
        name = "p" + hashlib.md5(rel.encode("utf-8")).hexdigest()[:12] + ".jpg"
        NAMES[rel] = name
    tp = os.path.join(THUMBS, name)
    fp = os.path.join(FULL, name)
    def stale(out):
        # 來源檔比輸出檔新（圖被換過）就重新轉檔
        return not os.path.exists(out) or os.path.getmtime(src) > os.path.getmtime(out)
    if stale(tp):
        subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "75",
                        "-Z", "520", src, "--out", tp], capture_output=True)
    if stale(fp):
        subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "82",
                        "-Z", "1800", src, "--out", fp], capture_output=True)
    if not (os.path.exists(tp) and os.path.exists(fp)):
        print(f"  跳過（轉檔失敗）: {src}", flush=True)
        continue
    w, h = sips_size(tp)
    if w == 0 or h == 0:
        print(f"  跳過（讀不到尺寸）: {src}", flush=True)
        continue
    myear = datetime.datetime.fromtimestamp(os.path.getmtime(src)).year
    if year:
        group_years[film] = year
    else:
        group_guess.setdefault(film, []).append(myear)
    manifest.append({"f": name, "t": title, "g": film, "w": w, "h": h})
    if i % 100 == 0:
        print(f"  進度 {i}/{len(entries)}", flush=True)

# 估年份：用該片檔案最常見的年份
estimated = []
films = {}
for m in manifest:
    g = m["g"]
    if g not in films:
        if g in group_years:
            y, est = group_years[g], False
        else:
            ys = group_guess.get(g, [])
            y = max(set(ys), key=ys.count) if ys else 0
            est = True
            if g not in (OTHER, "近期作品精選"):
                estimated.append(f"{g}（約{y}）")
        films[g] = (y, est)

with open(NAMES_PATH, "w", encoding="utf-8") as fh:
    json.dump(NAMES, fh, ensure_ascii=False, indent=0)

out = {"films": [{"n": g, "y": y, "e": est} for g, (y, est) in films.items()],
       "items": manifest}
with open(os.path.join(SITE, "images.js"), "w", encoding="utf-8") as fh:
    fh.write("const DATA = ")
    json.dump(out, fh, ensure_ascii=False, separators=(",", ":"))
    fh.write(";")

print(f"完成：{len(manifest)} 張，{len(films)} 部作品", flush=True)
print("\n年份用檔案日期推估（可能不準）的作品：", flush=True)
for s in sorted(estimated):
    print("  " + s, flush=True)
