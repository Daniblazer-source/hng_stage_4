# SwiftDeploy CLI 🚀

`swiftdeploy` is a declarative infrastructure-as-code (IaC) tool designed to manage and orchestrate a containerized API stack with a built-in Nginx reverse proxy.

## 🏗 Architecture
All external traffic is routed through Nginx on the host port specified in the manifest, which then proxies requests to the internal API service.

- **Frontend:** Nginx (Reverse Proxy)
- **Backend:** FastAPI (Python)
- **Deployment:** Docker Compose (Generated)

## 🛠 Setup & Installation

1. **Build the Application Image:**
   ```bash
   docker build -t swift-deploy-1-node:latest .
   ```
2. **Install CLI Dependencies:**
   ```bash
   pip install -r app/requirements.txt
   ```
3. **Set Execution Permissions:**
   ```bash
   chmod +x swiftdeploy
   ```
   # 🕹 Subcommands
  ## validate
  Performs pre-flight checks to ensure the environment is ready for deployment.
  ```bash
./swiftdeploy validate
```
Checks: YAML syntax, required manifest fields, local image existence, and port availability.
## deploy
Generates configurations and brings the stack online.
```bash
./swiftdeploy deploy
```
Action: Renders docker-compose.yml and nginx.conf from templates, starts containers, and monitors the healthcheck.
## promote
Updates the deployment environment mode dynamically.
```bash
./swiftdeploy promote canary
```
## teardown
Stops and removes the deployment.
```bash
./swiftdeploy teardown --clean
```
Action: Stops all containers. Use the --clean flag to delete the generated configuration files.
# 🧪 Testing the Stack
## Health Check
```bash
curl http://localhost:8081/healthz
```
## Chaos Engineering
Verify the /chaos endpoint (available in Canary mode):
```bash
curl -X POST http://localhost:8081/chaos \
     -H "Content-Type: application/json" \
     -d '{"mode": "slow", "duration": 2}'
```
## Header Verification
Verify the proxy headers are injected:
```bash
curl -I http://localhost:8081/
```
Look for X-Deployed-By: swiftdeploy and x-mode: canary.
# 📄 Manifest Schema
The `manifest.yaml` acts as the single source of truth for the deployment:

`services`: API image and internal port configuration.

`nginx`: Proxy port and timeout settings.

`mode`: Current environment state (stable/canary).
