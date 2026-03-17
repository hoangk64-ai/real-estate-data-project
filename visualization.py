import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

print("START VISUALIZATION")

os.makedirs("outputs", exist_ok=True)

df = pd.read_csv("outputs/cleaned_data.csv")

df["price_billion"] = df["price"] / 1e9
df["price_per_m2_million"] = df["price_per_m2"] / 1e6

# log transform for better shape
df["log_price"] = np.log10(df["price"])
df["log_area"] = np.log10(df["area_m2"])

sns.set_style("whitegrid")

# tick values for readable labels
price_ticks = [1e9, 3e9, 1e10, 3e10, 1e11, 3e11]
price_tick_pos = np.log10(price_ticks)
price_tick_labels = ["1B", "3B", "10B", "30B", "100B", "300B"]

area_ticks = [30, 100, 300, 1000, 3000, 10000]
area_tick_pos = np.log10(area_ticks)
area_tick_labels = ["30", "100", "300", "1,000", "3,000", "10,000"]

# 1. Price distribution
plt.figure(figsize=(8, 5))
sns.histplot(df["log_price"], bins=40, kde=True)
plt.title("Price Distribution")
plt.xlabel("Price (Billion VND)")
plt.ylabel("Number of Listings")
plt.xticks(price_tick_pos, price_tick_labels)
plt.tight_layout()
plt.savefig("outputs/price_distribution.png", dpi=300)
plt.close()

# 2. Land area distribution
plt.figure(figsize=(8, 5))
sns.histplot(df["log_area"], bins=40, kde=True)
plt.title("Land Area Distribution")
plt.xlabel("Land Area (m²)")
plt.ylabel("Number of Listings")
plt.xticks(area_tick_pos, area_tick_labels)
plt.tight_layout()
plt.savefig("outputs/area_distribution.png", dpi=300)
plt.close()

# 3. Price comparison by province
plt.figure(figsize=(8, 5))
sns.boxplot(x="tinh_thanh", y="price_billion", data=df)
plt.title("Price Comparison by Province")
plt.xlabel("Province")
plt.ylabel("Price (Billion VND)")
plt.ylim(0, 300)
plt.tight_layout()
plt.savefig("outputs/price_comparison_by_province.png", dpi=300)
plt.close()

# 4. Relationship between area and price
plt.figure(figsize=(8, 5))
sns.scatterplot(
    x="log_area",
    y="log_price",
    hue="tinh_thanh",
    data=df,
    alpha=0.7
)
plt.title("Relationship Between Area and Price")
plt.xlabel("Land Area (m²)")
plt.ylabel("Price (Billion VND)")
plt.xticks(area_tick_pos, area_tick_labels)
plt.yticks(price_tick_pos, price_tick_labels)
plt.tight_layout()
plt.savefig("outputs/area_vs_price.png", dpi=300)
plt.close()

# 5. Top locations with most listings
top_locations = df["vi_tri"].value_counts().head(8)

plt.figure(figsize=(9, 5))
sns.barplot(x=top_locations.values, y=top_locations.index)
plt.title("Top Locations with Most Listings")
plt.xlabel("Number of Listings")
plt.ylabel("Location")
plt.tight_layout()
plt.savefig("outputs/top_locations_with_most_listings.png", dpi=300)
plt.close()

# 6. Normalized feature distribution
price_norm = (df["price"] - df["price"].min()) / (df["price"].max() - df["price"].min())
area_norm = (df["area_m2"] - df["area_m2"].min()) / (df["area_m2"].max() - df["area_m2"].min())

plt.figure(figsize=(8, 5))
sns.kdeplot(price_norm, label="Price (Normalized)")
sns.kdeplot(area_norm, label="Area (Normalized)")
plt.title("Normalized Price and Area Distribution")
plt.xlabel("Scaled Value (0–1)")
plt.ylabel("Density")
plt.legend()
plt.tight_layout()
plt.savefig("outputs/normalized_feature_distribution.png", dpi=300)
plt.close()

# 7. Correlation heatmap
corr = df[["price_billion", "area_m2", "price_per_m2_million"]].corr()

plt.figure(figsize=(6, 5))
sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f")
plt.title("Correlation Matrix")
plt.tight_layout()
plt.savefig("outputs/correlation_heatmap.png", dpi=300)
plt.close()

# 8. Combined dashboard
fig, axes = plt.subplots(2, 3, figsize=(18, 10))
fig.suptitle("REAL ESTATE DATA ANALYSIS\nDa Nang and Quang Nam", fontsize=18)

sns.histplot(df["log_price"], bins=35, kde=True, ax=axes[0, 0])
axes[0, 0].set_title("Price Distribution")
axes[0, 0].set_xlabel("Price (Billion VND)")
axes[0, 0].set_ylabel("Number of Listings")
axes[0, 0].set_xticks(price_tick_pos)
axes[0, 0].set_xticklabels(price_tick_labels)

sns.histplot(df["log_area"], bins=35, kde=True, ax=axes[0, 1])
axes[0, 1].set_title("Land Area Distribution")
axes[0, 1].set_xlabel("Land Area (m²)")
axes[0, 1].set_ylabel("Number of Listings")
axes[0, 1].set_xticks(area_tick_pos)
axes[0, 1].set_xticklabels(area_tick_labels)

sns.boxplot(x="tinh_thanh", y="price_billion", data=df, ax=axes[0, 2])
axes[0, 2].set_title("Price Comparison by Province")
axes[0, 2].set_xlabel("Province")
axes[0, 2].set_ylabel("Price (Billion VND)")
axes[0, 2].set_ylim(0, 300)

sns.scatterplot(
    x="log_area",
    y="log_price",
    hue="tinh_thanh",
    data=df,
    alpha=0.7,
    ax=axes[1, 0]
)
axes[1, 0].set_title("Relationship Between Area and Price")
axes[1, 0].set_xlabel("Land Area (m²)")
axes[1, 0].set_ylabel("Price (Billion VND)")
axes[1, 0].set_xticks(area_tick_pos)
axes[1, 0].set_xticklabels(area_tick_labels)
axes[1, 0].set_yticks(price_tick_pos)
axes[1, 0].set_yticklabels(price_tick_labels)

sns.barplot(x=top_locations.values, y=top_locations.index, ax=axes[1, 1])
axes[1, 1].set_title("Top Locations with Most Listings")
axes[1, 1].set_xlabel("Number of Listings")
axes[1, 1].set_ylabel("Location")

sns.kdeplot(price_norm, label="Price (Normalized)", ax=axes[1, 2])
sns.kdeplot(area_norm, label="Area (Normalized)", ax=axes[1, 2])
axes[1, 2].set_title("Normalized Price and Area Distribution")
axes[1, 2].set_xlabel("Scaled Value (0–1)")
axes[1, 2].set_ylabel("Density")
axes[1, 2].legend()

plt.tight_layout()
plt.savefig("outputs/eda_dashboard.png", dpi=300)
plt.close()

print("\nVISUALIZATION COMPLETED")
print("Saved charts in outputs/")