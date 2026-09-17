# Lab 3: Implement a Three-Tier Network Monitoring Application

## Duration

**3 hours**

In this standalone lab, you will deploy an NGINX web tier, a Flask application tier, and a persistent MySQL database tier. You will create an administrator, manage an IOS XE router inventory, and monitor router CPU and memory through RESTCONF.

## Objectives

- Deploy the three-tier application with Docker Compose.
- Store application users and router inventory in MySQL.
- Create the first administrator and sign in.
- Add an instructor-authorized IOS XE router.
- Select a router and collect CPU and memory data.
- Verify database persistence.

## Required environment

- An instructor-approved Ubuntu workstation with Docker Engine and Docker Compose.
- Cisco Secure Client connected to the laboratory VPN.
- An instructor-authorized IOS XE router with RESTCONF enabled.
- The complete instructor-provided Lab 3 files.

## Architecture and data flow

```mermaid
flowchart LR
    U["Learner browser"]

    subgraph H["Ubuntu workstation"]
        W["NGINX web container<br/>127.0.0.1:8088"]
        A["Flask application container<br/>host network · port 8000"]
        D[("MySQL database container<br/>internal data network · port 3306")]
    end

    V["Cisco Secure Client VPN"]
    R["IOS XE router<br/>RESTCONF · port 443"]

    U -->|"Open web interface"| W
    W -->|"API requests<br/>host.docker.internal:8000"| A
    A <-->|"SQL<br/>127.0.0.1:3307"| D
    A <-->|"HTTPS RESTCONF"| V
    V <-->|"VPN tunnel"| R
```

1. The browser loads the interface from NGINX on port `8088`.
2. NGINX sends `/api` requests to the Flask application on port `8000`.
3. Flask reads the router inventory and encrypted credentials from MySQL, then collects metrics through the VPN.
4. The browser requests new metrics every 5, 10, or 15 seconds and updates the CPU and memory charts.

## Step 1: Create the Lab 3 repository

Create a blank private GitLab project named `netdevops-lab03-three-tier` and initialize it with a README.

```bash
mkdir -p ~/netdevops-labs
cd ~/netdevops-labs
git clone https://gitlab.com/YOUR-GITLAB-NAMESPACE/netdevops-lab03-three-tier.git
cd netdevops-lab03-three-tier
git switch -c feature/lab03-three-tier
```

Copy only the supplied Lab 3 files into the new repository:

```bash
cp -R "/path/to/Lab 03 - Implement a Three-Tier Application/." \
  ~/netdevops-labs/netdevops-lab03-three-tier/
```

Create the Lab 3 Python environment:

```bash
cd ~/netdevops-labs/netdevops-lab03-three-tier
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt -r requirements-dev.txt
```

## Step 2: Configure `.env`

Create the runtime environment file:

```bash
cp .env.example .env
chmod 600 .env
```

Generate two MySQL passwords and one Flask secret. Copy the three outputs:

```bash
openssl rand -hex 16
openssl rand -hex 16
openssl rand -hex 32
```

Generate the inventory encryption key and copy its output:

```bash
python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'
```

Open `.env`:

```bash
nano .env
```

Replace every `replace-with-...` value:

```text
MYSQL_IMAGE=mysql:8.4
MYSQL_DATABASE=network_monitor
MYSQL_USER=network_app
MYSQL_PASSWORD=replace-with-first-16-byte-hex-value
MYSQL_ROOT_PASSWORD=replace-with-second-16-byte-hex-value
DATABASE_URL=mysql+pymysql://network_app:replace-with-same-MYSQL_PASSWORD-value@127.0.0.1:3307/network_monitor
FLASK_SECRET_KEY=replace-with-32-byte-hex-value
INVENTORY_ENCRYPTION_KEY=replace-with-generated-fernet-key
SESSION_COOKIE_SECURE=false
```

Use the exact `MYSQL_PASSWORD` value inside `DATABASE_URL`. Save with **Ctrl+O**, press **Enter**, and exit with **Ctrl+X**.

Confirm that no placeholders remain:

```bash
grep -n 'replace-with' .env && echo "ERROR: update every placeholder" || echo ".env is ready"
```

Never commit or share `.env`.

## Step 3: Test and build

Confirm that the required files are in the current directory:

```bash
test -f compose.yaml && test -f .env && echo "Lab 3 project files found"
```

Run the application tests and validate Compose:

```bash
python -m pytest -q
docker compose config --quiet
```

Build the web and application images and pull MySQL:

```bash
docker compose build --pull web app
docker compose pull db
```

## Step 4: Start the application

```bash
docker compose up -d
docker compose ps
```

Wait until `db`, `app`, and `web` report `healthy`.

Verify the three service paths:

```bash
docker compose exec app python -c \
  "import socket; socket.create_connection(('127.0.0.1',3307),5); print('MySQL reachable')"
docker compose exec web wget -q -O - http://host.docker.internal:8000/health/ready
curl -fsS http://127.0.0.1:8088/health
```

## Step 5: Create the administrator

Open `http://127.0.0.1:8088`.

1. Enter an administrator username.
2. Enter any non-empty password. A simple password is acceptable for this isolated lab.
3. Select **Create administrator**.
4. Sign in with the new account.

## Step 6: Add a router to inventory

1. Open the **Inventory management** tab.
2. Enter the assigned router name, management address, RESTCONF port, username, and password.
3. Select **Add to inventory**.
4. Confirm that the router appears in **Configured routers**.

Do not add a production router or a router that the instructor has not authorized.

## Step 7: Monitor the router

1. Open the **Monitoring** tab.
2. Select the router from the dropdown list.
3. Select a refresh interval of 5, 10, or 15 seconds.
4. Confirm that CPU utilization, memory utilization, collection time, and router name update automatically.
5. Confirm that the separate CPU and memory charts display the last 30 samples.

Use **Collect now** when you want an additional sample immediately.

## Step 8: Verify persistence

Stop and recreate the containers without deleting the database volume:

```bash
docker compose down
docker compose up -d
docker compose ps
```

Sign in again and confirm that the administrator and router inventory still exist.

## Step 9: Commit and push

```bash
git status --ignored
git add web app tests compose.yaml requirements.txt requirements-dev.txt \
  .env.example .dockerignore .gitignore
git diff --staged
git commit -m "Deploy three-tier network monitoring application"
git push -u origin feature/lab03-three-tier
```

Confirm that `.env` is not included in the commit.

## Completion criteria

- All three containers report `healthy`.
- The administrator can sign in.
- The inventory page stores an authorized router without displaying its password.
- The monitoring dropdown lists the router.
- CPU and memory values are collected through the VPN.
- The CPU and memory charts display multiple automatically collected samples.
- The administrator and inventory survive container recreation.
- `.env` is not committed.

## Cleanup

Stop the services without deleting the database:

```bash
docker compose stop
```

## Troubleshooting

Run all commands from the repository containing `compose.yaml` and `.env`:

```bash
cd ~/netdevops-labs/netdevops-lab03-three-tier
ls -l compose.yaml .env
```

### A container is unhealthy or restarting

```bash
docker compose ps
docker compose logs --no-color --tail=200 db app web
```

### The web image was built before the NGINX fix

```bash
docker compose rm -sf web
docker image rm network-monitor-web:lab03 2>/dev/null || true
docker compose build --no-cache web
docker compose up -d --force-recreate web
```

### MySQL passwords were changed after the first start

MySQL applies the initial passwords only when it creates a new data volume. The following command permanently deletes the Lab 3 administrator and router inventory:

```bash
docker compose down --volumes
docker compose up -d
```

### Compose searches for `.env` in the wrong directory

```bash
env | grep '^COMPOSE_'
unset COMPOSE_FILE COMPOSE_PROJECT_NAME
docker compose up -d
```

### RESTCONF collection times out

Confirm that Cisco Secure Client is connected, then test the router port from the host-networked application container:

```bash
docker compose exec app python -c \
  "import socket; socket.create_connection(('ROUTER_IP',443),5); print('Router reachable')"
```

Replace `ROUTER_IP` with the assigned router address. If the connection fails, verify the VPN, router address, RESTCONF port, and instructor authorization.
