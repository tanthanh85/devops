# Lab 5: Build, Test, and Deploy with GitLab CI/CD

## Duration

**2 hours**

In this standalone lab, you will deliver the same three-tier application used in Lab 4 through GitLab CI/CD. Learners work on a feature branch, open a merge request, obtain approval, and merge into `main`. Only the resulting push to `main` creates a pipeline.

The pipeline tests the application, builds both application images directly in Minikube's container runtime, deploys MySQL, Flask, and NGINX, and verifies the running Services. Learners do not run deployment commands manually.

## Objectives

- Configure a trusted local GitLab shell runner for the course workstation.
- Protect `main` from direct pushes.
- Require one merge-request approval before merge.
- Store runtime secrets as protected GitLab CI/CD variables.
- Restrict pipeline creation to pushes on the default branch.
- Test and build the Lab 4 application in CI.
- Deploy all three tiers to Minikube from CI.
- Verify the deployment and Pod identities from CI.

## Delivery flow

```mermaid
flowchart LR
    F["Feature branch"] --> P["Push to GitLab"]
    P --> M["Merge request to main"]
    M --> R["Instructor review"]
    R --> A["Approval"]
    A --> G["Merge to main"]
    G --> T["Test"]
    T --> B["Build images"]
    B --> D["Deploy to Minikube"]
    D --> V["Verify Kubernetes rollout"]
    V --> W["Post-deployment web test"]
```

Feature-branch pushes and merge-request events do not create pipelines in this lab. The merge commit pushed to `main` starts the pipeline.

## Required environment

- The Lab 1 Ubuntu workstation with Docker, Minikube, `kubectl`, Git, Python, and GitLab Runner.
- A private GitLab project where an instructor or another authorized user can approve merge requests.
- The complete instructor-provided Lab 5 files.
- A running Minikube profile named `network-devops`.
- A local C8000v or the Lab 4 RESTCONF VPN relay when router monitoring is tested.

The shell runner executes trusted repository commands directly on the workstation. Use it only for this private course project.

## Supplied files

```text
Lab 05 - Build Test and Deploy with GitLab CI-CD/
├── .gitlab-ci.yml
├── .env.example
├── Lab5.md
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

## Step 1: Create the Lab 5 repository

Create a blank private GitLab project named `netdevops-lab05-gitlab-cicd` and initialize it with a README.

Clone the project and create the working branch:

```bash
mkdir -p ~/netdevops-labs
cd ~/netdevops-labs
git clone https://gitlab.com/YOUR-GITLAB-NAMESPACE/netdevops-lab05-gitlab-cicd.git
cd netdevops-lab05-gitlab-cicd
git switch -c feature/lab05-cicd
```

Copy only the supplied Lab 5 files into this repository:

```bash
cp -R "/path/to/Lab 05 - Build Test and Deploy with GitLab CI-CD/." .
git status
```

## Step 2: Start Minikube

```bash
minikube start --profile network-devops --driver=docker
minikube profile network-devops
minikube status --profile network-devops
```

The CI runner uses this profile. Do not deploy the application manually.

## Step 3: Create and register the project runner

In GitLab:

1. Open **Settings > CI/CD > Runners**.
2. Select **Create project runner**.
3. Select Linux.
4. Add the tags `lab5` and `minikube`.
5. Disable **Run untagged jobs**.
6. Create the runner and copy its authentication token beginning with `glrt-`.

Register a dedicated user-mode configuration on Ubuntu:

```bash
mkdir -p ~/.gitlab-runner-lab05
gitlab-runner --config ~/.gitlab-runner-lab05/config.toml register
```

Enter:

- GitLab URL: `https://gitlab.com`
- Token: the project runner authentication token
- Description: `lab05-minikube-shell-runner`
- Tags: `lab5,minikube`
- Executor: `shell`

Verify the registration:

```bash
gitlab-runner --config ~/.gitlab-runner-lab05/config.toml list
gitlab-runner --config ~/.gitlab-runner-lab05/config.toml verify
```

In a separate terminal, start the runner as the current Ubuntu user and keep it running during the lab:

```bash
gitlab-runner --config ~/.gitlab-runner-lab05/config.toml run
```

Running it as the current user gives the jobs access to that user's Docker, Minikube, and Kubernetes configuration.

## Step 4: Protect `main` and require approval

In GitLab, configure the default branch before pushing the feature branch:

1. Open **Settings > Repository > Branch rules**.
2. Protect `main`.
3. Set **Allowed to push and merge** to **No one**.
4. Allow only the instructor or designated maintainer role to merge.
5. Disable force pushes.
6. Under the project's merge checks, leave **Pipelines must succeed** disabled because this lab intentionally creates no merge-request pipeline. The approved merge triggers the validation pipeline on `main` afterward.

Configure merge-request approval:

1. Open **Settings > Merge requests > Merge request approvals**.
2. Create an approval rule for the `main` branch.
3. Require one approval.
4. Add the instructor or designated reviewer as an approver.
5. Prevent authors from approving their own merge requests when that option is available.

These settings prevent learners from bypassing review with a direct push to `main`.

## Step 5: Create protected CI/CD variables

Generate the values on Ubuntu:

```bash
openssl rand -hex 16
openssl rand -hex 16
openssl rand -hex 32
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

In **Settings > CI/CD > Variables**, create these project variables:

| Key | Value | Settings |
|---|---|---|
| `MYSQL_PASSWORD` | First 16-byte hexadecimal value | Protected and masked |
| `MYSQL_ROOT_PASSWORD` | Second 16-byte hexadecimal value | Protected and masked |
| `FLASK_SECRET_KEY` | 32-byte hexadecimal value | Protected and masked |
| `INVENTORY_ENCRYPTION_KEY` | Generated Fernet key | Protected and masked |

Use the environment scope `course/minikube` when the GitLab interface provides it. Keep `main` protected so these variables are available to its pipeline.

Do not create `.env`, Kubernetes Secrets, or application credentials manually in this lab. The pipeline creates the Kubernetes Secret from the protected variables.

## Step 6: Review the main-only pipeline

Open `.gitlab-ci.yml` and identify the global workflow rule:

```yaml
workflow:
  rules:
    - if: '$CI_PIPELINE_SOURCE == "push" && $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'
    - when: never
```

The pipeline contains five automatic stages:

1. `unit-test` installs dependencies and runs `pytest`.
2. `build-images` builds commit-specific Flask and NGINX images directly in Minikube's container runtime.
3. `deploy-minikube` creates the runtime Secret and deploys MySQL, Flask, and NGINX.
4. `verify-deployment` checks Pod readiness and Kubernetes Service endpoints.
5. `post-deployment-web-test` accesses the web Service through a temporary port-forward and verifies the page, health endpoint, setup API, and Web/App Pod identity endpoints.

The optional `cleanup-minikube` job is manual and appears only in the successful `main` pipeline.

## Step 7: Commit and push the feature branch

```bash
git status
git add .
git diff --staged
git commit -m "Add GitLab pipeline for Minikube deployment"
git push -u origin feature/lab05-cicd
```

Open **Build > Pipelines**. Confirm that the feature-branch push did not create a pipeline.

## Step 8: Create the merge request

In GitLab:

1. Open **Code > Merge requests**.
2. Create a merge request from `feature/lab05-cicd` into `main`.
3. Title it **Deploy the three-tier application with GitLab CI/CD**.
4. Assign the instructor or designated reviewer.
5. Submit the merge request.

Confirm that creating the merge request does not create a pipeline. Review the changes in the **Changes** tab.

## Step 9: Review and approve

The designated reviewer must:

1. Review `.gitlab-ci.yml`, the application changes, and Kubernetes manifests.
2. Confirm that no plaintext secret or `.env` file is included.
3. Select **Approve**.

The learner must not approve their own merge request.

## Step 10: Merge into `main`

After approval, select **Merge**. Do not bypass the merge request and do not push directly to `main`.

The merge creates a push on `main`, which starts the only pipeline for this workflow.

## Step 11: Follow the pipeline

Open **Build > Pipelines**, select the `main` pipeline, and follow each job in order:

```text
unit-test → build-images → deploy-minikube → verify-deployment → post-deployment-web-test
```

Do not run `docker build`, `kubectl apply`, `kubectl set image`, or `kubectl create secret` manually. Correct a failure on a new feature branch and repeat the merge-request process.

## Step 12: Verify the deployed application

After the pipeline succeeds, open the web Service:

```bash
minikube service network-monitor-web \
  --namespace network-devops-lab05 \
  --profile network-devops
```

1. Create the administrator and sign in.
2. Add the instructor-provided router using the Lab 4 connection method.
3. Confirm automatic CPU and memory monitoring.
4. Confirm that the interface displays the responding Web Pod and App Pod names.

## Step 13: Make a follow-up change

Create another feature branch from the updated default branch:

```bash
git switch main
git pull --ff-only
git switch -c feature/lab05-follow-up
```

Make an instructor-approved documentation or interface change, then commit and push it. Repeat the merge request, review, approval, and merge workflow. Confirm that a new `main` pipeline builds images tagged with the new commit ID and updates the Deployments.

## Completion criteria

- The Lab 4 application source, tests, and Kubernetes manifests are present.
- Direct pushes to `main` are blocked.
- A merge request requires an authorized approval.
- Feature-branch pushes and merge-request events do not create pipelines.
- Merging the approved request creates a pipeline on `main`.
- Unit tests pass before images are built.
- CI builds commit-specific application and web images.
- CI deploys MySQL, Flask, and NGINX to `network-devops-lab05`.
- CI verifies Kubernetes readiness and Service endpoints.
- The post-deployment stage confirms that the web page and application API are accessible.
- The application works without a manual deployment command.

## Cleanup

When the lab evidence has been collected, open the successful `main` pipeline and start the manual `cleanup-minikube` job. It deletes only the `network-devops-lab05` namespace, including its MySQL persistent volume claim.

Stop the user-mode runner with `Ctrl+C` in its terminal.

## Troubleshooting

### No pipeline appears after a feature-branch push

This is expected. Only a push to the default branch creates a pipeline.

### The merge button is disabled

Confirm that the designated reviewer approved the merge request and that the learner has not attempted a direct push to `main`.

### Jobs remain pending

Confirm that the local runner terminal is still running, that GitLab reports the project runner online, and that its tags are `lab5` and `minikube`:

```bash
gitlab-runner --config ~/.gitlab-runner-lab05/config.toml verify
```

### The build job cannot access Docker or Minikube

Confirm that the runner was started as the same Ubuntu user who can run these commands:

```bash
docker version
minikube status --profile network-devops
kubectl get nodes
```

### Deployment fails after changing MySQL variables

The persistent MySQL volume was initialized with the original credentials. Use stable protected variables for the entire lab. If the instructor authorizes a full reset, run the manual cleanup job, correct the variables, and merge a new feature branch so the pipeline creates a fresh database.
