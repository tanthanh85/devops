# Lab 4: Deploy the Web and Application Tiers on Minikube

## Duration

**2 hours**

In this standalone lab, you will deploy the same working network-monitoring application used in Lab 3. MySQL runs in Docker on the Ubuntu workstation. The Flask application tier and NGINX web tier run in Minikube.

The supplied Lab 4 folder contains a complete copy of the application. You do not need to complete Lab 3 first.

## Objectives

- Run the MySQL database tier with Docker Compose.
- Build the existing Flask and NGINX images.
- Load the images into Minikube.
- Store runtime configuration in a Kubernetes Secret.
- Deploy the application and web tiers as Kubernetes Deployments and Services.
- Verify inventory management and automatic RESTCONF monitoring.
- Display the responding web and application Pod names in the interface.
- Scale the web and application tiers.

## Required environment

- The Lab 1 workstation with Docker, Minikube, `kubectl`, Git, and Python.
- Cisco Secure Client connected when the assigned router requires the course VPN.
- An instructor-authorized IOS XE router with RESTCONF enabled.
- The complete instructor-provided Lab 4 files.

## Architecture

```mermaid
flowchart LR
    B["Learner browser"]

    subgraph K["Minikube"]
        WS["Web Service<br/>NodePort"]
        W["NGINX web Pods<br/>report Web Pod name"]
        AS["Application Service<br/>port 8000"]
        A["Flask application Pods<br/>report App Pod name"]

        WS --> W
        W --> AS
        AS --> A
    end

    subgraph U["Ubuntu workstation"]
        D[("MySQL Docker container<br/>port 3307")]
        V["Cisco Secure Client VPN"]
    end

    R["IOS XE router<br/>RESTCONF port 443"]

    B --> WS
    A <-->|"SQL via host.minikube.internal:3307"| D
    A <-->|"HTTPS RESTCONF"| V
    V <-->|"VPN tunnel"| R
```

## Supplied files

```text
Lab 04 - Deploy and Scale on Kubernetes/
├── Lab4.md
├── .env.example
├── database-compose.yaml
├── app/
├── web/
├── tests/
├── requirements.txt
├── requirements-dev.txt
└── kubernetes/
    ├── namespace.yaml
    ├── app.yaml
    └── web.yaml
```

## Step 1: Create the Lab 4 repository

Create a blank private GitLab project named `netdevops-lab04-kubernetes` and initialize it with a README.

```bash
mkdir -p ~/netdevops-labs
cd ~/netdevops-labs
git clone https://gitlab.com/YOUR-GITLAB-NAMESPACE/netdevops-lab04-kubernetes.git
cd netdevops-lab04-kubernetes
git switch -c feature/lab04-minikube
```

Copy only the supplied Lab 4 files into this repository. Do not copy files from a learner's Lab 3 repository.

```bash
cp -R "/path/to/Lab 04 - Deploy and Scale on Kubernetes/." .
git status
```

## Step 2: Configure the database environment

Create the local environment file:

```bash
cp .env.example .env
chmod 600 .env
```

Generate the required values:

```bash
openssl rand -hex 16
openssl rand -hex 16
openssl rand -hex 32
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Edit `.env` and replace every placeholder:

```dotenv
MYSQL_IMAGE=mysql:8.4
MYSQL_DATABASE=network_monitor
MYSQL_USER=network_app
MYSQL_PASSWORD=replace-with-first-16-byte-hex-value
MYSQL_ROOT_PASSWORD=replace-with-second-16-byte-hex-value
DATABASE_URL=mysql+pymysql://network_app:replace-with-same-MYSQL_PASSWORD-value@host.minikube.internal:3307/network_monitor
FLASK_SECRET_KEY=replace-with-32-byte-hex-value
INVENTORY_ENCRYPTION_KEY=replace-with-generated-fernet-key
SESSION_COOKIE_SECURE=false
```

Do not commit `.env`.

## Step 3: Start Minikube and MySQL

Start the course Minikube profile:

```bash
minikube start --profile network-devops --driver=docker
minikube profile network-devops
kubectl get nodes
```

Start only the database tier on the Ubuntu workstation:

```bash
docker compose --env-file .env -f database-compose.yaml up -d
docker compose --env-file .env -f database-compose.yaml ps
```

Wait until the database reports `healthy`.

The database port is reachable from Minikube for this isolated lab. Do not use this configuration on a shared or production workstation.

## Step 4: Test and build the application

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt -r requirements-dev.txt
python -m pytest -q
```

Build the same application and web tiers used in Lab 3:

```bash
docker build -t network-monitor-app:lab04 -f app/Dockerfile .
docker build -t network-monitor-web:lab04 -f web/Dockerfile .
```

Load both images into Minikube:

```bash
minikube image load network-monitor-app:lab04 --profile network-devops
minikube image load network-monitor-web:lab04 --profile network-devops
minikube image ls --profile network-devops | grep network-monitor
```

## Step 5: Create the Kubernetes runtime configuration

Load the values from `.env` into the current shell:

```bash
set -a
source .env
set +a
```

Create the namespace and application Secret:

```bash
kubectl apply -f kubernetes/namespace.yaml
kubectl -n network-devops create secret generic network-monitor-runtime \
  --from-literal=DATABASE_URL="$DATABASE_URL" \
  --from-literal=FLASK_SECRET_KEY="$FLASK_SECRET_KEY" \
  --from-literal=INVENTORY_ENCRYPTION_KEY="$INVENTORY_ENCRYPTION_KEY" \
  --from-literal=SESSION_COOKIE_SECURE="$SESSION_COOKIE_SECURE" \
  --dry-run=client -o yaml | kubectl apply -f -
```

Confirm the Secret exists without displaying its values:

```bash
kubectl -n network-devops get secret network-monitor-runtime
```

## Step 6: Deploy the application tier

```bash
kubectl apply -f kubernetes/app.yaml
kubectl -n network-devops rollout status deployment/network-monitor-app --timeout=180s
kubectl -n network-devops get pods -l tier=app -o wide
kubectl -n network-devops get service network-monitor-app
```

Verify the application readiness endpoint from inside the cluster:

```bash
kubectl -n network-devops run app-check --rm -i --restart=Never \
  --image=curlimages/curl:8.12.1 -- \
  curl -fsS http://network-monitor-app:8000/health/ready
```

Expected response:

```json
{"status":"ready"}
```

## Step 7: Deploy the web tier

```bash
kubectl apply -f kubernetes/web.yaml
kubectl -n network-devops rollout status deployment/network-monitor-web --timeout=180s
kubectl -n network-devops get pods -l tier=web -o wide
kubectl -n network-devops get service network-monitor-web
```

Open the web service:

```bash
minikube service network-monitor-web \
  --namespace network-devops \
  --profile network-devops
```

## Step 8: Verify the monitoring workflow

1. Create the administrator and sign in.
2. Open **Inventory management** and add the assigned router.
3. Open **Monitoring** and select the router.
4. Select a 5-, 10-, or 15-second refresh interval.
5. Confirm that the CPU and memory values and both charts update automatically.
6. Confirm that the header displays the responding **Web Pod** and **App Pod** names.

Compare the displayed names with the running Pods:

```bash
kubectl -n network-devops get pods -o wide
```

## Step 9: Scale the Minikube tiers

Scale the stateless web tier to three Pods and the application tier to two Pods:

```bash
kubectl -n network-devops scale deployment/network-monitor-web --replicas=3
kubectl -n network-devops scale deployment/network-monitor-app --replicas=2
kubectl -n network-devops rollout status deployment/network-monitor-web
kubectl -n network-devops rollout status deployment/network-monitor-app
kubectl -n network-devops get pods -o wide
```

Refresh the monitoring page and confirm that the application still works through both Services.

Wait for automatic collections or select **Collect now** several times. Observe the **Web Pod** and **App Pod** names in the header. Kubernetes may reuse an existing connection, so a different Pod is not guaranteed on every request.

To make repeated new connections from the terminal:

```bash
WEB_URL=$(minikube service network-monitor-web \
  --namespace network-devops \
  --profile network-devops \
  --url)

for attempt in $(seq 1 12); do
  curl -s -H 'Connection: close' "$WEB_URL/instance"
  curl -s -H 'Connection: close' "$WEB_URL/api/instance"
done
```

The returned `instance` values should match names shown by `kubectl get pods`.

## Step 10: Verify database persistence

Restart both Minikube Deployments:

```bash
kubectl -n network-devops rollout restart deployment/network-monitor-app
kubectl -n network-devops rollout restart deployment/network-monitor-web
kubectl -n network-devops rollout status deployment/network-monitor-app
kubectl -n network-devops rollout status deployment/network-monitor-web
```

Sign in again and confirm that the administrator and router inventory still exist in MySQL.

## Step 11: Commit and push

```bash
git status
git add .
git status
git commit -m "Deploy web and application tiers on Minikube"
git push -u origin feature/lab04-minikube
```

Confirm that `.env` is not staged before committing.

## Completion criteria

- The original Lab 3 application tests pass.
- MySQL is healthy on the Ubuntu workstation.
- The application and web images are present in Minikube.
- The application and web Deployments are ready.
- The browser reaches the application through the web Service.
- Inventory management works with the existing MySQL data model.
- CPU and memory metrics refresh automatically.
- The interface displays the responding Web Pod and App Pod names.
- Three web Pods and two application Pods run successfully.
- Data remains available after both Minikube Deployments restart.

## Cleanup

Remove the Kubernetes workloads and stop the database without deleting its volume:

```bash
kubectl delete namespace network-devops
docker compose --env-file .env -f database-compose.yaml stop
```

## Troubleshooting

### An image cannot be pulled

Confirm that both local images were loaded into the selected profile:

```bash
minikube image ls --profile network-devops | grep network-monitor
kubectl -n network-devops describe pod <pod-name>
```

### The application Pod is not ready

```bash
docker compose --env-file .env -f database-compose.yaml ps
kubectl -n network-devops logs deployment/network-monitor-app --tail=200
kubectl -n network-devops describe deployment network-monitor-app
```

Confirm that `DATABASE_URL` in `.env` uses `host.minikube.internal:3307`, then recreate the Secret and restart the application Deployment.

### Router collection times out

Connect Cisco Secure Client before starting Minikube. Confirm that the Ubuntu workstation can reach the router, then restart the profile so the Minikube node receives the current routes:

```bash
ping -c 3 ROUTER_IP
minikube stop --profile network-devops
minikube start --profile network-devops --driver=docker
kubectl -n network-devops rollout restart deployment/network-monitor-app
```

### The old web interface is displayed

Rebuild and reload the image, then recreate the web Pods:

```bash
docker build --no-cache -t network-monitor-web:lab04 -f web/Dockerfile .
minikube image load network-monitor-web:lab04 --profile network-devops --overwrite
kubectl -n network-devops rollout restart deployment/network-monitor-web
kubectl -n network-devops rollout status deployment/network-monitor-web
```
