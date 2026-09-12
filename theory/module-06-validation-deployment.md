# Module 6: Validating the Build and Improving the Deployment Flow

## 1. Purpose

Passing unit tests does not prove that an application image is deployable or that a release produces the intended operational outcome. This module covers build validation, infrastructure validation, pre-deployment health checks, deployment strategies, post-deployment testing, idempotence, failure classification, rollback, remediation, and improved deployment flow. The principles apply to software deployment generally. Existing network tests supply one set of domain-specific acceptance evidence for the course application.

Module 5 built the pipeline and its trust zones. Module 6 strengthens the promotion decision by asking what state existed before deployment, what actually changed, whether the service converged, and how recovery should proceed. Those controls require reliable environments, which Module 7 will define as code.

## 2. Three forms of state in an automation application

The automation application is assumed to know how to collect and interpret these states. This course uses them as deployment acceptance evidence and concentrates on when the pipeline collects them, how it evaluates them, and which result permits promotion or triggers recovery.

The loop below shows why stored configuration is an intermediate result. Operational observations must be compared with the original intent.

<p align="center">
  <img src="assets/course-figures/three-network-states.png" alt="Relationship among intended, configured, and operational network state" width="860" />
</p>

| State | Meaning | Routing-service scenario |
|---|---|---|
| Intended state | Reviewed outcome the organization wants | Interface or service prefix, routing policy, and expected tests |
| Configuration state | Commands or modeled configuration stored by the device | Interface and routing configuration returned by the device |
| Operational state | Current protocol and forwarding behavior | Interface state, neighbor state, learned route, and reachability |

The three states can disagree. A template may correctly represent intent while the device rejects part of it. The device may accept every command while the SVI stays down. The SVI may come up while the test peer never learns the route. A complete pipeline compares all three.

## 3. Network change state machine

Timeout and partial outcomes leave the normal promotion path rather than being treated as safe failures.

<p align="center">
  <img src="assets/course-figures/network-change-state.png" alt="Network change states including unknown and recovery paths" width="860" />
</p>

An `UNKNOWN/PARTIAL` state is important. A timeout after sending configuration does not prove that nothing changed. The workflow must collect current state before retrying.

## 4. Evidence chain

A release should accumulate evidence as it moves through the pipeline:

The evidence chain begins with source review and continues through static checks, unit tests, image inspection, integration tests, the infrastructure plan, pre-deployment checks, deployment, acceptance tests, and operational observation.

Each result should identify the source commit, artifact, pipeline, and target environment. This traceability supports approval, troubleshooting, and audit.

## 5. Build validation

Build validation confirms that the repository produces the expected artifact under controlled conditions. It may include:

- Dependency resolution and integrity
- Test execution and coverage
- Image creation
- Image metadata and runtime-user checks
- Vulnerability and secret scanning
- SBOM generation
- Artifact signature or provenance
- A minimal startup and health test

A successful build should not depend on files that exist only on a developer workstation.

## 6. Infrastructure validation

Infrastructure definitions need their own controls:

- Format and syntax checks
- Provider or module initialization
- Variable and schema validation
- Policy checks
- Plan generation
- Target and resource-count checks
- Cost or quota review when applicable
- Security review of network exposure and permissions

The plan is evidence, not approval by itself. Reviewers must understand the target and the meaning of the proposed actions.

## 7. Pre-deployment health checks

Before a release changes an environment, verify that the environment is safe to change. Useful checks include:

- Target identity and environment classification
- Current service health
- Available capacity
- Dependency reachability
- Credential validity without displaying the credential
- Required backups or snapshots
- Compatible database schema
- Absence of another conflicting deployment
- Availability of the previous known-good artifact

Deploying into an already degraded environment can make diagnosis and recovery harder.

### 7.1 Example pre-check set for a routing-service scenario

Pre-checks should establish whether the target is the expected system and whether its present condition permits the approved change. The following set illustrates checks that can stop deployment before any configuration is modified.

| Check | Reason | Blocking condition |
|---|---|---|
| DNS, route, and management port | Prove the runner can reach the management interface | Target unreachable or wrong path |
| Device identity and serial/hostname | Prevent change to the wrong system | Inventory and device identity differ |
| Authentication and authorization | Prove the service identity can perform the intended method | Login fails or privilege is insufficient |
| CPU and memory | Avoid adding change load to an unstable device | Threshold or trend violates policy |
| Interface and line-protocol state | Record baseline and detect unrelated failure | Required uplink or peer link is down |
| OSPF neighbor state | Confirm routing is healthy before change | Required neighbor is not `FULL` |
| Routing table and reachability | Establish baseline forwarding | Required baseline route or probe fails |
| Existing VLAN, SVI, and prefix | Detect collision or unmanaged prior state | Conflicting configuration exists |
| Running configuration backup | Support investigation and recovery | Backup cannot be collected or protected |
| Configuration lock/checkpoint capability | Select transaction and recovery approach | Required safety capability unavailable |

Thresholds must be policy, not arbitrary constants hidden in code.

## 8. Configuration generation and diff

The pipeline loads the reviewed YAML intent, validates it, normalizes addresses, and renders platform-specific configuration. A Jinja2 fragment might be:

```jinja2
vlan {{ vlan.id }}
 name {{ vlan.name }}
!
interface {{ svi.name }}
 description {{ svi.description }}
 ip address {{ svi.ipv4_address | ipaddr('address') }} {{ svi.ipv4_address | ipaddr('netmask') }}
 no shutdown
!
router ospf {{ routing.process_id }}
 passive-interface {{ svi.name }}
 network {{ routing.advertise_prefix | ipaddr('network') }} {{ routing.advertise_prefix | ipaddr('hostmask') }} area {{ routing.area }}
```

Filters and exact syntax depend on the rendering environment and target network operating system. The pipeline tests rendered output with approved fixtures. It does not send a template containing undefined variables.

The proposed diff must identify additions, removals, replacements, and unexpected lines. Review should assess protocol effect, device count, configuration section, and recovery path rather than only line count.

## 9. Deployment interfaces and transactions

Deployment safety depends partly on the transaction semantics offered by the target interface. The following subsections compare common approaches and show why the same validation and recovery design cannot be assumed for every interface.

### 9.1 SSH CLI

CLI automation may enter configuration commands and collect output. It needs prompt handling, timeouts, error-pattern detection, and post-write verification. Command echo does not prove configuration acceptance.

### 9.2 NETCONF

NETCONF exchanges capabilities and structured RPCs. Where supported, candidate configuration and `validate`, confirmed commit, or rollback-on-error can improve transaction safety. Capabilities vary, so the client must inspect the server response rather than assume support.

### 9.3 RESTCONF

RESTCONF exposes YANG-modeled data through HTTP. The client must construct the correct resource path, content type, method, and payload for the device release. It should validate TLS, distinguish HTTP errors from YANG errors, and read state back after modification.

### 9.4 Ansible

Ansible can coordinate modules, templates, backups, and assertions across devices. Check and diff modes are useful only when the selected module and platform support them accurately. Review collection documentation and test behavior.

## 10. Scoped deployment controls

The change job should require an explicit environment, site, and device limit. It verifies inventory fingerprint, device identity, change ID, commit, approved diff hash, and automation image digest.

For multiple branches, use a canary and bounded batches. Stop when failure rate, protocol convergence, or telemetry crosses policy. Do not launch the maximum parallelism simply because the tool supports it.

### 10.1 Network blast-radius framework

Blast radius is multidimensional. Count devices, but also identify routing domains, redundancy pairs, controller scopes, tenants, sites, services, and management dependencies. Changing two route reflectors in the same cluster can be riskier than changing ten independent access switches.

- **Wrong-device prevention:** resolve a stable inventory identifier, connect through the expected management path, collect hostname/serial/platform, compare the inventory fingerprint, and display the final target set before approval.
- **Per-device locking:** prevent two jobs from writing to the same device. Treat an expired lock carefully because the earlier job may still be running.
- **Routing-domain locking:** serialize changes that touch the same adjacency, route-reflector cluster, redistribution boundary, or policy control point even when device names differ.
- **Bounded concurrency:** specify maximum parallel targets and maximum acceptable failures. A tool default is not a safety policy.
- **Rate limiting:** constrain API requests, login attempts, configuration operations, and controller jobs to avoid control-plane overload.
- **Maintenance windows:** enforce start and stop boundaries, required operators, and sufficient time for observation and recovery.
- **Credential scope:** bind identity to required methods, targets, configuration domains, and duration; read-only validation should not receive write privilege.
- **Out-of-band access:** verify recovery access before a change that can affect in-band management or routing reachability.

Stop conditions must be machine-readable where possible: identity mismatch, unhealthy baseline, unexpected diff, excessive target count, lost management access, convergence timeout, new critical logs, increased packet loss, or failure of an unaffected-service check.

## 11. Network post-checks

Post-checks should compare the new state with both intent and baseline:

- The requested interface or service object exists with the expected attributes.
- `Vlan120` has the correct description and address.
- Interface administrative and operational state match the lab expectation.
- OSPF process and passive-interface policy match intent.
- Required OSPF neighbor remains `FULL`.
- The peer routing table contains the scenario prefix through the expected protocol and next hop.
- The defined reachability probe succeeds with acceptable loss and latency.
- No required baseline neighbor, route, interface, or service disappeared.
- CPU, memory, errors, drops, and logs remain within policy.
- The running configuration contains no unexpected drift.

Some checks need a convergence window. Poll with a bounded timeout and preserve intermediate observations. A fixed long sleep wastes time and hides convergence behavior.

## 12. pyATS and Genie validation

pyATS provides a test framework, while Genie parsers convert supported device output into structured data. A testbed file defines devices and connection details, with secrets supplied externally.

Illustrative test logic follows. Parser commands and supported structured output depend on the target network OS, pyATS/Genie release, and installed parser packages.

```python
from pyats import aetest

class CommonSetup(aetest.CommonSetup):
    @aetest.subsection
    def connect(self, testbed):
        device = testbed.devices["distribution-01"]
        device.connect(log_stdout=False)
        self.parent.parameters["device"] = device

class VerifyRouting(aetest.Testcase):
    @aetest.test
    def ospf_neighbor_full(self, device):
        parsed = device.parse("show ip ospf neighbor")
        states = collect_neighbor_states(parsed)
        self.failed("Required OSPF neighbor is not FULL") if "FULL" not in states else self.passed()

    @aetest.test
    def branch_prefix_present(self, device):
        routes = device.parse("show ip route 10.20.120.0 255.255.255.0")
        assert_expected_ospf_route(routes, "10.20.120.0/24")
```

Production code needs robust structured traversal, explicit expected neighbor identity, meaningful failure evidence, and parser-error handling. Tests should distinguish unavailable parser support from an absent network state.

## 13. Applied failure scenario: configuration accepted, routing service fails

In the course reference scenario, the pipeline successfully creates VLAN 120 and its gateway on `distribution-01` and applies the approved OSPF intent. The device returns no configuration error, but post-checks show:

```text
Vlan120                 10.20.120.1    YES manual up   up
Required OSPF neighbor                 EXSTART/BDR
Expected route 10.20.120.0/24          absent on routing-peer-01
Reachability to 10.20.120.1            failed from routing-peer-01
```

> **FAILURE SCENARIO**
> A timeout after a configuration request creates an uncertain outcome: the device may have changed even though the client received no success response. The workflow must rediscover configured and operational state before retrying, rolling back, or declaring failure.

The pipeline must fail the release and stop promotion. Possible causes include MTU mismatch, authentication mismatch, network type mismatch, access policy, or an unrelated peer condition. Removing the newly advertised lab prefix may not fix an existing peer problem. The correct response is evidence-driven:

1. Compare the neighbor with the pre-check baseline.
2. Inspect OSPF and interface logs and telemetry.
3. Determine whether the change affected the adjacency.
4. Roll back when the change caused degradation and rollback is safe.
5. Otherwise preserve the change state, mark the environment unhealthy, and remediate the peer under a separate controlled action.
6. Run the full post-check suite again.

## 14. Deployment strategies

Application deployment names are useful only after translating them into network control mechanisms:

| Application pattern | Network interpretation | Network-specific gate |
|---|---|---|
| Rolling update | Serial device or bounded-batch rollout | Stop between batches on convergence, error-rate, or service policy |
| Blue-green | Parallel policy, VRF, controller object, or alternate path with controlled cutover | Prove state synchronization, route preference, and reversal path |
| Canary | One device, site, tenant, or maintenance domain first | Compare protocol, path, packet-loss, latency, and incident signals |
| Feature flag | Pre-stage configuration and activate a controlled policy/object later | Prevent stale dormant configuration and audit activation ownership |
| Recreate | Remove and replace a disposable lab service or virtual appliance | Rarely appropriate for a shared physical router or switch |

### 14.1 Recreate

Stop the old version and start the new version. This is simple but normally creates interruption. It may suit a training or low-criticality environment.

### 14.2 Rolling update

Replace instances gradually while some old instances remain available. The application and schema must tolerate temporary version overlap.

### 14.3 Blue-green

Run old and new environments in parallel, validate the new environment, then switch traffic. Recovery can be fast if the old environment remains intact. The approach needs additional capacity and careful data handling.

### 14.4 Canary

Send a small portion of traffic to the new version and compare behavior before increasing exposure. Canary analysis needs reliable metrics and a clear decision policy.

### 14.5 Feature control

Deploy code with a feature disabled, then enable it for selected users or environments. This separates deployment from feature exposure but adds configuration lifecycle and cleanup work.

No strategy removes risk. Database changes, external side effects, stateful protocols, and long-running work need special handling.

## 15. Post-deployment validation

Deployment success means more than a command returning zero. Validation should proceed from cheap technical checks to meaningful service behavior:

1. Confirm the expected artifact identity.
2. Confirm processes or workloads are ready.
3. Check application and dependency health.
4. Exercise a small functional transaction.
5. Review error rate, latency, saturation, and logs.
6. Confirm that rollback or remediation remains possible.

Synthetic transactions should use isolated test data and safe cleanup.

For a network change, replace an application-only `HTTP 200` test with layered evidence: confirm the stored configuration, interface state, protocol adjacency, expected and forbidden routes, next hop, forwarding path, loss and latency, device resources, new errors, and unaffected baseline services. The selected checks must derive from intent rather than from whatever commands are convenient to collect.

## 16. Smoke, integration, and acceptance checks

A smoke test answers whether basic critical behavior works. An integration check examines a component boundary. An acceptance test evaluates a user or business outcome.

The pipeline needs a compact set that completes quickly while detecting common release failures. Broader tests can run in the on-demand environment or on a schedule.

## 17. Idempotence and repeatability

An idempotent operation reaches the same intended state when repeated. It does not mean the operation performs no work or produces identical logs. Deployment scripts should inspect current state and change only what is required.

Repeatability matters when a job is retried after an uncertain failure. The workflow should avoid duplicating resources or corrupting state.

## 18. Failure handling

The pipeline should stop at the failing boundary and preserve evidence. Cleanup should remove disposable resources without hiding the original error.

Different failures need different responses:

- A deterministic test defect requires a source change.
- A transient registry timeout may justify a bounded retry.
- An authentication failure requires corrected access, not repeated attempts.
- A failed health check may require rollback or investigation.
- A partially applied infrastructure change requires state inspection before retry.

### 18.1 Practical failure: a healthy container with an incompatible dependency

Assume the new API container starts and its liveness probe passes, but workers fail when reading jobs created by the previous version. The deployment platform sees a running process; users see stalled automation. The post-deployment check must therefore submit a representative job and verify its terminal state, not merely call `/health`. If the database change is backward compatible, shift traffic back to the previous image and investigate. If the migration is irreversible, rolling back the image may make matters worse; stop promotion, preserve the queue and schema evidence, and use the documented forward-remediation path.

## 19. Rollback and remediation

Recovery begins with causality and reversibility, not with an automatic rollback command.

<p align="center">
  <img src="assets/course-figures/rollback-decision.png" alt="Decision tree for investigation, rollback, or forward remediation" width="860" />
</p>

Both recovery paths end in renewed validation; reversing commands is not itself proof of restored service.

Rollback restores a prior artifact or configuration. It works best for stateless application changes with compatible data. Some database or infrastructure changes cannot be reversed safely.

Network recovery mechanisms have different guarantees:

- **Checkpoint or configuration replace:** restores a known device snapshot, but may overwrite legitimate concurrent changes unless locking and scope are correct.
- **NETCONF confirmed commit:** automatically reverts an unconfirmed transaction when supported and correctly timed; capability discovery and session behavior matter.
- **Controller transaction rollback:** uses the controller's ownership and transaction model; direct device edits may create unmanaged divergence.
- **Inverse intent:** removes or reverses only the intended delta, but must be generated and tested like any other change.
- **Forward remediation:** preserves valid new state and applies a new corrective action when reversal would be unsafe or the failure is unrelated.
- **Manual recovery:** uses a tested runbook and preferably out-of-band access when automation identity, reachability, or evidence cannot be trusted.

Forward remediation applies a new corrective change. Teams often need both options. The release plan should define the trigger, responsible role, required evidence, and data implications.

Test recovery before an incident. An undocumented rollback command that no one has exercised is only a hypothesis.

## 20. Improved deployment flow

An improved flow uses an on-demand environment, immutable artifact, automatic health checks, and controlled promotion:

The improved flow validates the merge request, builds the image once, creates a test environment, deploys the image digest, runs system tests, collects evidence, and removes the test environment. Approval then promotes the same digest for final verification and observation.

## 21. Knowledge check

Use these questions to assess whether you can connect an approved artifact to controlled deployment, post-change evidence, and recovery decisions.

1. What information connects a post-deployment test to the source change it validates?
2. Why should a pipeline inspect environment health before changing it?
3. Which deployment strategy requires the application to tolerate old and new versions at the same time?
4. Why might database migration prevent a simple rollback?
5. When is retrying a failed operation unsafe?

## 22. Summary

Deployment succeeds only when the intended service works, not when a tool reports that an update was accepted. The pipeline must connect source, artifact, target, rollout, and operational evidence; distinguish retryable failures from uncertain or partial changes; and choose rollback only when data and infrastructure remain compatible with the previous release.

**What the learner now has:** a deployment flow that connects approved intent to target identity, a pre-change baseline, transaction behavior, post-change service evidence, and a defensible recovery decision.

**What the next module adds:** Module 7 adds disposable, reproducible infrastructure on which expensive tests can run safely. Continue to [Extending DevOps to Infrastructure and On-Demand Testing](module-07-infrastructure-devops.md).
