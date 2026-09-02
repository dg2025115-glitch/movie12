import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------
# 기본 설정
# -----------------------------
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide",
)

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"


@st.cache_data
def load_data(url: str) -> pd.DataFrame:
    df = pd.read_csv(url)

    # genre 열에 세로막대 기호(|)로 여러 장르가 적힌 경우, 첫 번째 장르만 사용
    if "genre" in df.columns:
        df["genre_main"] = (
            df["genre"].astype(str).str.split("|").str[0].str.strip()
        )

    # openDt(여덟 자리 숫자)를 날짜형으로 변환
    if "openDt" in df.columns:
        df["openDt"] = pd.to_datetime(
            df["openDt"].astype(str), format="%Y%m%d", errors="coerce"
        )

    return df


# -----------------------------
# 데이터 불러오기
# -----------------------------
st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")
st.caption(
    "최근 1년간 박스오피스 10위권에 든 영화 가운데, 해당 기간에 개봉한 216편의 데이터를 살펴봅니다."
)

with st.spinner("데이터를 불러오는 중입니다..."):
    df = load_data(DATA_URL)

with st.expander("📄 원본 데이터 미리 보기"):
    st.dataframe(df, use_container_width=True)

st.divider()

# =========================================================
# 그래프 1. 장르별 영화 편수 - 도넛 그래프
# =========================================================
st.header("1. 장르별 영화 편수")

genre_counts = (
    df["genre_main"]
    .value_counts()
    .reset_index()
)
genre_counts.columns = ["genre", "count"]

fig_genre = px.pie(
    genre_counts,
    names="genre",
    values="count",
    hole=0.5,
    title="장르별 영화 편수 분포",
)
fig_genre.update_traces(
    textinfo="label+percent",
    hovertemplate="<b>%{label}</b><br>편수: %{value}편<br>비율: %{percent}<extra></extra>",
)
fig_genre.update_layout(
    legend_title_text="장르",
    margin=dict(t=60, b=20, l=20, r=20),
)

st.plotly_chart(fig_genre, use_container_width=True)

st.info("**이 그래프로 알 수 있는 것:** ")

st.divider()

# =========================================================
# 그래프 2. 장르 안에 영화 - 트리맵 (칸 크기 = 총 관객)
# =========================================================
st.header("2. 장르 속 영화별 총 관객 (트리맵)")

fig_treemap = px.treemap(
    df,
    path=[px.Constant("전체"), "genre_main", "movieNm"],
    values="total_audi",
    title="장르 → 영화별 총 관객 트리맵",
)
fig_treemap.update_traces(
    hovertemplate="<b>%{label}</b><br>총 관객: %{value:,}명<extra></extra>",
)
fig_treemap.update_layout(margin=dict(t=60, b=20, l=20, r=20))

st.plotly_chart(fig_treemap, use_container_width=True)

st.info("**이 그래프로 알 수 있는 것:** ")

st.divider()

# =========================================================
# 그래프 3. 총 관객 히스토그램
# =========================================================
st.header("3. 총 관객 분포 (히스토그램)")

fig_hist = px.histogram(
    df,
    x="total_audi",
    nbins=30,
    title="영화별 총 관객 분포",
)
fig_hist.update_traces(
    hovertemplate="구간: %{x}<br>영화 수: %{y}편<extra></extra>",
)
fig_hist.update_layout(
    xaxis_title="총 관객",
    yaxis_title="영화 편수",
    margin=dict(t=60, b=20, l=20, r=20),
)

st.plotly_chart(fig_hist, use_container_width=True)

# 가장 많은 영화가 몰린 구간과, 총 관객 1위 영화 계산
bin_series = pd.cut(df["total_audi"], bins=30)
top_bin = bin_series.value_counts().idxmax()
top_movie_row = df.loc[df["total_audi"].idxmax()]

st.info(
    f"**이 그래프로 알 수 있는 것:** 대부분의 영화는 총 관객 **{int(top_bin.left):,}명 ~ "
    f"{int(top_bin.right):,}명** 구간에 몰려 있고, 가장 관객이 많은 영화는 "
    f"**'{top_movie_row['movieNm']}'**({int(top_movie_row['total_audi']):,}명)입니다."
)

st.divider()

# =========================================================
# 그래프 4. 개봉일 스크린수 vs 총 관객 - 산점도
# =========================================================
st.header("4. 개봉일 스크린수와 총 관객의 관계 (산점도)")

fig_scatter = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    color="genre_main",
    hover_name="movieNm",
    title="개봉일 스크린수 vs 총 관객",
    labels={"first_scrn": "개봉일 스크린수", "total_audi": "총 관객", "genre_main": "장르"},
)
fig_scatter.update_layout(margin=dict(t=60, b=20, l=20, r=20))

st.plotly_chart(fig_scatter, use_container_width=True)

st.info("**이 그래프로 알 수 있는 것:** ")

st.divider()

# =========================================================
# 그래프 5. 장르별 총 관객 - 상자 그림 (10편 이상 장르만)
# =========================================================
st.header("5. 장르별 총 관객 분포 (상자 그림)")

genre_movie_counts = df["genre_main"].value_counts()
genres_10plus = genre_movie_counts[genre_movie_counts >= 10].index
df_box = df[df["genre_main"].isin(genres_10plus)]

fig_box = px.box(
    df_box,
    x="genre_main",
    y="total_audi",
    hover_name="movieNm",
    points="outliers",
    title="장르별 총 관객 상자 그림 (영화 10편 이상 장르만)",
    labels={"genre_main": "장르", "total_audi": "총 관객"},
)
fig_box.update_layout(margin=dict(t=60, b=20, l=20, r=20))

st.plotly_chart(fig_box, use_container_width=True)

st.info("**이 그래프로 알 수 있는 것:** ")

st.divider()

# =========================================================
# 그래프 6. 개봉일 스크린수 vs 총 관객 - 버블 그래프 (크기 = 첫 주 관객)
# =========================================================
st.header("6. 개봉일 스크린수와 총 관객, 첫 주 관객까지 (버블 그래프)")

fig_bubble = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    color="genre_main",
    size="first_week_audi",
    hover_name="movieNm",
    size_max=45,
    title="개봉일 스크린수 vs 총 관객 (점 크기 = 첫 주 관객)",
    labels={
        "first_scrn": "개봉일 스크린수",
        "total_audi": "총 관객",
        "genre_main": "장르",
        "first_week_audi": "첫 주 관객",
    },
)
fig_bubble.update_layout(margin=dict(t=60, b=20, l=20, r=20))

st.plotly_chart(fig_bubble, use_container_width=True)

st.info("**이 그래프로 알 수 있는 것:** ")

st.divider()

# =========================================================
# 그래프 7. 제작 국가 → 장르 - 선버스트 (칸 크기 = 영화 편수)
# =========================================================
st.header("7. 제작 국가별 장르 구성 (선버스트)")

df_sunburst = df.copy()
df_sunburst["count"] = 1

fig_sunburst = px.sunburst(
    df_sunburst,
    path=["nation", "genre_main"],
    values="count",
    title="제작 국가 → 장르 (칸 크기 = 영화 편수)",
)
fig_sunburst.update_traces(
    hovertemplate="<b>%{label}</b><br>영화 편수: %{value}편<extra></extra>",
)
fig_sunburst.update_layout(margin=dict(t=60, b=20, l=20, r=20))

st.plotly_chart(fig_sunburst, use_container_width=True)

st.info("**이 그래프로 알 수 있는 것:** ")

st.divider()
