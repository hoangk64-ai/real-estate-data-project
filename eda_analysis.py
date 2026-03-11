"""
Exploratory Data Analysis
Author: Nguyen Huy

Tasks:
- Data exploration
- Statistical analysis
- Data visualization
- Insight extraction
"""


import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

db_path = "real_estate_danang_quangnam.db"

if not os.path.exists(db_path):
    alt_path = os.path.join("data", "real_estate_danang_quangnam.db")
    if os.path.exists(alt_path):
        db_path = alt_path

conn = sqlite3.connect(db_path)
df = pd.read_sql("SELECT * FROM bds_data", conn)
conn.close()

df = df.drop_duplicates()
df = df.replace("", np.nan)

for col in ["tieu_de", "vi_tri", "muc_gia", "dien_tich"]:
    if col in df.columns:
        df[col] = df[col].astype(str).str.strip()

df = df.dropna(subset=["muc_gia", "dien_tich"])
df = df[~df["muc_gia"].str.contains("thỏa thuận", case=False, na=False)]

df["price_text"] = df["muc_gia"].str.lower().str.replace(",", ".", regex=False)
df["price_text"] = df["price_text"].str.replace("tỷ", "", regex=False)
df["price_text"] = df["price_text"].str.replace("ty", "", regex=False)
df["price_text"] = df["price_text"].str.replace("triệu", "", regex=False)
df["price_text"] = df["price_text"].str.replace("trieu", "", regex=False)

df["price"] = pd.to_numeric(df["price_text"], errors="coerce")
df = df.dropna(subset=["price"])

df.loc[df["muc_gia"].str.contains("tỷ", case=False, na=False), "price"] *= 1e9
df.loc[df["muc_gia"].str.contains("triệu", case=False, na=False), "price"] *= 1e6

df["area_m2"] = df["dien_tich"].str.lower().str.replace("m²", "", regex=False).str.replace("m2", "", regex=False).str.strip()
df["area_m2"] = pd.to_numeric(df["area_m2"], errors="coerce")
df = df.dropna(subset=["area_m2"])

df = df[(df["price"] > 0) & (df["area_m2"] > 0)]
df["price_per_m2"] = df["price"] / df["area_m2"]

os.makedirs("outputs", exist_ok=True)

print("===== DATASET OVERVIEW =====")
print("Shape:", df.shape)
print("\nColumns:")
print(df.columns.tolist())

print("\n===== MISSING VALUES =====")
print(df.isnull().sum())

print("\n===== DESCRIPTIVE STATISTICS =====")
print(df[["price", "area_m2", "price_per_m2"]].describe())

print("\n===== RECORDS BY PROVINCE =====")
print(df["tinh_thanh"].value_counts())

print("\n===== AVERAGE PRICE BY PROVINCE =====")
print(df.groupby("tinh_thanh")["price"].mean().sort_values(ascending=False))

print("\n===== AVERAGE PRICE PER M2 BY PROVINCE =====")
print(df.groupby("tinh_thanh")["price_per_m2"].mean().sort_values(ascending=False))

with open("outputs/eda_summary.txt", "w", encoding="utf-8") as f:
    f.write("DATASET OVERVIEW\n")
    f.write(str(df.shape) + "\n\n")
    f.write("MISSING VALUES\n")
    f.write(str(df.isnull().sum()) + "\n\n")
    f.write("DESCRIPTIVE STATISTICS\n")
    f.write(str(df[["price", "area_m2", "price_per_m2"]].describe()) + "\n\n")
    f.write("RECORDS BY PROVINCE\n")
    f.write(str(df["tinh_thanh"].value_counts()) + "\n\n")
    f.write("AVERAGE PRICE BY PROVINCE\n")
    f.write(str(df.groupby("tinh_thanh")["price"].mean().sort_values(ascending=False)) + "\n\n")
    f.write("AVERAGE PRICE PER M2 BY PROVINCE\n")
    f.write(str(df.groupby("tinh_thanh")["price_per_m2"].mean().sort_values(ascending=False)) + "\n\n")

plt.figure(figsize=(8, 5))
df["price"].hist(bins=30)
plt.title("Distribution of House Prices")
plt.xlabel("Price (VND)")
plt.ylabel("Frequency")
plt.tight_layout()
plt.savefig("outputs/price_distribution.png")
plt.close()

plt.figure(figsize=(8, 5))
df["area_m2"].hist(bins=30)
plt.title("Distribution of Area")
plt.xlabel("Area (m2)")
plt.ylabel("Frequency")
plt.tight_layout()
plt.savefig("outputs/area_distribution.png")
plt.close()

plt.figure(figsize=(8, 5))
plt.scatter(df["area_m2"], df["price"], alpha=0.5)
plt.title("Area vs Price")
plt.xlabel("Area (m2)")
plt.ylabel("Price (VND)")
plt.tight_layout()
plt.savefig("outputs/area_vs_price.png")
plt.close()

avg_price = df.groupby("tinh_thanh")["price"].mean().sort_values(ascending=False)
plt.figure(figsize=(8, 5))
avg_price.plot(kind="bar")
plt.title("Average Price by Province")
plt.xlabel("Province")
plt.ylabel("Average Price (VND)")
plt.tight_layout()
plt.savefig("outputs/avg_price_by_province.png")
plt.close()

plt.figure(figsize=(8, 5))
plt.boxplot(df["price"].dropna())
plt.title("Boxplot of Price")
plt.ylabel("Price (VND)")
plt.tight_layout()
plt.savefig("outputs/price_boxplot.png")
plt.close()

print("\nDone. Results saved in outputs/")
