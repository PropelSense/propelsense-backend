# ML Prediction History API

## Overview

Complete CRUD API for ML prediction history. Each prediction is associated with a user and stored in the database for future reference.

## Authentication

All endpoints require JWT authentication via Bearer token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## Endpoints

### 1. Make Prediction (with History)

**POST** `/api/v1/ml/predict/power`

Make a power prediction and optionally save it to history.

**Request:**

```json
{
  "features": {
    "draft_aft_telegram": 8.75,
    "draft_fore_telegram": 8.55,
    "stw": 18.2,
    "diff_speed_overground": 0.1,
    "awind_vcomp_provider": 5.2,
    "awind_ucomp_provider": 3.1,
    "rcurrent_vcomp": 0.05,
    "rcurrent_ucomp": -0.08,
    "comb_wind_swell_wave_height": 1.2,
    "timeSinceDryDock": 120
  },
  "save_to_history": true
}
```

**Response:**

```json
{
  "id": 123,
  "predicted_power_kw": 18500.5,
  "predicted_power_mw": 18.5,
  "model_used": "xgboost",
  "metadata": {
    "model_used": "xgboost",
    "n_features": 19,
    "unit": "kW",
    "model_performance": {
      "mae_dev_in_kw": 866,
      "r2_dev_in": 0.978
    }
  },
  "created_at": "2026-02-17T10:30:00Z"
}
```

### 2. Get Prediction History

**GET** `/api/v1/ml/history`

Get paginated list of user's prediction history.

**Query Parameters:**

- `page` (int, default: 1) - Page number
- `page_size` (int, default: 20, max: 100) - Items per page
- `sort_by` (string, default: "created_at") - Field to sort by
- `sort_desc` (bool, default: true) - Sort descending

**Response:**

```json
{
  "total": 150,
  "predictions": [
    {
      "id": 123,
      "user_id": "uuid-here",
      "user_email": "user@example.com",
      "draft_aft_telegram": 8.75,
      "draft_fore_telegram": 8.55,
      "stw": 18.2,
      "diff_speed_overground": 0.1,
      "awind_vcomp_provider": 5.2,
      "awind_ucomp_provider": 3.1,
      "rcurrent_vcomp": 0.05,
      "rcurrent_ucomp": -0.08,
      "comb_wind_swell_wave_height": 1.2,
      "timeSinceDryDock": 120,
      "predicted_power_kw": 18500.5,
      "predicted_power_mw": 18.5,
      "model_used": "xgboost",
      "model_metadata": { ... },
      "created_at": "2026-02-17T10:30:00Z",
      "updated_at": "2026-02-17T10:30:00Z"
    }
  ],
  "page": 1,
  "page_size": 20
}
```

### 3. Get Specific Prediction

**GET** `/api/v1/ml/history/{prediction_id}`

Get details of a specific prediction (user must own it).

**Response:**

```json
{
  "id": 123,
  "user_id": "uuid-here",
  "user_email": "user@example.com",
  "draft_aft_telegram": 8.75,
  "predicted_power_kw": 18500.5,
  "predicted_power_mw": 18.5,
  "model_used": "xgboost",
  "created_at": "2026-02-17T10:30:00Z",
  ...
}
```

### 4. Delete Prediction

**DELETE** `/api/v1/ml/history/{prediction_id}`

Delete a specific prediction (user must own it).

**Response:**

```json
{
  "message": "Prediction 123 deleted successfully"
}
```

### 5. Get Prediction Statistics

**GET** `/api/v1/ml/history/stats/summary`

Get statistics about user's predictions.

**Response:**

```json
{
  "total_predictions": 150,
  "avg_power_kw": 18250.5,
  "max_power_kw": 22300.0,
  "min_power_kw": 15200.0,
  "most_recent": "2026-02-17T10:30:00Z",
  "predictions_this_month": 25
}
```

### 6. Delete All Predictions

**DELETE** `/api/v1/ml/history`

Delete all predictions for the authenticated user.

⚠️ **Warning:** This action cannot be undone!

**Response:**

```json
{
  "message": "Deleted 150 predictions",
  "count": 150
}
```

## Database Schema

### prediction_history table

```sql
CREATE TABLE prediction_history (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    user_email VARCHAR(255),
    input_features JSONB NOT NULL,

    -- Input feature columns (for querying)
    draft_aft_telegram FLOAT,
    draft_fore_telegram FLOAT,
    stw FLOAT,
    diff_speed_overground FLOAT,
    awind_vcomp_provider FLOAT,
    awind_ucomp_provider FLOAT,
    rcurrent_vcomp FLOAT,
    rcurrent_ucomp FLOAT,
    comb_wind_swell_wave_height FLOAT,
    timeSinceDryDock FLOAT,

    -- Prediction results
    predicted_power_kw FLOAT NOT NULL,
    predicted_power_mw FLOAT NOT NULL,

    -- Model info
    model_used VARCHAR(50) NOT NULL DEFAULT 'xgboost',
    model_metadata JSONB,

    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_prediction_history_user_id ON prediction_history(user_id);
CREATE INDEX idx_prediction_history_created_at ON prediction_history(created_at);
CREATE INDEX idx_prediction_history_user_created ON prediction_history(user_id, created_at DESC);
```

## Usage Examples

### Python with requests

```python
import requests

BASE_URL = "http://localhost:8000/api/v1/ml"
TOKEN = "your-jwt-token"
headers = {"Authorization": f"Bearer {TOKEN}"}

# Make prediction with history
response = requests.post(
    f"{BASE_URL}/predict/power",
    headers=headers,
    json={
        "features": {
            "draft_aft_telegram": 8.75,
            "draft_fore_telegram": 8.55,
            "stw": 18.2,
            "diff_speed_overground": 0.1,
            "awind_vcomp_provider": 5.2,
            "awind_ucomp_provider": 3.1,
            "rcurrent_vcomp": 0.05,
            "rcurrent_ucomp": -0.08,
            "comb_wind_swell_wave_height": 1.2,
            "timeSinceDryDock": 120
        },
        "save_to_history": True
    }
)
result = response.json()
print(f"Prediction ID: {result['id']}")
print(f"Predicted Power: {result['predicted_power_kw']} kW")

# Get history
history = requests.get(
    f"{BASE_URL}/history",
    headers=headers,
    params={"page": 1, "page_size": 10}
)
print(f"Total predictions: {history.json()['total']}")

# Get stats
stats = requests.get(f"{BASE_URL}/history/stats/summary", headers=headers)
print(f"Average power: {stats.json()['avg_power_kw']} kW")
```

### JavaScript/TypeScript

```typescript
const BASE_URL = "http://localhost:8000/api/v1/ml";
const TOKEN = "your-jwt-token";

// Make prediction
const makePrediction = async (features) => {
  const response = await fetch(`${BASE_URL}/predict/power`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${TOKEN}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      features,
      save_to_history: true,
    }),
  });
  return await response.json();
};

// Get history
const getHistory = async (page = 1, pageSize = 20) => {
  const response = await fetch(
    `${BASE_URL}/history?page=${page}&page_size=${pageSize}`,
    {
      headers: { Authorization: `Bearer ${TOKEN}` },
    },
  );
  return await response.json();
};

// Get stats
const getStats = async () => {
  const response = await fetch(`${BASE_URL}/history/stats/summary`, {
    headers: { Authorization: `Bearer ${TOKEN}` },
  });
  return await response.json();
};
```

## Error Responses

### 401 Unauthorized

```json
{
  "detail": "Could not validate credentials"
}
```

### 404 Not Found

```json
{
  "detail": "Prediction 123 not found"
}
```

### 422 Validation Error

```json
{
  "detail": "Invalid input features: stw must be between 0 and 40"
}
```

### 500 Internal Server Error

```json
{
  "detail": "Prediction failed: [error message]"
}
```

## Migration

To update your existing database to support the new prediction history schema, run:

```bash
cd backend
python scripts/migrate_prediction_history.py
```

This will:

- Add new columns to the prediction_history table
- Create indexes for better performance
- Preserve existing data (if any)
