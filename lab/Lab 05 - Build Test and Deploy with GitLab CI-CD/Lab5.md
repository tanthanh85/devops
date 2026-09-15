# Lab 5: Build, Test, and Deploy with GitLab CI/CD

## Duration

**6 hours**

Lab 4 proved that the monitoring application can run and scale on Minikube. Those operations were still coordinated from a terminal. In this lab, you will express the same checks and deployment controls as a GitLab CI/CD pipeline executed by the private Docker runner prepared in Lab 1.

The pipeline reuses the existing `network-monitor-web:lab04`, `network-monitor-app:lab04`, and `mysql:8.4` images. It builds one new image, `network-monitor-e2e`, whose only purpose is to test the deployed application through its web interface. The test signs in with a dedicated account, collects CPU and memory observations from an authorized inventory target, and checks the displayed values and chart.

## Objectives

- Map build, unit-test, deployment, and acceptance-test responsibilities to GitLab jobs.
- Configure a private Docker runner to reach the learner's Minikube API safely.
- Protect the kubeconfig and test credentials as GitLab CI/CD variables.
- Reuse the application images already validated in Lab 4.
- Build a dedicated browser-test image.
- Deploy version-controlled Kubernetes manifests through a protected job.
- Provision a non-administrator test account without committing its password.
- Test the application from the user's point of view.
- Explain pipeline ordering, environments, job dependencies, and failure behavior.

## Delivery flow

```mermaid
flowchart LR
    C[Commit] --> U[Unit tests]
    U --> I[Build test image]
    I --> D[Deploy reused images]
    D --> A[Browser acceptance test]
    A --> E[Pipeline result]
```

The arrows represent pipeline gates. A failed job stops later stages by default. The deployment job therefore cannot run when source tests fail, and the acceptance test cannot run until the Kubernetes rollout becomes ready.

## Required state

- Labs 1 through 4 completed in the same `network-devops` repository.
- Private GitLab.com project created in Lab 2.
- Local GitLab Runner installed but not yet registered.
- Minikube profile `network-devops` running on the runner host.
- Existing images available to Minikube:
  - `network-monitor-app:lab04`
  - `network-monitor-web:lab04`
  - `mysql:8.4`
- Lab 4 namespace, Vault records, application Secret, administrator, and authorized router inventory retained.
- The selected router must be reachable from Minikube and return RESTCONF CPU and memory data.

Do not use a production cluster, production credentials, or an unrestricted shared runner. The local runner controls the Docker daemon and receives a Kubernetes credential capable of changing the course namespace.

## Supplied Lab 5 structure

```text
Lab 05 - Build Test and Deploy with GitLab CI-CD/
├── Lab5.md
├── .gitlab-ci.yml
├── ci/
│   └── e2e/
│       ├── Dockerfile
│       ├── package.json
│       └── tests/
│           └── monitoring.spec.js
├── kubernetes/
│   └── test-user-job.yaml
└── scripts/
    └── provision-test-user.sh
```

## Part 1: Prepare the feature branch

Add the supplied CI/CD files to the application repository without replacing the working Lab 4 runtime files.

```bash
cd ~/network-devops
git status
git pull --ff-only
git switch -c feature/lab05-gitlab-pipeline
mkdir -p ci/e2e/tests kubernetes scripts
cp "/path/to/Lab 05 - Build Test and Deploy with GitLab CI-CD/.gitlab-ci.yml" .
cp -R "/path/to/Lab 05 - Build Test and Deploy with GitLab CI-CD/ci/." ci/
cp -R "/path/to/Lab 05 - Build Test and Deploy with GitLab CI-CD/kubernetes/." kubernetes/
cp -R "/path/to/Lab 05 - Build Test and Deploy with GitLab CI-CD/scripts/." scripts/
```

The repository must already contain the Lab 3 application source and tests and the Lab 4 runtime manifests. Resolve any path differences before creating the pipeline.

## Part 2: Register and prepare the Docker runner

In the GitLab.com `network-devops` project:

1. Open **Settings > CI/CD** and expand **Runners**.
2. Select **Create project runner**.
3. Select Linux and add the tags `docker,validation`.
4. Leave **Run untagged jobs** disabled.
5. Create the runner and copy its authentication token beginning with `glrt-`.

Start and register the runner container installed in Lab 1:

```bash
docker start course-gitlab-runner
docker exec -it course-gitlab-runner gitlab-runner register
```

Enter the following values when prompted:

- GitLab URL: `https://gitlab.com`
- Token: the project runner authentication token
- Description: `course-docker-runner`
- Executor: `docker`
- Default image: `python:3.12-slim`

Confirm that registration succeeded and that GitLab.com reports the runner as online:

```bash
docker exec course-gitlab-runner gitlab-runner list
docker exec course-gitlab-runner gitlab-runner verify
```

Do not store the runner authentication token in the project or include it in screenshots.

The Docker runner executes each job in an isolated container. Pipeline jobs need two controlled capabilities:

1. The image-build job requires the host Docker socket.
2. Kubernetes jobs require a flattened kubeconfig supplied as a protected file variable.

Confirm the runner configuration contains the Docker socket and uses locally built images when present:

```toml
[[runners]]
  executor = "docker"
  [runners.docker]
    image = "python:3.12-slim"
    privileged = false
    pull_policy = "if-not-present"
    volumes = ["/cache", "/var/run/docker.sock:/var/run/docker.sock"]
```

The exact `config.toml` is stored in the runner's Docker volume. Inspect it without printing the authentication token:

```bash
docker exec course-gitlab-runner sh -c \
  'grep -E "executor|image|privileged|pull_policy|volumes" /etc/gitlab-runner/config.toml'
docker restart course-gitlab-runner
docker exec course-gitlab-runner gitlab-runner verify
```

Do not enable privileged mode for this lab. Docker-socket access is already highly privileged and is acceptable only on the dedicated course workstation.

## Part 3: Create a portable kubeconfig

The default Minikube kubeconfig refers to certificate files on the workstation. A CI job cannot read those paths. Flatten the selected context so the certificate data is embedded:

```bash
mkdir -p ~/course-platform
kubectl config view --minify --flatten --raw > ~/course-platform/minikube-ci.kubeconfig
KUBECONFIG=~/course-platform/minikube-ci.kubeconfig kubectl get nodes
```

This file contains credentials. Upload it to GitLab in the next part, then remove it immediately. Never add it to Git or pipeline artifacts.

## Part 4: Configure protected GitLab variables

In **Settings > CI/CD > Variables**, create these variables:

| Variable | Type | Protection | Purpose |
|---|---|---|---|
| `KUBE_CONFIG` | File | Protected | Flattened Minikube kubeconfig |
| `E2E_USERNAME` | Variable | Protected and masked | Dedicated test username, such as `ci-monitor` |
| `E2E_PASSWORD` | Variable | Protected and masked | Unique test password of at least 12 characters |

Use environment scope `course/minikube` if available. Do not expose either credential in command output. After saving `KUBE_CONFIG`, delete the local copy:

```bash
rm ~/course-platform/minikube-ci.kubeconfig
git status --ignored
```

Protected variables are available only to pipelines on protected branches or tags. Ask the instructor to protect `main` and allow the learner's role to merge before running the deployment pipeline.

## Part 5: Review the pipeline stages

The supplied `.gitlab-ci.yml` defines four stages:

| Stage | Job | Result |
|---|---|---|
| `verify` | `unit-test` | Application source tests pass |
| `package-test` | `build-e2e-image` | Browser-test image exists on the runner host |
| `deploy` | `deploy-minikube` | Existing application images are deployed and ready |
| `acceptance` | `browser-acceptance` | Authenticated monitoring works through the web page |

The runtime application images are not rebuilt in this lab. The deployment job inspects their presence inside Minikube before applying the manifests. If an image is missing, the job fails and identifies the prerequisite that must be restored.

## Part 6: Understand the browser-test image

The test image contains Chromium, Playwright, `kubectl`, and the test specification. It contains no test username, password, router password, kubeconfig, or application secret.

Build and inspect it locally:

```bash
docker build -t network-monitor-e2e:local ci/e2e
docker image inspect network-monitor-e2e:local \
  --format 'Image={{.Id}} User={{.Config.User}}'
```

The pipeline gives credentials to the running test container as short-lived environment variables. GitLab masking reduces accidental log exposure, but scripts must still avoid commands such as `env`, `set -x`, or verbose HTTP tracing.

## Part 7: Understand test-user provisioning

The supplied Kubernetes Job uses the existing application image and application model to create or update one non-administrator account. Its password arrives from a temporary Kubernetes Secret created by `provision-test-user.sh`.

```mermaid
flowchart LR
    V[Protected GitLab variables] --> S[Temporary Kubernetes Secret]
    S --> J[One-time provisioning Job]
    J --> M[(MySQL users table)]
    M --> T[Browser sign-in]
```

The Secret is removed after the Job succeeds. The database retains only the password hash. The account can read Vault-backed router inventory and collect metrics; the application exposes no router inventory mutation operations.

## Part 8: Validate the files locally

Run fast local checks so formatting or manifest errors do not consume runner time.

```bash
python -m pytest -q
docker build -t network-monitor-e2e:local ci/e2e
kubectl apply --dry-run=client -f kubernetes/test-user-job.yaml
git diff --check
```

The provisioning manifest will validate without the temporary credential Secret, but the Job can run only after the script creates that Secret.

## Part 9: Commit and run the merge-request pipeline

Push the pipeline definition and use a merge request to exercise its non-production validation path.

```bash
git add .gitlab-ci.yml ci/e2e kubernetes/test-user-job.yaml \
  scripts/provision-test-user.sh
git diff --staged
git commit -m "Add GitLab delivery and acceptance pipeline"
git push -u origin feature/lab05-gitlab-pipeline
```

Create a merge request into `main`. The merge-request pipeline runs source tests and builds the test image, but the rules prevent deployment from an unprotected feature branch. Review the job logs and confirm that no protected values appear.

## Part 10: Review and merge

Before merging, verify:

- Unit tests exercise authentication and inventory authorization.
- The test image is the only image built by this pipeline.
- Deployment jobs are restricted to the default protected branch.
- The Kubernetes credential is a file variable and is not in the repository.
- The testing user is not an administrator.
- The browser test has a defined timeout and verifies the complete application workflow.

Merge the approved change. The default-branch pipeline should progress through all four stages.

## Part 11: Follow the deployment job

The deployment job performs these controls in order:

1. Select the supplied kubeconfig.
2. Confirm the target context, namespace, and node.
3. Confirm the Lab 4 application images are already present.
4. Apply the version-controlled manifests.
5. Wait for MySQL, Flask, and NGINX rollouts.
6. Provision the restricted test user.
7. Report the deployed workload and service state in the job log.

## Part 12: Follow the browser acceptance test

The acceptance job runs inside `network-monitor-e2e`. It starts a local `kubectl port-forward`, then Playwright:

1. Opens the monitoring web page.
2. Signs in using `E2E_USERNAME` and `E2E_PASSWORD`.
3. Confirms an inventory router is available.
4. Collects two observations through the web interface.
5. Confirms CPU and memory percentages are displayed as numbers.
6. Confirms the chart canvas contains rendered pixels.
7. Confirms the web-instance badge identifies a Pod.
8. Reports whether the complete browser workflow passed.

This end-to-end test proves that the deployed application works through the same browser boundary used by an operator.

## Part 13: Review the pipeline result

In GitLab, open **Build > Pipelines** and select the default-branch pipeline. Confirm that the graph completed in this order:

- `unit-test`
- `build-e2e-image`
- `deploy-minikube`
- `browser-acceptance`

Open each job and identify its image, commands, duration, and final status. The pipeline is complete only when the deployment is ready and the browser acceptance job retrieves CPU and memory data successfully.

## Completion criteria

- The private Docker runner completes tagged jobs without privileged mode.
- The kubeconfig and testing credentials exist only as protected GitLab variables and temporary runtime values.
- Unit tests pass before deployment.
- The pipeline builds only the dedicated browser-test image.
- The previously built web, app, and database images remain the deployed runtime images.
- Kubernetes rollouts become ready on the protected default branch.
- A non-administrator testing account is provisioned idempotently.
- The browser test retrieves and displays numeric CPU and memory data.
- The chart contains rendered data and the instance badge identifies a web Pod.

## Cleanup

Remove the local test image when it is no longer required:

```bash
docker image rm network-monitor-e2e:local
```

Retain the GitLab variables, runner, Minikube namespace, and persistent data for later security and observability exercises. If the instructor ends the environment, delete the `e2e-test-credentials` Secret if a failed job left it behind:

```bash
kubectl -n network-devops delete secret e2e-test-credentials --ignore-not-found
```

## Key takeaways

- CI/CD turns a working sequence into a reviewed, repeatable control path.
- Runtime images do not need to be rebuilt when their content has not changed.
- Acceptance tests should cross the same web boundary used by a learner or operator.
- Test identities require least privilege and the same secret discipline as other identities.
- A successful deployment is not sufficient; the delivered service must produce the expected result.
