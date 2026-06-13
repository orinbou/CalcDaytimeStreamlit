import datetime

import ephem
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import streamlit as st
from matplotlib import ticker
from pytz import exceptions as pytz_exc
from pytz import timezone
from timezonefinder import TimezoneFinder

SF_YMD = "%Y-%m-%d"
SF_HMS = "%H:%M:%S"

# オリジナルfaviconを設置
st.set_page_config(page_title="CalcDaytime", page_icon="assets/favicon.png", layout="wide")

def get_query_param(key: str, default: str) -> str:
    try:
        value = st.query_params.get(key, default)
        if isinstance(value, list):
            value = value[0]
        return str(value) if value not in (None, "") else default
    except Exception:
        params = st.experimental_get_query_params()
        value = params.get(key, [default])
        return value[0] if value else default


def set_query_params(lat: str, lon: str) -> None:
    try:
        st.query_params["lat"] = lat
        st.query_params["lon"] = lon
    except Exception:
        st.experimental_set_query_params(lat=lat, lon=lon)


def hours_to_hms(hours: float) -> str:
    total_seconds = int(round(hours * 3600))
    return f"{total_seconds // 3600:02d}:{(total_seconds % 3600) // 60:02d}:{total_seconds % 60:02d}"


def format_row(
    label: str,
    idx: int,
    x_dates: list[datetime.datetime],
    x_sr_datetimes: list[datetime.datetime],
    x_ss_datetimes: list[datetime.datetime],
    y_daytimes: list[float],
) -> str:
    return (
        f"{label}: (日付, 日の出, 日の入, 日中長[時間]) = "
        f"({x_dates[idx].strftime(SF_YMD)}, "
        f"{x_sr_datetimes[idx].strftime(SF_HMS)}, "
        f"{x_ss_datetimes[idx].strftime(SF_HMS)}, "
        f"{hours_to_hms(y_daytimes[idx])})"
    )


lat_default = get_query_param("lat", "35.4500")
lon_default = get_query_param("lon", "139.6500")

with st.sidebar:
    st.title("CalcDaytime")
    st.caption("powered by Streamlit")
    lat = st.text_input("緯度", value=lat_default)
    lon = st.text_input("経度", value=lon_default)
    st.info("Python の天文計算ライブラリ PyEphem を使用して日の出/日の入を計算します。")
    st.markdown("参考: [天文計算ライブラリ => PyEphem](https://rhodesmill.org/pyephem/)")
    st.markdown("参考: [国立天文台 => 横浜（神奈川）](https://eco.mtk.nao.ac.jp/koyomi/dni/2024/dni15.html)")

set_query_params(lat=lat, lon=lon)

try:
    lat_float = float(lat)
    lon_float = float(lon)
except ValueError:
    st.error("緯度・経度は数値で入力してください。")
    st.stop()

st.markdown("## 入力情報")
st.write(f"位置情報: (緯度, 経度) = ({lat}, {lon})")

point = ephem.Observer()
try:
    point.lat = str(lat_float)
    point.lon = str(lon_float)
except ValueError:
    st.error("緯度・経度の形式が不正です。")
    st.stop()

tf = TimezoneFinder()
tz_name = tf.timezone_at(lat=lat_float, lng=lon_float)
tz = timezone(tz_name) if tz_name else timezone("UTC")

st.write(f"タイムゾーン: {tz_name if tz_name else 'UTC'}")
st.markdown(f"🌎[地図で位置を確認する](https://www.google.com/maps?q={lat},{lon})")

now_utc = datetime.datetime.now(datetime.timezone.utc)
today_str = now_utc.astimezone(tz).strftime(SF_YMD)
start_year = now_utc.astimezone(tz).year

x_dates: list[datetime.datetime] = []
y_sr_times: list[float] = []
y_ss_times: list[float] = []
y_daytimes: list[float] = []
x_sr_datetimes: list[datetime.datetime] = []
x_ss_datetimes: list[datetime.datetime] = []

sun = ephem.Sun()
today_info = None
skipped_dates: list[str] = []

for i in range(366):
    naive_date = datetime.datetime(year=start_year, month=1, day=1, hour=12) + datetime.timedelta(days=i)
    try:
        date_local = tz.localize(naive_date)
    except (pytz_exc.NonExistentTimeError, pytz_exc.AmbiguousTimeError):
        date_local = tz.localize(naive_date, is_dst=None)

    point.date = date_local.astimezone(timezone("UTC"))
    try:
        dt1local = ephem.localtime(point.previous_rising(sun)).astimezone(tz)
        dt2local = ephem.localtime(point.next_setting(sun)).astimezone(tz)
    except (ephem.NeverUpError, ephem.AlwaysUpError):
        skipped_dates.append(date_local.strftime(SF_YMD))
        continue

    day = (dt2local - dt1local).total_seconds() / 3600

    dst_hours_sr = dt1local.dst().total_seconds() / 3600 if dt1local.dst() else 0
    dst_hours_ss = dt2local.dst().total_seconds() / 3600 if dt2local.dst() else 0

    sr_time = dt1local.hour + dt1local.minute / 60.0 + dt1local.second / 3600.0 - dst_hours_sr
    ss_time = dt2local.hour + dt2local.minute / 60.0 + dt2local.second / 3600.0 - dst_hours_ss

    if dt2local.date() > dt1local.date():
        ss_time += 24

    dt0_naive = datetime.datetime(dt1local.year, dt1local.month, dt1local.day)
    try:
        dt0local = tz.localize(dt0_naive, is_dst=False)
    except (pytz_exc.NonExistentTimeError, pytz_exc.AmbiguousTimeError):
        dt0local = tz.localize(dt0_naive)

    x_dates.append(dt0local)
    y_sr_times.append(sr_time)
    y_ss_times.append(ss_time)
    y_daytimes.append(day)
    x_sr_datetimes.append(dt1local)
    x_ss_datetimes.append(dt2local)

    dt0str = dt0local.strftime(SF_YMD)
    dt1str = dt1local.strftime(SF_HMS)
    dt2str = dt2local.strftime(SF_HMS)

    if dt0str == today_str:
        today_info = (
            f"本日の情報: (日付, 日の出, 日の入, 日中長[時間]) = "
            f"({dt0str}, {dt1str}, {dt2str}, {hours_to_hms(day)})"
        )

st.markdown("## 概要情報")
if skipped_dates:
    st.warning(
        "この地点では日の出/日の入りが発生しない日があるため、"
        f"{len(skipped_dates)}日分を除外して表示しています。"
    )

if not y_daytimes:
    st.error("指定した地点では計算可能な日の出/日の入りデータが取得できませんでした。")
    st.stop()

if today_info:
    st.write(today_info)

st.subheader("日の出🌅")
st.write(format_row("【最早】", y_sr_times.index(min(y_sr_times)), x_dates, x_sr_datetimes, x_ss_datetimes, y_daytimes))
st.write(format_row("【最遅】", y_sr_times.index(max(y_sr_times)), x_dates, x_sr_datetimes, x_ss_datetimes, y_daytimes))

st.subheader("日の入🌇")
st.write(format_row("【最早】", y_ss_times.index(min(y_ss_times)), x_dates, x_sr_datetimes, x_ss_datetimes, y_daytimes))
st.write(format_row("【最遅】", y_ss_times.index(max(y_ss_times)), x_dates, x_sr_datetimes, x_ss_datetimes, y_daytimes))

st.subheader("日中長🌞")
st.write(format_row("【夏至】", y_daytimes.index(max(y_daytimes)), x_dates, x_sr_datetimes, x_ss_datetimes, y_daytimes))
st.write(format_row("【冬至】", y_daytimes.index(min(y_daytimes)), x_dates, x_sr_datetimes, x_ss_datetimes, y_daytimes))

fig1, ax1 = plt.subplots(figsize=(10, 5))
ax1.plot(mdates.date2num(x_dates), y_sr_times, color="darkorange")
ax1.plot(mdates.date2num(x_dates), y_ss_times, color="darkblue")
ax1.axvline(now_utc.astimezone(tz), color="r", linestyle="solid", linewidth=2)
ax1.set_title("Sunrise and Sunset Time")
ax1.set_xlabel("Date")
ax1.set_ylabel("Day Time")
ax1.legend(["Sunrise Time", "Sunset Time", "Today"])
ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
ax1.yaxis.set_major_locator(ticker.MultipleLocator(2))
ax1.grid(axis="x")
ax1.minorticks_on()
ax1.grid(which="both", axis="y")
fig1.autofmt_xdate()
st.pyplot(fig1, clear_figure=True)

fig2, ax2 = plt.subplots(figsize=(10, 5))
ax2.plot(mdates.date2num(x_dates), y_daytimes, color="darkorange")
ax2.axvline(now_utc.astimezone(tz), color="r", linestyle="solid", linewidth=2)
ax2.set_title("Day Time Length")
ax2.set_xlabel("Date")
ax2.set_ylabel("Day Time Length [hour]")
ax2.legend(["Day Time Length", "Today"])
ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
ax2.yaxis.set_major_locator(ticker.MultipleLocator(1))
ax2.grid(axis="x")
ax2.minorticks_on()
ax2.grid(which="both", axis="y")
fig2.autofmt_xdate()
st.pyplot(fig2, clear_figure=True)
