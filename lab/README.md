# DevOps Course Labs

Each lab is self-contained and can be completed in any order. Learners create a new local folder and a new private GitLab repository for every lab. The instructor-provided files for a lab include the complete baseline needed for that lab; never copy files from another lab repository.

Use this naming pattern:

```text
Local parent folder: ~/netdevops-labs/
Repository:          netdevops-labNN-short-topic
```

Examples include `netdevops-lab02-docker`, `netdevops-lab04-kubernetes`, and `netdevops-lab07-elastic-alerts`. Keep completed lab folders as independent evidence. Do not empty or overwrite one lab folder when starting another.

| Lab | Focus | Result |
|---|---|---|
| [Lab 1](Lab%2001%20-%20Workstation%20Installation/Lab1.md) | Workstation and platform installation | Verified VS Code, Python, Ansible, Docker, Kubernetes, GitLab, monitoring, and secrets tooling |
| [Lab 2](Lab%2002%20-%20Package%20the%20Network%20Monitoring%20Application/Lab2.md) | Docker packaging | Tested Flask monitoring application packaged as a reproducible image |
| [Lab 3](Lab%2003%20-%20Implement%20a%20Three-Tier%20Application/Lab3.md) | Three-tier Docker Compose deployment | Web, application, and persistent MySQL tiers with authenticated router inventory |
| [Lab 4](Lab%2004%20-%20Deploy%20and%20Scale%20on%20Kubernetes/Lab4.md) | Minikube deployment and scaling | The complete Lab 3 web, application, and persistent MySQL tiers deployed on Minikube |
| [Lab 5](Lab%2005%20-%20Build%20Test%20and%20Deploy%20with%20GitLab%20CI-CD/Lab5.md) | GitLab CI/CD delivery | Tested deployment to Minikube with browser-level monitoring evidence |
| [Lab 6](Lab%2006%20-%20Monitor%20with%20the%20Elastic%20Stack/Lab6.md) | Kubernetes and application observability | Correlated logs, container metrics, synthetic checks, and Kibana dashboards |
| [Lab 7](Lab%2007%20-%20Send%20Elastic%20Alerts%20to%20a%20Webhook/Lab7.md) | Elastic webhook alerting | Authenticated active and recovery alerts for latency, cluster health, CPU, and memory |
| [Lab 8](Lab%2008%20-%20Production-Grade%20Network%20CI-CD/Lab8.md) | Production-grade network CI/CD | NetBox intent delivered through on-demand CML testing, Ansible deployment, pyATS validation, controlled production promotion, and complete Elastic audit evidence |

The application performs read-only monitoring against instructor-authorized Cisco IOS XE routers. Credentials, tokens, private keys, `.env` files, and sensitive device output must remain outside Git.
