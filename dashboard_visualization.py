import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

sns.set_style("whitegrid")

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

df["area_m2"] = (
    df["dien_tich"]
    .str.lower()
    .str.replace("m²", "", regex=False)
    .str.replace("m2", "", regex=False)
    .str.strip()
)
df["area_m2"] = pd.to_numeric(df["area_m2"], errors="coerce")
df = df.dropna(subset=["area_m2"])

df = df[(df["price"] > 0) & (df["area_m2"] > 0)]
df["price_billion"] = df["price"] / 1e9
df["price_per_m2"] = df["price"] / df["area_m2"]
df["price_norm"] = (df["price"] - df["price"].min()) / (df["price"].max() - df["price"].min())
df["area_norm"] = (df["area_m2"] - df["area_m2"].min()) / (df["area_m2"].max() - df["area_m2"].min())

if "vi_tri" in df.columns:
    df["quan_huyen"] = df["vi_tri"].str.split(",").str[0].str.strip()
else:
    df["quan_huyen"] = "Unknown"

top_locations = df["quan_huyen"].value_counts().head(8).sort_values()

os.makedirs("outputs", exist_ok=True)

fig, axes = plt.subplots(2, 3, figsize=(20, 10))
fig.suptitle("PHÂN TÍCH DỮ LIỆU BẤT ĐỘNG SẢN", fontsize=18, fontweight="bold")

# 1. Price distribution
sns.histplot(df["price_billion"], bins=30, kde=True, ax=axes[0, 0])
axes[0, 0].set_title("Phân bố giá nhà")
axes[0, 0].set_xlabel("Giá (tỷ VND)")
axes[0, 0].set_ylabel("Tần suất")

# 2. Area distribution
sns.histplot(df["area_m2"], bins=30, kde=True, ax=axes[0, 1])
axes[0, 1].set_title("Phân bố diện tích")
axes[0, 1].set_xlabel("Diện tích (m²)")
axes[0, 1].set_ylabel("Tần suất")

# 3. Boxplot by province
sns.boxplot(data=df, x="tinh_thanh", y="price_billion", ax=axes[0, 2])
axes[0, 2].set_title("Biến động giá: Đà Nẵng vs Quảng Nam")
axes[0, 2].set_xlabel("Tỉnh/Thành")
axes[0, 2].set_ylabel("Giá (tỷ VND)")

# 4. Scatter area vs price
sns.scatterplot(data=df, x="area_m2", y="price_billion", hue="tinh_thanh", alpha=0.7, ax=axes[1, 0])
axes[1, 0].set_title("Tương quan Giá & Diện tích")
axes[1, 0].set_xlabel("Diện tích (m²)")
axes[1, 0].set_ylabel("Giá (tỷ VND)")

# 5. Top locations
top_locations.plot(kind="barh", ax=axes[1, 1])
axes[1, 1].set_title("Top 8 khu vực nhiều tin đăng nhất")
axes[1, 1].set_xlabel("Số lượng tin")
axes[1, 1].set_ylabel("Quận/Huyện")

# 6. Normalized KDE
sns.kdeplot(df["price_norm"], fill=True, label="Giá (Norm)", ax=axes[1, 2])
sns.kdeplot(df["area_norm"], fill=True, label="Diện tích (Norm)", ax=axes[1, 2])
axes[1, 2].set_title("Kiểm tra dữ liệu chuẩn hóa [0,1]")
axes[1, 2].set_xlabel("Giá trị chuẩn hóa")
axes[1, 2].set_ylabel("Density")
axes[1, 2].legend()

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig("outputs/dashboard_visualization.png", dpi=300, bbox_inches="tight")
plt.show()

print("Dashboard saved at outputs/dashboard_visualization.png")