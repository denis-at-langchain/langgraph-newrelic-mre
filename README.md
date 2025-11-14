# LangGraph + New Relic Integration Issue - Minimal Reproducible Example

## 🎯 Problem Statement

**LangGraph Platform controls the ASGI server lifecycle**, specifically how Uvicorn is initialized, causing **direct conflicts with New Relic's automatic instrumentation hooks**.

### Current Status

New Relic currently only works with a **required Uvicorn suppression workaround** applied:

```python
class DummyUvicornModule:
    def __getattr__(self, name):
        def dummy_func(*args, **kwargs):
            return None
        return dummy_func

sys.modules['newrelic.hooks.adapter_uvicorn'] = DummyUvicornModule()
```

✅ **Status:** WORKING but with known limitations.

### ⚠️ Limitations of Current Solution

- **Reduced New Relic Monitoring**
  - Limited metrics collection
  - Incomplete distributed tracing  
  - Missing Uvicorn-level instrumentation (e.g., thread pool metrics)

---

## 📂 Repository Structure

This is a **minimal reproducible example** that demonstrates the issue without any custom frameworks or internal dependencies.

```
.
├── agent.py                    # Minimal LangGraph agent with New Relic init
├── requirements-minimal.txt    # Clean dependencies (public PyPI only)
├── Dockerfile-minimal          # Public Docker image configuration
├── langgraph-minimal.json      # LangGraph configuration
├── newrelic-minimal.ini        # New Relic configuration (sanitized)
├── env.example                 # Environment variables template
└── README.md                   # This file
```

---

## 🚀 Step-by-Step Deployment Guide

### Prerequisites

1. **New Relic Account**: Free account at https://newrelic.com/signup
2. **LangSmith Account**: Access to https://beta.smith.langchain.com/
3. **GitHub Account**: For repository hosting
4. **Git installed**: On your local machine

---

### Step 1: Set Up Your New Relic Account

1. **Sign up** for New Relic (if you don't have an account):
   - Go to https://newrelic.com/signup
   - Choose the free tier

2. **Get your License Key**:
   - Log in to New Relic
   - Click on your profile (top right) → **API Keys**
   - Copy your **License Key** (starts with a long alphanumeric string)
   - Save it securely - you'll need it later

3. **Create an Application** (optional):
   - Go to **APM & Services** → **Add Data**
   - Search for "Python" → Select "Python"
   - Note the app name you want to use (default: `langgraph-newrelic-mre`)

---

### Step 2: Prepare Your Local Repository

1. **Navigate to the project directory**:
   ```bash
   cd /Users/dk/lab/sandbox/11550/build
   ```

2. **Initialize Git** (if not already done):
   ```bash
   git init
   ```

3. **Copy the minimal files** to the root:
   ```bash
   # Create a clean directory for the MRE
   mkdir -p ../langgraph-newrelic-mre
   cd ../langgraph-newrelic-mre
   
   # Copy minimal files
   cp ../build/agent.py .
   cp ../build/requirements-minimal.txt ./requirements.txt
   cp ../build/Dockerfile-minimal ./Dockerfile
   cp ../build/langgraph-minimal.json ./langgraph.json
   cp ../build/newrelic-minimal.ini ./newrelic.ini
   cp ../build/env.example .env.example
   cp ../build/README.md .
   cp ../build/.gitignore .
   ```

4. **Create a `.env` file** with your credentials:
   ```bash
   cp env.example .env
   ```
   
   Edit `.env` and add your New Relic license key:
   ```bash
   NEW_RELIC_LICENSE_KEY=your_actual_license_key_here
   NEW_RELIC_APP_NAME=langgraph-newrelic-mre
   NEW_RELIC_LOG_LEVEL=info
   ```

5. **Add files to Git**:
   ```bash
   git add .
   git commit -m "Initial commit: LangGraph + New Relic MRE"
   ```

---

### Step 3: Push to GitHub

1. **Create a new GitHub repository**:
   - Go to https://github.com/new
   - Repository name: `langgraph-newrelic-mre`
   - Description: "Minimal reproducible example for LangGraph + New Relic integration issue"
   - Make it **Public** (so LangSmith can access it)
   - Do NOT initialize with README (we already have one)
   - Click **Create repository**

2. **Add GitHub remote and push**:
   ```bash
   # Replace YOUR_USERNAME with your actual GitHub username
   git remote add origin https://github.com/YOUR_USERNAME/langgraph-newrelic-mre.git
   git branch -M main
   git push -u origin main
   ```

3. **Verify the push**:
   - Go to `https://github.com/YOUR_USERNAME/langgraph-newrelic-mre`
   - You should see all your files

---

### Step 4: Deploy to LangSmith

1. **Log in to LangSmith**:
   - Go to https://beta.smith.langchain.com/
   - Sign in with your credentials

2. **Navigate to Deployments**:
   - Click on **"Deployments"** in the left sidebar
   - Click **"+ New Deployment"** or **"Deploy"**

3. **Configure the deployment**:

   **a. Source Configuration:**
   - **Source Type**: GitHub Repository
   - **Repository URL**: `https://github.com/YOUR_USERNAME/langgraph-newrelic-mre`
   - **Branch**: `main`
   - **Graph Path**: Leave default (it will find `langgraph.json`)

   **b. Environment Variables (Secrets):**
   - Click **"Add Environment Variable"**
   - Add your New Relic license key:
     - Key: `NEW_RELIC_LICENSE_KEY`
     - Value: `your_actual_license_key_here`
     - Check ☑️ **"Secret"** (to hide the value)
   
   - (Optional) Add OpenAI key if you want to test with real LLM:
     - Key: `OPENAI_API_KEY`
     - Value: `your_openai_key`
     - Check ☑️ **"Secret"**

   **c. Deployment Settings:**
   - **Deployment Name**: `newrelic-mre`
   - **Python Version**: 3.11 (should auto-detect from `langgraph.json`)
   - **Resource Allocation**: Choose based on your plan (default is fine)

4. **Deploy**:
   - Click **"Deploy"** or **"Create Deployment"**
   - Wait for the build to complete (this may take 5-10 minutes)

5. **Monitor the build**:
   - You should see build logs in real-time
   - Look for the New Relic initialization messages:
     - ✅ `New Relic agent initialized with config: ./newrelic.ini`
     - OR ❌ Error messages indicating the conflict

---

### Step 5: Test the Deployment

1. **Get your deployment URL**:
   - Once deployed, LangSmith will provide an API endpoint
   - Example: `https://your-deployment.langchain.app`

2. **Test the agent**:
   
   **Using curl:**
   ```bash
   curl -X POST "https://your-deployment.langchain.app/runs/stream" \
     -H "Content-Type: application/json" \
     -d '{
       "assistant_id": "agent",
       "input": {
         "messages": [
           {"role": "user", "content": "Hello, test message"}
         ]
       }
     }'
   ```

   **Using Python:**
   ```python
   import requests
   
   url = "https://your-deployment.langchain.app/runs/stream"
   payload = {
       "assistant_id": "agent",
       "input": {
           "messages": [
               {"role": "user", "content": "Hello, test message"}
           ]
       }
   }
   
   response = requests.post(url, json=payload)
   print(response.json())
   ```

3. **Check New Relic**:
   - Go to your New Relic dashboard
   - Navigate to **APM & Services** → **langgraph-newrelic-mre**
   - Look for:
     - ✅ Transactions appearing
     - ✅ Distributed traces
     - ⚠️ Missing Uvicorn metrics (due to the conflict)

---

## 🔍 Expected Behavior vs. Actual Behavior

### Expected (Without LangGraph Platform)
When deploying New Relic with a standard ASGI app:
- ✅ Full Uvicorn instrumentation
- ✅ Thread pool metrics
- ✅ Complete request lifecycle tracking
- ✅ All middleware hooks working

### Actual (With LangGraph Platform)
When deploying to LangGraph Platform:
- ⚠️ Uvicorn hooks conflict with platform's server management
- ⚠️ Need workaround to suppress `newrelic.hooks.adapter_uvicorn`
- ⚠️ Limited visibility into server-level metrics
- ✅ Application-level monitoring works (with workaround)

---

## 🐛 Reproducing the Issue

### Without Workaround (Shows the Error)

Remove the workaround from `agent.py` and redeploy to see the original error:

```python
# Comment out or remove this workaround
# class DummyUvicornModule:
#     def __getattr__(self, name):
#         def dummy_func(*args, **kwargs):
#             return None
#         return dummy_func
# sys.modules['newrelic.hooks.adapter_uvicorn'] = DummyUvicornModule()
```

**Expected Error:**
```
Error initializing New Relic: [Error details about Uvicorn hook conflicts]
```

### With Workaround (Current Status)

The current `agent.py` includes the workaround, which allows New Relic to initialize but with reduced functionality.

---

## 📊 What to Report to New Relic / LangChain

When reporting this issue, provide:

1. **Repository Link**: Your GitHub repo URL
2. **Deployment URL**: Your LangSmith deployment URL
3. **New Relic App Link**: Link to your app in New Relic dashboard
4. **Build Logs**: Copy the build logs from LangSmith deployment
5. **New Relic Logs**: Any errors from New Relic dashboard

### Key Information

- **LangGraph Version**: Check `requirements-minimal.txt`
- **New Relic Version**: Check `requirements-minimal.txt`  
- **Python Version**: 3.11
- **Platform**: LangSmith (LangGraph Platform)
- **Issue Type**: ASGI server lifecycle conflict

---

## 🛠️ Technical Details

### Why This Happens

1. **LangGraph Platform** manages its own Uvicorn server lifecycle
2. **New Relic** tries to instrument Uvicorn automatically on import
3. **Conflict**: New Relic's hooks expect to control Uvicorn initialization
4. **Result**: Either initialization fails OR partial instrumentation

### Workaround Explanation

```python
# This suppresses New Relic's Uvicorn adapter
sys.modules['newrelic.hooks.adapter_uvicorn'] = DummyUvicornModule()
```

**What it does:**
- Prevents New Relic from loading its Uvicorn instrumentation
- Allows the agent to initialize without errors
- **Trade-off**: Loses Uvicorn-level metrics

**What's missing:**
- Uvicorn worker metrics
- Thread pool utilization
- Connection handling metrics
- Some middleware timings

---

## 📝 Local Testing (Optional)

### Test Locally Before Deployment

1. **Install dependencies**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Set environment variables**:
   ```bash
   export NEW_RELIC_LICENSE_KEY=your_license_key
   export NEW_RELIC_APP_NAME=langgraph-newrelic-local
   ```

3. **Run with LangGraph CLI** (if you have it):
   ```bash
   pip install langgraph-cli
   langgraph dev
   ```

4. **Or test the agent directly**:
   ```python
   python -c "import agent; print('Agent loaded successfully')"
   ```

---

## 🤝 Contributing

If you find solutions or improvements:

1. Fork this repository
2. Create a feature branch
3. Submit a pull request with your findings

---

## 📞 Support Contacts

- **LangChain/LangGraph**: https://github.com/langchain-ai/langgraph/issues
- **New Relic**: https://support.newrelic.com/
- **LangSmith Support**: support@langchain.com

---

## 📄 License

This is a minimal reproducible example for bug reporting purposes.
Feel free to use and modify as needed.

---

## ✅ Checklist

Before deploying, ensure you have:

- [ ] New Relic account and license key
- [ ] LangSmith account access
- [ ] GitHub repository created and pushed
- [ ] `.env` file with your credentials (for local testing)
- [ ] Environment variables configured in LangSmith deployment
- [ ] Tested the deployment and checked New Relic dashboard

---

## 🔗 Useful Links

- **LangGraph Documentation**: https://langchain-ai.github.io/langgraph/
- **LangSmith Deployment Guide**: https://docs.smith.langchain.com/
- **New Relic Python Agent**: https://docs.newrelic.com/docs/apm/agents/python-agent/
- **New Relic AI Monitoring**: https://docs.newrelic.com/docs/ai-monitoring/

---

**Last Updated**: November 14, 2025

