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

Each module resolves a problem exposed by the preceding one. The automation review identifies uncontrolled state and individual execution. Infrastructure as Code establishes declared ownership and repeatable environments. The DevOps model generalizes those controls into shared flow and feedback. Application packaging creates the identified artifact and runtime contracts needed by that model. CI/CD turns the contracts into an executable promotion and validation policy. Security and observability protect the resulting system and return operational evidence to the next planning decision.

## 4. Course reference scenario

The course follows a network engineering team as it turns an existing Python automation utility into an operated software service. Reviewed intent enters through GitLab. An unprivileged validation runner checks schema and policy, runs tests, renders a candidate, builds and scans an image, and records its digest. After approval, a protected worker obtains a short-lived credential, reaches only the named targets, performs pre-checks, executes the approved change, verifies operational state, and retains evidence. Telemetry then informs promotion, recovery, and subsequent improvement.

The reference change is deliberately small enough to understand while still exposing realistic delivery risks:

| Item | Reference value |
|---|---|
| Site | `campus-west` |
| Primary target | `distribution-01` |
| Peer used for validation | `routing-peer-01` |
| Service | VLAN 120, `USERS` |
| Gateway and prefix | `10.20.120.1/24`; `10.20.120.0/24` |
| Routing intent | OSPF process 100, area 0 |
| Change identifier | `CHG-2026-0042` |
| Delivery components | GitLab, validation runner, registry, automation API, queue, worker, job database, protected runner, telemetry collector, and dashboard |

Addresses in `192.0.2.0/24`, `198.51.100.0/24`, and `203.0.113.0/24` are documentation addresses. Names such as `registry.example`, `lab-nos`, and `vendor.collection.network_os`, synthetic XML namespaces beginning with `urn:example:`, and digest text such as `APPROVED_DIGEST` are placeholders. They show structure and control flow; learners must replace them with values supported by their own registry, software version, provider, collection, platform, and data model.

Not every example represents this change. A section that uses another identifier or topology states that it is an independent example. This allows the guide to demonstrate additional failure modes without implying that every technology must be applied to one network service.

## 5. Five-day progression and time distribution

The course allocates approximately 20 hours to theory and 20 hours to cumulative lab work. Module 0 is a prerequisite review and transition into the main course; it can be assigned as pre-reading or taught selectively at the start of Day 1. Installation occupies the first lab block.

| Day | Theory aligned to the DEVOPS outline | Reference system at the end of the day | Theory | Lab |
|---|---|---|---:|---:|
| 1 | Network automation review and Infrastructure as Code foundations | Installed environment; automation foundations refreshed; Terraform, Ansible, and Python ownership established | 4 h | 4 h |
| 2 | DevOps model, container fundamentals, and secure image packaging | Delivery risks and lifecycle controls identified; application packaged as a locked, non-root image | 4 h | 4 h |
| 3 | Multitier application operation, Kubernetes, and on-demand environment integration | Application deployed with explicit networks, health contracts, state, and an orchestration decision in a controlled environment | 4 h | 4 h |
| 4 | CI/CD, automated qualification, deployment validation, and recovery | GitLab pipeline that builds once, promotes by digest, controls protected execution, verifies operational outcomes, and retains evidence | 4 h | 4 h |
| 5 | Security and observability | Trust boundaries and short-lived identity applied; application, delivery, platform, and network signals correlated for detection, response, and improvement | 4 h | 4 h |

The repository grows with the system. Day 1 establishes application source, tests, and infrastructure definitions; Day 2 adds delivery controls and container packaging; Day 3 adds Compose, optional Kubernetes definitions, and on-demand environment integration; Day 4 adds CI/CD, deployment, and evidence paths; and Day 5 adds security policy and observability configuration. Directories are introduced when they have an owner and a working purpose rather than created empty on the first day.

```text
network-devops/
├── automation/          # supplied Python and Ansible behavior
├── intended-state/      # schemas and safe examples
├── inventory/           # environment-specific target data
├── templates/           # deterministic rendering
├── tests/               # unit, fixture, integration, and pyATS tests
├── docker/              # image construction
├── compose/             # local multitier deployment
├── terraform/           # disposable environment resources
├── observability/       # collectors, dashboards, and alert rules
├── policy/              # delivery and network guardrails
├── kubernetes/          # optional orchestrated deployment
├── docs/                # operation and recovery decisions
├── .gitlab-ci.yml
└── README.md
```

## 6. Modules

The modules follow the requested learning sequence: review the automation foundation, establish Infrastructure as Code, introduce the DevOps model, package and operate the application, control delivery through CI/CD, and finish with security and observability. The table summarizes the engineering focus of each stage.

| Module | Subject | Central engineering question |
|---|---|---|
| 0 | [Network Automation Review and the Path to DevOps](module-00-network-automation-review.md) | Which automation foundations do learners already have, and how does DevOps turn them into a dependable team delivery system? |
| 1 | [Infrastructure as Code and On-Demand Environments](module-01-infrastructure-as-code.md) | How do Terraform, Ansible, Python, and pipelines create and govern controlled infrastructure? |
| 2 | [Introducing the DevOps Model](module-02-devops-model.md) | How do DevOps philosophy, flow, feedback, measurement, and shared ownership improve software delivery? |
| 3 | [Packaging and Operating Applications](module-03-packaging-applications.md) | How is one application packaged, composed into a service, and operated with Docker, Compose, and Kubernetes? |
| 4 | [Continuous Integration, Delivery, and Deployment Validation](module-04-cicd-delivery-validation.md) | How does GitLab CI convert source into a tested artifact, deploy it safely, verify the outcome, and support recovery? |
| 5 | [Security and Observability](module-05-security-observability.md) | How are delivery boundaries protected and correlated evidence used to operate and improve the system? |

## 7. Learning outcomes

After completing the guide and labs, learners should be able to:

- Relate existing Python, Ansible, API, structured-data, and network-validation knowledge to a controlled software delivery lifecycle.
- Apply DevOps principles to infrastructure and create on-demand test environments with Terraform and Ansible.
- Describe DevOps philosophy and practices and apply them to operational delivery challenges.
- Explain container architecture and use Docker tooling.
- Package an existing Python application into a secure container image.
- Use container networking and Compose to deploy a multitier application.
- Explain Kubernetes building blocks, APIs, manifests, deployment automation, multidata-center considerations, monitoring, and logging.
- Explain CI/CD concepts and implement a GitLab pipeline that builds, tests, and deploys applications.
- Automate build and deployment validation and improve the deployment flow with health checks, controlled promotion, and recovery.
- Implement metric and log collection, dashboards, analysis, alerts, and application instrumentation.
- Explain how telemetry, health monitoring, and controlled chaos experiments improve stability and reliability.
- Secure repositories, pipelines, runners, images, credentials, infrastructure access, and retained evidence.
- Compare modern application, microservices, public/private cloud, and multicloud deployment architectures.
