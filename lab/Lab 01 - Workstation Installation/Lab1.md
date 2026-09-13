# Lab 1: Workstation Installation

## Duration

**4 hours**

This lab prepares the workstation used throughout the course. You will install command-line development tools locally, create the course repository on GitLab.com, and deploy the selected supporting platforms as containers. Later labs reuse the same GitLab.com repository, Python environment, Docker Engine, Kubernetes cluster, local runner, secrets service, and monitoring platform.

The instructions target a dedicated Ubuntu LTS workstation. Complete the lab only on an instructor-approved system. Package names and vendor installation procedures can change; use the course versions supplied by the instructor and compare the commands with the official documentation before using them outside the lab.

## Objectives

- Install and verify Python, pip, Git, Ansible, Visual Studio Code, Docker Engine, and Docker Compose.
- Create and activate an isolated Python virtual environment.
- Install and verify `kubectl` and Minikube.
- Create and secure a GitLab.com account and course project.
- Start a local GitLab Runner and register it with the GitLab.com project.
- Start an Elastic Stack laboratory environment for log collection and visualization.
- Start HashiCorp Vault in development mode for later secrets exercises.
- Record installed versions and demonstrate safe platform start, stop, and cleanup operations.

## Workstation architecture

```mermaid
flowchart LR
    U["Ubuntu workstation"] --> D["Docker Engine and Compose"]
    U --> P["Python virtual environment<br/>Ansible and application tools"]
    U --> C["Visual Studio Code<br/>Course extensions"]
    U --> K["kubectl"]
    D --> M["Minikube<br/>Docker driver"]
    U --> G["GitLab.com repository"]
    D --> GR["Local GitLab Runner"]
    GR --> G
    D --> E["Elasticsearch, Logstash, Kibana"]
    D --> V["Vault development server"]
```

## Required environment

Recommended minimum for running selected platforms concurrently:

| Resource | Minimum | Recommended |
|---|---:|---:|
| CPU | 6 logical CPUs | 8–12 logical CPUs |
| Memory | 16 GB | 24 GB or more |
| Free disk | 60 GB | 100 GB or more |
| Virtualization | Enabled | Enabled with nested virtualization if the workstation is a VM |

The Elastic Stack and Minikube are resource-intensive. Do not keep every platform running when it is not required. Never expose these lab services to an untrusted network.

Suggested local ports:

| Service | URL or port |
|---|---|
| GitLab.com | `https://gitlab.com` |
| Vault | `http://127.0.0.1:8200` |
| Elasticsearch | `http://127.0.0.1:9200` |
| Kibana | `http://127.0.0.1:5601` |
| Logstash input for later labs | `127.0.0.1:5044` |

## Part 1: Inspect and update the workstation

```bash
whoami
hostnamectl
cat /etc/os-release
uname -m
free -h
df -h /
egrep -c '(vmx|svm)' /proc/cpuinfo
sudo apt update
sudo apt upgrade -y
sudo apt install -y git curl wget jq ca-certificates gnupg lsb-release \
  openssh-client make unzip apt-transport-https
```

The virtualization check should return a value greater than zero. If it returns zero on a virtual machine, ask the instructor whether nested virtualization is enabled. The Minikube Docker driver does not require a second hypervisor, but sufficient CPU and memory are still required.

Configure Git identity:

```bash
git config --global user.name "Your Name"
git config --global user.email "your-email@example.com"
git config --global init.defaultBranch main
git --version
```

## Part 2: Install Python, pip, and the virtual environment

```bash
sudo apt install -y python3 python3-pip python3-venv
python3 --version
python3 -m pip --version
mkdir -p ~/network-devops
cd ~/network-devops
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
which python
python --version
```

The path printed by `which python` must end in `network-devops/.venv/bin/python`. Install the Python tools used in the first course stages:

```bash
python -m pip install ansible ansible-lint requests flask pytest pyyaml
python -m pip check
ansible --version
ansible-lint --version
```

Create a simple verification file:

```bash
python - <<'PY'
import flask, requests, yaml
print("Python imports passed")
PY
```

Use `deactivate` to leave the environment and `source ~/network-devops/.venv/bin/activate` to return to it. Do not install course libraries into the system Python environment with `sudo pip`.

## Part 3: Install Visual Studio Code

Install the official Visual Studio Code Snap package on the Ubuntu workstation:

```bash
sudo snap install --classic code
code --version
```

If Snap is unavailable or prohibited by the instructor, use Microsoft's current Debian/Ubuntu package procedure instead of adding an unofficial repository. The `code` command must be available in the learner's terminal before continuing.

Install the extensions used during the course:

```bash
code --install-extension ms-python.python
code --install-extension redhat.vscode-yaml
code --install-extension ms-azuretools.vscode-docker
code --install-extension ms-kubernetes-tools.vscode-kubernetes-tools
code --install-extension GitLab.gitlab-workflow
code --install-extension hashicorp.terraform
code --list-extensions --show-versions
```

Open the cumulative course directory rather than an individual file:

```bash
cd ~/network-devops
code .
```

In VS Code, select the interpreter from `~/network-devops/.venv/bin/python`. Open a terminal inside the editor and verify that Git sees the same repository:

```bash
git status
python --version
```

Extensions execute with the learner's permissions and may access workspace content. Install only the extensions listed by the instructor, review their publishers, and do not paste tokens or passwords into extension settings.

## Part 4: Install Docker Engine and Docker Compose

Remove conflicting unofficial packages if they are present, then use Docker's official Ubuntu repository:

```bash
for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do
  sudo apt-get remove -y "$pkg" 2>/dev/null || true
done
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
```

```bash
. /etc/os-release
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu ${UBUNTU_CODENAME:-$VERSION_CODENAME} stable" |
  sudo tee /etc/apt/sources.list.d/docker.list >/dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io \
  docker-buildx-plugin docker-compose-plugin
sudo systemctl enable --now docker
sudo usermod -aG docker "$USER"
```

Sign out and back in so that group membership is refreshed. Then verify:

```bash
docker version
docker compose version
docker run --rm hello-world
```

Membership in the `docker` group grants control of the Docker daemon and is effectively privileged access to the workstation. Use it only on the dedicated lab host.

## Part 5: Install `kubectl`

Install the Kubernetes client from the official package repository. The repository minor version must match the instructor-approved Kubernetes release:

```bash
KUBERNETES_MINOR=v1.35
curl -fsSL "https://pkgs.k8s.io/core:/stable:/${KUBERNETES_MINOR}/deb/Release.key" |
  sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
echo "deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/${KUBERNETES_MINOR}/deb/ /" |
  sudo tee /etc/apt/sources.list.d/kubernetes.list >/dev/null
sudo apt update
sudo apt install -y kubectl
kubectl version --client
```

If the course uses another minor release, replace `v1.35` before adding the repository. Do not assume the example remains current in a later course delivery.

## Part 6: Install and start Minikube

Download the binary that matches the workstation architecture:

```bash
case "$(uname -m)" in
  x86_64) MINIKUBE_ARCH=amd64 ;;
  aarch64|arm64) MINIKUBE_ARCH=arm64 ;;
  *) echo "Unsupported architecture"; exit 1 ;;
esac
curl -LO "https://storage.googleapis.com/minikube/releases/latest/minikube-linux-${MINIKUBE_ARCH}"
sudo install "minikube-linux-${MINIKUBE_ARCH}" /usr/local/bin/minikube
rm "minikube-linux-${MINIKUBE_ARCH}"
minikube version
```

Create the course cluster with the Docker driver:

```bash
minikube start --driver=docker --cpus=4 --memory=8192 --disk-size=30g \
  --profile network-devops
minikube profile network-devops
kubectl cluster-info
kubectl get nodes -o wide
kubectl create namespace network-devops
kubectl get namespaces
```

Lifecycle commands:

```bash
minikube stop --profile network-devops
minikube start --profile network-devops
minikube status --profile network-devops
```

`minikube delete --profile network-devops` permanently deletes the cluster. Use it only when instructed.

## Part 7: Create and secure the GitLab.com account

Open [GitLab.com](https://gitlab.com/users/sign_up) and create an individual account, or sign in with the instructor-approved account. Use an address that you can verify during the lab. Do not create a self-managed GitLab server on the workstation.

After signing in:

1. Verify the account email address.
2. Open **Edit profile > Access > Password and authentication** and enable two-factor authentication.
3. Store recovery codes in the instructor-approved password manager.
4. Review active sessions and sign out any session you do not recognize.
5. Do not create a personal access token unless a later exercise explicitly requires one.

Create the cumulative project using the current GitLab interface:

1. Select **Create new > New project/repository**.
2. Select **Create blank project**.
3. Enter `network-devops` as the project name and slug.
4. Select **Private** unless the instructor requires another visibility level.
5. Select **Initialize repository with a README**.
6. Select **Create project**.

Clone the project using the HTTPS URL displayed by GitLab:

```bash
cd ~
git clone https://gitlab.com/YOUR-GITLAB-NAMESPACE/network-devops.git
cd network-devops
git remote -v
git status
```

Authenticate with the browser or credential-manager flow offered by Git. Do not place an account password or access token in the clone URL, shell history, or repository. Create a first branch and publish it:

```bash
git switch -c setup/lab01-workstation
mkdir -p evidence
cp "/path/to/Lab 01 - Workstation Installation/verify_workstation.py" .
cp "/path/to/Lab 01 - Workstation Installation/requirements.txt" .
git add verify_workstation.py requirements.txt
git commit -m "Add workstation verification"
git push -u origin setup/lab01-workstation
```

Open the project on GitLab.com and confirm the branch is visible. A later module adds merge-request and pipeline controls; this checkpoint proves account, repository, authentication, and push access.

## Part 8: Install and register the local GitLab Runner

GitLab.com hosts the repository and pipeline control plane. The learner workstation runs only a project runner. Copy the supplied runner Compose project:

```bash
mkdir -p ~/network-devops/platform
cp -R "/path/to/Lab 01 - Workstation Installation/platform/." \
  ~/network-devops/platform/
cd ~/network-devops/platform/gitlab-runner
cp .env.example .env
# Confirm the instructor-approved image tag before continuing.
docker compose config --quiet
docker compose pull
docker compose up -d
docker compose ps
docker exec course-gitlab-runner gitlab-runner --version
```

In the GitLab.com `network-devops` project:

1. Open **Settings > CI/CD**.
2. Expand **Runners**.
3. Select **Create project runner**.
4. Select Linux and add the tags `docker,validation`.
5. Allow untagged jobs only if directed by the instructor.
6. Create the runner and copy its authentication token beginning with `glrt-`.

Register the containerized runner:

```bash
docker exec -it course-gitlab-runner gitlab-runner register
```

Use these answers:

- GitLab URL: `https://gitlab.com`
- Token: the project runner authentication token
- Description: `course-docker-runner`
- Executor: `docker`
- Default image: `python:3.12-slim`

Verify the registration and then return to the GitLab.com runner page:

```bash
docker exec course-gitlab-runner gitlab-runner list
docker exec course-gitlab-runner gitlab-runner verify
```

The runner should appear online. The authentication token is stored in the runner configuration volume; do not copy it into Git or evidence files. Mounting the Docker socket gives jobs broad control of the workstation, so this runner must remain locked to the learner's private course project and must not execute untrusted project code.

## Part 9: Install the Elastic Stack laboratory services

Elastic requires Elasticsearch, Logstash, and Kibana to use the same version. Use the supplied pinned Compose file and confirm its version with the instructor; do not improvise mixed versions.

```bash
cd ~/network-devops/platform/elastic
cp .env.example .env
# Replace STACK_VERSION with the instructor-approved version.
docker compose config --quiet
docker compose pull
docker compose up -d
```

The supplied Compose project includes Elasticsearch, Logstash, and Kibana at one version. The installation is complete only when all three services are present and healthy:

```bash
docker compose ps
curl -s http://127.0.0.1:9200 | jq
docker compose ps --services | grep -E 'elasticsearch|logstash|kibana'
```

Open `http://127.0.0.1:5601`. Do not combine a Logstash image from a different stack version. A production Elastic deployment requires TLS, authentication, durable storage, capacity planning, backup, and lifecycle policy; the quickstart is not a production design.

Stop it when verification is complete:

```bash
docker compose stop
```

## Part 10: Install HashiCorp Vault for laboratory use

Use the supplied Compose definition to start Vault in development mode bound to the workstation loopback address:

```bash
cd ~/network-devops/platform/vault
cp .env.example .env
# Replace VAULT_VERSION with the instructor-approved version.
docker compose up -d
export VAULT_ADDR=http://127.0.0.1:8200
curl -s "$VAULT_ADDR/v1/sys/health" | jq
```

The development server is initialized, unsealed, in-memory, and deliberately insecure. Its root token grants complete access, and its data disappears when the container is removed. Never use this configuration or token outside the lab.

Stop and restart it without deleting the container:

```bash
docker stop course-vault
docker start course-vault
```

## Part 11: Capture the workstation baseline

```bash
mkdir -p ~/network-devops/evidence
{
  date -Is
  python3 --version
  code --version | head -1
  git --version
  ansible --version | head -1
  docker --version
  docker compose version
  kubectl version --client
  minikube version
  docker exec course-gitlab-runner gitlab-runner --version | head -1
} | tee ~/network-devops/evidence/lab01-versions.txt
docker ps -a --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}' \
  | tee ~/network-devops/evidence/lab01-containers.txt
```

Review the evidence files before committing them. They must contain versions and state only—never passwords, runner tokens, Vault tokens, sandbox credentials, or application secrets.

## Platform lifecycle summary

| Platform | Start | Stop without deleting data |
|---|---|---|
| GitLab.com | Browser-based service; no local lifecycle | Sign out when required |
| Runner | `docker compose up -d` in `platform/gitlab-runner` | `docker compose stop` |
| Minikube | `minikube start -p network-devops` | `minikube stop -p network-devops` |
| Elastic | `docker compose up -d` in its directory | `docker compose stop` |
| Vault | `docker compose up -d` in `platform/vault` | `docker compose stop` |

## Completion criteria

- Python and pip run successfully inside the project virtual environment.
- Ansible reports its executable, Python, and collection paths.
- Visual Studio Code opens the course directory, uses the project interpreter, and contains the required extensions.
- Docker Engine and Docker Compose pass their verification commands.
- `kubectl` reaches the `network-devops` Minikube profile.
- The GitLab.com account is verified, protected with two-factor authentication, and contains the `network-devops` project.
- The project runner appears online and passes `gitlab-runner verify`.
- Elasticsearch, Logstash, and Kibana start, and Elasticsearch answers its local health request.
- Vault's health endpoint responds, and the learner can explain why development mode is unsafe.
- Version evidence contains no secret values.

## Cleanup

For normal course continuation, stop unused local platforms but retain their containers and volumes. Do not delete the GitLab.com project or application data.

```bash
docker stop course-vault course-gitlab-runner 2>/dev/null || true
minikube stop --profile network-devops
docker system df
```

Do not run broad pruning commands. They can remove images, volumes, or caches required by later labs.

## Further references

- [Python virtual environments](https://docs.python.org/3/library/venv.html)
- [Visual Studio Code on Linux](https://code.visualstudio.com/docs/setup/linux)
- [Visual Studio Code command line](https://code.visualstudio.com/docs/configure/command-line)
- [Docker Engine on Ubuntu](https://docs.docker.com/engine/install/ubuntu/)
- [Install kubectl on Linux](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/)
- [Minikube start](https://minikube.sigs.k8s.io/docs/start/)
- [Create a GitLab project](https://docs.gitlab.com/user/project/)
- [GitLab Runner in Docker](https://docs.gitlab.com/runner/install/docker/)
- [Elastic local development installation](https://www.elastic.co/docs/deploy-manage/deploy/self-managed/local-development-installation-quickstart)
- [Vault developer quickstart](https://developer.hashicorp.com/vault/docs/get-started/developer-qs)

## Key takeaways

- Small development tools run locally; larger course platforms use controlled containers and persistent volumes.
- Version capture makes the learning environment reproducible and supportable.
- Stopping a service and deleting its state are different lifecycle operations.
- GitLab Runner, Docker socket access, and Vault root tokens are privileged trust boundaries.
- Local-development configurations are suitable for learning, not production deployment.
