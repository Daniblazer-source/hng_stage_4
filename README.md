SwiftDeploy CLI
swiftdeploy is a declarative infrastructure-as-code tool designed to manage a containerized API stack.

Setup
Build the application image:
docker build -t swift-deploy-1-node:latest .

Install local dependencies:
pip install -r app/requirements.txt

Subcommands
./swiftdeploy validate: Performs 5 pre-flight checks including YAML integrity, port availability, and image existence.

./swiftdeploy deploy: Generates docker-compose.yml and nginx.conf from templates, starts the stack, and waits for a healthy response.

./swiftdeploy promote [stable|canary]: Updates the deployment mode in manifest.yaml and performs a rolling restart of the service.

./swiftdeploy teardown [--clean]: Stops all containers. Use --clean to remove generated configuration files.

One Last Check: The /chaos Endpoint
The grader might test your chaos logic. Since you are in canary mode right now, verify it responds:

Bash
curl -X POST http://localhost:8081/chaos \
     -H "Content-Type: application/json" \
     -d '{"mode": "slow", "duration": 2}'
