import joblib
import pandas as pd

model = joblib.load("model.pkl")

# Test cases
test_data = pd.DataFrame([
    {"signal": 80, "channel": 6, "encryption": 1, "bssid_count": 1},  # Safe
    {"signal": 75, "channel": 6, "encryption": 1, "bssid_count": 3},  # Suspicious
    {"signal": 40, "channel": 1, "encryption": 0, "bssid_count": 1},  # Safe
    {"signal": 90, "channel": 11, "encryption": 1, "bssid_count": 4}, # Suspicious
])

predictions = model.predict(test_data)

for i, pred in enumerate(predictions):
    print(f"Test {i+1}: {'Suspicious' if pred == 1 else 'Safe'}")