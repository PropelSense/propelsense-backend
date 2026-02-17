# ML Prediction History - Setup Complete ✅

## What Was Built

A complete CRUD system for ML prediction history that:

- **Saves predictions** to database with user association
- **Tracks all input features** and prediction results
- **Provides history management** (view, delete, stats)
- **Secures access** with JWT authentication
- **Optimizes queries** with database indexes

## Files Created/Modified

### New Files

1. **`app/services/prediction_history_service.py`** - CRUD operations for prediction history
2. **`scripts/migrate_prediction_history.py`** - Database migration script
3. **`PREDICTION_HISTORY_API.md`** - Complete API documentation

### Modified Files

1. **`app/models/prediction_history.py`** - Updated database model with user fields
2. **`app/schemas/ml_prediction.py`** - Added history schemas and save_to_history option
3. **`app/api/v1/endpoints/ml_prediction.py`** - Added 6 new CRUD endpoints

## API Endpoints

### Prediction

- **POST** `/api/v1/ml/predict/power` - Make prediction (optionally save to history)

### History Management

- **GET** `/api/v1/ml/history` - Get paginated history
- **GET** `/api/v1/ml/history/{id}` - Get specific prediction
- **DELETE** `/api/v1/ml/history/{id}` - Delete prediction
- **GET** `/api/v1/ml/history/stats/summary` - Get statistics
- **DELETE** `/api/v1/ml/history` - Delete all user predictions

### Model Info

- **GET** `/api/v1/ml/models/available` - Get model info
- **GET** `/api/v1/ml/models/status` - Check model status

## Database Schema

```sql
prediction_history
├── id (PRIMARY KEY)
├── user_id (indexed) - Supabase user ID
├── user_email
├── input_features (JSONB) - All input features as JSON
├── draft_aft_telegram
├── draft_fore_telegram
├── stw
├── diff_speed_overground
├── awind_vcomp_provider
├── awind_ucomp_provider
├── rcurrent_vcomp
├── rcurrent_ucomp
├── comb_wind_swell_wave_height
├── timeSinceDryDock
├── predicted_power_kw
├── predicted_power_mw
├── model_used (default: 'xgboost')
├── model_metadata (JSONB)
├── created_at (indexed)
└── updated_at
```

## Setup Instructions

### 1. Run Database Migration

```bash
cd backend
python scripts/migrate_prediction_history.py
```

This will:

- Add new columns to prediction_history table
- Create performance indexes
- Handle existing data safely

### 2. Test the Endpoints

Start the server:

```bash
python run.py
```

Test prediction with history:

```bash
curl -X POST "http://localhost:8000/api/v1/ml/predict/power" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```

Get history:

```bash
curl "http://localhost:8000/api/v1/ml/history?page=1&page_size=10" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

Get statistics:

```bash
curl "http://localhost:8000/api/v1/ml/history/stats/summary" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### 3. View API Documentation

Visit: `http://localhost:8000/docs`

You'll see all endpoints with:

- Request/response schemas
- Try-it-out functionality
- Authentication handling

## Features

### ✅ User Association

- Every prediction linked to a user via JWT
- Users can only see/modify their own predictions
- User email stored for reference

### ✅ Complete Feature Storage

- All 10 input features stored individually
- Full feature dict stored as JSON (flexibility)
- Easy querying by any feature

### ✅ Pagination & Sorting

- Efficient pagination for large datasets
- Customizable page size (max 100)
- Sort by any field (ASC/DESC)

### ✅ Statistics

- Total predictions count
- Average/min/max power predictions
- Monthly prediction count
- Most recent prediction timestamp

### ✅ Security

- JWT authentication required
- User isolation enforced
- Authorization checks on all operations

### ✅ Performance

- Database indexes on user_id and created_at
- Composite index for user + date queries
- Efficient pagination queries

## Usage Example

```python
import requests

BASE_URL = "http://localhost:8000/api/v1/ml"
TOKEN = "your-jwt-token"
headers = {"Authorization": f"Bearer {TOKEN}"}

# 1. Make prediction and save to history
prediction = requests.post(
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
).json()

print(f"Prediction saved with ID: {prediction['id']}")
print(f"Power: {prediction['predicted_power_kw']} kW")

# 2. Get recent predictions
history = requests.get(
    f"{BASE_URL}/history",
    headers=headers,
    params={"page": 1, "page_size": 5}
).json()

print(f"\nYou have {history['total']} predictions")
for pred in history['predictions']:
    print(f"  - {pred['created_at']}: {pred['predicted_power_kw']} kW")

# 3. Get statistics
stats = requests.get(
    f"{BASE_URL}/history/stats/summary",
    headers=headers
).json()

print(f"\nStatistics:")
print(f"  Total: {stats['total_predictions']}")
print(f"  Average: {stats['avg_power_kw']} kW")
print(f"  This month: {stats['predictions_this_month']}")

# 4. Delete a prediction
requests.delete(
    f"{BASE_URL}/history/{prediction['id']}",
    headers=headers
)
print(f"\nDeleted prediction {prediction['id']}")
```

## Next Steps

### Frontend Integration

1. Create prediction history page/component
2. Display paginated history table
3. Show statistics dashboard
4. Add delete functionality
5. Enable filtering by date/power range

### Optional Enhancements

1. **Export functionality** - Download history as CSV/Excel
2. **Filtering** - Filter by date range, power range, features
3. **Comparison** - Compare multiple predictions side-by-side
4. **Visualization** - Charts showing prediction trends over time
5. **Notes** - Allow users to add notes to predictions
6. **Favorites** - Mark important predictions
7. **Sharing** - Share predictions with team members

## Testing Checklist

- [ ] Run migration script successfully
- [ ] Start backend server without errors
- [ ] Make authenticated prediction request
- [ ] Verify prediction saved with ID
- [ ] Get prediction history (paginated)
- [ ] Get specific prediction by ID
- [ ] Get prediction statistics
- [ ] Delete specific prediction
- [ ] Verify XGBoost model loaded on startup
- [ ] Check API documentation at /docs

## Support

For issues or questions:

1. Check the logs: Backend will log all operations
2. Review API documentation: Visit `/docs` endpoint
3. Check database: Verify prediction_history table structure
4. Test auth: Ensure JWT token is valid

---

**Status**: ✅ Ready for testing and integration
**Dependencies**: PostgreSQL, JWT authentication, XGBoost model
**Performance**: Optimized with indexes for fast queries
**Security**: User-isolated with JWT authentication
