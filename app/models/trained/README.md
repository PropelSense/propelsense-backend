# Trained Models Directory

Place your trained ML model files here:

## Supported Formats:

### scikit-learn
- `.pkl` - Pickle format
- `.joblib` - Joblib format (recommended)

### PyTorch
- `.pt` - PyTorch format
- `.pth` - PyTorch checkpoint

### TensorFlow / Keras
- `.h5` - HDF5 format
- `.pb` - Protobuf format
- `.keras` - Keras native format

### ONNX
- `.onnx` - ONNX format (cross-framework)

### Custom
- Any custom format your model uses

## Example Files:
```
trained/
├── propulsion_power_v1.joblib
├── propulsion_classifier.h5
├── regression_model.onnx
└── model_metadata.json
```

## Usage:

```python
from app.models.propulsion_model import PropulsionPowerModel

# Load model
model = PropulsionPowerModel(model_path="app/models/trained/propulsion_power_v1.joblib")
model.load()

# Make prediction
result = model.predict({
    "rpm": 2500,
    "torque": 150,
    "temperature": 85
})
```

**Note**: This directory is gitignored. Do not commit large model files to git.
Use Git LFS, cloud storage, or artifact management systems for model versioning.
