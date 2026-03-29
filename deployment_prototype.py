import pandas as pd
import joblib

print("START DEPLOYMENT PROTOTYPE")

model = joblib.load("house_price_model.pkl")
model_columns = joblib.load("model_columns.pkl")
district_map = joblib.load("district_map.pkl")

area_m2 = float(input("Enter land area (m2): "))
tinh_thanh = input("Enter province (Đà Nẵng or Quảng Nam): ").strip()

if tinh_thanh not in district_map:
    print("Invalid province.")
    print("Available provinces:", ", ".join(district_map.keys()))
    exit()

print("Available districts in", tinh_thanh + ":")
for d in district_map[tinh_thanh]:
    print("-", d)

quan_huyen = input("Enter district: ").strip()

if quan_huyen not in district_map[tinh_thanh]:
    print("Invalid district for the selected province.")
    exit()

sample = pd.DataFrame([{
    "area_m2": area_m2,
    "tinh_thanh": tinh_thanh,
    "quan_huyen": quan_huyen
}])

sample = pd.get_dummies(sample, columns=["tinh_thanh", "quan_huyen"], drop_first=False)
sample = sample.reindex(columns=model_columns, fill_value=0)

predicted_price = model.predict(sample)[0]

print("Predicted price (VND):", round(predicted_price))
print("Predicted price (billion VND):", round(predicted_price / 1e9, 2))
print("DEPLOYMENT PROTOTYPE COMPLETED")