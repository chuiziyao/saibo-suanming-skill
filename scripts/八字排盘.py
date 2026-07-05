# -*- coding: utf-8 -*-
"""
赛博算命 - 核心八字排盘计算引擎 v2.0

基于 sxtwl（寿星天文历）进行精确的四柱八字排盘、大运推算、
十神分析、神煞查询等功能。日历精度覆盖公元前2000年至公元2100年。

依赖：
  pip install sxtwl

作者：锤无双
"""

from datetime import datetime, timedelta
import calendar

# sxtwl 为可选依赖，未安装时降级为简化版
try:
    import sxtwl
    _HAS_SXTWL = True
except ImportError:
    _HAS_SXTWL = False

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

# 节气名称（sxtwl 使用 0-23 索引，冬至=0）
JIEQI_NAMES = ["冬至", "小寒", "大寒", "立春", "雨水", "惊蛰", "春分", "清明", "谷雨",
               "立夏", "小满", "芒种", "夏至", "小暑", "大暑", "立秋", "处暑", "白露",
               "秋分", "寒露", "霜降", "立冬", "小雪", "大雪"]

# 用于大运推算的关键节气：立春(3)、惊蛰(5)、清明(7)、立夏(9)、芒种(11)、
# 小暑(13)、立秋(15)、白露(17)、寒露(19)、立冬(21)、大雪(23)、小寒(1)
# 每月节气的索引
MONTH_JIEQI = {
    2: 3,   # 立春
    3: 5,   # 惊蛰
    4: 7,   # 清明
    5: 9,   # 立夏
    6: 11,  # 芒种
    7: 13,  # 小暑
    8: 15,  # 立秋
    9: 17,  # 白露
    10: 19, # 寒露
    11: 21, # 立冬
    12: 23, # 大雪
    1: 1,   # 小寒
}


# ============================================================
# 核心计算函数（基于 sxtwl 天文历库）
# ============================================================

def _get_sxtwl_day(year, month, day):
    """获取 sxtwl 日对象（如未安装则返回 None）"""
    if _HAS_SXTWL:
        try:
            return sxtwl.fromSolar(year, month, day)
        except Exception:
            return None
    return None


def _sxtwl_ganzhi_to_str(gz):
    """将 sxtwl 的 GZ 对象转为干支字符串"""
    return TIANGAN[gz.tg] + DIZHI[gz.dz]


def get_year_ganzhi(year, month, day):
    """
    根据公历日期计算年柱（以立春为界，使用 sxtwl）
    降级：使用公式简化版
    """
    sxtwl_day = _get_sxtwl_day(year, month, day)
    if sxtwl_day:
        yTG = sxtwl_day.getYearGZ()  # 立春为界
        return _sxtwl_ganzhi_to_str(yTG)

    # 降级：简化公式
    if month < 2 or (month == 2 and day < 4):
        year -= 1
    gan_idx = (year - 4) % 10
    zhi_idx = (year - 4) % 12
    return TIANGAN[gan_idx] + DIZHI[zhi_idx]


def get_month_ganzhi(year, month, day):
    """
    根据公历日期计算月柱（以节气为界，使用 sxtwl）
    降级：使用五虎遁简化版
    """
    sxtwl_day = _get_sxtwl_day(year, month, day)
    if sxtwl_day:
        mTG = sxtwl_day.getMonthGZ()
        return _sxtwl_ganzhi_to_str(mTG)

    # 降级：五虎遁
    year_gan = get_year_ganzhi(year, month, day)[0]
    month_zhi_map = {1: "丑", 2: "寅", 3: "卯", 4: "辰", 5: "巳", 6: "午",
                     7: "未", 8: "申", 9: "酉", 10: "戌", 11: "亥", 12: "子"}
    if month == 1 or (month == 2 and day < 4):
        month_zhi = "丑"
    else:
        month_zhi = month_zhi_map.get(month, "寅")

    month_gan_start = {"甲": "丙", "己": "丙", "乙": "戊", "庚": "戊",
                       "丙": "庚", "辛": "庚", "丁": "壬", "壬": "壬",
                       "戊": "甲", "癸": "甲"}
    start_gan = month_gan_start[year_gan]
    start_idx = TIANGAN.index(start_gan)
    offset = (DIZHI.index(month_zhi) - 2) % 12
    gan_idx = (start_idx + offset) % 10
    return TIANGAN[gan_idx] + month_zhi


def get_day_ganzhi(year, month, day):
    """
    根据公历日期计算日柱（使用 sxtwl 精确计算）
    降级：使用简化基准日推算
    """
    sxtwl_day = _get_sxtwl_day(year, month, day)
    if sxtwl_day:
        dTG = sxtwl_day.getDayGZ()
        return _sxtwl_ganzhi_to_str(dTG)

    # 降级：简化版（不精确）
    base_date = datetime(2000, 1, 1)
    target_date = datetime(year, month, day)
    delta_days = (target_date - base_date).days
    gan_idx = (TIANGAN.index("甲") + delta_days) % 10
    zhi_idx = (DIZHI.index("午") + delta_days) % 12
    return TIANGAN[gan_idx] + DIZHI[zhi_idx]


def get_hour_ganzhi(day_gan, hour):
    """
    计算时柱（五鼠遁日起时法）
    注：sxtwl 的 getHourGZ() 也使用此算法，故此处直接用五鼠遁
    """
    shichen_zhi = None
    for (start, end), zhi in SHICHEN_MAP.items():
        if start <= end:
            if start <= hour < end:
                shichen_zhi = zhi
                break
        else:
            if hour >= start or hour < end:
                shichen_zhi = zhi
                break
    if not shichen_zhi:
        shichen_zhi = "子"

    day_gan_start = {"甲": "甲", "己": "甲", "乙": "丙", "庚": "丙",
                     "丙": "戊", "辛": "戊", "丁": "庚", "壬": "庚",
                     "戊": "壬", "癸": "壬"}
    start_gan = day_gan_start[day_gan]
    start_idx = TIANGAN.index(start_gan)
    gan_idx = (start_idx + DIZHI.index(shichen_zhi)) % 10
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
    - 男命阳年/女命阴年：顺排（从月柱往后推）
    - 男命阴年/女命阳年：逆排（从月柱往前推）
    - 起运岁数：从出生日到下一个/上一个节气的天数 ÷ 3

    使用 sxtwl 精确定位节气，降级时固定 3 岁起运。
    """
    year = bazi_result["birth_year"]
    month = bazi_result["birth_month"]
    day = bazi_result["birth_day"]
    year_pillar = bazi_result["year_pillar"]
    month_pillar = bazi_result["month_pillar"]
    day_master = bazi_result["day_master"]

    year_gan = year_pillar[0]
    year_yin_yang = TIANGAN_YINYANG[year_gan]
    is_yang_year = year_yin_yang == "阳"

    # 顺逆判断
    if gender == "男":
        shun = is_yang_year
    else:
        shun = not is_yang_year

    # ---- 起运岁数（sxtwl 精确版本） ----
    if _HAS_SXTWL:
        try:
            # 确定出生月对应的节气
            birth_solar = sxtwl.fromSolar(year, month, day)

            if shun:
                # 顺排：找到出生后的下一个节气
                cursor = birth_solar
                for _ in range(40):  # 最多找40天
                    cursor = cursor.after(1)
                    if cursor.hasJieQi():
                        jieqi_idx = cursor.getJieQi()
                        # 只取每月"节"（奇数索引），跳过"气"（偶数索引）
                        # 立春=3, 惊蛰=5, 清明=7, 立夏=9, 芒种=11, ...
                        if jieqi_idx % 2 == 1:
                            jd_next = cursor.getJieQiJD()
                            jd_birth = sxtwl.toJD(birth_solar)
                            days_diff = jd_next - jd_birth
                            break
                else:
                    jd_birth = sxtwl.toJD(birth_solar)
                    days_diff = 30  # fallback
            else:
                # 逆排：找到出生前的上一个节气
                cursor = birth_solar
                for _ in range(40):
                    cursor = cursor.before(1)
                    if cursor.hasJieQi():
                        jieqi_idx = cursor.getJieQi()
                        if jieqi_idx % 2 == 1:
                            jd_prev = cursor.getJieQiJD()
                            jd_birth = sxtwl.toJD(birth_solar)
                            days_diff = jd_birth - jd_prev
                            break
                else:
                    days_diff = 30

            qiyun_age = round(days_diff / 3, 1)
            if qiyun_age < 1:
                qiyun_age = 1
        except Exception:
            qiyun_age = 3  # 降级
    else:
        qiyun_age = 3  # 无 sxtwl 降级

    # ---- 推算大运干支 ----
    month_gan = month_pillar[0]
    month_zhi = month_pillar[1]
    month_gan_idx = TIANGAN.index(month_gan)
    month_zhi_idx = DIZHI.index(month_zhi)

    dayuns = []
    for i in range(1, 9):
        if shun:
            gan_idx = (month_gan_idx + i) % 10
            zhi_idx = (month_zhi_idx + i) % 12
        else:
            gan_idx = (month_gan_idx - i) % 10
            zhi_idx = (month_zhi_idx - i) % 12
        dayuns.append({
            "step": i,
            "start_age": int(qiyun_age + (i - 1) * 10),
            "end_age": int(qiyun_age + i * 10),
            "ganzhi": TIANGAN[gan_idx] + DIZHI[zhi_idx],
            "gan": TIANGAN[gan_idx],
            "zhi": DIZHI[zhi_idx],
            "gan_wuxing": TIANGAN_WUXING[TIANGAN[gan_idx]],
            "zhi_wuxing": DIZHI_WUXING[DIZHI[zhi_idx]],
            "direction": "顺行" if shun else "逆行"
        })

    # 获取起运时的节气名称（用于展示）
    jieqi_info = ""
    if _HAS_SXTWL:
        try:
            birth_solar = sxtwl.fromSolar(year, month, day)
            if shun:
                cursor = birth_solar
                for _ in range(40):
                    cursor = cursor.after(1)
                    if cursor.hasJieQi():
                        idx = cursor.getJieQi()
                        if idx % 2 == 1:
                            jieqi_info = f"顺排（到下一个节气：{JIEQI_NAMES[idx]}）"
                            break
            else:
                cursor = birth_solar
                for _ in range(40):
                    cursor = cursor.before(1)
                    if cursor.hasJieQi():
                        idx = cursor.getJieQi()
                        if idx % 2 == 1:
                            jieqi_info = f"逆排（到上一个节气：{JIEQI_NAMES[idx]}）"
                            break
        except Exception:
            pass

    return {
        "qiyun_age": qiyun_age,
        "direction": "顺排" if shun else "逆排",
        "jieqi_info": jieqi_info,
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
# 专项问题预测函数（v1.2 新增 11 项）
# ============================================================

def predict_children(bazi_result, dayun_result, gender):
    """
    预测子女情况：大致数量、头胎性别、生育最佳大运
    男性以官杀为子女星，女性以食伤为子女星
    兼看时柱（子女宫）
    """
    day_master = bazi_result["day_master"]
    day_pillar = bazi_result["day_pillar"]
    hour_pillar = bazi_result["hour_pillar"]
    wuxing_count = bazi_result["wuxing_count"]

    hour_gan = hour_pillar[0]
    hour_zhi = hour_pillar[1]
    hour_gan_wx = TIANGAN_WUXING[hour_gan]
    hour_zhi_wx = DIZHI_WUXING[hour_zhi]

    # 子女星
    if gender == "男":
        children_star = "官杀（正官/七杀）"
        star_wx = WUXING_KE[TIANGAN_WUXING[day_master]]  # 官杀五行
    else:
        children_star = "食伤（食神/伤官）"
        star_wx = WUXING_SHENG[TIANGAN_WUXING[day_master]]  # 食伤五行

    # 子女数量判断：看四柱中子女星出现的次数 + 时柱旺衰
    star_count = 0
    pillars = [bazi_result["year_pillar"], bazi_result["month_pillar"],
               bazi_result["day_pillar"], bazi_result["hour_pillar"]]
    for p in pillars:
        gan_wx = TIANGAN_WUXING.get(p[0], "")
        zhi_wx = DIZHI_WUXING.get(p[1], "")
        if gan_wx == star_wx:
            star_count += 1
        if zhi_wx == star_wx:
            star_count += 0.5  # 地支藏干算半个

    # 子女数量估算
    if star_count >= 3:
        child_estimate = "3个或以上"
    elif star_count >= 2:
        child_estimate = "2-3个"
    elif star_count >= 1:
        child_estimate = "1-2个"
    else:
        child_estimate = "1个左右（子女星不显，缘分略浅但不代表没有）"

    # 头胎性别：时柱天干阴阳 + 日主阴阳
    day_yy = "阳" if TIANGAN.index(day_master) % 2 == 0 else "阴"
    hour_yy = "阳" if TIANGAN.index(hour_gan) % 2 == 0 else "阴"

    # 时柱地支是否逢冲
    liu_chong = {"子":"午","午":"子","丑":"未","未":"丑","寅":"申","申":"寅","卯":"酉","酉":"卯","辰":"戌","戌":"辰","巳":"亥","亥":"巳"}
    hour_being_chonged = any(liu_chong.get(hour_zhi) == p[1] for p in pillars)

    # 头胎性别判断
    if day_yy == hour_yy:
        first_child_gender = "大概率是儿子"
        first_child_reason = "日主与子女宫同阴阳，阳生阳/阴生阴应男"
    else:
        first_child_gender = "大概率是女儿"
        first_child_reason = "日主与子女宫阴阳相异，阳生阴/阴生阳应女"

    # 子女宫旺衰
    if any(hour_gan_wx == s for s in [wuxing_count.get(k, 0) and k for k in wuxing_count]):
        children_palace_quality = "旺相，子女将来有出息"
    elif hour_being_chonged:
        children_palace_quality = "子女宫受冲，子女成长过程中需多加引导和关爱"
    else:
        children_palace_quality = "平稳，需注重子女教育和培养"

    # 最佳生育时段
    best_periods = []
    for dy in dayun_result["dayuns"]:
        sa = dy["start_age"]
        ea = dy["end_age"]
        if 25 <= sa <= 45:
            ganzhi = dy["ganzhi"]
            shishen = get_shishen(day_master, dy["gan"])
            if (gender == "男" and "官" in shishen) or (gender == "女" and "食" in shishen or "伤" in shishen):
                best_periods.append(f"{sa}-{ea}岁（{ganzhi}，{shishen}运）")

    if not best_periods:
        best_periods = ["25-35岁为常规生育黄金期"]

    return {
        "子女星": children_star,
        "子女数量估算": child_estimate,
        "头胎性别推断": first_child_gender,
        "性别推断依据": first_child_reason,
        "子女宫评价": children_palace_quality,
        "最佳生育时期": best_periods
    }


def predict_spouse(bazi_result, gender):
    """
    预测配偶情况：方位、性格特征、婚姻质量
    男命以正财为妻，女命以正官为夫
    兼看日支（夫妻宫）
    """
    day_master = bazi_result["day_master"]
    day_pillar = bazi_result["day_pillar"]
    day_zhi = day_pillar[1]
    day_zhi_wx = DIZHI_WUXING[day_zhi]

    # 夫妻宫十神
    spouse_palace_shishen = get_shishen(day_master, day_zhi[0] if day_zhi in TIANGAN else day_zhi) if day_zhi in TIANGAN else ""

    # 配偶星
    if gender == "男":
        spouse_star = "正财"
        star_wx = WUXING_KE[TIANGAN_WUXING[day_master]]
    else:
        spouse_star = "正官"
        star_wx = ""

    # 配偶方位：根据日支（夫妻宫）地支方位
    dz_direction = {
        "子": "正北", "午": "正南",
        "卯": "正东", "酉": "正西",
        "寅": "东北", "申": "西南",
        "巳": "东南", "亥": "西北",
        "辰": "东南偏东", "戌": "西北偏西",
        "丑": "东北偏北", "未": "西南偏南"
    }
    spouse_direction = dz_direction.get(day_zhi, "无法判断")

    # 配偶性格特征：基于日支五行
    wx_personality = {
        "金": "刚毅果断、讲义气、有原则，但有时固执己见",
        "木": "仁慈善良、有进取心、身材修长，但有时优柔寡断",
        "水": "聪明灵活、善交际、适应力强，但有时情绪化",
        "火": "热情开朗、行动力强、有领导力，但有时急躁冲动",
        "土": "稳重踏实、诚信可靠、包容心强，但有时保守迟钝"
    }
    spouse_personality = wx_personality.get(day_zhi_wx, "性格平稳")

    # 婚姻质量评估
    day_zhi_being_chonged = False
    liu_chong = {"子":"午","午":"子","丑":"未","未":"丑","寅":"申","申":"寅","卯":"酉","酉":"卯","辰":"戌","戌":"辰","巳":"亥","亥":"巳"}
    pillars = [bazi_result["year_pillar"], bazi_result["month_pillar"],
               bazi_result["day_pillar"], bazi_result["hour_pillar"]]
    for p in pillars:
        if liu_chong.get(day_zhi) == p[1] and p != day_pillar:
            day_zhi_being_chonged = True
            break

    # 日柱是否得令
    month_zhi = bazi_result["month_pillar"][1]
    month_wx = DIZHI_WUXING[month_zhi]
    day_master_supported = (month_wx == TIANGAN_WUXING[day_master] or
                            month_wx == WUXING_SHENG_ME[TIANGAN_WUXING[day_master]])

    if day_zhi_being_chonged:
        marriage_quality = "⚡ 夫妻宫受冲，婚姻需用心经营，中年可能有波动。建议晚婚（28岁后），婚前充分了解对方"
    elif not day_master_supported:
        marriage_quality = "婚姻总体平稳，妻子/丈夫在事业上助益一般，需双方互相扶持"
    else:
        marriage_quality = "✅ 夫妻宫安稳，婚姻基础较好。配偶对自身事业有正面帮助"

    # 配偶家庭背景
    if "伤官" in str(spouse_palace_shishen) or "七杀" in str(spouse_palace_shishen):
        spouse_background = "配偶个性较强，或在家庭中排行靠前（长子/长女），有主见"
    else:
        spouse_background = "配偶家庭背景中等偏上，性格温和，与其相处融洽"

    return {
        "配偶星": spouse_star,
        "配偶方位": spouse_direction,
        "配偶性格": spouse_personality,
        "婚姻质量": marriage_quality,
        "配偶背景": spouse_background,
        "夫妻宫地支": day_zhi
    }


def predict_resolve_bad_luck(year_bazi_map, xiyong_result):
    """
    流年不利化解方法
    基于喜用神给出五行化解建议
    """
    xiyong = xiyong_result["xiyong"] or []
    jishen = xiyong_result["jishen"] or []

    wx_colors = {"金": "白色、金色、银色", "木": "绿色、青色", "水": "黑色、深蓝色",
                  "火": "红色、紫色", "土": "黄色、棕色、卡其色"}
    wx_directions = {"金": "西方", "木": "东方", "水": "北方", "火": "南方", "土": "中央/本地"}
    wx_accessories = {"金": "金属饰品、银饰、白水晶", "木": "木质饰品、绿松石、翡翠",
                       "水": "黑曜石、海蓝宝、黑玛瑙", "火": "红玛瑙、石榴石、红纹石",
                       "土": "黄水晶、蜜蜡、和田玉"}
    wx_activities = {"金": "多去银行、金融场所、接触金属器械", "木": "多去公园、森林、种植绿植",
                      "水": "多去水边、游泳、养鱼、泡温泉", "火": "多去热闹场所、参加社交活动",
                      "土": "多去山区、田园、种花养草"}

    methods = []
    for wx in xiyong:
        methods.append({
            "五行": wx,
            "颜色": wx_colors.get(wx, ""),
            "方位": wx_directions.get(wx, ""),
            "饰品": wx_accessories.get(wx, ""),
            "活动": wx_activities.get(wx, ""),
            "搭配建议": f"多穿{wx_colors.get(wx, '')}衣物，在{wx_directions.get(wx, '')}方摆放相应物品"
        })

    # 通用化解方法
    general_methods = [
        "流年不利时，减少重大决策（投资、跳槽、结婚等）",
        "多做善事、捐款、放生，积累福报",
        "佩戴本命佛或喜用神相关饰品",
        "改变居家/办公风水布局，增强喜用神方位能量",
        "流年不利的月份，减少外出应酬，多在家休养",
        "年底前清扫房屋，丢弃破旧物品，迎接新年运势"
    ]

    return {
        "喜用神方法": methods,
        "通用方法": general_methods,
        "核心原则": f"以{'、'.join(xiyong) if xiyong else '中和'}五行为主导，抑制{'、'.join(jishen) if jishen else '过旺'}五行"
    }


def predict_official_career(bazi_result, dayun_result, gender):
    """
    官运分析：是否适合当官、官运走势
    基于正官/七杀在命局中的位置和旺衰
    """
    day_master = bazi_result["day_master"]
    day_wx = TIANGAN_WUXING[day_master]
    xiyong = analyze_xiyongshen(bazi_result)["xiyong"]
    jishen = analyze_xiyongshen(bazi_result)["jishen"]

    # 正官/七杀五行
    guan_sha_wx = WUXING_KE[day_wx]

    # 统计官杀在四柱中的出现
    pillars = [bazi_result["year_pillar"], bazi_result["month_pillar"],
               bazi_result["day_pillar"], bazi_result["hour_pillar"]]

    guan_count = 0
    sha_count = 0
    guan_positions = []
    for p_name, p in zip(["年柱", "月柱", "日柱", "时柱"], pillars):
        shishen_gan = get_shishen(day_master, p[0])
        if "正官" in shishen_gan:
            guan_count += 1
            guan_positions.append(f"{p_name}({p}，{shishen_gan})")
        if "七杀" in shishen_gan:
            sha_count += 1
            guan_positions.append(f"{p_name}({p}，{shishen_gan})")

    # 官运判断
    if guan_sha_wx in xiyong:
        official_suitability = "✅ 适合从政/管理岗位"
        suitability_detail = f"官杀五行为{'、'.join(xiyong)}（喜用神），官运旺且能带来正面发展。适合考公务员、国企管理、事业单位。"
    elif guan_count >= 2:
        official_suitability = "⚡ 官杀混杂，管理有压力但可胜任"
        suitability_detail = "官杀虽多但不为喜用，管理岗位伴随压力。适合技术管理、中层管理，不宜追求极高权力。"
    else:
        official_suitability = "➖ 官运一般，管理路线不是首选"
        suitability_detail = "命局官杀力量不足，主动求官较吃力。可考虑专业路线或技术专家方向。"

    # 大运官运走势
    official_peaks = []
    for dy in dayun_result["dayuns"]:
        shishen_gan = get_shishen(day_master, dy["gan"])
        if "官" in shishen_gan:
            quality = "吉" if guan_sha_wx in xiyong else "中"
            official_peaks.append({
                "age": f"{dy['start_age']}-{dy['end_age']}",
                "ganzhi": dy["ganzhi"],
                "analysis": f"{'正官' if '正官' in shishen_gan else '七杀'}运，{'官运亨通，利于升职掌权' if quality == '吉' else '官运有提升但伴随压力和挑战'}"
            })

    if not official_peaks:
        official_peaks.append({"age": "无", "ganzhi": "无", "analysis": "一生大运中官运机遇较少，建议走专业或技术路线"})

    current_peaks = [p for p in official_peaks if p["age"] != "无" and
                     any(int(p["age"].split("-")[0]) <= a <= int(p["age"].split("-")[1])
                     for a in range(25, 55))]

    return {
        "适合从政/管理": official_suitability,
        "详细分析": suitability_detail,
        "官杀出现位置": guan_positions if guan_positions else ["四柱中官杀不显"],
        "官运高峰期": official_peaks[:3],
        "职业生涯建议": "走管理路线" if guan_sha_wx in xiyong else "走专业技术路线，以技术实力服人"
    }


def predict_wealth_life_stages(bazi_result, dayun_result, gender):
    """
    财运分阶段分析：童年、青年、中年、晚年
    """
    day_master = bazi_result["day_master"]
    day_wx = TIANGAN_WUXING[day_master]
    xiyong = analyze_xiyongshen(bazi_result)["xiyong"]

    cai_wx = WUXING_KE[day_wx]
    cai_is_xiyong = cai_wx in xiyong

    stages = {"童年（0-12岁）": [], "少年（12-18岁）": [], "青年（18-35岁）": [],
              "中年（35-55岁）": [], "晚年（55岁+）": []}

    for dy in dayun_result["dayuns"]:
        sa, ea = dy["start_age"], dy["end_age"]
        shishen = get_shishen(day_master, dy["gan"])
        wx = dy["gan_wuxing"]
        entry = f"{dy['ganzhi']}（{shishen}）"

        rating = "中等"
        if "财" in shishen and cai_is_xiyong:
            rating = "旺"
        elif "财" in shishen and not cai_is_xiyong:
            rating = "有财但有波折"
        elif "劫" in shishen:
            rating = "较差（易破财）"
        elif "印" in shishen and cai_is_xiyong:
            rating = "积累期"
        elif wx in xiyong:
            rating = "稳中有升"

        d = f"{dy['ganzhi']}({sa}-{ea}岁)：{rating}"

        if sa < 12:
            stages["童年（0-12岁）"].append(d)
        elif sa < 18:
            stages["少年（12-18岁）"].append(d)
        elif sa < 35:
            stages["青年（18-35岁）"].append(d)
        elif sa < 55:
            stages["中年（35-55岁）"].append(d)
        else:
            stages["晚年（55岁+）"].append(d)

    # 总结
    childhood = "家庭经济状况一般，花钱之处较多" if any("劫" in s for s in stages["童年（0-12岁）"]) else "童年生活无忧，家庭经济稳定"
    youth = "初入社会，财运平平，以积累经验和人脉为主"
    middle_age = "财运" + ("逐步走高，事业步入正轨" if cai_is_xiyong else "有起有落，需靠努力和智慧积累财富")
    later_life = "晚年财运" + ("相当不错，可享清福" if "丙子" in str(stages["晚年（55岁+）"]) or cai_is_xiyong else "平稳，够用但不奢侈")

    return {
        "童年": {"大运": stages["童年（0-12岁）"], "总结": childhood},
        "少年": {"大运": stages["少年（12-18岁）"], "总结": youth},
        "青年": {"大运": stages["青年（18-35岁）"], "总结": youth},
        "中年": {"大运": stages["中年（35-55岁）"], "总结": middle_age},
        "晚年": {"大运": stages["晚年（55岁+）"], "总结": later_life},
        "总体评价": "财运随年龄稳步上升" if cai_is_xiyong else "财运早年平淡、中年发力、晚年丰收"
    }


def predict_peach_blossom(bazi_result, dayun_result, gender):
    """
    桃花运分析：一生桃花运走势，桃花劫判断
    """
    day_master = bazi_result["day_master"]
    shensha = get_shensha(bazi_result["day_pillar"], bazi_result["hour_pillar"], bazi_result["year_pillar"])
    has_peach = "桃花星" in shensha

    pillars = [bazi_result["year_pillar"], bazi_result["month_pillar"],
               bazi_result["day_pillar"], bazi_result["hour_pillar"]]

    # 桃花劫条件：桃花 + 劫财/伤官
    has_jiecai = False
    for p_name, p in zip(["年", "月", "日", "时"], pillars):
        if "劫财" in get_shishen(day_master, p[0]):
            has_jiecai = True
            break

    # 桃花旺的大运
    peach_dayuns = []
    peach_trouble_dayuns = []
    for dy in dayun_result["dayuns"]:
        sa, ea = dy["start_age"], dy["end_age"]
        shishen = get_shishen(day_master, dy["gan"])
        if sa >= 18:
            if "财" in shishen and gender == "男":
                peach_dayuns.append(f"{dy['ganzhi']}({sa}-{ea}岁)：{'正财为妻星，此运易遇正缘' if '正' in shishen else '偏财为桃花，异性缘旺'}")
            if "官" in shishen and gender == "女":
                peach_dayuns.append(f"{dy['ganzhi']}({sa}-{ea}岁)：官星为夫星，此运易遇正缘")
            if "劫" in shishen:
                peach_trouble_dayuns.append(f"{dy['ganzhi']}({sa}-{ea}岁)：劫财运，桃花多但易成桃花劫")

    peach_blossom_analysis = {
        "命中桃花": "🌸 命带桃花星，异性缘佳，人缘好" if has_peach else "桃花不显，感情较为平淡，正缘需等待",
        "桃花劫风险": "⚠️ 桃花劫风险较高，劫财+桃花组合，慎防第三者插足、破财桃花" if has_jiecai and has_peach else "桃花劫风险较低" if has_peach else "因桃花不旺，桃花劫风险也低",
        "桃花旺期": peach_dayuns[:3] if peach_dayuns else ["18岁后逐年有异性缘，但桃花力度一般"],
        "桃花劫预警": peach_trouble_dayuns if peach_trouble_dayuns else [],
        "感情建议": "既有桃花星加持，把握正缘大运的窗口期。远离劫财运中的烂桃花" if has_peach else "主动扩展社交圈，不急于求成"
    }

    return peach_blossom_analysis


def predict_best_child_birth_time(bazi_result, dayun_result, gender):
    """
    测算生儿子/生女儿的最佳年月份
    基于大运子女星 + 阴阳避忌
    """
    day_master = bazi_result["day_master"]
    birth_year = bazi_result["birth_year"]

    if gender == "男":
        son_star = "七杀"  # 阳官杀应男
        daughter_star = "正官"  # 阴官杀应女
    else:
        son_star = "伤官"  # 阳食伤应男
        daughter_star = "食神"  # 阴食伤应女

    son_years = []
    daughter_years = []

    # 在大运中寻找子女星有利的年份
    for dy in dayun_result["dayuns"]:
        sa, ea = dy["start_age"], dy["end_age"]
        if sa < 25 or sa > 45:
            continue
        target_years = range(birth_year + sa, birth_year + min(ea, 45))
        for yr in target_years[:3]:  # 每个大运取前3年
            liunian_gan = TIANGAN[((yr - 4) % 60) % 10]  # 简化流年天干
            liunian_shishen = get_shishen(day_master, liunian_gan)
            if yr <= 2026 + 10:  # 未来年份
                if son_star in liunian_shishen:
                    son_years.append(f"{yr}年（{liunian_shishen}流年）→ 宜生儿子")
                if daughter_star in liunian_shishen:
                    daughter_years.append(f"{yr}年（{liunian_shishen}流年）→ 宜生女儿")

    # 如果没有精确结果，给通用建议
    if not son_years:
        son_years = [f"生育子女的常规最佳年龄25-35岁，具体需精确排流月"]
    if not daughter_years:
        daughter_years = [f"生育子女的常规最佳年龄25-35岁，具体需精确排流月"]

    return {
        "生儿子的有利年份": son_years[:5],
        "生女儿的有利年份": daughter_years[:5],
        "方法说明": "生男生女与流年天干密切相关，建议在目标年份的春季（3-5月）或秋季（9-11月）受孕"
    }


def predict_best_work_direction(bazi_result, gender):
    """
    毕业后最佳工作方位
    基于喜用神五行对应方位
    """
    xiyong = analyze_xiyongshen(bazi_result)["xiyong"]

    wx_direction = {"金": "西方", "木": "东方", "水": "北方", "火": "南方", "土": "中央/本地"}
    wx_cities = {
        "金": "西部城市（成都、重庆、西安）或金融中心（上海陆家嘴、深圳福田）",
        "木": "东部城市（上海、杭州、南京、苏州）或文化教育发达城市",
        "水": "北方城市（北京、天津、青岛、大连）或沿海沿江城市",
        "火": "南部城市（广州、深圳、海口、厦门）或科技互联网中心",
        "土": "中部城市（武汉、郑州、长沙）或本地发展"
    }
    wx_industries = {
        "金": "金融、法律、精密制造、机械、汽车、珠宝",
        "木": "教育、文化、出版、医疗、环保、农林",
        "水": "物流、贸易、旅游、传媒、咨询、航海",
        "火": "IT互联网、能源、餐饮、娱乐、市场营销",
        "土": "房地产、建筑、矿业、农业、公务员"
    }

    best_direction = wx_direction.get(xiyong[0], "本地") if xiyong else "本地"
    best_cities = wx_cities.get(xiyong[0], "") if xiyong else ""
    best_industries = wx_industries.get(xiyong[0], "") if xiyong else ""

    return {
        "最佳方位": f"去{best_direction}发展最为有利",
        "推荐城市": best_cities,
        "适合行业": best_industries,
        "次要方位": wx_direction.get(xiyong[1], "") if len(xiyong) > 1 else "",
        "原理": f"日主{'、'.join(xiyong) if xiyong else '中和'}为喜用神，{'、'.join(xiyong) if xiyong else '中和'}对应的方位和行业对命主最有利"
    }


def predict_career_or_business(bazi_result, dayun_result, gender):
    """
    分析适合打工还是创业当老板
    基于正官（稳定） vs 偏财/七杀（创业）对比
    """
    day_master = bazi_result["day_master"]
    xiyong = analyze_xiyongshen(bazi_result)["xiyong"]
    wuxing_count = bazi_result["wuxing_count"]

    pillars = [bazi_result["year_pillar"], bazi_result["month_pillar"],
               bazi_result["day_pillar"], bazi_result["hour_pillar"]]

    zheng_guan = 0
    pian_cai = 0
    qi_sha = 0
    for p in pillars:
        ss = get_shishen(day_master, p[0])
        if "正官" in ss: zheng_guan += 1
        if "偏财" in ss: pian_cai += 1
        if "七杀" in ss: qi_sha += 1

    # 判断倾向
    stable_score = zheng_guan * 3
    biz_score = pian_cai * 2 + qi_sha * 2

    if stable_score > biz_score + 2:
        recommendation = "✅ 适合打工/体制内"
        detail = "命局正官力量强，性格稳重守规矩，适合在大型企业、国企、政府机关稳定发展。按部就班升职是最优路径。"
    elif biz_score > stable_score + 2:
        recommendation = "🚀 适合创业/自己当老板"
        detail = "偏财七杀旺，有冒险精神和商业嗅觉。创业虽然辛苦但回报高。注意控制风险，不宜同时铺太多摊子。"
    else:
        recommendation = "🔄 两者皆可，建议先打工后创业"
        detail = "命局官杀财星均衡，具备打工者的稳重和创业者的敏锐。建议先在平台积累资源和人脉（25-35岁），再考虑创业（35岁后）。"

    # 各阶段建议
    stages_advice = []
    for dy in dayun_result["dayuns"]:
        sa, ea = dy["start_age"], dy["end_age"]
        shishen = get_shishen(day_master, dy["gan"])
        if 20 <= sa <= 50:
            if "官" in shishen:
                stages_advice.append(f"{sa}-{ea}岁（{dy['ganzhi']}）：宜打工积累，不适合创业")
            elif "财" in shishen:
                stages_advice.append(f"{sa}-{ea}岁（{dy['ganzhi']}）：财运佳，创业有机会但需谨慎")

    return {
        "核心判断": recommendation,
        "详细分析": detail,
        "各阶段建议": stages_advice[:4],
        "统计": f"正官{zheng_guan}个，偏财{pian_cai}个，七杀{qi_sha}个"
    }


def predict_life_lowest_point(bazi_result, dayun_result, gender):
    """
    测算人生最低谷的年份
    基于大运综合评分，找出运势最差的阶段
    """
    day_master = bazi_result["day_master"]
    xiyong = analyze_xiyongshen(bazi_result)["xiyong"]
    jishen = analyze_xiyongshen(bazi_result)["jishen"]

    # 对所有大运打分
    scored_dayuns = []
    for dy in dayun_result["dayuns"]:
        sa, ea = dy["start_age"], dy["end_age"]
        shishen = get_shishen(day_master, dy["gan"])
        gan_wx = dy["gan_wuxing"]
        zhi_wx = dy["zhi_wuxing"]

        score = 0
        if gan_wx in xiyong: score += 2
        if gan_wx in jishen: score -= 2
        if zhi_wx in xiyong: score += 1
        if zhi_wx in jishen: score -= 1
        if "劫" in shishen: score -= 2
        if "杀" in shishen: score -= 1
        if "官" in shishen: score -= 1  # 身弱忌官杀
        if "财" in shishen: score += 2

        scored_dayuns.append({
            "age": f"{sa}-{ea}", "ganzhi": dy["ganzhi"],
            "shishen": shishen, "score": score
        })

    scored_dayuns.sort(key=lambda x: x["score"])
    lowest = scored_dayuns[:2]  # 最低的2个
    highest = sorted(scored_dayuns, key=lambda x: -x["score"])[:2]  # 最高的2个

    # 化解方法
    resolve = predict_resolve_bad_luck({}, analyze_xiyongshen(bazi_result))

    return {
        "最低谷时期": [{
            "age": l["age"],
            "大运": l["ganzhi"],
            "十神": l["shishen"],
            "低谷原因": f"大运{'、'.join(l['ganzhi'])}，五行不利，事业财运承压" if l["score"] <= -2 else "运势稍逊，但并非大难"
        } for l in lowest],
        "化解建议": resolve["通用方法"][:4],
        "核心原则": resolve["核心原则"]
    }


def predict_life_peak_period(bazi_result, dayun_result, gender):
    """
    测算人生最辉煌/收获最大的时期
    基于大运综合评分 + 偏财/正官/正印等关键指标
    """
    day_master = bazi_result["day_master"]
    xiyong = analyze_xiyongshen(bazi_result)["xiyong"]
    jishen = analyze_xiyongshen(bazi_result)["jishen"]

    scored_dayuns = []
    for dy in dayun_result["dayuns"]:
        sa, ea = dy["start_age"], dy["end_age"]
        shishen = get_shishen(day_master, dy["gan"])
        gan_wx = dy["gan_wuxing"]
        zhi_wx = dy["zhi_wuxing"]

        score = 0
        if gan_wx in xiyong: score += 3
        if gan_wx in jishen: score -= 2
        if zhi_wx in xiyong: score += 1
        if zhi_wx in jishen: score -= 1
        if "财" in shishen: score += 3
        if "官" in shishen: score += 2
        if "印" in shishen: score += 1
        if "劫" in shishen: score -= 2
        if "伤" in shishen: score -= 1

        # 对于每个大运，找出最旺的流年（取该大运中间年份）
        mid_year = bazi_result["birth_year"] + (sa + ea) // 2

        scored_dayuns.append({
            "age": f"{sa}-{ea}", "ganzhi": dy["ganzhi"],
            "shishen": shishen, "score": score,
            "mid_year": mid_year
        })

    scored_dayuns.sort(key=lambda x: -x["score"])
    peaks = scored_dayuns[:3]

    return {
        "最辉煌时期": [{
            "age": p["age"],
            "大运": p["ganzhi"],
            "十神": p["shishen"],
            "收获类型": "财官印俱全，事业财运双丰收" if p["score"] >= 4 else "运势上佳，事业有较大突破" if p["score"] >= 2 else "稳中有升，积累期",
            "关键年份": f"约{p['mid_year']}年前后为峰值期"
        } for p in peaks],
        "建议": "巅峰时期切勿骄傲自满，多积德积福，为低谷做准备。财富要分散配置，不宜全部压在单一投资上"
    }


# ============================================================
# v2.0 新增：时辰不明处理函数
# ============================================================

def analyze_unknown_hour(year, month, day, gender):
    """
    当用户出生时辰不明确时：
    1. 列出 12 个时辰的关键差异（日主相同，时柱不同）
    2. 指出最可能影响命局的 3-4 个关键时辰
    3. 提供关键差异点，供用户根据实际人生事件倒推

    返回:
        dict: 包含时辰对比表、关键差异点、倒推问题
    """
    # 先排基础三柱（年月日柱不依赖时辰）
    year_pillar = get_year_ganzhi(year, month, day)
    month_pillar = get_month_ganzhi(year, month, day)
    day_pillar = get_day_ganzhi(year, month, day)
    day_master = day_pillar[0]

    # 12 时辰分析
    hour_variants = []
    for hour_24 in range(0, 24, 2):  # 每 2 小时一个时辰（取中间值）
        hz = get_hour_ganzhi(day_master, hour_24)

        # 快速构建临时命盘
        tmp_bazi = {
            "year_pillar": year_pillar, "month_pillar": month_pillar,
            "day_pillar": day_pillar, "hour_pillar": hz,
            "day_master": day_master, "day_master_wuxing": TIANGAN_WUXING[day_master],
            "birth_year": year, "birth_month": month, "birth_day": day,
            "wuxing_count": {}  # 略，不需要完整五行统计
        }

        # 子女宫分析
        hour_zhi = hz[1]
        hour_wx = DIZHI_WUXING[hour_zhi]
        day_zhi = day_pillar[1]
        liu_chong = {"子": "午", "午": "子", "丑": "未", "未": "丑", "寅": "申", "申": "寅",
                     "卯": "酉", "酉": "卯", "辰": "戌", "戌": "辰", "巳": "亥", "亥": "巳"}

        children_palace_note = ""
        if liu_chong.get(day_zhi) == hour_zhi:
            children_palace_note = "⚠️ 子女宫逢冲，子女缘分稍薄或子女个性较强"
        elif liu_chong.get(hour_zhi) == day_zhi:
            children_palace_note = "⚠️ 子女宫被冲，子女成长或亲子关系有挑战"

        # 时柱十神（影响晚年/子女）
        hour_shishen = get_shishen(day_master, hz[0])

        # 桃花判断
        zodiac_group = {"申": "申子辰", "子": "申子辰", "辰": "申子辰",
                        "寅": "寅午戌", "午": "寅午戌", "戌": "寅午戌",
                        "巳": "巳酉丑", "酉": "巳酉丑", "丑": "巳酉丑",
                        "亥": "亥卯未", "卯": "亥卯未", "未": "亥卯未"}
        group = zodiac_group.get(hour_zhi, "")
        peach_zhi = {"申子辰": "酉", "寅午戌": "卯", "巳酉丑": "午", "亥卯未": "子"}
        has_peach = (hour_zhi == peach_zhi.get(group, ""))

        variant = {
            "hour": f"{hour_24:02d}:00",
            "shichen": SHICHEN_NAMES.get(hz[1], hz[1]),
            "hour_pillar": hz,
            "shishen": hour_shishen,
            "children": "子女宫" + ("旺" if hour_wx in [TIANGAN_WUXING[day_master], WUXING_SHENG_ME[TIANGAN_WUXING[day_master]]] else "平"),
            "children_note": children_palace_note,
            "peach": "桃花" if has_peach else "无",
            "personality": f"晚年/子女特征：{_describe_hour_shishen(hour_shishen)}"
        }
        hour_variants.append(variant)

    # 找出最具区分度的时辰（时柱十神不同的）
    seen_shishen = set()
    key_variants = []
    for v in hour_variants:
        if v["shishen"] not in seen_shishen and len(key_variants) < 5:
            seen_shishen.add(v["shishen"])
            key_variants.append(v)

    # 倒推问题
    reverse_questions = [
        "您的性格更偏向开朗外向（午时附近），还是安静内敛（子时附近）？",
        "您的兄弟姐妹数量或关系密切程度如何？（比肩/劫财时柱→兄弟缘分强）",
        "您的子女数量/养育体验？（时柱为子女宫，官杀/食伤时柱子女缘分较强）",
        "您是否有过异地求学/工作的经历？在哪几年？（驿马星时柱→早年动迁）",
        "您的感情/桃花经历如何？大致在哪几年有明显桃花？（桃花星时柱→异性缘强）",
        "您和父母的关系？父亲/母亲哪一方更亲近？（印星旺→母亲亲近，财星旺→父亲亲近）",
    ]

    return {
        "已知年月日柱": f"{year_pillar} {month_pillar} {day_pillar}",
        "日主": day_master,
        "日主五行": TIANGAN_WUXING[day_master],
        "十二时辰对比": hour_variants,
        "关键差异时辰": key_variants,
        "倒推问卷": reverse_questions,
        "说明": "请根据您的实际人生经历回答以上问题，AI 将帮您逐步缩小时辰范围。通常回答 3-5 个关键问题即可确定时辰。"
    }


def _describe_hour_shishen(shishen):
    """描述时柱十神对晚年和子女的影响"""
    desc = {
        "比肩": "晚年独立自主，子女自食其力",
        "劫财": "晚年社交活跃但需防破财，子女个性强",
        "食神": "晚年安逸享福，子女温顺孝顺",
        "伤官": "晚年思维活跃但易孤独，子女才华出众但叛逆",
        "偏财": "晚年财运佳慷慨大方，子女独立有能力",
        "正财": "晚年经济稳定，子女踏实稳重",
        "七杀": "晚年有权威但压力大，子女坚毅有魄力",
        "正官": "晚年有声望受人尊重，子女守规矩有出息",
        "偏印": "晚年喜欢独处钻研，子女聪明但个性孤僻",
        "正印": "晚年有贵人缘内心安宁，子女温和好学",
    }
    return desc.get(shishen, "性格平稳")


def guide_hour_deduction(hour_variants, user_answers):
    """
    根据用户对倒推问题的回答，推荐最可能的时辰

    参数:
        hour_variants: analyze_unknown_hour() 返回的 "十二时辰对比"
        user_answers: dict，如 {"外向": True, "桃花旺": True, "子女多": False}

    返回:
        list: 按可能性排序的时辰推荐
    """
    scores = []
    for v in hour_variants:
        score = 0
        shishen = v["shishen"]
        has_peach = v["peach"] != "无"

        # 外向型 → 阳气旺的时辰（午、巳、未等火土时辰）
        if user_answers.get("外向"):
            if any(x in v["shichen"] for x in ["午", "巳", "未", "申", "酉"]):
                score += 2

        # 内向型 → 阴气重的时辰
        if user_answers.get("内向"):
            if any(x in v["shichen"] for x in ["子", "亥", "丑", "寅", "卯"]):
                score += 2

        # 桃花旺
        if user_answers.get("桃花旺") and has_peach:
            score += 3

        # 子女多 → 官杀/食伤时柱
        if user_answers.get("子女多"):
            if shishen in ["七杀", "正官", "食神", "伤官"]:
                score += 2

        # 兄弟缘强 → 比肩/劫财
        if user_answers.get("兄弟缘强"):
            if shishen in ["比肩", "劫财"]:
                score += 2

        # 母亲亲 → 印星
        if user_answers.get("母亲亲"):
            if shishen in ["正印", "偏印"]:
                score += 2

        # 父亲亲 → 财星
        if user_answers.get("父亲亲"):
            if shishen in ["正财", "偏财"]:
                score += 2

        scores.append((v, score))

    scores.sort(key=lambda x: -x[1])
    return [
        {
            "时辰": v["shichen"],
            "时柱": v["hour_pillar"],
            "十神": v["shishen"],
            "可能性": "高" if s >= 4 else "中" if s >= 2 else "低",
            "依据": f"得分 {s}",
            "特征": f"桃花：{v['peach']}，{v['personality']}"
        }
        for v, s in scores[:6]
    ]


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
