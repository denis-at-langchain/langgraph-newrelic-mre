# Minimal Dockerfile for New Relic + LangGraph MRE
# Uses official LangGraph API image from public Docker Hub

FROM langchain/langgraph-api:3.11

# Add requirements
ADD requirements.txt /deps/requirements.txt
RUN PYTHONDONTWRITEBYTECODE=1 pip install --no-cache-dir -r /deps/requirements.txt

# Add agent code and New Relic config
ADD agent.py /deps/agent.py
ADD newrelic.ini /deps/newrelic.ini

# Set working directory
WORKDIR /deps

# Set New Relic environment variables for the config file location
# License key MUST be set via LangSmith deployment secrets
ENV NEW_RELIC_CONFIG_FILE=/deps/newrelic.ini

# Note: NEW_RELIC_LICENSE_KEY must be set via LangSmith secrets for activation
# Note: NEW_RELIC_ENVIRONMENT can be set via LangSmith deployment settings

