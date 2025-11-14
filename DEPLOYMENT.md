# LangGraph + New Relic Deployment Guide

## Solution to Uvicorn Initialization Conflict

The key issue was **programmatic New Relic initialization at module import time** conflicting with LangGraph Platform's Uvicorn initialization.

### What Changed

1. **Removed programmatic initialization** from `agent.py`
2. **Using environment variable-based configuration** instead
3. **Graph compilation in thread** using `asyncio.to_thread()` for additional isolation

## Deployment Steps for LangSmith Platform

### 1. Set Environment Variables in LangSmith Deployment

In your LangSmith deployment settings, add these **runtime** environment variables:

```bash
# Required: New Relic License Key (set as secret)
NEW_RELIC_LICENSE_KEY=your_license_key_here

# Required: Application Name
NEW_RELIC_APP_NAME=langgraph-newrelic-mre

# Optional: Environment (dev, staging, production)
NEW_RELIC_ENVIRONMENT=production

# Optional: Log Level
NEW_RELIC_LOG_LEVEL=info
```

**Note**: `NEW_RELIC_CONFIG_FILE=/deps/newrelic.ini` is already set in the Dockerfile via `langgraph.json`, so you don't need to set it again in LangSmith.

### 2. Deploy

The `langgraph.json` configuration will:
- Install `newrelic` package from `requirements.txt`
- Copy `newrelic.ini` to `/deps/newrelic.ini` via `dockerfile_lines`
- Set `NEW_RELIC_CONFIG_FILE=/deps/newrelic.ini` environment variable
- Let New Relic auto-instrument via environment variables

**Note**: The `newrelic.ini` file is copied using `ADD newrelic.ini /deps/newrelic.ini` in `dockerfile_lines` because the `dependencies` field only accepts directories (Python packages), not individual files.

### 3. Verify

Check your deployment logs for:
```
✅ LangGraph compiled successfully
🚀 Ready to deploy!
```

And in New Relic, you should see:
- APM data for your application
- Traces for graph invocations
- ASGI/Uvicorn instrumentation working correctly

## How It Works

### Environment Variable Initialization

Instead of calling `newrelic.agent.initialize()` in Python code, New Relic automatically initializes when:

1. The `newrelic` package is installed
2. Environment variables are set (especially `NEW_RELIC_LICENSE_KEY`)
3. The application starts

This avoids timing conflicts with LangGraph Platform's Uvicorn initialization.

### Thread-Based Graph Compilation

The graph compiles in a separate thread:

```python
async def compile_graph():
    def _compile():
        return graph_builder.compile()
    return await asyncio.to_thread(_compile)

graph = asyncio.run(compile_graph())
```

This provides additional isolation during initialization.

## Configuration Strategy: Dockerfile vs. Runtime

### When to use `dockerfile_lines` in `langgraph.json`

Use for **constants** that are the same across all deployments:
- File paths (e.g., `NEW_RELIC_CONFIG_FILE=/deps/newrelic.ini`)
- Default configurations that rarely change

**Benefits**: Baked into the image, no need to set per deployment

### When to use LangSmith deployment environment variables

Use for **deployment-specific** or **sensitive** values:
- Secrets (e.g., `NEW_RELIC_LICENSE_KEY`)
- Environment names (e.g., `NEW_RELIC_ENVIRONMENT=staging` vs `production`)
- App names that vary per deployment
- Values you want to change without rebuilding the image

**Benefits**: Can be updated without rebuilding, proper secret management, per-environment configuration

## Troubleshooting

### Build Error: `NotADirectoryError: Local dependency must be a directory: newrelic.ini`

**Cause**: You have `newrelic.ini` in the `dependencies` array in `langgraph.json`

**Fix**: The `dependencies` field only accepts directories (Python packages). Use `dockerfile_lines` instead:

```json
"dockerfile_lines": [
  "ADD newrelic.ini /deps/newrelic.ini",
  "ENV NEW_RELIC_CONFIG_FILE=/deps/newrelic.ini"
]
```

### If you still see `AttributeError: 'Config' object has no attribute '_nr_loaded_app'`

1. Ensure you've removed ALL programmatic `newrelic.agent.initialize()` calls from `agent.py`
2. Verify environment variables are set in LangSmith deployment settings
3. Check that `newrelic.ini` is being copied to `/deps/` directory via `dockerfile_lines`
4. Verify the build logs show the file being added

### If New Relic data isn't appearing

1. Verify `NEW_RELIC_LICENSE_KEY` is set and valid
2. Check `NEW_RELIC_APP_NAME` matches what you expect in New Relic UI
3. Review application logs for New Relic initialization messages

## References

- [New Relic Python Agent Configuration](https://docs.newrelic.com/docs/apm/agents/python-agent/configuration/python-agent-configuration/)
- [LangGraph Platform Documentation](https://docs.smith.langchain.com/)

