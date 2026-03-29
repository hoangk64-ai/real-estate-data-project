import sqlite3
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

print("START MODEL TRAINING")

conn = sqlite3.connect("data/cleaned_data.db")
df = pd.read_sql("SELECT * FROM cleaned_data", conn)
conn.close()

df["quan_huyen"] = df["vi_tri"].astype(str).str.split("(").str[0].str.strip()

features = ["area_m2", "tinh_thanh", "quan_huyen"]
target = "price"

df = df[features + [target]].dropna()

district_map = (
    df.groupby("tinh_thanh")["quan_huyen"]
    .apply(lambda x: sorted(x.dropna().unique().tolist()))
    .to_dict()
)

print("===== AVAILABLE DISTRICTS BY PROVINCE =====")
for province, districts in district_map.items():
    print(province + ":", ", ".join(districts))

df = pd.get_dummies(df, columns=["tinh_thanh", "quan_huyen"], drop_first=False)

X = df.drop(columns=[target])
y = df[target]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

mae = mean_absolute_error(y_test, y_pred)
rmse = mean_squared_error(y_test, y_pred) ** 0.5
r2 = r2_score(y_test, y_pred)

print("===== MODEL EVALUATION =====")
print("MAE:", round(mae, 2))
print("RMSE:", round(rmse, 2))
print("R2:", round(r2, 4))

joblib.dump(model, "house_price_model.pkl")
joblib.dump(X.columns.tolist(), "model_columns.pkl")
joblib.dump(district_map, "district_map.pkl")

print("Model saved as house_price_model.pkl")
print("Columns saved as model_columns.pkl")
print("District map saved as district_map.pkl")
print("MODEL TRAINING COMPLETED")