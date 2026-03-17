import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

print("START EDA")

# load cleaned data
df = pd.read_csv("outputs/cleaned_data.csv")

print("Shape:", df.shape)
print("Columns:", df.columns)

# create output folder
os.makedirs("outputs", exist_ok=True)

# ===== DESCRIPTIVE STATISTICS =====

print("\nDESCRIPTIVE STATISTICS")
print(df[["price","area_m2","price_per_m2"]].describe())

# ===== RECORDS BY PROVINCE =====

print("\nRECORDS BY PROVINCE")
print(df["tinh_thanh"].value_counts())

# ===== AVERAGE PRICE BY PROVINCE =====

print("\nAVERAGE PRICE BY PROVINCE")
print(df.groupby("tinh_thanh")["price"].mean())

# ===== AVERAGE PRICE PER M2 =====

print("\nAVERAGE PRICE PER M2 BY PROVINCE")
print(df.groupby("tinh_thanh")["price_per_m2"].mean())

# ===== PRICE DISTRIBUTION =====

plt.figure()
plt.hist(df["price"], bins=50)
plt.title("Price Distribution")
plt.xlabel("Price")
plt.ylabel("Count")
plt.savefig("outputs/price_distribution.png")
plt.close()

# ===== AREA DISTRIBUTION =====

plt.figure()
plt.hist(df["area_m2"], bins=50)
plt.title("Area Distribution")
plt.xlabel("Area (m2)")
plt.ylabel("Count")
plt.savefig("outputs/area_distribution.png")
plt.close()

# ===== PRICE VS AREA =====

plt.figure()
plt.scatter(df["area_m2"], df["price"], alpha=0.5)
plt.title("Price vs Area")
plt.xlabel("Area (m2)")
plt.ylabel("Price")
plt.savefig("outputs/area_vs_price.png")
plt.close()

# ===== PRICE PER M2 BOXPLOT =====

plt.figure()
plt.boxplot(df["price_per_m2"])
plt.title("Price per m2 Distribution")
plt.savefig("outputs/price_per_m2_boxplot.png")
plt.close()

# ===== CORRELATION HEATMAP =====

plt.figure()

corr = df[["price","area_m2","price_per_m2"]].corr()

sns.heatmap(corr, annot=True)

plt.title("Correlation Matrix")

plt.savefig("outputs/correlation_heatmap.png")

plt.close()

print("\nEDA COMPLETED")
print("Charts saved in outputs folder")