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

features = ["area_m2", "tinh_thanh"]
target = "price"

df = df[features + [target]].dropna()

df = pd.get_dummies(df, columns=["tinh_thanh"], drop_first=False)

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

print("Model saved as house_price_model.pkl")
print("Columns saved as model_columns.pkl")
print("MODEL TRAINING COMPLETED")