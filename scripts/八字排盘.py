# -*- coding: utf-8 -*-
"""
赛博算命 - 核心八字排盘计算引擎

提供完整的四柱八字排盘、大运推算、十神分析等功能。
本模块不依赖任何外部包，使用标准库实现。

作者：锤无双
"""

from datetime import datetime, timedelta
import calendar

# ============================================================
# 基础常量定义
# ============================================================

# 天干
TIANGAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
# 地支
DIZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 天干阴阳
TIANGAN_YINYANG = {
    "甲": "阳", "乙": "阴", "丙": "阳", "丁": "阴", "戊": "阳",
    "己": "阴", "庚": "阳", "辛": "阴", "壬": "阳", "癸": "阴"
}

# 地支阴阳
DIZHI_YINYANG = {
    "子": "阳", "丑": "阴", "寅": "阳", "卯": "阴", "辰": "阳", "巳": "阴",
    "午": "阳", "未": "阴", "申": "阳", "酉": "阴", "戌": "阳", "亥": "阴"
}

# 天干五行
TIANGAN_WUXING = {
    "甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土",
    "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水"
}

# 地支五行
DIZHI_WUXING = {
    "子": "水", "丑": "土", "寅": "木", "卯": "木", "辰": "土", "巳": "火",
    "午": "火", "未": "土", "申": "金", "酉": "金", "戌": "土", "亥": "水"
}

# 地支藏干
DIZHI_CANGGAN = {
    "子": ["癸"],
    "丑": ["己", "癸", "辛"],
    "寅": ["甲", "丙", "戊"],
    "卯": ["乙"],
    "辰": ["戊", "乙", "癸"],
    "巳": ["丙", "戊", "庚"],
    "午": ["丁", "己"],
    "未": ["己", "丁", "乙"],
    "申": ["庚", "壬", "戊"],
    "酉": ["辛"],
    "戌": ["戊", "辛", "丁"],
    "亥": ["壬", "甲"]
}

# 时辰对应（子时分早晚子时）
SHICHEN_MAP = {
    (23, 1): "子", (1, 3): "丑", (3, 5): "寅", (5, 7): "卯",
    (7, 9): "辰", (9, 11): "巳", (11, 13): "午", (13, 15): "未",
    (15, 17): "申", (17, 19): "酉", (19, 21): "戌", (21, 23): "亥"
}

# 时辰名称
SHICHEN_NAMES = {
    "子": "子时（23-01）", "丑": "丑时（01-03）", "寅": "寅时（03-05）",
    "卯": "卯时（05-07）", "辰": "辰时（07-09）", "巳": "巳时（09-11）",
    "午": "午时（11-13）", "未": "未时（13-15）", "申": "申时（15-17）",
    "酉": "酉时（17-19）", "戌": "戌时（19-21）", "亥": "亥时（21-23）"
}

# 五行相生相克
WUXING_SHENG = {"金": "水", "水": "木", "木": "火", "火": "土", "土": "金"}
WUXING_KE = {"金": "木", "木": "土", "土": "水", "水": "火", "火": "金"}
WUXING_SHENG_ME = {"水": "金", "木": "水", "火": "木", "土": "火", "金": "土"}

# 十二长生
CHANGSHENG = ["长生", "沐浴", "冠带", "临官", "帝旺", "衰", "病", "死", "墓", "绝", "胎", "养"]

# 长生位置表（按天干阳顺阴逆）
CHANGSHENG_TABLE = {
    "甲": ("亥", ["长生", "沐浴", "冠带", "临官", "帝旺", "衰", "病", "死", "墓", "绝", "胎", "养"]),
    "乙": ("午", ["长生", "沐浴", "冠带", "临官", "帝旺", "衰", "病", "死", "墓", "绝", "胎", "养"]),  # 阴逆
    "丙": ("寅", ["长生", "沐浴", "冠带", "临官", "帝旺", "衰", "病", "死", "墓", "绝", "胎", "养"]),
    "丁": ("酉", ["长生", "沐浴", "冠带", "临官", "帝旺", "衰", "病", "死", "墓", "绝", "胎", "养"]),  # 阴逆
    "戊": ("寅", ["长生", "沐浴", "冠带", "临官", "帝旺", "衰", "病", "死", "墓", "绝", "胎", "养"]),
    "己": ("酉", ["长生", "沐浴", "冠带", "临官", "帝旺", "衰", "病", "死", "墓", "绝", "胎", "养"]),  # 阴逆
    "庚": ("巳", ["长生", "沐浴", "冠带", "临官", "帝旺", "衰", "病", "死", "墓", "绝", "胎", "养"]),
    "辛": ("子", ["长生", "沐浴", "冠带", "临官", "帝旺", "衰", "病", "死", "墓", "绝", "胎", "养"]),  # 阴逆
    "壬": ("申", ["长生", "沐浴", "冠带", "临官", "帝旺", "衰", "病", "死", "墓", "绝", "胎", "养"]),
    "癸": ("卯", ["长生", "沐浴", "冠带", "临官", "帝旺", "衰", "病", "死", "墓", "绝", "胎", "养"]),  # 阴逆
}

# 节气数据（每年24节气近似日期，月份/日）
# 注：实际排盘需精确节气表，此处给出近似日期用于演示
JIEQI_2024_2030 = {
    2024: {
        "小寒": (1, 6), "立春": (2, 4), "惊蛰": (3, 5), "清明": (4, 4),
        "立夏": (5, 5), "芒种": (6, 5), "小暑": (7, 6), "立秋": (8, 7),
        "白露": (9, 7), "寒露": (10, 8), "立冬": (11, 7), "大雪": (12, 6)
    },
    2025: {
        "小寒": (1, 5), "立春": (2, 3), "惊蛰": (3, 5), "清明": (4, 4),
        "立夏": (5, 5), "芒种": (6, 5), "小暑": (7, 7), "立秋": (8, 7),
        "白露": (9, 7), "寒露": (10, 8), "立冬": (11, 7), "大雪": (12, 7)
    },
    2026: {
        "小寒": (1, 5), "立春": (2, 4), "惊蛰": (3, 6), "清明": (4, 5),
        "立夏": (5, 5), "芒种": (6, 6), "小暑": (7, 7), "立秋": (8, 7),
        "白露": (9, 8), "寒露": (10, 8), "立冬": (11, 7), "大雪": (12, 7)
    },
}

# 农历年表（简化版，1900-2100年）
# 实际使用中推荐引入专业农历库（如lunardate、sxtwl）
# 这里只给出一个用于演示的近似表
LUNAR_YEAR_STEM = {
    2024: "甲", 2025: "乙", 2026: "丙", 2027: "丁", 2028: "戊",
    2029: "己", 2030: "庚", 2031: "辛", 2032: "壬", 2033: "癸"
}
LUNAR_YEAR_BRANCH = {
    2024: "辰", 2025: "巳", 2026: "午", 2027: "未", 2028: "申",
    2029: "酉", 2030: "戌", 2031: "亥", 2032: "子", 2033: "丑"
}


# ============================================================
# 核心计算函数
# ============================================================

def get_year_ganzhi(year, month, day):
    """
    根据公历日期计算年柱（考虑立春分界）
    立春前属于上一年
    """
    # 简化处理：立春约在2月4日
    if month < 2 or (month == 2 and day < 4):
        year -= 1

    # 年干 = (年份 - 4) % 10
    gan_idx = (year - 4) % 10
    # 年支 = (年份 - 4) % 12
    zhi_idx = (year - 4) % 12
    return TIANGAN[gan_idx] + DIZHI[zhi_idx]


def get_month_ganzhi(year, month, day):
    """
    根据公历日期计算月柱（以节气为界）
    简化处理：使用月份近似节气分界
    """
    # 节气月支对照
    # 立春~惊蛰 = 寅月，惊蛰~清明 = 卯月，依此类推
    solar_terms_month = [
        (2, 4, "寅"),   # 立春
        (3, 5, "卯"),   # 惊蛰
        (4, 4, "辰"),   # 清明
        (5, 5, "巳"),   # 立夏
        (6, 5, "午"),   # 芒种
        (7, 7, "未"),   # 小暑
        (8, 7, "申"),   # 立秋
        (9, 7, "酉"),   # 白露
        (10, 8, "戌"),  # 寒露
        (11, 7, "亥"),  # 立冬
        (12, 7, "子"),  # 大雪
        (1, 5, "丑"),   # 小寒
    ]

    # 确定节气月支
    month_zhi = "寅"  # 默认正月
    for m, d, zhi in solar_terms_month:
        # 处理跨年情况
        check_m, check_d = m, d
        # 如果是1月节气，需要判断是否在year-1的节气之后
        if m == 1 and month == 1 and day < d:
            # 还在上一年的丑月范围
            month_zhi = "丑"
            continue
        if (month > check_m) or (month == check_m and day >= check_d):
            # 找到当月节气
            # 实际要找到最接近的
            pass

    # 简化逻辑：根据月份直接判断
    # 寅月(2月)、卯月(3月)、辰月(4月)、巳月(5月)、午月(6月)、未月(7月)
    # 申月(8月)、酉月(9月)、戌月(10月)、亥月(11月)、子月(12月)、丑月(1月)
    month_zhi_map = {
        1: "丑", 2: "寅", 3: "卯", 4: "辰", 5: "巳", 6: "午",
        7: "未", 8: "申", 9: "酉", 10: "戌", 11: "亥", 12: "子"
    }
    # 调整立春前的特殊情况
    if month == 1 or (month == 2 and day < 4):
        month_zhi = "丑"
    else:
        month_zhi = month_zhi_map.get(month, "寅")

    # 月干根据年干推算（五虎遁年起月法）
    # 甲己之年丙作首，乙庚之岁戊为头
    # 丙辛之岁寻庚上，丁壬壬位顺行流
    # 戊癸之年何处起，甲寅之上好追求
    year_gan = get_year_ganzhi(year, month, day)[0]
    month_gan_start = {
        "甲": "丙", "己": "丙",
        "乙": "戊", "庚": "戊",
        "丙": "庚", "辛": "庚",
        "丁": "壬", "壬": "壬",
        "戊": "甲", "癸": "甲"
    }
    start_gan = month_gan_start[year_gan]
    start_idx = TIANGAN.index(start_gan)
    zhi_idx = DIZHI.index(month_zhi)
    # 寅月对应索引0
    offset = (zhi_idx - 2) % 12  # 寅的索引是2
    gan_idx = (start_idx + offset) % 10
    return TIANGAN[gan_idx] + month_zhi


def get_day_ganzhi(year, month, day):
    """
    根据公历日期计算日柱（使用基准日推算法）
    基准：1900年1月1日 = 甲戌日（仅作演示）
    """
    # 实际专业排盘建议使用寿星天文历（sxtwl）精确计算
    # 这里是简化版本：以2000年1月1日为甲午日（不准确，仅演示）
    base_date = datetime(2000, 1, 1)
    target_date = datetime(year, month, day)
    delta_days = (target_date - base_date).days

    # 甲午的ganzhi索引
    base_gan_idx = TIANGAN.index("甲")
    base_zhi_idx = DIZHI.index("午")

    # 推算日柱（粗略，实际应使用精确公式）
    gan_idx = (base_gan_idx + delta_days) % 10
    zhi_idx = (base_zhi_idx + delta_days) % 12
    return TIANGAN[gan_idx] + DIZHI[zhi_idx]


def get_hour_ganzhi(day_gan, hour):
    """
    根据日干和小时计算时柱（五鼠遁日起时法）
    甲己还加甲，乙庚丙作初
    丙辛从戊起，丁壬庚子居
    戊癸何方发，壬子是真途
    """
    # 先确定时辰地支
    shichen_zhi = None
    for (start, end), zhi in SHICHEN_MAP.items():
        if start <= end:
            if start <= hour < end:
                shichen_zhi = zhi
                break
        else:  # 跨日情况（子时23:00-01:00）
            if hour >= start or hour < end:
                shichen_zhi = zhi
                break

    if not shichen_zhi:
        shichen_zhi = "子"

    # 根据日干推算时干
    day_gan_start = {
        "甲": "甲", "己": "甲",
        "乙": "丙", "庚": "丙",
        "丙": "戊", "辛": "戊",
        "丁": "庚", "壬": "庚",
        "戊": "壬", "癸": "壬"
    }
    start_gan = day_gan_start[day_gan]
    start_idx = TIANGAN.index(start_gan)
    zhi_idx = DIZHI.index(shichen_zhi)
    # 子时对应索引0
    offset = zhi_idx
    gan_idx = (start_idx + offset) % 10
    return TIANGAN[gan_idx] + shichen_zhi


def calc_bazi(year, month, day, hour, gender):
    """
    排四柱八字

    参数:
        year, month, day: 公历出生年月日
        hour: 出生小时（0-23）
        gender: '男' 或 '女'

    返回:
        dict: 包含四柱、年柱、月柱、日柱、时柱、五行统计等
    """
    year_pillar = get_year_ganzhi(year, month, day)
    month_pillar = get_month_ganzhi(year, month, day)
    day_pillar = get_day_ganzhi(year, month, day)
    hour_pillar = get_hour_ganzhi(day_pillar[0], hour)

    bazi = [year_pillar, month_pillar, day_pillar, hour_pillar]

    # 五行统计
    wuxing_count = {"金": 0, "木": 0, "水": 0, "火": 0, "土": 0}
    for pillar in bazi:
        # 天干
        wuxing_count[TIANGAN_WUXING[pillar[0]]] += 1
        # 地支
        wuxing_count[DIZHI_WUXING[pillar[1]]] += 1

    # 日主（日干）
    day_master = day_pillar[0]
    day_master_wuxing = TIANGAN_WUXING[day_master]

    return {
        "year_pillar": year_pillar,
        "month_pillar": month_pillar,
        "day_pillar": day_pillar,
        "hour_pillar": hour_pillar,
        "bazi": bazi,
        "day_master": day_master,
        "day_master_wuxing": day_master_wuxing,
        "wuxing_count": wuxing_count,
        "gender": gender,
        "birth_year": year,
        "birth_month": month,
        "birth_day": day,
        "birth_hour": hour
    }


def calc_dayun(bazi_result, gender):
    """
    计算大运（每10年一转）

    起运规则：
    - 男命阳年/女命阴年：顺排
    - 男命阴年/女命阳年：逆排
    - 顺排：从月柱下一位开始
    - 逆排：从月柱前一位开始
    """
    year_pillar = bazi_result["year_pillar"]
    month_pillar = bazi_result["month_pillar"]
    day_master = bazi_result["day_master"]

    year_gan = year_pillar[0]
    year_yin_yang = TIANGAN_YINYANG[year_gan]
    is_yang_year = year_yin_yang == "阳"

    # 顺逆判断
    if gender == "男":
        shun = is_yang_year
    else:  # 女
        shun = not is_yang_year

    # 起运岁数（简化：固定3岁起运）
    qiyun_age = 3

    # 推算大运干支
    month_gan = month_pillar[0]
    month_zhi = month_pillar[1]
    month_gan_idx = TIANGAN.index(month_gan)
    month_zhi_idx = DIZHI.index(month_zhi)

    dayuns = []
    for i in range(1, 9):  # 8步大运
        if shun:
            gan_idx = (month_gan_idx + i) % 10
            zhi_idx = (month_zhi_idx + i) % 12
        else:
            gan_idx = (month_gan_idx - i) % 10
            zhi_idx = (month_zhi_idx - i) % 12
        dayuns.append({
            "step": i,
            "start_age": qiyun_age + (i - 1) * 10,
            "end_age": qiyun_age + i * 10,
            "ganzhi": TIANGAN[gan_idx] + DIZHI[zhi_idx],
            "gan": TIANGAN[gan_idx],
            "zhi": DIZHI[zhi_idx],
            "gan_wuxing": TIANGAN_WUXING[TIANGAN[gan_idx]],
            "zhi_wuxing": DIZHI_WUXING[DIZHI[zhi_idx]],
            "direction": "顺行" if shun else "逆行"
        })

    return {
        "qiyun_age": qiyun_age,
        "direction": "顺排" if shun else "逆排",
        "dayuns": dayuns
    }


def get_shishen(day_master, other_gan):
    """
    根据日干和其他天干计算十神关系

    十神：
    - 同我：比肩（阳见阳）、劫财（阳见阴或阴见阳）
    - 我克：食神（阳见阳）、伤官（阳见阴或阴见阳）
    - 克我：偏财（阳见阳）、正财（阳见阴或阴见阳）
    - 我生：七杀（阳见阳）、正官（阳见阴或阴见阳）
    - 生我：偏印（阳见阳）、正印（阳见阴或阴见阳）
    """
    me_yy = TIANGAN_YINYANG[day_master]
    me_wx = TIANGAN_WUXING[day_master]
    other_yy = TIANGAN_YINYANG[other_gan]
    other_wx = TIANGAN_WUXING[other_gan]

    # 同我
    if other_wx == me_wx:
        return "比肩" if me_yy == other_yy else "劫财"

    # 我生（日主生出的 = 食神/伤官）
    if WUXING_SHENG[me_wx] == other_wx:
        return "食神" if me_yy == other_yy else "伤官"

    # 我克（日主克的 = 偏财/正财）
    if WUXING_KE[me_wx] == other_wx:
        return "偏财" if me_yy == other_yy else "正财"

    # 克我（克日主的 = 七杀/正官）
    if WUXING_KE[other_wx] == me_wx:
        return "七杀" if me_yy == other_yy else "正官"

    # 生我（生日主的 = 偏印/正印）
    if WUXING_SHENG_ME[me_wx] == other_wx:
        return "偏印" if me_yy == other_yy else "正印"

    return "未知"


def get_shensha(day_pillar, hour_pillar, year_pillar):
    """
    计算常见神煞（简化版）
    """
    day_zhi = day_pillar[1]
    year_zhi = year_pillar[1]

    shensha = []

    # 天乙贵人
    tiangui_gan = {
        "甲": ["丑", "未"], "戊": ["丑", "未"],
        "乙": ["子", "申"], "己": ["子", "申"],
        "丙": ["亥", "酉"], "丁": ["亥", "酉"],
        "庚": ["丑", "未"], "辛": ["寅", "午"],
        "壬": ["卯", "巳"], "癸": ["卯", "巳"]
    }

    day_gan = day_pillar[0]
    if day_zhi in tiangui_gan.get(day_gan, []):
        shensha.append("天乙贵人")

    # 文昌贵人
    wenchang_gan = {
        "甲": "巳", "乙": "午", "丙": "申", "丁": "酉",
        "戊": "申", "己": "酉", "庚": "亥", "辛": "子",
        "壬": "寅", "癸": "卯"
    }
    if wenchang_gan.get(day_gan) == day_zhi or wenchang_gan.get(day_gan) in [hour_pillar[1], year_pillar[1]]:
        shensha.append("文昌贵人")

    # 驿马
    yima = {"申": "寅", "子": "寅", "辰": "寅",
            "寅": "申", "午": "申", "戌": "申",
            "巳": "亥", "酉": "亥", "丑": "亥",
            "亥": "巳", "卯": "巳", "未": "巳"}
    if yima.get(year_zhi) == day_zhi or yima.get(year_zhi) in [hour_pillar[1]]:
        shensha.append("驿马星")

    # 桃花
    taohua = {"申": "酉", "子": "酉", "辰": "酉",
              "寅": "卯", "午": "卯", "戌": "卯",
              "巳": "午", "酉": "午", "丑": "午",
              "亥": "子", "卯": "子", "未": "子"}
    if taohua.get(year_zhi) == day_zhi or taohua.get(year_zhi) in [hour_pillar[1]]:
        shensha.append("桃花星")

    # 华盖
    huagai = {"申": "辰", "子": "辰", "辰": "辰",
              "寅": "戌", "午": "戌", "戌": "戌",
              "巳": "丑", "酉": "丑", "丑": "丑",
              "亥": "未", "卯": "未", "未": "未"}
    if huagai.get(year_zhi) == day_zhi or huagai.get(year_zhi) in [hour_pillar[1]]:
        shensha.append("华盖星")

    return shensha


def get_geju(bazi_result):
    """
    判断命局格局（简化版）
    """
    day_master = bazi_result["day_master"]
    month_zhi = bazi_result["month_pillar"][1]
    wuxing_count = bazi_result["wuxing_count"]

    # 月令所藏天干与日主的关系
    canggan = DIZHI_CANGGAN.get(month_zhi, [])
    if not canggan:
        return "普通命局"

    main_qi = canggan[0]  # 月令主气
    shishen = get_shishen(day_master, main_qi)

    geju_map = {
        "正官": "正官格",
        "七杀": "七杀格（偏官格）",
        "正印": "正印格",
        "偏印": "偏印格（枭神格）",
        "正财": "正财格",
        "偏财": "偏财格",
        "食神": "食神格",
        "伤官": "伤官格",
        "比肩": "比肩格",
        "劫财": "劫财格"
    }

    return geju_map.get(shishen, "普通命局")


def analyze_xiyongshen(bazi_result):
    """
    分析喜用神（基于五行平衡原理）

    简化规则：
    - 日主旺：克泄耗日主为喜用
    - 日主弱：生扶日主为喜用
    """
    day_master = bazi_result["day_master"]
    day_wx = TIANGAN_WUXING[day_master]
    wuxing_count = bazi_result["wuxing_count"]

    # 日主数量（含地支主气）
    dm_count = 0
    for pillar in bazi_result["bazi"]:
        dm_count += sum(1 for ch in pillar if TIANGAN_WUXING.get(ch) == day_wx)
        # 加地支主气
        for zhi in [pillar[1]]:
            if zhi in DIZHI_CANGGAN:
                main_gan = DIZHI_CANGGAN[zhi][0]
                if TIANGAN_WUXING[main_gan] == day_wx:
                    dm_count += 1

    is_strong = dm_count >= 4

    if is_strong:
        # 喜用神：克我、我克、我生
        xiyong = []
        xiyong.append(WUXING_KE[day_wx])  # 官杀（克我）
        xiyong.append(WUXING_SHENG[day_wx])  # 食伤（我生）
        # 也可用财
        ji_wx = WUXING_SHENG_ME[day_wx]  # 我克（财）
        return {
            "is_strong": True,
            "day_master_strength": "身旺" if is_strong else "身弱",
            "xiyong": list(set(xiyong)),
            "jishen": [day_wx, WUXING_SHENG_ME[WUXING_SHENG[day_wx]]]  # 比劫、印
        }
    else:
        # 喜用神：生我、同我
        xiyong = []
        xiyong.append(WUXING_SHENG_ME[day_wx])  # 印（生我）
        xiyong.append(day_wx)  # 比劫（同我）
        return {
            "is_strong": False,
            "day_master_strength": "身旺" if is_strong else "身弱",
            "xiyong": list(set(xiyong)),
            "jishen": [WUXING_KE[day_wx], WUXING_SHENG[day_wx]]  # 官杀、食伤
        }


# ============================================================
# 大运关键事件预测
# ============================================================

def predict_life_events(bazi_result, dayun_result, gender):
    """
    预测每步大运中的关键人生事件

    基于：
    - 大运天干地支与日主的十神关系
    - 大运五行与原局冲克
    - 年龄段合理性判断
    - 神煞影响

    预测事件类型：
    - 学业/考试/升学
    - 事业起步/转折
    - 婚姻/感情大事
    - 子女出生
    - 父母健康/离去
    - 官司/纠纷
    - 意外/伤病
    - 迁移/搬家
    - 财运暴发/破败

    返回:
        list: 每步大运的关键事件列表
    """
    day_master = bazi_result["day_master"]
    day_wx = TIANGAN_WUXING[day_master]
    year_pillar = bazi_result["year_pillar"]
    month_pillar = bazi_result["month_pillar"]
    day_pillar = bazi_result["day_pillar"]
    hour_pillar = bazi_result["hour_pillar"]
    birth_year = bazi_result["birth_year"]
    yong_shen_wx = analyze_xiyongshen(bazi_result)["xiyong"]

    xiyong = bazi_result.get("xiyongshen", [])
    wuxing_count = bazi_result["wuxing_count"]

    # 六冲对照表
    liu_chong = {"子": "午", "午": "子", "丑": "未", "未": "丑",
                 "寅": "申", "申": "寅", "卯": "酉", "酉": "卯",
                 "辰": "戌", "戌": "辰", "巳": "亥", "亥": "巳"}

    # 获取年柱、月柱的干支
    year_gan = year_pillar[0]
    year_zhi = year_pillar[1]
    month_gan = month_pillar[0]
    month_zhi = month_pillar[1]
    day_zhi = day_pillar[1]
    hour_zhi = hour_pillar[1]

    # 子女宫情况（时柱）
    children_gong = hour_pillar
    children_gan = children_gong[0]
    children_zhi = children_gong[1]

    # 父母星判断
    if gender == "男":
        father_star_wx = WUXING_KE[day_wx]  # 偏财为父
        mother_star_wx = WUXING_SHENG_ME[day_wx]  # 正印为母
        spouse_star = "正财"
        children_star = "官杀"
    else:
        father_star_wx = WUXING_KE[day_wx]  # 偏财为父
        mother_star_wx = WUXING_SHENG_ME[day_wx]  # 正印为母
        spouse_star = "正官"
        children_star = "食伤"

    all_events = []

    for dy in dayun_result["dayuns"]:
        step = dy["step"]
        start_age = dy["start_age"]
        end_age = dy["end_age"]
        ganzhi = dy["ganzhi"]
        gan = dy["gan"]
        zhi = dy["zhi"]
        gan_wx = dy["gan_wuxing"]
        zhi_wx = dy["zhi_wuxing"]
        direction = dy["direction"]

        shishen = get_shishen(day_master, gan)
        events = []
        luck_level = "平运"  # 默认平运

        # ========== 按年龄段判断事件 ==========

        # 1. 学业/升学 (6-22岁)
        if start_age <= 22:
            if shishen in ["正印", "偏印", "食神"]:
                if 6 <= start_age <= 12:
                    events.append({
                        "类型": "学业",
                        "等级": "优",
                        "描述": f"{start_age}-{min(end_age,12)}岁入学阶段，大运{ganzhi}逢{shishen}，学业天赋显露，读书理解力强。{'印星护身，多得师长喜爱' if '印' in shishen else '食神吐秀，逻辑清晰'}",
                        "建议": "打好基础，培养学习习惯，不宜过早偏科"
                    })
                    luck_level = "上吉"
                elif 13 <= start_age <= 18:
                    events.append({
                        "类型": "考试",
                        "等级": "优" if shishen in ["正印", "偏印"] else "良",
                        "描述": f"{start_age}-{min(end_age,18)}岁中学阶段，大运{ganzhi}逢{shishen}。{'升学运佳，考试临场发挥出色' if '印' in shishen else '聪明伶俐但需戒骄戒躁'}",
                        "建议": "重点加强薄弱科目，考前保持平常心"
                    })
                elif 19 <= start_age <= 22:
                    events.append({
                        "类型": "升学",
                        "等级": "优" if shishen in ["正印", "偏印"] else "良",
                        "描述": f"{start_age}-{min(end_age,22)}岁大学/高等教育阶段。{shishen}运利于深造、考研、留学，{'印星助学业有成，宜继续深造' if '印' in shishen else '食神生财，可兼顾学术与实践'}",
                        "建议": "把握进修机会，提升学历和专业能力"
                    })
            elif shishen in ["七杀", "伤官", "劫财"] and start_age <= 18:
                events.append({
                    "类型": "学业",
                    "等级": "差",
                    "描述": f"{start_age}-{min(end_age,18)}岁学业阶段遇{shishen}，{'学习压力大，需克服浮躁心态' if shishen == '七杀' else '聪明但叛逆，与师长关系紧张' if shishen == '伤官' else '竞争激烈，同学间互相较劲'}",
                    "建议": "端正学习态度，家长需耐心引导，不宜施压过大"
                })
                luck_level = "差"

            elif shishen in ["正官", "正财"] and start_age <= 22:
                events.append({
                    "类型": "学业",
                    "等级": "良",
                    "描述": f"{start_age}-{min(end_age,22)}岁学业阶段，{shishen}运稳健。正官主自律、正财主务实，学业按部就班，成绩稳定",
                    "建议": "保持节奏，稳中求进"
                })

        # 2. 事业起步/转折 (20-35岁)
        if 20 <= start_age <= 35:
            if shishen in ["正官", "七杀"]:
                events.append({
                    "类型": "事业",
                    "等级": "吉",
                    "描述": f"{start_age}-{min(end_age,35)}岁事业运走{shishen}，{'正官主贵人相助、升职机遇' if shishen == '正官' else '七杀代表压力和突破，越是艰难越能成事'}。职场上能站稳脚跟，获得认可。",
                    "建议": "勇于承担责任，积累核心经验" if shishen == "正官" else "化压力为动力，不宜频繁跳槽"
                })
                luck_level = "上吉" if shishen == "正官" else "吉"
            elif shishen in ["正财", "偏财"]:
                events.append({
                    "类型": "事业",
                    "等级": "吉",
                    "描述": f"{start_age}-{min(end_age,35)}岁事业运走{shishen}，{'正财主稳定收入、升职加薪' if shishen == '正财' else '偏财主机遇、商业嗅觉敏锐'}。财运带动事业，收入提升明显。",
                    "建议": "踏实积累财富，同时投资自我提升"
                })
                luck_level = "吉"
            elif shishen in ["食神", "伤官"]:
                if shishen == "伤官":
                    events.append({
                        "类型": "事业",
                        "等级": "中",
                        "描述": f"{start_age}-{min(end_age,35)}岁事业运走伤官，才华横溢但易与上司冲突。适合技术路线、自由职业、创业方向",
                        "建议": "收敛锋芒，用实力说话；若创业则宜选小众赛道"
                    })
                    luck_level = "中"
                else:
                    events.append({
                        "类型": "事业",
                        "等级": "良",
                        "描述": f"{start_age}-{min(end_age,35)}岁事业运走食神，贵人相助、口碑好，适合教育、餐饮、文化行业",
                        "建议": "发挥专业优势，建立行业口碑"
                    })
            elif shishen in ["比肩", "劫财"]:
                if shishen == "劫财":
                    events.append({
                        "类型": "事业",
                        "等级": "险",
                        "描述": f"{start_age}-{min(end_age,35)}岁事业运走劫财，竞争激烈，同事间易有利益冲突。慎防合伙纠纷、辞职冲动",
                        "建议": "守成为主，不宜创业或换行，合同条款务必看清"
                    })
                    luck_level = "差"
                else:
                    events.append({
                        "类型": "事业",
                        "等级": "良",
                        "描述": f"{start_age}-{min(end_age,35)}岁事业运走比肩，独立能力强，适合一技之长的发展路径",
                        "建议": "增强专业壁垒，做不可替代的人"
                    })

        # 3. 结婚/感情大事 (20-35岁)
        if 20 <= start_age <= 35:
            if gender == "男":
                marriage_triggers = ["正财", "偏财"]
            else:
                marriage_triggers = ["正官", "七杀"]

            if shishen in marriage_triggers:
                marriage_age_hint = start_age + 2  # 大运开始后2年左右
                events.append({
                    "类型": "婚姻",
                    "等级": "大吉",
                    "描述": f"{start_age}-{min(end_age,35)}岁走{shishen}运，{'正财为妻星，此运遇正缘概率极高，宜把握良缘' if gender == '男' else '正官为夫星，此运利于婚姻稳定'}。约{marriage_age_hint}岁前后为最佳婚期窗口",
                    "建议": "主动社交，拓展人际圈；相亲、朋友介绍成功率较高"
                })
                luck_level = "上吉"
            elif shishen == "劫财" and gender == "男":
                events.append({
                    "类型": "婚姻",
                    "等级": "险",
                    "描述": f"{start_age}-{min(end_age,35)}岁走劫财运，{'劫财克财，感情中易遇竞争对手，恋爱中需防第三者' if gender == '男' else '感情波折较多，需耐心等待'}",
                    "建议": "已婚者多交流、少猜忌；恋爱者适当保持距离，不宜过于热络"
                })
            elif shishen == "伤官" and gender == "女":
                events.append({
                    "类型": "婚姻",
                    "等级": "险",
                    "描述": f"{start_age}-{min(end_age,35)}岁走伤官运，伤官克官，婚姻运程受阻。与伴侣易生口角，感情容易受伤",
                    "建议": "控制情绪，少挑剔、多包容；婚前需充分了解对方"
                })

        # 4. 子女出生 (25-45岁)
        if 25 <= start_age <= 45:
            if gender == "男":
                children_trigger = ["正官", "七杀"]
            else:
                children_trigger = ["食神", "伤官"]

            if shishen in children_trigger or (start_age <= 35 and start_age >= 25):
                # 检查子女宫（时柱）是否旺相
                children_wx = DIZHI_WUXING.get(children_zhi, "")
                children_is_strong = children_wx in yong_shen_wx

                if shishen in children_trigger:
                    child_age = start_age + 3  # 大运中期
                    events.append({
                        "类型": "子女",
                        "等级": "吉",
                        "描述": f"{start_age}-{min(end_age,45)}岁子女运走{shishen}，{'子女星得力，此运易添丁。时柱' + children_gong + ('旺相，子女将来有出息' if children_is_strong else '一般，需多关注子女教育和健康')}",
                        "建议": f"约{child_age}岁前后是添丁最佳窗口期，提前做好规划"
                    })
                elif shishen in ["伤官", "七杀"] and start_age >= 30:
                    events.append({
                        "类型": "子女",
                        "等级": "中",
                        "描述": f"{start_age}-{min(end_age,45)}岁子女运一般，{shishen}运虽有波折但不影响子女缘分",
                        "建议": "顺其自然，不宜过度焦虑"
                    })

        # 5. 父母健康/离去警示 (40-70岁)
        if start_age >= 40:
            # 判断父母星是否被大运冲克
            parent_warning = False
            parent_reason = ""

            # 大运地支冲年柱地支（冲父母宫）
            year_dizhi = year_zhi

            if liu_chong.get(year_dizhi) == zhi:
                parent_warning = True
                parent_reason = f"大运地支{ganzhi}冲年柱{year_pillar}（父母宫受冲），此运需格外关注父母健康状况"

            # 大运天干五行克父母星
            if gan_wx == WUXING_KE.get(father_star_wx) or gan_wx == WUXING_KE.get(mother_star_wx):
                parent_warning = True
                if not parent_reason:
                    parent_reason = f"大运{ganzhi}五行{gan_wx}克制父母星，父母健康需留意"

            if parent_warning:
                severity = "⚠️" if start_age >= 55 else "⚡"
                events.append({
                    "类型": "父母",
                    "等级": "险",
                    "描述": f"{severity} {start_age}-{end_age}岁{parent_reason}。建议每年带父母体检，关注心血管和慢性病史",
                    "建议": "多陪伴父母，定期体检；家中常备急救药品"
                })

        # 6. 官司/纠纷
        lawsuit_triggers = {
            "七杀": {"等级": "险", "描述": "七杀攻身，易遇小人暗算、官非纠纷。慎防合同陷阱、法律诉讼"},
            "伤官": {"等级": "险", "描述": "伤官见官，祸患百端。易与权威发生冲突，慎防口舌之争升级为法律纠纷"},
            "劫财": {"等级": "中", "描述": "劫财竞争，易有合伙纠纷、借贷纠纷、遗产纷争"},
        }

        if shishen in lawsuit_triggers:
            trig = lawsuit_triggers[shishen]
            events.append({
                "类型": "官司",
                "等级": trig["等级"],
                "描述": f"{start_age}-{end_age}岁大运{ganzhi}逢{shishen}，{trig['描述']}",
                "建议": "重要文件务必留存证据，合同条款仔细审查，避免口头协议"
            })

        # 7. 意外/伤病
        if shishen == "七杀" or shishen == "伤官":
            # 检查大运是否冲克日柱
            day_dizhi = day_zhi
            if liu_chong.get(day_dizhi) == zhi:
                events.append({
                    "类型": "伤病",
                    "等级": "险",
                    "描述": f"{start_age}-{end_age}岁大运{ganzhi}冲日柱{day_pillar}（日主受冲），此运需格外注意身体健康。{TIANGAN_WUXING.get(day_master)}代表的身体系统易受损",
                    "建议": "避免高风险活动（极限运动、长途自驾），购买意外保险"
                })

        # 8. 迁移/搬家
        if zhi in ["寅", "申", "巳", "亥"]:  # 四驿马
            events.append({
                "类型": "迁移",
                "等级": "中",
                "描述": f"{start_age}-{end_age}岁大运逢驿马星，此运多动少静，利于异地发展、出国、迁居。驿马逢{'申' if zhi == '申' else zhi}，{'变动多含机遇' if zhi in ['寅', '申'] else '变动中宜求稳'}",
                "建议": "拥抱变化，每一次迁移都是成长的机会"
            })

        # 9. 财运暴发/破败
        if shishen == "偏财":
            events.append({
                "类型": "财运",
                "等级": "吉",
                "描述": f"{start_age}-{end_age}岁走偏财运，投资运极佳，易有意外之财。适合创业、经商、投资理财",
                "建议": "大胆把握商机，但需分散投资降低风险"
            })
            luck_level = "上吉"
        elif shishen == "劫财":
            events.append({
                "类型": "财运",
                "等级": "险",
                "描述": f"{start_age}-{end_age}岁走劫财运，财运不聚，挣得多花得多。慎防朋友借钱不还、投资亏损、赌博破财",
                "建议": "强制储蓄，拒绝担保，不碰高风险投资"
            })
            luck_level = "差"
        elif shishen == "正财":
            events.append({
                "类型": "财运",
                "等级": "良",
                "描述": f"{start_age}-{end_age}岁走正财运，收入稳定增长，适合稳健理财、购房置业",
                "建议": "踏实积累，积少成多"
            })

        # 综合大运等级
        if not events:
            events.append({
                "类型": "综合",
                "等级": "中",
                "描述": f"{start_age}-{end_age}岁大运{ganzhi}走{shishen}运，运势平稳，无大起大落",
                "建议": "此运适合修身养性、积累实力，为下一个大运做准备"
            })

        all_events.append({
            "step": step,
            "start_age": start_age,
            "end_age": end_age,
            "ganzhi": ganzhi,
            "shishen": shishen,
            "luck_level": luck_level,
            "events": events
        })

    return all_events


# ============================================================
# 运势预测函数
# ============================================================

def predict_liunian(bazi_result, dayun_result, target_year, gender):
    """
    预测指定年份的流年运势

    参数:
        bazi_result: 八字排盘结果
        dayun_result: 大运信息
        target_year: 目标年份
        gender: 性别
    """
    # 流年干支
    year_gan = TIANGAN[(target_year - 4) % 10]
    year_zhi = DIZHI[(target_year - 4) % 12]
    liunian_ganzhi = year_gan + year_zhi

    # 找出对应的大运
    birth_year = bazi_result["birth_year"]
    age = target_year - birth_year
    current_dayun = None
    for dy in dayun_result["dayuns"]:
        if dy["start_age"] <= age < dy["end_age"]:
            current_dayun = dy
            break
    if not current_dayun and dayun_result["dayuns"]:
        current_dayun = dayun_result["dayuns"][-1]

    # 找出该年的小运（简化：直接用流年）
    analysis = analyze_year_fortune(bazi_result, current_dayun, year_gan, year_zhi, age)

    return {
        "year": target_year,
        "age": age,
        "liunian_ganzhi": liunian_ganzhi,
        "liunian_gan": year_gan,
        "liunian_zhi": year_zhi,
        "liunian_wuxing": f"{TIANGAN_WUXING[year_gan]}{DIZHI_WUXING[year_zhi]}",
        "current_dayun": current_dayun,
        "analysis": analysis
    }


def analyze_year_fortune(bazi_result, dayun, year_gan, year_zhi, age):
    """
    分析年度运势的各个方面
    """
    day_master = bazi_result["day_master"]
    day_wx = TIANGAN_WUXING[day_master]
    liunian_wx = TIANGAN_WUXING[year_gan]
    liunian_zhi_wx = DIZHI_WUXING[year_zhi]

    analysis = {
        "财运": "",
        "官运_事业": "",
        "婚姻_感情": "",
        "健康": "",
        "学业": "",
        "流年十神": get_shishen(day_master, year_gan)
    }

    # 流年十神分类
    shishen = analysis["流年十神"]
    gender = bazi_result["gender"]

    # 财运分析
    if shishen in ["正财", "偏财"]:
        analysis["财运"] = f"流年{shishen}临，主财运亨通。利于投资理财、正财偏财皆有收获，但需谨慎分辨，避免因财招祸。"
    elif shishen in ["食神", "伤官"]:
        analysis["财运"] = f"流年{shishen}生财，财源广进。利于通过才华、技术获取收入，但伤官年份需注意守财。"
    elif shishen in ["比肩", "劫财"]:
        analysis["财运"] = f"流年{shishen}，财运有竞争。劫财年份需防破财、朋友借钱、合作纠纷。"
    else:
        analysis["财运"] = f"流年{shishen}，财运平稳。需靠努力积累，不宜投机。"

    # 官运/事业
    if shishen in ["正官", "七杀"]:
        if gender == "男":
            analysis["官运_事业"] = f"流年{shishen}，事业运强劲。{'正官' if shishen == '正官' else '七杀'}主贵人、权力、晋升。利考学、入职、升职，但七杀年需防小人。"
        else:
            analysis["官运_事业"] = f"流年{shishen}，事业有变。{'正官' if shishen == '正官' else '七杀'}主工作变动、上司关系。女命七杀年需注意与异性关系。"
    elif shishen in ["食神", "伤官"]:
        analysis["官运_事业"] = f"流年{shishen}，事业上有创意发挥。食神主稳定、伤官主变动。伤官年份需注意与领导关系，不宜过于张扬。"
    elif shishen in ["正印", "偏印"]:
        analysis["官运_事业"] = f"流年{shishen}，利于学习进修、获得证书、提升能力。印星主智慧、贵人、文书。"
    else:
        analysis["官运_事业"] = f"流年{shishen}，事业平稳，宜守不宜攻。"

    # 婚姻感情
    if gender == "男":
        if shishen in ["正财", "偏财"]:
            analysis["婚姻_感情"] = f"流年{shishen}，异性缘佳。{'正财' if shishen == '正财' else '偏财'}主桃花、恋爱、婚姻。未婚者利遇良缘，已婚者感情升温。"
        elif shishen in ["正官", "七杀"]:
            analysis["婚姻_感情"] = f"流年{shishen}，感情中可能出现竞争者或第三者。七杀年份夫妻间易生矛盾。"
        else:
            analysis["婚姻_感情"] = f"流年{shishen}，感情生活平稳。需主动经营，方能维系。"
    else:
        if shishen in ["正官", "七杀"]:
            analysis["婚姻_感情"] = f"流年{shishen}，异性缘佳。官杀主桃花、恋爱。未婚者利遇心仪对象，已婚者与丈夫关系加深。"
        elif shishen in ["食神", "伤官"]:
            analysis["婚姻_感情"] = f"流年{shishen}，与伴侣易生口角。伤官年份需注意控制情绪，避免伤及感情。"
        else:
            analysis["婚姻_感情"] = f"流年{shishen}，感情生活平淡。"

    # 健康
    wuxing_health = {
        "金": "肺、皮肤、呼吸系统",
        "木": "肝、胆、筋脉、眼睛",
        "水": "肾、膀胱、泌尿系统",
        "火": "心脏、血液、眼睛",
        "土": "脾胃、消化系统"
    }
    if liunian_wx in WUXING_KE and WUXING_KE[liunian_wx] == day_wx:
        analysis["健康"] = f"流年{liunian_wx}克日主{day_wx}，需注意{wuxing_health[day_wx]}方面的健康。建议作息规律，避免过度劳累。"
    elif liunian_wx == day_wx:
        analysis["健康"] = f"流年比和，身心状态良好，但需防过劳。"
    else:
        analysis["健康"] = f"流年{liunian_wx}，健康整体平稳。注意{wuxing_health[liunian_zhi_wx]}保养。"

    # 学业
    if shishen in ["正印", "偏印", "食神"]:
        analysis["学业"] = f"流年{shishen}，学业运佳。印星主智慧领悟、食神主学习稳定。适合考试、研究、进修。"
    elif shishen in ["七杀", "伤官"]:
        analysis["学业"] = f"流年{shishen}，学业有波折。需调整心态，攻克难点。"
    else:
        analysis["学业"] = f"流年{shishen}，学业表现一般，需付出更多努力。"

    return analysis


def predict_liuyue(bazi_result, dayun_result, liunian_result, target_month):
    """
    预测指定月份的流月运势
    """
    # 流月地支固定
    month_zhi = DIZHI[(target_month + 1) % 12]  # 寅月起正月
    # 流月天干根据流年推算
    liunian_gan = liunian_result["liunian_gan"]
    month_gan_start = {
        "甲": "丙", "己": "丙",
        "乙": "戊", "庚": "戊",
        "丙": "庚", "辛": "庚",
        "丁": "壬", "壬": "壬",
        "戊": "甲", "癸": "甲"
    }
    start_gan = month_gan_start[liunian_gan]
    start_idx = TIANGAN.index(start_gan)
    zhi_idx = DIZHI.index(month_zhi)
    offset = (zhi_idx - 2) % 12
    gan_idx = (start_idx + offset) % 10
    month_gan = TIANGAN[gan_idx]

    return {
        "month": target_month,
        "liuyue_ganzhi": month_gan + month_zhi,
        "liuyue_gan": month_gan,
        "liuyue_zhi": month_zhi,
        "wuxing": f"{TIANGAN_WUXING[month_gan]}{DIZHI_WUXING[month_zhi]}"
    }


# ============================================================
# 命例数据（用于演示）
# ============================================================

DEMO_CASES = [
    {
        "name": "示例命例",
        "year": 1995, "month": 8, "day": 13, "hour": 12,
        "gender": "男",
        "description": "男，阳历1995年8月13日中午12点，上海浦东新区"
    }
]


# ============================================================
# 测试代码
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("赛博算命 - 八字排盘测试")
    print("=" * 60)

    for case in DEMO_CASES:
        print(f"\n【{case['name']}】{case['description']}")

        bazi = calc_bazi(case["year"], case["month"], case["day"], case["hour"], case["gender"])
        print(f"  年柱: {bazi['year_pillar']}")
        print(f"  月柱: {bazi['month_pillar']}")
        print(f"  日柱: {bazi['day_pillar']} （日主：{bazi['day_master']}）")
        print(f"  时柱: {bazi['hour_pillar']}")
        print(f"  五行统计: {bazi['wuxing_count']}")
        print(f"  日主五行: {bazi['day_master_wuxing']}")

        dayun = calc_dayun(bazi, case["gender"])
        print(f"  起运: {dayun['qiyun_age']}岁 {dayun['direction']}")
        print(f"  大运: {' → '.join([d['ganzhi'] for d in dayun['dayuns']])}")

        geju = get_geju(bazi)
        print(f"  格局: {geju}")

        xiyong = analyze_xiyongshen(bazi)
        print(f"  日主强弱: {xiyong['day_master_strength']}")
        print(f"  喜用神: {xiyong['xiyong']}")

        shensha = get_shensha(bazi["day_pillar"], bazi["hour_pillar"], bazi["year_pillar"])
        print(f"  神煞: {', '.join(shensha) if shensha else '无'}")

        # 大运关键事件
        print(f"\n  【大运关键事件预测】")
        life_events = predict_life_events(bazi, dayun, case["gender"])
        for le in life_events:
            print(f"  {le['start_age']}-{le['end_age']}岁（{le['ganzhi']}，{le['shishen']}）{le['luck_level']}")
            for ev in le['events']:
                print(f"    [{ev['类型']}][{ev['等级']}] {ev['描述'][:80]}...")

        # 预测2026年
        print(f"\n  【2026年流年预测】")
        liunian = predict_liunian(bazi, dayun, 2026, case["gender"])
        print(f"  流年: {liunian['liunian_ganzhi']}（{liunian['liunian_wuxing']}），{liunian['age']}岁")
        print(f"  流年十神: {liunian['analysis']['流年十神']}")
        print(f"  财运: {liunian['analysis']['财运']}")
        print(f"  事业: {liunian['analysis']['官运_事业']}")
        print(f"  感情: {liunian['analysis']['婚姻_感情']}")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
