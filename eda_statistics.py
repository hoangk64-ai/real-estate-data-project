import pandas as pd
import numpy as np
import sqlite3
import os

print("START EDA STATISTICS")

# tạo folder outputs nếu chưa có
os.makedirs("outputs", exist_ok=True)

# kết nối database
conn = sqlite3.connect("data/cleaned_data.db")

# đọc bảng cleaned_data
df = pd.read_sql("SELECT * FROM cleaned_data", conn)

conn.close()

print("\n===== DATASET OVERVIEW =====")
print("Shape:", df.shape)
print("Columns:", list(df.columns))

print("\n===== MISSING VALUES =====")
print(df.isnull().sum())

print("\n===== DATA TYPES =====")
print(df.dtypes)

# thêm đơn vị dễ đọc
df["price_billion"] = df["price"] / 1e9
df["price_per_m2_million"] = df["price_per_m2"] / 1e6

print("\n===== DESCRIPTIVE STATISTICS =====")

desc = df[["price_billion", "area_m2", "price_per_m2_million"]].describe()

print(desc)

desc.to_csv("outputs/eda_summary.csv")

print("\n===== RECORDS BY PROVINCE =====")

records_by_province = df["tinh_thanh"].value_counts()

print(records_by_province)

records_by_province.to_csv("outputs/records_by_province.csv")

print("\n===== AVERAGE PRICE BY PROVINCE =====")

avg_price = df.groupby("tinh_thanh")["price_billion"].mean().sort_values(ascending=False)

print(avg_price)

avg_price.to_csv("outputs/avg_price_by_province.csv")

print("\n===== AVERAGE AREA BY PROVINCE =====")

avg_area = df.groupby("tinh_thanh")["area_m2"].mean().sort_values(ascending=False)

print(avg_area)

avg_area.to_csv("outputs/avg_area_by_province.csv")

print("\n===== AVERAGE PRICE PER M2 BY PROVINCE =====")

avg_ppm = df.groupby("tinh_thanh")["price_per_m2_million"].mean().sort_values(ascending=False)

print(avg_ppm)

avg_ppm.to_csv("outputs/avg_price_per_m2_by_province.csv")

print("\n===== CORRELATION =====")

corr = df[["price_billion", "area_m2", "price_per_m2_million"]].corr()

print(corr)

corr.to_csv("outputs/correlation_matrix.csv")

print("\n===== TOP 10 LOCATIONS WITH MOST LISTINGS =====")

top_locations = df["vi_tri"].value_counts().head(10)

print(top_locations)

top_locations.to_csv("outputs/top_locations.csv")

print("\nEDA STATISTICS COMPLETED")
print("Saved csv files in outputs/")