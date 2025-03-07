import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

script_dir = Path(os.getcwd()) if "__file__" not in globals() else Path(__file__).parent
csv_path = script_dir / "Dashboard" / "all_data.csv"
logo_path = script_dir / "logo.png"

# Load dataset
all_df = pd.read_csv(csv_path)
all_df["date"] = pd.to_datetime(all_df[["year", "month", "day"]])
all_df.sort_values(by="date", inplace=True)
all_df.reset_index(inplace=True, drop=True)

# Daftar parameter yang digunakan
parameters = ["PM2.5", "PM10", "CO", "SO2", "NO2", "O3"]

# Sidebar untuk memilih rentang waktu
min_date = all_df["date"].min()
max_date = all_df["date"].max()

with st.sidebar:
    st.image(logo_path)
    start_date, end_date = st.date_input("Rentang Waktu", min_value=min_date, max_value=max_date, value=[min_date, max_date])
    selected_parameter = st.sidebar.selectbox("Pilih Parameter", parameters)

# Filter data berdasarkan rentang waktu
filtered_df = all_df[(all_df["date"] >= pd.to_datetime(start_date)) & (all_df["date"] <= pd.to_datetime(end_date))]

# Menambahkan kategori waktu (Siang vs Malam)
filtered_df["waktu"] = filtered_df["date"].dt.hour.apply(lambda x: "Siang" if 6 <= x <= 18 else "Malam")

# Fungsi untuk membuat DataFrame

def create_daily_airquality_df(df):
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    daily_df = df.resample('D', on='date')[numeric_cols].mean().reset_index()
    return daily_df

def create_sum_pollutants_df(df):
    sum_df = df[parameters].sum().to_frame().reset_index()
    sum_df.columns = ['pollutant', 'total_concentration']
    return sum_df.sort_values(by='total_concentration', ascending=False)

def create_by_station_df(df):
    return df.groupby('station')[parameters].mean().reset_index()

def create_by_time_df(df):
    df = df.copy()
    df['hour'] = df['date'].dt.hour
    return df.groupby('hour')[parameters].mean().reset_index()

def create_rfm_airquality_df(df):
    rfm_df = df.groupby("station", as_index=False).agg({
        "date": ["max", "count"],
        "PM2.5": "mean"
    })
    rfm_df.columns = ["station", "max_measurement_date", "frequency", "monetary"]
    recent_date = df["date"].max()
    rfm_df["recency"] = (recent_date - rfm_df["max_measurement_date"]).dt.days
    rfm_df.drop("max_measurement_date", axis=1, inplace=True)
    return rfm_df

# Membuat DataFrame untuk analisis
daily_airquality_df = create_daily_airquality_df(filtered_df)
sum_pollutants_df = create_sum_pollutants_df(filtered_df)
by_station_df = create_by_station_df(filtered_df)
by_time_df = create_by_time_df(filtered_df)
rfm_df = create_rfm_airquality_df(filtered_df)

with st.container():
    st.write("Bagian 1")

# Dashboard Header
st.header("Pemantauan Kualitas Udara 2013 - 2017 di 12 Stasiun Beijing 🌍")

# Perbandingan Siang vs Malam
st.subheader(f"Perbandingan Rata-rata {selected_parameter} Siang vs Malam")
colors = ["#A3BFD9", "#D4D8E4"]
fig, ax = plt.subplots(figsize=(12, 6))
pollution_by_station = all_df.groupby(["station", "waktu"])[selected_parameter].mean().reset_index()
sns.barplot(data=pollution_by_station, x="station", y=selected_parameter, hue="waktu", palette=colors, ax=ax, edgecolor="black")
ax.set_title(f"Perbandingan {selected_parameter} per Stasiun", fontsize=14)
ax.set_xlabel("Stasiun")
ax.set_ylabel(f"{selected_parameter} (µg/m³)")
ax.tick_params(axis='x', rotation=45)
ax.grid(axis="y", linestyle="--", alpha=0.7)
st.pyplot(fig)

# Distribusi berdasarkan Kecepatan Angin
st.subheader(f"Distribusi {selected_parameter} Berdasarkan Kecepatan Angin")
fig, ax = plt.subplots(figsize=(8, 5))
sns.boxplot(x="wind_category", y=selected_parameter, data=filtered_df, hue="wind_category",
            palette=["#72BCD4", "#A0C4D4", "#D3D3D3", "#909090"], ax=ax)
ax.set_xlabel("Kategori Kecepatan Angin")
ax.set_ylabel(f"{selected_parameter} (µg/m³)")
ax.grid(axis="y", linestyle="--", alpha=0.7)
st.pyplot(fig)

# Tren Harian Parameter Kualitas Udara per Stasiun
st.subheader(f"Tren Harian {selected_parameter} per Stasiun")
pollution_trend = filtered_df.groupby(["date", "station"])[selected_parameter].mean().reset_index()
fig, ax = plt.subplots(figsize=(12, 6))
station_colors = ["#A3BFD9", "#B0E0E6", "#C1D3F0", "#D4D8E4", "#A7B8C7", "#A0C4D7", "#8FA8BF", "#7D97B3", "#6B86A7", "#5A769B", "#889EB3", "#9CB3C9"]
stations = pollution_trend['station'].unique()
for station, station_color in zip(stations, station_colors):
    station_data = pollution_trend[pollution_trend['station'] == station]
    sns.lineplot(data=station_data, x='date', y=selected_parameter, marker="o", color=station_color, ax=ax, label=station)
ax.set_title(f"Tren Harian {selected_parameter} per Stasiun", fontsize=12)
ax.set_xlabel("Tanggal")
ax.set_ylabel(f"{selected_parameter} (\u00b5g/m³)")
ax.grid(axis="both", linestyle="--", alpha=0.7)
ax.tick_params(axis="x", rotation=45)
ax.legend(title="Stasiun", fontsize=8)
st.pyplot(fig)

# Rata-rata Konsentrasi Polutan per Stasiun
st.subheader(f"Rata-rata {selected_parameter} per Stasiun")
fig, ax = plt.subplots(figsize=(10, 6))
colors_ = ["#A3BFD9", "#B0E0E6", "#C1D3F0", "#D4D8E4", "#A7B8C7", "#A0C4D7"]
colors_ = colors_ * (len(by_station_df) // len(colors_) + 1)  
station_sorted = by_station_df.sort_values(by=selected_parameter, ascending=False)
sns.barplot(
    data=station_sorted,
    x=selected_parameter,
    y="station",
    palette=colors_[:len(station_sorted)],  
    ax=ax
)
ax.set_xlabel(f"{selected_parameter} (µg/m³)")
ax.set_ylabel("Stasiun")
ax.set_title(f"Rata-rata {selected_parameter} per Stasiun", fontsize=13)
ax.tick_params(axis='y', labelsize=10)
ax.grid(axis="x", linestyle="--", alpha=0.7)
st.pyplot(fig)

st.divider()  # Garis pemisah

with st.container():
    st.write("Bagian 2")

# Analisis RFM Per-Parameter
station_pollution = all_df.groupby("station")[selected_parameter].mean().reset_index()
station_pollution["mean_pollution"] = station_pollution[selected_parameter].mean()

pollution_threshold = 100
all_df["mean_pollution"] = all_df[selected_parameter]
rfm_df = all_df[all_df["mean_pollution"] > pollution_threshold].groupby(by="station", as_index=False).agg({
    "date": ["max", "count"],
    "mean_pollution": "mean"
})
rfm_df.columns = ["station", "max_pollution_date", "frequency", "monetary"]
latest_date = all_df["date"].max()
rfm_df["recency"] = (latest_date - rfm_df["max_pollution_date"]).dt.days
rfm_df['r_rank'] = rfm_df['recency'].rank(ascending=False)
rfm_df['f_rank'] = rfm_df['frequency'].rank(ascending=True)
rfm_df['m_rank'] = rfm_df['monetary'].rank(ascending=True)
rfm_df['r_rank_norm'] = (rfm_df['r_rank']/rfm_df['r_rank'].max())*100
rfm_df['f_rank_norm'] = (rfm_df['f_rank']/rfm_df['f_rank'].max())*100
rfm_df['m_rank_norm'] = (rfm_df['m_rank']/rfm_df['m_rank'].max())*100
rfm_df.drop(columns=['r_rank', 'f_rank', 'm_rank'], inplace=True)
rfm_df['RFM_score'] = (0.15 * rfm_df['r_rank_norm'] +
                        0.28 * rfm_df['f_rank_norm'] +
                        0.57 * rfm_df['m_rank_norm']) * 0.05
rfm_df = rfm_df.round(2)

st.subheader(f"Skor RFM {selected_parameter} untuk Setiap Stasiun Pemantauan")
st.dataframe(rfm_df[['station', 'RFM_score']])
rfm_df["station_segment"] = np.where(
    rfm_df['RFM_score'] > 4.5, "Stasiun Kritis",
    np.where(rfm_df['RFM_score'] > 4, "Stasiun Risiko Tinggi",
    np.where(rfm_df['RFM_score'] > 3, "Stasiun Risiko Sedang",
    np.where(rfm_df['RFM_score'] > 1.6, "Stasiun Risiko Rendah",
    "Stasiun Aman"))))

st.subheader(f"Segmentasi {selected_parameter} Stasiun berdasarkan RFM")
st.dataframe(rfm_df[['station', 'RFM_score', 'station_segment']])

st.subheader(f"Analisis RFM {selected_parameter} untuk Stasiun Pemantauan Kualitas Udara")
colors = ["#A3BFD9", "#B0E0E6", "#C1D3F0", "#D4D8E4", "#A7B8C7"]
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(30, 6))
sns.barplot(y="recency", x="station", hue="station",
            data=rfm_df.sort_values(by="recency", ascending=True).head(5),
            palette=colors, legend=False, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("By Recency (days)", loc="center", fontsize=18)
ax[0].tick_params(axis='x', labelsize=15)
sns.barplot(y="frequency", x="station", hue="station",
            data=rfm_df.sort_values(by="frequency", ascending=False).head(5),
            palette=colors, legend=False, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].set_title("By Frequency", loc="center", fontsize=18)
ax[1].tick_params(axis='x', labelsize=15)
sns.barplot(y="monetary", x="station", hue="station",
            data=rfm_df.sort_values(by="monetary", ascending=False).head(5),
            palette=colors, legend=False, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel(None)
ax[2].set_title("By Monetary", loc="center", fontsize=18)
ax[2].tick_params(axis='x', labelsize=15)
plt.suptitle(f"5 Stasiun Teratas Berdasarkan Analisis RFM {selected_parameter}", fontsize=20)
st.pyplot(fig)

st.subheader(f"Distribusi Stasiun Berdasarkan Kategori Risiko {selected_parameter}")
station_segment_df = rfm_df.groupby("station_segment").station.nunique().reset_index()
plt.figure(figsize=(10, 5))
colors_ = ["#A3BFD9", "#B0E0E6", "#C1D3F0", "#D4D8E4", "#A7B8C7"]
sns.barplot(x="station", y="station_segment", hue="station_segment",
            data=station_segment_df, palette=colors_, legend=False)
plt.title(f"Jumlah Stasiun untuk Setiap Segmen Risiko {selected_parameter}")
st.pyplot(plt)

st.write("Gunakan sidebar untuk memilih parameter yang ingin dianalisis.")
