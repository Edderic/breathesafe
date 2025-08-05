# Training Module Tests

This directory contains comprehensive tests for the `train.py` module.

## Test Structure

The test suite is organized into the following test classes:

### TestDataLoading
- Tests API data fetching functionality
- Mocks external API calls to avoid dependencies
- Tests both successful and error scenarios

### TestDataPreprocessing
- Tests data scaling and normalization
- Tests data type conversion
- Tests train/test split functionality
- Tests categorical variable encoding
- Tests outlier filtering

### TestModelTraining
- Tests PyMC model training functionality
- Uses synthetic data for faster testing
- Tests model and trace creation

### TestModelEvaluation
- Tests model evaluation and prediction
- Tests log loss calculation
- Uses mocked model and trace objects

### TestFileOperations
- Tests file I/O operations
- Uses temporary files for testing
- Tests JSON serialization/deserialization

### TestUtilityFunctions
- Tests utility and display functions
- Tests diagnostics and performance display

### TestIntegration
- Tests the complete training pipeline
- Uses synthetic data and mocked dependencies
- Tests end-to-end functionality

## Running Tests

### From the training directory:
```bash
python -m pytest tests/ -v
```

### Using the test runner:
```bash
python run_tests.py
```

### From the project root:
```bash
cd python/mask_recommender/training
python -m pytest tests/ -v
```

## Test Data

The tests use synthetic data that mimics the structure of real data:
- Facial measurements (face_width, face_length, etc.)
- Mask information (mask_id, strap_type, style)
- Fit test results (qlft_pass)
- User IDs are changed to avoid conflicts with real data

## Dependencies

The tests require the same environment as the training script:
- PyMC for Bayesian modeling
- NumPy and Pandas for data manipulation
- Scikit-learn for preprocessing
- pytest for testing framework

## Mocking Strategy

- **API Calls**: All external API calls are mocked to avoid dependencies
- **File Operations**: File I/O is mocked or uses temporary files
- **Heavy Computations**: Some PyMC operations are mocked for faster testing
- **External Dependencies**: All external services are mocked

## Coverage

The test suite covers:
- ✅ All functions in the training module
- ✅ Data preprocessing pipeline
- ✅ Model training functionality
- ✅ Model evaluation
- ✅ File I/O operations
- ✅ Error handling
- ✅ Integration testing

## Notes

- Tests can take longer to run due to PyMC model training
- Some tests suppress warnings for cleaner output
- Integration tests may fail if PyMC model doesn't converge (expected behavior)
- All file operations use temporary files that are cleaned up automatically 