# Implementing DevOps Solutions and Practices using Cisco Platforms (DevOps) v1.0

## Study guide purpose

This independent five-day study guide follows the scope and sequence of **Implementing DevOps Solutions and Practices using Cisco Platforms (DevOps) v1.0**. It is not an official Cisco publication. The guide focuses on applying DevOps practices to an existing network automation application and its supporting infrastructure: container packaging, multitier deployment, GitLab CI/CD, automated validation, Infrastructure as Code, on-demand testing, observability, security, multicloud design, and Kubernetes.

The guide is intended for network engineers, network automation engineers, DevNet engineers, infrastructure engineers, architects, systems engineers, and operations engineers transitioning to DevOps practices.

## Prerequisite knowledge

Learners should have completed, or possess knowledge equivalent to:

- **Developing Applications and Automating Workflows Using Cisco Core Platforms (DEVASC)**
- **Developing Applications Using Cisco Core Platforms and APIs (DEVCOR)**

The course therefore assumes that learners can already work with Python, Git, Linux CLI tools, JSON/YAML, REST APIs, authentication, software-development workflows, and network programmability concepts. It does not reteach Python fundamentals, API fundamentals, YANG syntax, or basic network automation. Short examples appear only to explain how DevOps controls package, test, deploy, secure, and observe an existing automation solution.

## Course outcome

Learners take an existing network automation application and progressively turn it into a controlled DevOps delivery solution. One evolving lab repository is used throughout the course. Learners containerize the application, deploy supporting services, build a GitLab pipeline, automate tests and deployment, provision test infrastructure, add monitoring and logging, secure the workflow, and evaluate Kubernetes deployment.

The automation application's internal network logic is treated as supplied functionality. Course work concentrates on the delivery system around it: reproducibility, flow, validation, promotion, infrastructure, visibility, stability, and security.

## Five-day distribution

The course allocates approximately 20 hours to theory and 20 hours to cumulative lab work. Installation occupies the first lab block. Instructors can move selected reference sections to pre-reading when learners already understand Python, Git, or containers.

| Day | Theory aligned to the DEVOPS outline | Evolving lab capability | Theory | Lab |
|---|---|---|---:|---:|
| 1 | DevOps model, containers, and Docker tooling | Install the lab environment; inspect the supplied application; package and run its first container | 4 h | 4 h |
| 2 | Secure image packaging, container networking, and multitier applications | Build the application image; deploy API, worker, data, and supporting services with Compose | 4 h | 4 h |
| 3 | CI/CD, DevOps flow, build validation, and improved deployment | Implement GitLab CI; automate build, test, deployment, health checks, and recovery evidence | 4 h | 4 h |
| 4 | Infrastructure DevOps, on-demand test environments, monitoring, and visibility | Provision an isolated test environment; integrate Ansible/Terraform; add logs, metrics, dashboards, and alerts | 4 h | 4 h |
| 5 | Secure workflows, multicloud and application architectures, Kubernetes, and Kubernetes visibility | Secure the pipeline; compare deployment architectures; deploy and monitor the application on Kubernetes when justified | 4 h | 4 h |

## Modules

| Module | Subject | Central engineering question |
|---|---|---|
| 1 | [Introducing the DevOps Model](module-01-devops-model.md) | How do DevOps philosophy, flow, feedback, measurement, and shared ownership apply to automation delivery? |
| 2 | [Introducing Containers](module-02-containers.md) | How do containers create a consistent runtime and isolation boundary? |
| 3 | [Packaging an Application Using Docker](module-03-secure-images.md) | How is an existing automation application packaged into a secure, reproducible image? |
| 4 | [Deploying a Multitier Application](module-04-multitier-compose.md) | How do API, worker, queue, data, and monitoring services communicate and recover? |
| 5 | [Introducing CI/CD and Building the DevOps Flow](module-05-cicd.md) | How does GitLab CI convert a source change into tested, traceable artifacts? |
| 6 | [Validating the Build and Improving the Deployment Flow](module-06-validation-deployment.md) | How do automated health checks, deployment strategies, validation, and recovery improve releases? |
| 7 | [Extending DevOps to Infrastructure and On-Demand Testing](module-07-infrastructure-devops.md) | How do Terraform, Ansible, and pipelines create controlled test infrastructure? |
| 8 | [Monitoring NetDevOps and Engineering Visibility and Stability](module-08-observability.md) | How do logs, metrics, telemetry, alerts, and chaos experiments improve reliability? |
| 9 | [Securing DevOps Workflows and Examining Deployment Architectures](module-09-security-architecture.md) | How are secrets, pipelines, application architecture, and public/private cloud placement secured? |
| 10 | [Kubernetes Deployment, Multidata Center Integration, and Monitoring](module-10-kubernetes.md) | How are applications deployed, updated, secured, and observed with Kubernetes? |

## Learning outcomes

After completing the guide and labs, learners should be able to:

- Describe DevOps philosophy and practices and apply them to operational delivery challenges.
- Explain container architecture and use Docker tooling.
- Package an existing automation application into a secure container image.
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

## How to use the guide

1. Complete the modules in order or use individual chapters as topic references.
2. Begin with the supplied or instructor-provided network automation application; do not spend course time rebuilding its API or device logic from first principles.
3. Extend the same lab repository with containers, tests, pipelines, infrastructure definitions, monitoring, security controls, and deployment manifests as new topics are introduced.
4. Use read-only collection before a change operation.
5. Treat device configuration acceptance and operational success as separate outcomes.
6. Use only dedicated equipment, simulations, or authorized vendor sandbox resources.
7. Keep credentials, private keys, live inventory values, state files, and sensitive evidence outside Git.

## Lab and production boundaries

The course uses an all-in-one Ubuntu learning workstation and may use an authorized vendor sandbox, virtual network devices, a simulator, or instructor-provided mock services. This improves portability but does not represent a production architecture. Production designs normally isolate runners, secret management, registries, observability, control-plane services, and network access.

All configuration examples require adaptation to the assigned network operating system, release, and topology. Learners must verify data models, resource paths, transaction capabilities, and device behavior rather than assume that one payload works on every platform.
