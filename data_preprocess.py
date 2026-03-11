import sqlite3
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

#1. connect database

conn = sqlite3.connect(r"C:\Users\Huy Hoang\OneDrive\ProjectADY\real_estate_danang_quangnam.db")

df = pd.read_sql("SELECT * FROM bds_data", conn)

print("Original shape:", df.shape)

#2. data inspection

print("Dataset shape:", df.shape)

print("\nFirst rows:")
print(df.head())

print("\nDataset info:")
print(df.info())

print("\nStatistics:")
print(df.describe())

print("\nMissing values:")
print(df.isnull().sum())

#3. data cleaning

# remove duplicate rows
df = df.drop_duplicates()

# remove extra spaces
df["tieu_de"] = df["tieu_de"].str.strip()
df["vi_tri"] = df["vi_tri"].str.strip()

#4. handle missing data

# replace empty strings with NaN
df = df.replace("", np.nan)

# remove rows missing important values
df = df.dropna(subset=["muc_gia", "dien_tich"])

#5. remove non numeric price

# remove rows with "giá thỏa thuận"
df = df[~df["muc_gia"].str.contains("thỏa thuận", case=False, na=False)]

#6. convert price to number

df["price"] = df["muc_gia"].str.lower()

df["price"] = df["price"].str.replace("tỷ", "")
df["price"] = df["price"].str.replace("ty", "")
df["price"] = df["price"].str.replace("triệu", "")
df["price"] = df["price"].str.replace("trieu", "")

df["price"] = df["price"].str.replace(",", ".")

# convert to number safely
df["price"] = pd.to_numeric(df["price"], errors="coerce")

# remove rows still not numeric
df = df.dropna(subset=["price"])

# convert units
df.loc[df["muc_gia"].str.contains("tỷ", case=False, na=False), "price"] *= 1e9
df.loc[df["muc_gia"].str.contains("triệu", case=False, na=False), "price"] *= 1e6

#7. convert area to number

df["area_m2"] = df["dien_tich"]

df["area_m2"] = df["area_m2"].str.replace("m²", "")
df["area_m2"] = df["area_m2"].str.replace("m2", "")

df["area_m2"] = df["area_m2"].str.strip()

df["area_m2"] = pd.to_numeric(df["area_m2"], errors="coerce")

df = df.dropna(subset=["area_m2"])

#8. feature engineering

df["price_per_m2"] = df["price"] / df["area_m2"]

#9. data normalization

scaler = MinMaxScaler()

numeric_cols = ["price", "area_m2", "price_per_m2"]

df[numeric_cols] = scaler.fit_transform(df[numeric_cols])


#10. save clean data


clean_conn = sqlite3.connect(r"C:\Users\Huy Hoang\OneDrive\ProjectADY\cleaned_data.db")

df.to_sql(
    "cleaned_data",
    clean_conn,
    if_exists="replace",
    index=False
)

print("Cleaned shape:", df.shape)

clean_conn.commit()
clean_conn.close()

conn.close()

print("Data preprocessing completed successfully.")