# Port 5000 Conflict on macOS

## Problem

Port 5000 is used by **AirPlay Receiver** on macOS, which prevents the Flask app from starting on the default port.

## Solution

Use port **1234** instead (or any other available port):

### Start Flask App
```bash
cd python/mask_component_predictor
python3 app.py 1234
```

### Test from Rails
```bash
PORT=1234 rails mask_predictor:test
```

### Configure Rails Service
```bash
# In your shell profile (~/.zshrc or ~/.bashrc)
export MASK_PREDICTOR_PORT=1234

# Or in .env file
MASK_PREDICTOR_PORT=1234
```

## Alternative: Disable AirPlay Receiver

If you prefer to use port 5000:

1. Open **System Settings**
2. Go to **General** → **AirDrop & Handoff**
3. Toggle off **AirPlay Receiver**

## Recommended Setup

For development, we recommend using **port 1234** to avoid conflicts:

```bash
# Terminal 1: Start Python service
cd python/mask_component_predictor
python3 app.py 1234

# Terminal 2: Test from Rails
PORT=1234 rails mask_predictor:test

# Terminal 3: Start Rails server
MASK_PREDICTOR_PORT=1234 rails server
```

## Production

On Heroku, the `PORT` environment variable is automatically set by the platform, so no configuration is needed.
