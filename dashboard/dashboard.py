import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from pathlib import Path

sns.set(style='dark')

st.set_page_config(page_title="E-Commerce Data Analysis Dashboard", layout="wide")

@st.cache_data
def load_data():
    data_path = Path(__file__).parent / "import os

current_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(current_dir, "main_data.csv.gz")"
    df = pd.read_csv(data_path)
    df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])
    return df

all_df = load_data()

# --- SIDEBAR FILTER ---
st.sidebar.header("Filter Data Transaksi")

min_date = all_df["order_purchase_timestamp"].min().date()
max_date = all_df["order_purchase_timestamp"].max().date()

start_date, end_date = st.sidebar.date_input(
    label="Rentang Tanggal Pembelian",
    min_value=min_date,
    max_value=max_date,
    value=[min_date, max_date]
)

categories = ["Semua Kategori"] + sorted(all_df["product_category_name_english"].dropna().unique().tolist())
selected_category = st.sidebar.selectbox("Pilih Kategori Produk", categories)

main_df = all_df[
    (all_df["order_purchase_timestamp"].dt.date >= start_date) &
    (all_df["order_purchase_timestamp"].dt.date <= end_date)
]

if selected_category != "Semua Kategori":
    main_df = main_df[main_df["product_category_name_english"] == selected_category]

# --- HALAMAN UTAMA ---
st.title("📊 E-Commerce Public Dataset Dashboard (2017–2018)")
st.markdown("Dashboard interaktif untuk memantau performa pendapatan kategori produk dan segmentasi pelanggan (RFM).")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Pesanan Valid", value=f"{main_df['order_id'].nunique():,}")
with col2:
    st.metric("Total Revenue (BRL)", value=f"R$ {main_df['price'].sum():,.2f}")
with col3:
    st.metric("Total Pelanggan Unik", value=f"{main_df['customer_unique_id'].nunique():,}")

st.divider()

# --- VISUALISASI 1: KATEGORI PRODUK ---
st.subheader("1. Performa Pendapatan Kategori Produk (Top 5 vs Bottom 5)")
category_rev = main_df.groupby("product_category_name_english")["price"].sum().sort_values(ascending=False).reset_index()

if not category_rev.empty:
    fig1, ax1 = plt.subplots(nrows=1, ncols=2, figsize=(18, 6))
    colors_top = ["#2b5c8f"] + ["#b0c4de"] * (min(5, len(category_rev)) - 1)
    colors_bottom = ["#c0392b"] + ["#e6b0aa"] * (min(5, len(category_rev)) - 1)

    sns.barplot(x="price", y="product_category_name_english", data=category_rev.head(5), palette=colors_top, ax=ax1[0])
    ax1[0].set_title("Top 5 Kategori Revenue Tertinggi", fontsize=14)
    ax1[0].set_xlabel("Total Revenue (BRL)")
    ax1[0].set_ylabel(None)

    sns.barplot(x="price", y="product_category_name_english", data=category_rev.sort_values(by="price", ascending=True).head(5), palette=colors_bottom, ax=ax1[1])
    ax1[1].set_title("Bottom 5 Kategori Revenue Terendah", fontsize=14)
    ax1[1].set_xlabel("Total Revenue (BRL)")
    ax1[1].set_ylabel(None)
    ax1[1].invert_xaxis()
    ax1[1].yaxis.set_label_position("right")
    ax1[1].yaxis.tick_right()

    plt.tight_layout()
    st.pyplot(fig1)

st.divider()

# --- VISUALISASI 2: ANALISIS RFM ---
st.subheader("2. Best Customers Berdasarkan Parameter RFM")

if not main_df.empty:
    recent_date = main_df["order_purchase_timestamp"].max()
    rfm_df = main_df.groupby("customer_unique_id", as_index=False).agg({
        "order_purchase_timestamp": lambda x: (recent_date - x.max()).days,
        "order_id": "nunique",
        "price": "sum"
    })
    rfm_df.columns = ["customer_id", "recency", "frequency", "monetary"]

    fig2, ax2 = plt.subplots(nrows=1, ncols=3, figsize=(20, 5))

    top_r = rfm_df.sort_values(by="recency", ascending=True).head(5)
    sns.barplot(y="recency", x="customer_id", data=top_r, color="#2b5c8f", ax=ax2[0])
    ax2[0].set_title("By Recency (Days)")
    ax2[0].set_xticklabels([x[:5] for x in top_r["customer_id"]])

    top_f = rfm_df.sort_values(by="frequency", ascending=False).head(5)
    sns.barplot(y="frequency", x="customer_id", data=top_f, color="#2b5c8f", ax=ax2[1])
    ax2[1].set_title("By Frequency")
    ax2[1].set_xticklabels([x[:5] for x in top_f["customer_id"]])

    top_m = rfm_df.sort_values(by="monetary", ascending=False).head(5)
    sns.barplot(y="monetary", x="customer_id", data=top_m, color="#2b5c8f", ax=ax2[2])
    ax2[2].set_title("By Monetary (BRL)")
    ax2[2].set_xticklabels([x[:5] for x in top_m["customer_id"]])

    plt.tight_layout()
    st.pyplot(fig2)

st.caption("Copyright © 2026 - Proyek Analisis Data E-Commerce")
