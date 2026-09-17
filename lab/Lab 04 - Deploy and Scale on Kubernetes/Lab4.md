# Lab 4: Deploy the Three-Tier Application on Minikube

## Duration

**2 hours**

In this standalone lab, you will deploy the complete working three-tier network-monitoring application used in Lab 3 to Minikube. MySQL, Flask, and NGINX all run as Kubernetes workloads.

The supplied Lab 4 folder contains a complete copy of the application. You do not need to complete Lab 3 first.

This lab does not use `host.minikube.internal`, `host.docker.internal`, or workstation DNS. Communication between tiers uses Kubernetes Services. Minikube provides the internal Service name `network-monitor-db` to Pods automatically.

## Objectives

- Deploy MySQL as a persistent Kubernetes StatefulSet.
- Build the existing Flask and NGINX images.
- Load the images into Minikube.
- Store runtime configuration in a Kubernetes Secret.
- Deploy the database, application, and web tiers as Kubernetes workloads and Services.
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
        DS["Database Service<br/>port 3306"]
        D[("MySQL StatefulSet<br/>persistent volume")]

        WS --> W
        W --> AS
        AS --> A
        A --> DS
        DS --> D
    end

    G["Ubuntu Minikube bridge gateway<br/>RESTCONF relay · port 9443"]
    V["Cisco Secure Client VPN"]
    R["IOS XE router<br/>RESTCONF port 443"]

    B --> WS
    A <-->|"HTTPS via bridge IP:9443"| G
    G <-->|"TCP relay"| V
    V <-->|"VPN tunnel"| R
```

## Supplied files

```text
Lab 04 - Deploy and Scale on Kubernetes/
├── Lab4.md
├── .env.example
├── app/
├── web/
├── tests/
├── requirements.txt
├── requirements-dev.txt
└── kubernetes/
    ├── namespace.yaml
    ├── mysql.yaml
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
MYSQL_DATABASE=network_monitor
MYSQL_USER=network_app
MYSQL_PASSWORD=replace-with-first-16-byte-hex-value
MYSQL_ROOT_PASSWORD=replace-with-second-16-byte-hex-value
# Kubernetes Service address; no workstation DNS entry is required.
DATABASE_URL=mysql+pymysql://network_app:replace-with-same-value-as-MYSQL_PASSWORD@network-monitor-db:3306/network_monitor
FLASK_SECRET_KEY=replace-with-32-byte-hex-value
INVENTORY_ENCRYPTION_KEY=replace-with-generated-fernet-key
SESSION_COOKIE_SECURE=false
```

Do not commit `.env`.

## Step 3: Start Minikube

Start the course Minikube profile:

```bash
minikube start --profile network-devops --driver=docker
minikube profile network-devops
kubectl get nodes
```

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
minikube image load network-monitor-app:lab04 --profile network-devops --overwrite
minikube image load network-monitor-web:lab04 --profile network-devops --overwrite
minikube image ls --profile network-devops | grep network-monitor
```

## Step 5: Create the Kubernetes runtime configuration

Create the namespace and runtime Secret directly from `.env`:

```bash
kubectl apply -f kubernetes/namespace.yaml
kubectl -n network-devops create secret generic network-monitor-runtime \
  --from-env-file=.env \
  --dry-run=client -o yaml | kubectl apply -f -
```

Confirm that the Secret contains every required key without displaying any values:

```bash
kubectl -n network-devops get secret network-monitor-runtime \
  -o go-template='{{range $key, $value := .data}}{{$key}}{{"\n"}}{{end}}' | sort
```

Required keys:

```text
DATABASE_URL
FLASK_SECRET_KEY
INVENTORY_ENCRYPTION_KEY
MYSQL_DATABASE
MYSQL_PASSWORD
MYSQL_ROOT_PASSWORD
MYSQL_USER
SESSION_COOKIE_SECURE
```

## Step 6: Deploy the database tier

Create the MySQL Service, StatefulSet, and persistent volume claim:

```bash
kubectl apply -f kubernetes/mysql.yaml
kubectl -n network-devops rollout status statefulset/network-monitor-db --timeout=240s
kubectl -n network-devops get pod,service,pvc -l app=network-monitor -o wide
```

Confirm that the database Pod is ready and its persistent volume claim is `Bound`:

```bash
kubectl -n network-devops get pod network-monitor-db-0
kubectl -n network-devops get pvc
```

## Step 7: Deploy the application tier

```bash
kubectl apply -f kubernetes/app.yaml
kubectl -n network-devops rollout status deployment/network-monitor-app --timeout=180s
kubectl -n network-devops wait \
  --for=condition=Ready pod \
  -l app=network-monitor,tier=app \
  --timeout=180s
kubectl -n network-devops get pods -l tier=app -o wide
kubectl -n network-devops get service network-monitor-app
kubectl -n network-devops get endpointslice \
  -l kubernetes.io/service-name=network-monitor-app
```

Do not continue until the App Pod shows `1/1 Running` and the EndpointSlice lists
an address on port `8000`. An `EXTERNAL-IP` value of `<none>` is correct because
the application Service is available only inside the cluster.

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

## Step 8: Deploy the web tier

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

## Step 9: Create the RESTCONF VPN relay

Cisco Secure Client terminates the VPN on Ubuntu and does not normally export its
routes into a Docker-driver Minikube node. Create a TCP relay on the Ubuntu bridge
address so the App Pods can use Ubuntu's VPN route without host DNS.

Install `socat` on Ubuntu if it is not already available:

```bash
sudo apt-get update
sudo apt-get install -y socat
```

Determine the numeric Ubuntu gateway address used by the Minikube node:

```bash
MINIKUBE_HOST_IP=$(docker inspect network-devops \
  --format '{{range .NetworkSettings.Networks}}{{.Gateway}}{{end}}')
echo "$MINIKUBE_HOST_IP"
```

Confirm that Ubuntu can reach the assigned router through Cisco Secure Client:

```bash
ping -c 3 ROUTER_IP
```

In a separate terminal, start the relay and keep it running during the lab:

```bash
MINIKUBE_HOST_IP=$(docker inspect network-devops \
  --format '{{range .NetworkSettings.Networks}}{{.Gateway}}{{end}}')
ROUTER_IP=REPLACE_WITH_ROUTER_IP

sudo socat -d -d \
  TCP-LISTEN:9443,bind="$MINIKUBE_HOST_IP",reuseaddr,fork \
  TCP:"$ROUTER_IP":443
```

From the original terminal, verify that the App Pod can reach the relay:

```bash
kubectl -n network-devops exec deployment/network-monitor-app -- \
  python -c "import socket; socket.create_connection(('$MINIKUBE_HOST_IP',9443),5); print('RESTCONF relay reachable')"
```

## Step 10: Verify the monitoring workflow

1. Create the administrator and sign in.
2. Open **Inventory management** and add the numeric value of `$MINIKUBE_HOST_IP` as the router host, port `9443`, and the assigned router credentials.
3. Open **Monitoring** and select the router.
4. Select a 5-, 10-, or 15-second refresh interval.
5. Confirm that the CPU and memory values and both charts update automatically.
6. Confirm that the header displays the responding **Web Pod** and **App Pod** names.

Compare the displayed names with the running Pods:

```bash
kubectl -n network-devops get pods -o wide
```

## Step 11: Scale the Minikube tiers

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

## Step 12: Verify database persistence

Delete the MySQL Pod. The StatefulSet recreates it and mounts the same persistent volume:

```bash
kubectl -n network-devops delete pod network-monitor-db-0
kubectl -n network-devops rollout status statefulset/network-monitor-db --timeout=240s
kubectl -n network-devops get pod network-monitor-db-0
```

Restart both stateless Deployments:

```bash
kubectl -n network-devops rollout restart deployment/network-monitor-app
kubectl -n network-devops rollout restart deployment/network-monitor-web
kubectl -n network-devops rollout status deployment/network-monitor-app
kubectl -n network-devops rollout status deployment/network-monitor-web
```

Sign in again and confirm that the administrator and router inventory still exist in MySQL.

## Step 13: Commit and push

```bash
git status
git add .
git status
git commit -m "Deploy three-tier application on Minikube"
git push -u origin feature/lab04-minikube
```

Confirm that `.env` is not staged before committing.

## Completion criteria

- The original Lab 3 application tests pass.
- The MySQL StatefulSet is ready and its persistent volume claim is bound.
- The application and web images are present in Minikube.
- The database, application, and web workloads are ready.
- The App Pod reaches the router through the Ubuntu RESTCONF relay and Cisco Secure Client.
- The browser reaches the application through the web Service.
- Inventory management works with the existing MySQL data model.
- CPU and memory metrics refresh automatically.
- The interface displays the responding Web Pod and App Pod names.
- Three web Pods and two application Pods run successfully.
- Data remains available after the MySQL Pod and both Deployments restart.

## Cleanup

Remove the complete lab namespace, including its persistent volume claim:

```bash
kubectl delete namespace network-devops
```

This deletes the Lab 4 MySQL data. Run it only after collecting the required evidence.

Press `Ctrl+C` in the relay terminal to stop `socat`.

## Troubleshooting

### An image cannot be pulled

Confirm that both local images were loaded into the selected profile:

```bash
minikube image ls --profile network-devops | grep network-monitor
kubectl -n network-devops describe pod <pod-name>
```

### The application Pod is not ready

```bash
kubectl -n network-devops get pod network-monitor-db-0
kubectl -n network-devops logs network-monitor-db-0 --tail=200
kubectl -n network-devops get pods -l app=network-monitor,tier=app -o wide
kubectl -n network-devops get endpointslice \
  -l kubernetes.io/service-name=network-monitor-app
kubectl -n network-devops logs deployment/network-monitor-app --tail=200
kubectl -n network-devops describe pods -l app=network-monitor,tier=app
```

If the EndpointSlice has no endpoint address, the application Pod is not ready.
Confirm that MySQL is ready and that `DATABASE_URL` in `.env` uses
`network-monitor-db:3306`. Recreate the Secret if necessary, then restart and wait
for the application:

```bash
kubectl -n network-devops rollout restart deployment/network-monitor-app
kubectl -n network-devops rollout status deployment/network-monitor-app --timeout=180s
```

Run the `app-check` command only after the EndpointSlice contains an address.

### A Pod shows `CreateContainerConfigError`

Display the Pod events to identify the missing Secret or key:

```bash
kubectl -n network-devops describe pods \
  -l app=network-monitor,tier=app
```

Recreate the complete Secret from `.env`, then recreate the affected Pods:

```bash
kubectl -n network-devops create secret generic network-monitor-runtime \
  --from-env-file=.env \
  --dry-run=client -o yaml | kubectl apply -f -

kubectl -n network-devops rollout restart statefulset/network-monitor-db
kubectl -n network-devops rollout status statefulset/network-monitor-db --timeout=240s
kubectl -n network-devops rollout restart deployment/network-monitor-app
kubectl -n network-devops rollout status deployment/network-monitor-app --timeout=180s
```

If the event reports that Kubernetes cannot verify a non-root image user, rebuild
the corrected image, overwrite the copy held by Minikube, and restart the
Deployment:

```bash
docker build --no-cache -t network-monitor-app:lab04 -f app/Dockerfile .
minikube image load network-monitor-app:lab04 \
  --profile network-devops \
  --overwrite
kubectl -n network-devops rollout restart deployment/network-monitor-app
kubectl -n network-devops rollout status deployment/network-monitor-app --timeout=180s
```

### Router collection times out

Confirm that Cisco Secure Client is connected, the relay terminal is still running,
and the App Pod can reach the numeric bridge address:

```bash
ping -c 3 ROUTER_IP
MINIKUBE_HOST_IP=$(docker inspect network-devops \
  --format '{{range .NetworkSettings.Networks}}{{.Gateway}}{{end}}')
kubectl -n network-devops exec deployment/network-monitor-app -- \
  python -c "import socket; socket.create_connection(('$MINIKUBE_HOST_IP',9443),5); print('RESTCONF relay reachable')"
```

The inventory entry must use the value of `$MINIKUBE_HOST_IP` and port `9443`, not
the router's VPN address and not a host DNS name.

### The old web interface is displayed

Rebuild and reload the image, then recreate the web Pods:

```bash
docker build --no-cache -t network-monitor-web:lab04 -f web/Dockerfile .
minikube image load network-monitor-web:lab04 --profile network-devops --overwrite
kubectl -n network-devops rollout restart deployment/network-monitor-web
kubectl -n network-devops rollout status deployment/network-monitor-web
```
