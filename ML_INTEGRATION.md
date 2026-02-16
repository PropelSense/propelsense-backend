# ML Integration for Backend

## Overview
This backend integrates the XGBoost model for vessel propulsion power prediction. The model is hosted on Hugging Face Hub and downloaded/cached locally (993 KB).

## Why Only XGBoost?

- **Lightweight**: Only 993 KB (downloads in seconds)
- **Best Performance**: MAE of 866 kW, R² of 0.978
- **Production Ready**: Fast inference, low memory usage
- **Cloud-First**: Downloaded from Hugging Face Hub, no manual file management

**Note**: Random Forest was excluded due to its 17 GB size - impractical to download for every deployment.

## Available Endpoints

### 1. Predict Power
**POST** `/api/v1/ml/predict/power`

Predict vessel propulsion power.

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
  }
}
```

**Response:**
```json
{
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
  }
}
```

### 2. Get Model Info
**GET** `/api/v1/ml/models/available`

Get XGBoost model information.

**Response:**
```json
{
  "models": {
    "xgboost": {
      "name": "XGBoost",
      "size": "993 KB",
      "performance": {
        "mae_dev_in_kw": 866,
        "r2_dev_in": 0.978
      },
      "status": "Production ready"
    }
  }
}
```

### 3. Check Model Status
**GET** `/api/v1/ml/models/status`

Check if model is loaded in memory.

**Response:**
```json
{
  "xgboost_loaded": true,
  "feature_scaler_loaded": true,
  "cache_directory": "./model_cache",
  "model_source": "Hugging Face Hub",
  "repo_id": "hasnaynajmal/vessel-power-prediction"
}
```

## Model Performance

### XGBoost
- **Size**: 993 KB
- **In-Distribution**: MAE 866 kW, R² 0.978
- **Out-of-Distribution**: MAE 1,435 kW, R² 0.896
- **Load Time**: < 1 second
- **Memory**: < 100 MB

## Installation

1. Install ML dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Start the server:
```bash
python run.py
```

The XGBoost model will be automatically downloaded from Hugging Face Hub on first startup and cached in `./model_cache/`.

## Usage Example

```python
import requests

# Predict power
response = requests.post(
    "http://localhost:8000/api/v1/ml/predict/power",
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
        }
    }
)

result = response.json()
print(f"Predicted power: {result['predicted_power_kw']} kW")
print(f"Model: {result['model_used']}")
```

## Features

### Input Features (10 base features)
1. `draft_aft_telegram` - Aft draft (m)
2. `draft_fore_telegram` - Forward draft (m)
3. `stw` - Speed through water (knots)
4. `diff_speed_overground` - Speed difference
5. `awind_vcomp_provider` - Apparent wind V component (m/s)
6. `awind_ucomp_provider` - Apparent wind U component (m/s)
7. `rcurrent_vcomp` - Current V component (m/s)
8. `rcurrent_ucomp` - Current U component (m/s)
9. `comb_wind_swell_wave_height` - Combined wave height (m)
10. `timeSinceDryDock` - Days since last dry dock

### Derived Features (9 features, auto-calculated)
The service automatically derives:
- `stw_cubed`, `stw_squared` - Speed features
- `mean_draft`, `draft_diff` - Draft features
- `awind_speed`, `awind_direction` - Wind features
- `rcurrent_speed`, `rcurrent_direction` - Current features
- `diff_speed_abs` - Speed difference magnitude

## Architecture

```
User Request → FastAPI Endpoint → MLModelService
                                      ↓
                              Download from HF Hub (first time)
                                      ↓
                              Load & Cache Model (993 KB)
                                      ↓
                              Feature Engineering (19 features)
                                      ↓
                              XGBoost Prediction
                                      ↓
                              Return Power (kW/MW)
```

## Why Not Random Forest?

The Random Forest model is **17 GB** - too large to download for production use. Options if you need it:

1. **Hugging Face Inference Endpoints** (paid) - host the model in the cloud
2. **Deploy separately** - dedicated server with enough RAM/storage
3. **Stick with XGBoost** - better performance anyway!

## Notes

- XGBoost model pre-loaded on startup for instant predictions
- Models cached locally after first download
- No manual file management needed
- All predictions include performance metadata
- Typical inference time: < 50ms
