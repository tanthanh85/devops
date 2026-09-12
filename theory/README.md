# Implementing DevOps Solutions and Practices using Cisco Platforms (DevOps) v1.0

## 1. Study guide purpose

This independent five-day study guide follows the scope and sequence of **Implementing DevOps Solutions and Practices using Cisco Platforms (DevOps) v1.0**. It is not an official Cisco publication. The subject is DevOps for software delivery: container packaging, multitier deployment, GitLab CI/CD, automated testing, Infrastructure as Code, on-demand environments, observability, security, multicloud design, and Kubernetes. A network automation application provides a familiar lab workload, but the practices apply to software applications generally.

The guide is intended for network and infrastructure professionals who can already automate technical work but have not yet turned that automation into a dependable software delivery system.

## 2. Prerequisite knowledge

Learners should have completed, or possess knowledge equivalent to:

- **Developing Applications and Automating Workflows Using Cisco Core Platforms (DEVASC)**
- **Developing Applications Using Cisco Core Platforms and APIs (DEVCOR)**

The course assumes that learners can write Python scripts, build Ansible playbooks, exchange JSON or YAML with APIs, use Git, and work from a Linux command line. Many learners will already have useful scripts and playbooks, but may run them individually from a laptop, pass files through chat or email, install dependencies by hand, and rely on the author to diagnose failures. That approach solves a local task; it does not yet provide repeatable software delivery.

DevOps closes that gap by applying practices that software teams have refined over many years: shared source control, peer review, reproducible builds, automated tests, immutable artifacts, controlled promotion, observability, security throughout the lifecycle, and rapid feedback from operation. The course does not reteach Python, Ansible, API, YANG, or network-programmability fundamentals. It teaches learners how to engineer, release, and operate the resulting software as a team.

## 3. Course outcome

Learners take an existing Python application and progressively turn it into a controlled software delivery solution. The supplied application happens to perform network automation, allowing learners to reuse their domain knowledge without spending the course rebuilding the automation logic. One evolving repository is used throughout the five days. Learners containerize the application, deploy supporting services, build a GitLab pipeline, automate tests and releases, provision test infrastructure, add monitoring and logging, secure the workflow, and evaluate Kubernetes deployment.

The application's internal network logic is treated as supplied functionality. The assessed work concerns the delivery system around the software: reproducibility, collaboration, flow, testing, artifact promotion, infrastructure, visibility, stability, and security. The same methods transfer to web services, data-processing workers, internal tools, and other Python applications.

## 4. Five-day distribution

The course allocates approximately 20 hours to theory and 20 hours to cumulative lab work. Module 0 is a prerequisite review and transition into the main course; it can be assigned as pre-reading or taught selectively at the start of Day 1. Installation occupies the first lab block.

| Day | Theory aligned to the DEVOPS outline | Evolving lab capability | Theory | Lab |
|---|---|---|---:|---:|
| 1 | Network automation review, DevOps model, containers, and Docker tooling | Install the lab environment; inspect the supplied application; package and run its first container | 4 h | 4 h |
| 2 | Secure image packaging, container networking, and multitier applications | Build the application image; deploy API, worker, data, and supporting services with Compose | 4 h | 4 h |
| 3 | CI/CD, DevOps flow, build validation, and improved deployment | Implement GitLab CI; automate build, test, deployment, health checks, and recovery evidence | 4 h | 4 h |
| 4 | Infrastructure DevOps, on-demand test environments, monitoring, and visibility | Provision an isolated test environment; integrate Ansible/Terraform; add logs, metrics, dashboards, and alerts | 4 h | 4 h |
| 5 | Secure workflows, multicloud and application architectures, Kubernetes, and Kubernetes visibility | Secure the pipeline; compare deployment architectures; deploy and monitor the application on Kubernetes when justified | 4 h | 4 h |

## 5. Modules

The modules follow the path of a software delivery system: establish the automation foundation, package and integrate the application, control its release, and then operate it securely at scale. The table summarizes the engineering focus of each stage.

| Module | Subject | Central engineering question |
|---|---|---|
| 0 | [Network Automation Review and the Path to DevOps](module-00-network-automation-review.md) | Which automation foundations do learners already have, and how does DevOps turn them into a dependable team delivery system? |
| 1 | [Introducing the DevOps Model](module-01-devops-model.md) | How do DevOps philosophy, flow, feedback, measurement, and shared ownership improve software delivery? |
| 2 | [Introducing Containers](module-02-containers.md) | How do containers create a consistent runtime and isolation boundary? |
| 3 | [Packaging an Application Using Docker](module-03-secure-images.md) | How is an existing Python application packaged into a secure, reproducible image? |
| 4 | [Deploying a Multitier Application](module-04-multitier-compose.md) | How do API, worker, queue, data, and monitoring services communicate and recover? |
| 5 | [Introducing CI/CD and Building the DevOps Flow](module-05-cicd.md) | How does GitLab CI convert a source change into tested, traceable artifacts? |
| 6 | [Validating the Build and Improving the Deployment Flow](module-06-validation-deployment.md) | How do automated health checks, deployment strategies, validation, and recovery improve releases? |
| 7 | [Extending DevOps to Infrastructure and On-Demand Testing](module-07-infrastructure-devops.md) | How do Terraform, Ansible, and pipelines create controlled test infrastructure? |
| 8 | [Monitoring DevOps and Engineering Visibility and Stability](module-08-observability.md) | How do logs, metrics, telemetry, alerts, and chaos experiments improve reliability? |
| 9 | [Securing DevOps Workflows and Examining Deployment Architectures](module-09-security-architecture.md) | How are secrets, pipelines, application architecture, and public/private cloud placement secured? |
| 10 | [Kubernetes Deployment, Multidata Center Integration, and Monitoring](module-10-kubernetes.md) | How are applications deployed, updated, secured, and observed with Kubernetes? |

## 6. Learning outcomes

After completing the guide and labs, learners should be able to:

- Relate existing Python, Ansible, API, structured-data, and network-validation knowledge to a controlled software delivery lifecycle.
- Describe DevOps philosophy and practices and apply them to operational delivery challenges.
- Explain container architecture and use Docker tooling.
- Package an existing Python application into a secure container image.
- Use container networking and Compose to deploy a multitier application.
- Explain CI/CD concepts and implement a GitLab pipeline that builds, tests, and deploys applications.
- Automate build and deployment validation and improve the deployment flow with health checks, controlled promotion, and recovery.
- Apply DevOps principles to infrastructure and create on-demand test environments with Terraform and Ansible.
- Implement metric and log collection, dashboards, analysis, alerts, and application instrumentation.
- Explain how telemetry, health monitoring, and controlled chaos experiments improve stability and reliability.
- Secure repositories, pipelines, runners, images, credentials, infrastructure access, and retained evidence.
- Compare modern application, microservices, public/private cloud, and multicloud deployment architectures.
- Explain Kubernetes building blocks, use its APIs and manifests to deploy an application, and implement an automated deployment pipeline.
- Explain multidata-center Kubernetes design and Kubernetes monitoring, logging, and visibility.
