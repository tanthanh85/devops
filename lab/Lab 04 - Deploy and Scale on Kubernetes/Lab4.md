# Lab 4: Deploy, Secure, and Scale the Application on Kubernetes

## Duration

**7 hours**

Lab 3 separated the monitoring application into web, application, and database tiers. In this lab, you will deploy those tiers to Minikube, place all router connection information and login credentials in HashiCorp Vault, and scale the stateless web tier from one Pod to three.

The monitoring application no longer creates, changes, or deletes router inventory. Vault is the authoritative store for each router's name, address, RESTCONF port, username, password, CA reference, and enabled state. The web interface provides a read-only view of that inventory and retrieves CPU and memory data only after the application authenticates to Vault with its Kubernetes workload identity.

## Objectives

- Map the three-tier Compose application to Kubernetes objects.
- Deploy MySQL, Flask, NGINX, and Vault to Minikube.
- Configure Vault KV v2 and Kubernetes authentication.
- Bind a least-privilege policy to the application service account.
- Create complete router records directly in Vault.
- Confirm that the application exposes no router inventory mutation API.
- Display the responding web Pod name and IP address.
- Scale the web Deployment from one replica to three.
- Verify service distribution, persistence, Vault access, and RESTCONF monitoring.

## Runtime architecture

```mermaid
flowchart LR
    B[Browser] --> S[Web Service]
    S --> W1[Web Pod 1]
    S --> W2[Web Pod 2]
    S --> W3[Web Pod 3]
    W1 --> A[Application Service]
    W2 --> A
    W3 --> A
    A --> AP[Flask Pod]
    AP --> D[(MySQL users)]
    AP -->|Kubernetes identity| V[Vault router records]
    AP -->|RESTCONF| R[Authorized router]
```

MySQL retains application users and sessions. Vault owns router data. The application service account can list router names and read router records, but it cannot write or delete them.

## Supplied files

```text
Lab 04 - Deploy and Scale on Kubernetes/
├── Lab4.md
├── app/                       # Vault-backed Flask application
├── web/                       # Read-only inventory UI and Pod identity
├── tests/
├── requirements.txt
├── requirements-dev.txt
├── kubernetes/
│   ├── namespace.yaml
│   ├── configmap.yaml
│   ├── mysql.yaml
│   ├── vault.yaml
│   ├── token-review.yaml
│   ├── app.yaml
│   └── web.yaml
└── scripts/
    ├── create-secrets.sh
    ├── configure-vault.sh
    ├── store-router-record.sh
    ├── deploy.sh
    └── verify.sh
```

## Part 1: Prepare the cumulative branch

```bash
cd ~/network-devops
git status
git pull --ff-only
git switch -c feature/lab04-kubernetes-vault
cp -R "/path/to/Lab 04 - Deploy and Scale on Kubernetes/app" .
cp -R "/path/to/Lab 04 - Deploy and Scale on Kubernetes/web" .
cp -R "/path/to/Lab 04 - Deploy and Scale on Kubernetes/tests" .
cp -R "/path/to/Lab 04 - Deploy and Scale on Kubernetes/kubernetes" .
cp -R "/path/to/Lab 04 - Deploy and Scale on Kubernetes/scripts" .
cp "/path/to/Lab 04 - Deploy and Scale on Kubernetes/requirements"*.txt .
```

## Part 2: Test and build the images

```bash
python -m pip install -r requirements.txt -r requirements-dev.txt
python -m pytest -q
docker build -t network-monitor-app:lab04 -f app/Dockerfile .
docker build -t network-monitor-web:lab04 web
docker run --rm network-monitor-web:lab04 nginx -t
```

The tests prove that inventory comes from Vault, metric collection uses the complete Vault record, and `POST /api/routers` is unavailable.

## Part 3: Start Minikube and load images

```bash
minikube start --profile network-devops
minikube profile network-devops
minikube image load network-monitor-app:lab04 --profile network-devops
minikube image load network-monitor-web:lab04 --profile network-devops
minikube image ls --profile network-devops | grep network-monitor
kubectl get nodes -o wide
```

## Part 4: Create application and Vault bootstrap secrets

```bash
kubectl apply -f kubernetes/namespace.yaml
bash scripts/create-secrets.sh
read -rsp "Vault laboratory bootstrap token: " VAULT_BOOTSTRAP_TOKEN
echo
export VAULT_BOOTSTRAP_TOKEN
kubectl -n network-devops create secret generic vault-bootstrap \
  --from-literal=token="$VAULT_BOOTSTRAP_TOKEN" \
  --dry-run=client -o yaml | kubectl apply -f -
```

The bootstrap token is used only to configure the laboratory Vault server. Do not commit it, print it, or give it to the application. The supplied Vault runs in development mode and is not suitable for production.

## Part 5: Deploy and configure Vault

```bash
kubectl apply -f kubernetes/token-review.yaml
kubectl apply -f kubernetes/vault.yaml
kubectl -n network-devops rollout status deployment/vault --timeout=180s
bash scripts/configure-vault.sh
```

The policy allows:

```hcl
path "secret/metadata/network/routers" {
  capabilities = ["list"]
}
path "secret/data/network/routers/*" {
  capabilities = ["read"]
}
```

It grants no write, update, delete, administrative, or unrelated-secret access.

## Part 6: Add router information to Vault

Choose a short Vault-safe name. Enter every router field on the controlled workstation:

```bash
read -rp "Router name: " ROUTER_NAME
read -rp "Router host or IP: " ROUTER_HOST
read -rp "RESTCONF port [443]: " ROUTER_PORT
ROUTER_PORT=${ROUTER_PORT:-443}
read -rp "Router login username: " ROUTER_USERNAME
read -rsp "Router login password: " ROUTER_PASSWORD
echo
read -rp "CA bundle filename, or leave empty: " ROUTER_CA_BUNDLE
export ROUTER_NAME ROUTER_HOST ROUTER_PORT ROUTER_USERNAME ROUTER_PASSWORD ROUTER_CA_BUNDLE
bash scripts/store-router-record.sh
unset ROUTER_USERNAME ROUTER_PASSWORD
```

The resulting path is `secret/data/network/routers/<router-name>`. Its data contains:

```json
{
  "host": "router.example.net",
  "port": 443,
  "username": "monitoring-user",
  "password": "stored-only-in-vault",
  "ca_bundle_name": "router-ca.pem",
  "enabled": true
}
```

Repeat the procedure for additional instructor-authorized routers. Do not add router records through the monitoring page, application API, MySQL, Kubernetes ConfigMaps, or GitLab variables.

Inspect metadata without displaying secret values:

```bash
kubectl -n network-devops exec deployment/vault -- env \
  VAULT_ADDR=http://127.0.0.1:8200 VAULT_TOKEN="$VAULT_BOOTSTRAP_TOKEN" \
  vault kv metadata get "secret/network/routers/$ROUTER_NAME"
```

## Part 7: Deploy the three application tiers

```bash
kubectl apply -f kubernetes/configmap.yaml
kubectl apply -f kubernetes/mysql.yaml
kubectl -n network-devops rollout status deployment/mysql --timeout=180s
kubectl apply -f kubernetes/app.yaml
kubectl -n network-devops rollout status deployment/network-monitor-app --timeout=180s
kubectl apply -f kubernetes/web.yaml
kubectl -n network-devops rollout status deployment/network-monitor-web --timeout=180s
kubectl -n network-devops get deployment,pod,service,pvc -o wide
```

## Part 8: Open and verify the application

```bash
minikube service network-monitor-web --url --profile network-devops
```

Create the first web administrator if the Lab 3 database is empty, sign in, and select **Refresh inventory**. Confirm that the router appears without its username or password. Collect CPU and memory data.

The upper-right badge displays the web Pod name and Pod IP that answered `/instance`. The application Pod independently authenticates to Vault and reads the selected router record when metrics are requested.

## Part 9: Prove the mutation boundary

After authenticating and saving the session cookie with instructor guidance, confirm that the application refuses inventory creation:

```bash
curl -i -X POST "$WEB_URL/api/routers" \
  -H 'Content-Type: application/json' \
  -d '{"name":"must-not-be-created"}'
```

The expected response is `405 Method Not Allowed`. Router administration belongs to Vault in this lab.

## Part 10: Scale the web tier

```bash
kubectl -n network-devops scale deployment/network-monitor-web --replicas=3
kubectl -n network-devops rollout status deployment/network-monitor-web
kubectl -n network-devops get pods -l app=network-monitor,tier=web -o wide
kubectl -n network-devops get endpointslice \
  -l kubernetes.io/service-name=network-monitor-web
```

Open several tabs or issue repeated new connections:

```bash
WEB_URL=$(minikube service network-monitor-web --url --profile network-devops)
for attempt in $(seq 1 15); do
  curl -s -H 'Connection: close' "$WEB_URL/instance"
done | sort | uniq -c
```

Kubernetes distributes connections among ready endpoints but does not guarantee that each tab reaches a different Pod.

## Part 11: Test failure and recovery

Temporarily change the application Vault role to an unknown value and request metrics. The request should fail without revealing a credential. Restore `network-monitor`, reapply the manifest, and verify recovery.

Then update the router password in Vault and on the authorized router. The next request should use the new value without changing an application image, Deployment, database record, or web configuration.

## Part 12: Commit evidence

```bash
mkdir -p evidence/lab04
kubectl -n network-devops get deployment,pod,service,pvc -o wide > evidence/lab04/resources.txt
kubectl -n network-devops get endpointslice > evidence/lab04/endpoints.txt
git add app web tests requirements*.txt kubernetes scripts evidence/lab04
git diff --staged
git commit -m "Deploy Kubernetes application with Vault inventory"
git push -u origin feature/lab04-kubernetes-vault
```

Evidence must not contain Vault data, tokens, router credentials, Kubernetes Secret values, cookies, or sensitive router output.

## Completion criteria

- The application and web images pass tests and build successfully.
- Vault stores every router connection and authentication field.
- The application uses Kubernetes authentication and a short-lived Vault token.
- The web interface displays read-only Vault inventory without credentials.
- No application route creates, updates, or deletes router records.
- CPU and memory collection succeeds through Vault-backed RESTCONF authentication.
- Three ready web Pods serve the application and expose distinct runtime identities.
- Credential rotation requires no application deployment.
- MySQL is not used as router inventory.

## Cleanup

Retain the cluster for Lab 5. Scale the web tier to one and clear local shell values:

```bash
kubectl -n network-devops scale deployment/network-monitor-web --replicas=1
unset VAULT_BOOTSTRAP_TOKEN ROUTER_NAME ROUTER_HOST ROUTER_PORT ROUTER_CA_BUNDLE
minikube stop --profile network-devops
```

Vault development mode loses its data if the Vault Pod is replaced. Production Vault requires TLS, durable storage, controlled initialization and unsealing, audit logging, backups, and high availability.

## Key takeaways

- Vault can own both connection metadata and credentials behind one policy boundary.
- Workload identity avoids distributing a static Vault token to the application.
- Kubernetes scaling changes runtime capacity without changing router inventory.
- Inventory mutation should occur through the designated authority, not every consuming application.
