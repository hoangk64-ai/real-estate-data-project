import pandas as pd
import joblib

print("START DEPLOYMENT PROTOTYPE")

model = joblib.load("house_price_model.pkl")
model_columns = joblib.load("model_columns.pkl")

area_m2 = float(input("Enter land area (m2): "))
tinh_thanh = input("Enter province (Đà Nẵng or Quảng Nam): ").strip()

sample = pd.DataFrame([{
    "area_m2": area_m2,
    "tinh_thanh": tinh_thanh
}])

sample = pd.get_dummies(sample, columns=["tinh_thanh"], drop_first=False)
sample = sample.reindex(columns=model_columns, fill_value=0)

predicted_price = model.predict(sample)[0]

print("Predicted price (VND):", round(predicted_price))
print("Predicted price (billion VND):", round(predicted_price / 1e9, 2))

print("DEPLOYMENT PROTOTYPE COMPLETED")