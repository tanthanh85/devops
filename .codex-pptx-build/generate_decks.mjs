import fs from "node:fs/promises";
import path from "node:path";
import crypto from "node:crypto";
import { pathToFileURL } from "node:url";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const workspaceDir = "/Users/thandoan/Documents/Presentations/DevOps";
const skillDir = "/Users/thandoan/.codex/plugins/cache/openai-primary-runtime/presentations/26.909.12148/skills/presentations";
const pythonExecutable = "/Users/thandoan/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3";
const buildDir = path.join(workspaceDir, ".codex-pptx-build");
const outDir = path.join(workspaceDir, "presentations", "generated");
const assetDir = path.join(workspaceDir, "theory", "assets", "course-figures");
const coverDir = path.join(workspaceDir, "presentation-assets");
const courseCover = path.join(workspaceDir, "theory", "assets", "cover", "study-guide-cover-architecture.png");
const referencePath = path.join(workspaceDir, "presentations", "Module-00-Network-Automation-Review.pptx");
const { finalizePresentation } = await import(pathToFileURL(path.join(skillDir, "container_tools", "artifact_tool_utils.mjs")).href);

await fs.mkdir(buildDir, { recursive: true });
await fs.mkdir(outDir, { recursive: true });

const C = { navy: "#082B59", blue: "#0A6FAF", cyan: "#21A8D8", pale: "#F3F8FC", line: "#C8D7E5", ink: "#17324D", muted: "#5F758B", orange: "#F28C28", green: "#1BAA72", red: "#D9485F", white: "#FFFFFF" };
const family = "Helvetica Neue";
const slideSize = { width: 1280, height: 720 };

const decks = [
  {
    file: "00-Course-Introduction-DevOps-v1.0.pptx", label: "Course introduction", title: "Implementing DevOps Solutions and Practices using Cisco Platforms", subtitle: "DevOps v1.0", cover: courseCover,
    slides: [
      { type:"intro", title:"Course introduction", lead:"A five-day course for engineers who want to deliver automation applications through disciplined software practices.", points:["40 hours combining explanation, demonstration, and guided practice","Knowledge equivalent to DEVASC and DEVCOR","One application evolves as the delivery platform becomes more capable"] },
      { type:"diagram", title:"Course journey", image:"course-engineering-journey.png", caption:"The course follows the engineering decisions required to move an automation application into dependable operation." },
      { type:"split", title:"Five-day learning sequence", leftTitle:"Days 1 and 2", left:["Automation knowledge review","DevOps model and CALMS","Delivery lifecycle and evidence","Infrastructure ownership boundaries"], rightTitle:"Days 3 to 5", right:["Docker, Compose, and Kubernetes","GitLab pipeline design","Deployment validation and recovery","Security and operational feedback"] },
      { type:"split", title:"Starting knowledge", leftTitle:"Expected foundation", left:["Python scripting and virtual environments","REST APIs and structured data","Ansible and network automation workflows","Git fundamentals and Linux command line"], rightTitle:"Course emphasis", right:["Team delivery practices","Repeatable infrastructure and runtime environments","Controlled build, test, release, and deployment","Security evidence and operational feedback"] },
      { type:"split", title:"Learning expectations", leftTitle:"During class", left:["Participate in technical discussions","Use the assigned learner identity and resource range","Keep evidence from tests and deployments","Ask questions when observed behavior differs from intent"], rightTitle:"Working approach", right:["Read the task before changing the environment","Validate each boundary before continuing","Record assumptions and results","Restore shared resources after use"] },
      { type:"intro", title:"Knowledge gained", lead:"By the end of the course, learners can explain and apply the complete delivery path for a containerized automation service.", points:["Select ownership boundaries for Terraform, Ansible, Docker, and Kubernetes","Design GitLab pipelines with meaningful validation and promotion gates","Protect credentials and runner trust boundaries","Use logs, metrics, dashboards, and alerts to evaluate service behavior"] },
      { type:"split", title:"Course application", leftTitle:"Application capabilities", left:["Collect operational data through APIs","Present service information through a web interface","Persist application data","Run consistently across environments"], rightTitle:"Delivery capabilities", right:["Provision an isolated test environment","Package and scan release artifacts","Promote through protected pipelines","Correlate deployment and runtime evidence"] },
      { type:"split", title:"Instructor introduction", leftTitle:"Professional background", left:["Current role and technical focus","Relevant automation and delivery experience","Platforms and tools used in production","What you want learners to take from the course"], rightTitle:"Teaching approach", right:["Explain the engineering decision first","Demonstrate the observable result","Connect failures to design choices","Leave time for questions and comparison"] },
      { type:"split", title:"Learner introductions", leftTitle:"Please share", left:["Name and current role","Automation tools you use today","Experience with containers or CI/CD","One delivery problem you want to solve"], rightTitle:"Listen for", right:["Common platforms and constraints","Shared operational risks","Different levels of software experience","Opportunities for peer learning"] },
      { type:"intro", title:"Course agreements", lead:"A shared environment works when every learner treats identity, scope, and cleanup as part of the engineering task.", points:["Use only your assigned namespace, ports, and identifiers","Never place credentials in source control or terminal history","Stop when a validation gate fails","Preserve logs and pipeline evidence for review"] },
      { type:"split", title:"Evidence of learning", leftTitle:"Technical evidence", left:["Working source and configuration","Successful automated checks","Identified container images","Deployment and runtime records"], rightTitle:"Engineering judgement", right:["Explain tool ownership","Interpret failed validation","Select a safe recovery action","Connect symptoms to recent change"] },
      { type:"end", title:"Course orientation complete", subtitle:"Next: Network Automation Review" }
    ]
  },
  {
    file:"Module-00-Network-Automation-Review-v1.0.pptx", label:"Module 0", title:"Network Automation Review", subtitle:"Software foundations for automation applications", cover:path.join(coverDir,"module-00-cover.png"),
    slides:[
      {type:"intro", title:"Module introduction", lead:"This module refreshes the programming, data, interface, and validation concepts used throughout the course.", points:["Recognize the parts of a network automation application","Work with Python, JSON, YAML, XML, and dictionaries","Select an appropriate management interface","Use Git to record and exchange changes"]},
      {type:"diagram", title:"Automation application structure", image:"module-00-automation-system.png", caption:"Automation becomes easier to reason about when input, transformation, transport, validation, and evidence have clear boundaries."},
      {type:"split", title:"Automation responsibility boundaries", leftTitle:"Application responsibilities", left:["Validate input before use","Transform data deliberately","Handle errors and timeouts","Return a meaningful result"], rightTitle:"Operational responsibilities", right:["Control target scope","Protect access credentials","Observe device and service state","Retain evidence for investigation"]},
      {type:"diagram", title:"Structured data contracts", image:"module-00-structured-data.png", caption:"JSON, YAML, XML, and Python dictionaries represent the same intent in forms suited to different consumers."},
      {type:"split", title:"Python review", leftTitle:"Application logic", left:["Functions separate responsibilities","Exceptions expose failure conditions","Logging records context and outcome","Virtual environments isolate dependencies"], rightTitle:"Common libraries", right:["requests for HTTP APIs","ncclient for NETCONF","Netmiko for CLI automation","Flask for service interfaces"]},
      {type:"split", title:"API request lifecycle", leftTitle:"Before the request", left:["Select the resource and method","Build headers and authentication","Validate input data","Set a bounded timeout"], rightTitle:"After the response", right:["Check the status code","Parse the declared format","Validate required fields","Log context without secrets"]},
      {type:"diagram", title:"Interface selection", image:"module-00-interface-selection.png", caption:"The correct interface depends on data structure, transaction support, platform capability, and the evidence the workflow must collect."},
      {type:"split", title:"Ansible review", leftTitle:"Core objects", left:["Inventory identifies managed targets","Variables describe desired values","Playbooks coordinate tasks","Roles package reusable behavior"], rightTitle:"Operational controls", right:["Limit the target scope","Protect credentials","Check idempotence","Capture changed and failed results"]},
      {type:"diagram", title:"Intent and state", image:"module-00-three-states.png", caption:"A safe workflow distinguishes what should exist, what the tool applied, and what the service now reports."},
      {type:"diagram", title:"Model-driven telemetry", image:"module-00-telemetry-flow.png", caption:"Streaming telemetry delivers structured updates continuously, while polling asks for selected state at scheduled intervals."},
      {type:"split", title:"Git essentials", leftTitle:"Local workflow", left:["git status and git diff","git add and git commit","git log and git show","git branch and git switch"], rightTitle:"Team workflow", right:["Pull before starting work","Use a focused branch","Push reviewable commits","Resolve conflicts with context"]},
      {type:"split", title:"Testing boundaries", leftTitle:"Offline checks", left:["Data parsing and validation","Template rendering","Business rules","Error handling"], rightTitle:"Connected checks", right:["Authentication and reachability","API and device behavior","Configuration state","Service outcome"]},
      {type:"intro", title:"Key takeaways", lead:"Network automation already combines software logic, structured data, device interfaces, and operational validation.", points:["Treat input data as a contract","Choose interfaces according to the required behavior","Separate intended, applied, and operational state","Keep source and decisions in Git"]},
      {type:"end", title:"Module 0 complete", subtitle:"Next: Introducing the DevOps Model"}
    ]
  },
  {
    file:"Module-01-Introducing-the-DevOps-Model-v1.0.pptx", label:"Module 1", title:"Introducing the DevOps Model", subtitle:"People, process, technology, and evidence", cover:path.join(coverDir,"module-01-cover.png"),
    slides:[
      {type:"intro",title:"Module introduction",lead:"This module explains how software delivery practices turn useful automation into a service that a team can review, release, and operate.",points:["Use CALMS to examine delivery capability","Trace work through the complete lifecycle","Distinguish continuous integration, delivery, and deployment","Identify flow constraints and useful measures"]},
      {type:"diagram",title:"Delivery models",image:"module-01-delivery-models.png",caption:"Manual work, individually operated automation, and pipeline delivery differ in ownership, repeatability, validation, and evidence."},
      {type:"diagram",title:"CALMS model",image:"module-01-calms.png",caption:"Culture and sharing shape ownership. Automation and lean practices improve flow. Measurement shows whether the system works."},
      {type:"split",title:"CALMS assessment",leftTitle:"Flow and ownership",left:["Who owns the service outcome?","Where does work wait?","How large are typical changes?","How does knowledge move between people?"],rightTitle:"Automation and evidence",right:["Which decisions are repeatable?","Which failures stop promotion?","What evidence supports a release?","How does production feedback reach planning?"]},
      {type:"diagram",title:"Complete DevOps lifecycle",image:"module-01-lifecycle.png",caption:"Delivery continues after deployment. Operation, observation, learning, and retirement complete the lifecycle."},
      {type:"split",title:"Lifecycle responsibilities",leftTitle:"Before release",left:["Define the expected outcome","Design interfaces and controls","Integrate small changes","Build and qualify an artifact"],rightTitle:"After release",right:["Deploy within approved scope","Observe service behavior","Recover when outcomes differ","Retire access and obsolete versions"]},
      {type:"diagram",title:"Evidence chain",image:"module-01-evidence-chain.png",caption:"A release decision depends on traceable evidence that connects source, build inputs, tests, approvals, deployment, and observed outcome."},
      {type:"diagram",title:"Feedback speeds",image:"module-01-feedback-speeds.png",caption:"Fast checks protect developer flow. Broader integration and operational feedback answer questions that local tests cannot."},
      {type:"diagram",title:"Delivery architecture",image:"module-01-delivery-architecture.png",caption:"Version control, runners, registries, deployment targets, and observability systems form one delivery system with distinct trust boundaries."},
      {type:"split",title:"Release evidence",leftTitle:"Candidate identity",left:["Source revision","Dependency versions","Build environment","Artifact digest"],rightTitle:"Qualification evidence",right:["Test results","Security findings","Approval record","Deployment and post-check results"]},
      {type:"split",title:"CI, delivery, and deployment",leftTitle:"Continuous integration",left:["Integrates small changes frequently","Builds and tests every candidate","Returns feedback to the author","Keeps the main branch releasable"],rightTitle:"Release choices",right:["Continuous delivery keeps approval","Continuous deployment removes manual approval","Both require a qualified artifact","Promotion should preserve artifact identity"]},
      {type:"diagram",title:"Value stream",image:"module-01-value-stream.png",caption:"Improvement begins by measuring where work waits, where changes fail, and where teams repeat manual decisions."},
      {type:"split",title:"Delivery measures",leftTitle:"Flow",left:["Lead time for a change","Deployment frequency","Time waiting for approval","Time spent repeating work"],rightTitle:"Stability",right:["Change failure rate","Time to restore service","Escaped defects","Incomplete or missing evidence"]},
      {type:"intro",title:"Key takeaways",lead:"DevOps treats delivery as an engineering system whose output includes working software and credible operational evidence.",points:["Shared ownership matters as much as automation","Small batches reduce review and recovery risk","Pipelines should promote an identified artifact","Feedback must reach the people who can act on it"]},
      {type:"end",title:"Module 1 complete",subtitle:"Next: Infrastructure as Code and On-Demand Environments"}
    ]
  },
  {
    file:"Module-02-Infrastructure-as-Code-v1.0.pptx", label:"Module 2", title:"Infrastructure as Code and On-Demand Environments", subtitle:"Provisioning, configuration, testing, and cleanup", cover:courseCover,
    slides:[
      {type:"intro",title:"Module introduction",lead:"This module separates infrastructure provisioning from system configuration and shows how code can create short-lived test environments safely.",points:["Explain desired state and lifecycle management","Use Terraform state without confusing it with live truth","Assign configuration work to Ansible","Design create, verify, and destroy controls"]},
      {type:"diagram",title:"Tool ownership",image:"iac-tool-ownership.png",caption:"Terraform, Ansible, image tooling, and orchestration platforms solve different parts of the delivery problem."},
      {type:"split",title:"Three automation responsibilities",leftTitle:"Resource lifecycle",left:["Create and delete infrastructure","Track resource identity","Plan topology changes","Expose connection outputs"],rightTitle:"System behavior",right:["Configure operating systems and devices","Apply policy and application settings","Verify desired behavior","Remediate controlled drift"]},
      {type:"diagram",title:"Terraform lifecycle",image:"terraform-lifecycle.png",caption:"Initialization prepares providers, planning exposes the proposed change, and apply reconciles resources with the declared configuration."},
      {type:"split",title:"Plan review",leftTitle:"Review the proposal",left:["Resources created or destroyed","Replacement operations","Address and naming conflicts","Unexpected provider changes"],rightTitle:"Review the execution context",right:["Workspace and state backend","Provider identity","Variable sources","Approved learner resource range"]},
      {type:"split",title:"State and drift",leftTitle:"Terraform state",left:["Maps code to managed resources","Carries sensitive operational metadata","Requires controlled storage and locking","Supports planning and replacement decisions"],rightTitle:"Drift",right:["Appears when reality changes outside code","Can make a plan unsafe","Requires refresh and investigation","May lead to import, reconciliation, or replacement"]},
      {type:"diagram",title:"Drift reconciliation",image:"drift-reconciliation.png",caption:"A drift response begins with observation and classification before the team decides whether code or infrastructure should change."},
      {type:"diagram",title:"Terraform and Ansible handoff",image:"terraform-ansible-handoff.png",caption:"Provisioning creates the environment and exports connection data. Ansible consumes that output to configure and verify the systems."},
      {type:"split",title:"Handoff contract",leftTitle:"Terraform output",left:["Resource identifiers","Management addresses","Topology metadata","Readiness status"],rightTitle:"Ansible input",right:["Generated inventory","Connection variables","Configuration intent","Validation scope"]},
      {type:"diagram",title:"On-demand test environment",image:"test-environment-lifecycle.png",caption:"Temporary environments need ownership, unique naming, bounded lifetime, evidence collection, and cleanup even when tests fail."},
      {type:"diagram",title:"Automation platform options",image:"automation-platform-options.png",caption:"The environment may use simulation, virtualization, containers, or physical systems depending on fidelity and cost."},
      {type:"split",title:"Shared platform safeguards",leftTitle:"Isolation",left:["Per-learner identifiers and namespaces","Unique resource names and address ranges","Concurrency limits","Explicit ownership labels"],rightTitle:"Cleanup",right:["Destroy in an always-run stage","Use time-to-live metadata","Collect logs before deletion","Report orphaned resources"]},
      {type:"split",title:"Failure and cleanup",leftTitle:"Failure handling",left:["Preserve the failed plan and logs","Classify partial creation","Block unsafe reuse","Report the owning learner and pipeline"],rightTitle:"Cleanup handling",right:["Run after success or failure","Destroy only owned resources","Confirm the environment disappeared","Escalate cleanup failures"]},
      {type:"intro",title:"Key takeaways",lead:"Infrastructure code creates a controlled environment boundary, while configuration automation prepares the systems inside that boundary.",points:["Keep provisioning and configuration ownership clear","Treat state as protected operational data","Review plans before applying changes","Design cleanup as part of the workflow"]},
      {type:"end",title:"Module 2 complete",subtitle:"Next: Packaging and Operating Applications"}
    ]
  },
  {
    file:"Module-03-Packaging-and-Operating-Applications-v1.0.pptx", label:"Module 3", title:"Packaging and Operating Applications", subtitle:"Docker, Compose, and Kubernetes", cover:courseCover,
    slides:[
      {type:"intro",title:"Module introduction",lead:"This module packages an automation service into containers, combines its tiers, and deploys the application on an orchestration platform.",points:["Explain image and container boundaries","Build a secure and reproducible image","Operate a multitier application with Compose","Deploy and scale services with Kubernetes"]},
      {type:"diagram",title:"Containers and virtual machines",image:"containers-vs-vms.png",caption:"Containers share the host kernel, while virtual machines include a guest operating system. Each model provides a different isolation boundary."},
      {type:"diagram",title:"Docker architecture",image:"docker-architecture.png",caption:"The client requests operations from the daemon. The daemon builds images, manages networks and volumes, and starts containers."},
      {type:"split",title:"Docker object model",leftTitle:"Build objects",left:["Dockerfile","Build context","Image layers","Immutable image reference"],rightTitle:"Runtime objects",right:["Container process","Network attachment","Volume mount","Environment and secret inputs"]},
      {type:"diagram",title:"Image and container lifecycle",image:"docker-image-container-lifecycle.png",caption:"A Dockerfile produces an image. A container is a runtime instance whose writable state should remain disposable unless data uses a volume."},
      {type:"diagram",title:"Image layers and cache",image:"image-layers-cache.png",caption:"Layer order affects rebuild speed and reproducibility. Stable dependencies should precede frequently changing application source."},
      {type:"diagram",title:"Runtime boundary",image:"container-runtime-boundary.png",caption:"Configuration, secrets, persistent data, logs, and network access cross the container boundary through explicit runtime interfaces."},
      {type:"diagram",title:"Container network planes",image:"container-network-planes.png",caption:"Application traffic, management access, and external device connections have different reachability and security requirements."},
      {type:"diagram",title:"Dockerfile anatomy",image:"dockerfile-anatomy.png",caption:"A useful Dockerfile selects a trusted base, installs pinned dependencies, copies only required files, sets a non-root user, and defines startup behavior."},
      {type:"diagram",title:"Multistage build",image:"multistage-build.png",caption:"Build tools remain in an intermediate stage, while the runtime image receives only the application and required dependencies."},
      {type:"diagram",title:"Secure image supply chain",image:"secure-image-supply-chain.png",caption:"Scanning, signing, provenance, and registry policy help the platform distinguish a trusted release from an arbitrary image."},
      {type:"diagram",title:"Compose service model",image:"compose-automation-services.png",caption:"Compose declares services, networks, volumes, health checks, and runtime inputs for a complete application on one Docker host."},
      {type:"diagram",title:"Compose failure boundaries",image:"compose-failure-boundaries.png",caption:"A service failure should remain diagnosable through independent health checks, logs, restart behavior, and dependency timeouts."},
      {type:"diagram",title:"Service contracts",image:"service-contract-map.png",caption:"The web, application, and database tiers depend on explicit ports, data formats, readiness signals, and failure behavior."},
      {type:"diagram",title:"Readiness chain",image:"service-readiness-chain.png",caption:"A running process may still be unable to serve requests. Readiness checks should reflect the next service dependency."},
      {type:"diagram",title:"Kubernetes suitability",image:"kubernetes-suitability.png",caption:"Kubernetes adds scheduling, health reconciliation, service discovery, and scaling, but it also adds operational complexity."},
      {type:"diagram",title:"Kubernetes architecture",image:"kubernetes-cluster-architecture.png",caption:"The control plane maintains desired state while worker nodes run Pods and expose services through stable discovery and routing."},
      {type:"diagram",title:"Automation on Kubernetes",image:"kubernetes-automation-platform.png",caption:"Deployments operate stateless application tiers, Services provide discovery, and stateful dependencies use deliberate persistence and recovery controls."},
      {type:"diagram",title:"Worker access to managed systems",image:"kubernetes-worker-device-security.png",caption:"Network reach, workload identity, secrets, and policy determine whether a Pod can reach and change an external managed system."},
      {type:"diagram",title:"Health probes and recovery",image:"probes-and-recovery.png",caption:"Startup, readiness, and liveness probes answer different questions and drive different recovery actions."},
      {type:"intro",title:"Key takeaways",lead:"A container image packages the application. Compose connects services on one host. Kubernetes operates replicated services across a cluster.",points:["Keep images small, pinned, and non-root","Move configuration and secrets outside the image","Design explicit service and readiness contracts","Scale stateless tiers while protecting persistent state"]},
      {type:"end",title:"Module 3 complete",subtitle:"Next: Continuous Integration, Delivery, and Deployment Validation"}
    ]
  },
  {
    file:"Module-04-CICD-and-Deployment-Validation-v1.0.pptx", label:"Module 4", title:"Continuous Integration, Delivery, and Deployment Validation", subtitle:"Pipeline design, evidence, promotion, and recovery", cover:courseCover,
    slides:[
      {type:"intro",title:"Module introduction",lead:"This module turns build, test, deployment, and verification activities into pipelines with clear responsibilities and promotion evidence.",points:["Design GitLab stages and job dependencies","Choose runner boundaries and protected execution","Build once and promote the same artifact","Validate the target service and handle failure"]},
      {type:"diagram",title:"Pipeline gates",image:"pipeline-gates.png",caption:"Each gate should answer a specific release question and stop promotion when the evidence does not support the next action."},
      {type:"split",title:"GitLab pipeline structure",leftTitle:"Pipeline definition",left:["Stages establish broad order","Jobs define executable work","Rules select when jobs run","Needs express direct dependencies"],rightTitle:"Execution context",right:["Runner and executor","Container image","Variables and protected secrets","Artifacts and environment scope"]},
      {type:"diagram",title:"Test confidence",image:"test-confidence-pyramid.png",caption:"Fast unit checks cover logic broadly. Integration and end-to-end tests cover fewer paths but provide stronger system evidence."},
      {type:"diagram",title:"Artifacts and caches",image:"artifact-vs-cache.png",caption:"Artifacts carry identified outputs between jobs and releases. Caches accelerate work but should never determine release identity."},
      {type:"diagram",title:"Runner trust model",image:"runner-trust-model.png",caption:"Runner placement, executor type, credentials, network access, and branch protection determine what a job can affect."},
      {type:"split",title:"Runner selection",leftTitle:"General runner",left:["Build and unit test work","No production credentials","Restricted network reach","Disposable execution environment"],rightTitle:"Protected runner",right:["Protected branch or tag","Bounded deployment identity","Restricted target access","Enhanced audit and approval"]},
      {type:"diagram",title:"Pipeline purposes",image:"platform-vs-network-pipeline.png",caption:"An application delivery pipeline and a network intent pipeline can share a project while retaining different triggers, stages, permissions, and evidence."},
      {type:"diagram",title:"Network job trust sequence",image:"network-job-trust-sequence.png",caption:"A protected network job should validate the event, resolve approved intent, obtain bounded identity, change the target, and record the outcome."},
      {type:"diagram",title:"Network change state",image:"network-change-state.png",caption:"A deployment moves through preparation, application, verification, and outcome classification. Unknown outcomes require investigation before retry."},
      {type:"diagram",title:"Scoped deployment controls",image:"blast-radius-controls.png",caption:"Target limits, concurrency controls, change windows, and progressive batches reduce the effect of a failed change."},
      {type:"split",title:"Pre-check and post-check design",leftTitle:"Before change",left:["Confirm target identity","Measure the service baseline","Compare intended and current state","Prepare a recovery path"],rightTitle:"After change",right:["Confirm configuration state","Wait for protocol convergence","Test service behavior","Compare with the baseline"]},
      {type:"diagram",title:"Deployment strategies",image:"deployment-strategy-map.png",caption:"The right strategy depends on state, compatibility, traffic control, rollback cost, and the fidelity of health checks."},
      {type:"diagram",title:"Rollback decision",image:"rollback-decision.png",caption:"Rollback is one recovery option. Forward remediation may be safer when state changed irreversibly or the previous version cannot interpret current data."},
      {type:"split",title:"GitLab pipeline design",leftTitle:"Job contract",left:["Declared image and dependencies","Specific inputs and outputs","Clear pass or fail condition","Evidence retained for review"],rightTitle:"Promotion contract",right:["Protected environment and identity","Approval where risk requires it","Same artifact across environments","Post-deployment verification"]},
      {type:"split",title:"Pipeline failure categories",leftTitle:"Candidate failures",left:["Syntax or schema error","Failed unit or integration test","Vulnerable dependency","Unqualified artifact"],rightTitle:"Environment failures",right:["Runner or platform unavailable","Target baseline unhealthy","Deployment outcome unknown","Cleanup incomplete"]},
      {type:"intro",title:"Key takeaways",lead:"A useful pipeline automates decisions only when its tests and evidence support those decisions.",points:["Give each pipeline one operational purpose","Protect runners according to their reach","Promote one identified artifact","Treat deployment verification and cleanup as required stages"]},
      {type:"end",title:"Module 4 complete",subtitle:"Next: Security and Observability"}
    ]
  },
  {
    file:"Module-05-Security-and-Observability-v1.0.pptx", label:"Module 5", title:"Security and Observability", subtitle:"Trust boundaries, secrets, telemetry, and operational feedback", cover:courseCover,
    slides:[
      {type:"intro",title:"Module introduction",lead:"This module protects the delivery system and makes its behavior visible enough to investigate change, performance, and failure.",points:["Map trust boundaries across source, runners, registries, and targets","Retrieve secrets at runtime with bounded identity","Collect logs and metrics with useful context","Build alerts and dashboards that support action"]},
      {type:"diagram",title:"Delivery trust boundaries",image:"netdevops-trust-boundaries.png",caption:"Every boundary changes the identity, permissions, data exposure, or network reach available to the delivery workload."},
      {type:"split",title:"Threat model questions",leftTitle:"Assets and actors",left:["Which source and artifacts require integrity?","Who can approve or trigger deployment?","Which identities can reach managed targets?","Where can secrets or evidence leak?"],rightTitle:"Controls and response",right:["How is identity verified?","Where is scope enforced?","Which events require alerting?","How are credentials revoked?"]},
      {type:"diagram",title:"Security throughout delivery",image:"security-through-delivery.png",caption:"Source controls, dependency checks, artifact integrity, protected deployment, and runtime monitoring address different attack paths."},
      {type:"split",title:"Vault access pattern",leftTitle:"Authentication",left:["Pipeline proves workload identity","Vault evaluates policy","A short-lived token scopes access","Audit records identify the request"],rightTitle:"Secret use",right:["Job retrieves only required values","Values remain masked from output","Credentials live only for the task","Revocation closes the session"]},
      {type:"diagram",title:"Runner compromise response",image:"compromised-runner-response.png",caption:"Containment should revoke credentials, isolate the runner, preserve evidence, evaluate affected artifacts, and restore from a trusted baseline."},
      {type:"diagram",title:"Monitoring and observability",image:"monitoring-observability-telemetry.png",caption:"Telemetry provides raw signals. Monitoring evaluates known conditions. Observability supports investigation when the failure mode was not predicted."},
      {type:"diagram",title:"Observability architecture",image:"observability-architecture.png",caption:"Applications, containers, Kubernetes, delivery jobs, and managed systems should send correlated events to a common analysis path."},
      {type:"split",title:"Elastic data flow",leftTitle:"Collection",left:["Application and pipeline logs","Container and Kubernetes events","Host and workload metrics","Synthetic request measurements"],rightTitle:"Use",right:["Normalize and enrich events","Search by deployment identity","Build service dashboards","Trigger actionable webhook alerts"]},
      {type:"diagram",title:"Operational signals",image:"operational-signals.png",caption:"Logs explain events, metrics show trends, traces follow requests, and state collection confirms the behavior of managed infrastructure."},
      {type:"diagram",title:"Change-aware feedback",image:"change-aware-feedback-loop.png",caption:"Deployment identity and timestamps connect pipeline events to changes in application, cluster, and network behavior."},
      {type:"diagram",title:"Change correlation",image:"change-correlation-model.png",caption:"Useful audit records link actor, source revision, pipeline, artifact, target, action, result, and observed service outcome."},
      {type:"split",title:"Audit event content",leftTitle:"Identity and intent",left:["Timestamp and correlation identifier","Actor and workload identity","Source revision and pipeline","Target and requested action"],rightTitle:"Execution and outcome",right:["Tool and dependency versions","Command or API operation","Result and sanitized error detail","Artifact, evidence, and cleanup status"]},
      {type:"split",title:"Secrets management",leftTitle:"Vault responsibilities",left:["Authenticate the workload","Issue or return scoped secrets","Apply policy and lifetime","Record access for audit"],rightTitle:"Pipeline responsibilities",right:["Request secrets only at runtime","Avoid printing or persisting values","Limit the job and target scope","Revoke access after use"]},
      {type:"split",title:"Dashboards and alerts",leftTitle:"Dashboards",left:["Cluster and workload health","Application request success","Response time and resource pressure","Pipeline and change correlation"],rightTitle:"Alerts",right:["Identify a condition that needs action","Include service and deployment context","Use a tested notification path","Reduce duplicate and non-actionable signals"]},
      {type:"split",title:"Synthetic monitoring",leftTitle:"Test request",left:["Authenticate with a dedicated identity","Access the published service endpoint","Confirm device data appears","Measure total response time"],rightTitle:"Recorded evidence",right:["HTTP result and timing","Application instance identity","Target device and data timestamp","Related pipeline and deployment version"]},
      {type:"intro",title:"Key takeaways",lead:"Security controls limit what delivery components can do. Observability shows what they did and whether the service remained healthy.",points:["Use short-lived, scoped workload identity","Keep audit context across every pipeline stage","Correlate deployment and runtime signals","Design alerts around an operational response"]},
      {type:"end",title:"Module 5 complete",subtitle:"Course content complete"}
    ]
  }
];

function shape(slide, position, fill, radius="rect", line="none") {
  return slide.shapes.add({geometry:radius, position, fill, line:line==="none"?{fill:"none",width:0}:{fill:line,width:1}});
}
function textBox(slide, text, position, style={}) {
  const s=slide.shapes.add({geometry:"textbox",position,fill:"none",line:{fill:"none",width:0}});
  s.text=text;
  s.text.style={typeface:family,fontSize:style.fontSize??24,bold:style.bold??false,color:style.color??C.ink,alignment:style.align??"left",verticalAlignment:style.valign??"middle",autoFit:"shrinkText",wrap:"square",insets:style.insets??{left:4,right:4,top:2,bottom:2}};
  return s;
}
function chrome(slide, n, label, title) {
  slide.background.fill=C.white;
  shape(slide,{left:0,top:0,width:1280,height:34},C.navy);
  shape(slide,{left:1025,top:0,width:255,height:34},C.blue);
  textBox(slide,String(n),{left:8,top:0,width:28,height:34},{fontSize:16,bold:true,color:C.white,align:"center"});
  textBox(slide,label,{left:42,top:0,width:420,height:34},{fontSize:16,bold:true,color:C.white});
  textBox(slide,title,{left:48,top:48,width:1184,height:78},{fontSize:37,bold:true,color:C.navy});
  shape(slide,{left:48,top:137,width:1184,height:2},C.line);
}
async function addImage(slide, file, position, fit="contain") {
  const bytes=new Uint8Array(await fs.readFile(file));
  slide.images.add({blob:bytes,contentType:"image/png",alt:path.basename(file).replace(/[-_]/g," "),fit,position});
}
function setNotes(slide, lines) {
  slide.speakerNotes.textFrame.setText(lines.filter(Boolean).join("\n\n"));
}
async function coverSlide(p, d) {
  const s=p.slides.add(); s.background.fill=C.navy;
  await addImage(s,d.cover,{left:0,top:0,width:1280,height:720},"cover");
  shape(s,{left:0,top:0,width:590,height:720},C.navy);
  shape(s,{left:0,top:0,width:1280,height:34},C.navy); shape(s,{left:1025,top:0,width:255,height:34},C.blue);
  textBox(s,d.label,{left:42,top:0,width:410,height:34},{fontSize:16,bold:true,color:C.white});
  textBox(s,d.title,{left:48,top:120,width:500,height:210},{fontSize:48,bold:true,color:C.white});
  textBox(s,d.subtitle,{left:52,top:340,width:470,height:70},{fontSize:25,color:"#D8ECFA"});
  textBox(s,"Cisco learning and professional development",{left:52,top:635,width:480,height:30},{fontSize:17,color:C.white});
  setNotes(s,[
    `Purpose: Open ${d.label} and establish the subject of the deck.`,
    `Explain: ${d.title}. ${d.subtitle}.`,
    "Presenter cue: Briefly connect this module to the previous part of the course before discussing details.",
    "Transition: Move to the module introduction and learning focus."
  ]);
}
function addPointRows(slide, points, top=255) {
  const gap=64;
  points.forEach((p,i)=>{
    shape(slide,{left:78,top:top+i*gap+7,width:7,height:38},i%2?C.cyan:C.orange,"roundRect");
    textBox(slide,p,{left:102,top:top+i*gap,width:1090,height:52},{fontSize:24,color:C.ink});
  });
}
async function contentSlide(p,d,spec,n){
  const s=p.slides.add(); chrome(s,n,d.label,spec.title);
  if(spec.type==="intro"){
    textBox(s,spec.lead,{left:72,top:165,width:1136,height:72},{fontSize:25,color:C.muted});
    addPointRows(s,spec.points,260);
    setNotes(s,[`Purpose: Establish the scope of ${spec.title}.`,`Explain: ${spec.lead}`,`Discuss: ${spec.points.join(" ")}`,"Audience question: Which point is most familiar, and which point needs the most attention?","Transition: Introduce the first model or engineering boundary."]);
  } else if(spec.type==="diagram"){
    const file=path.join(assetDir,spec.image);
    await addImage(s,file,{left:64,top:165,width:1152,height:425},"contain");
    shape(s,{left:78,top:612,width:8,height:58},C.blue,"roundRect");
    textBox(s,spec.caption,{left:100,top:603,width:1090,height:70},{fontSize:20,color:C.ink});
    setNotes(s,[`Purpose: Explain ${spec.title.toLowerCase()} through the diagram.`,`Reading order: Start with the main boundary or input, follow the connections, then identify the output or feedback path.`,`Key explanation: ${spec.caption}`,"Audience question: Where would a failure become visible, and which component should own the response?","Transition: Connect the diagram to the next engineering decision."]);
  } else if(spec.type==="split"){
    shape(s,{left:640,top:180,width:2,height:445},C.line);
    textBox(s,spec.leftTitle,{left:72,top:176,width:520,height:50},{fontSize:27,bold:true,color:C.blue});
    textBox(s,spec.rightTitle,{left:688,top:176,width:520,height:50},{fontSize:27,bold:true,color:C.blue});
    spec.left.forEach((x,i)=>{ shape(s,{left:82,top:252+i*78,width:36,height:36},i%2?C.green:C.orange,"ellipse"); textBox(s,String(i+1),{left:82,top:252+i*78,width:36,height:36},{fontSize:17,bold:true,color:C.white,align:"center"}); textBox(s,x,{left:132,top:242+i*78,width:450,height:58},{fontSize:22}); });
    spec.right.forEach((x,i)=>{ shape(s,{left:698,top:252+i*78,width:36,height:36},i%2?C.green:C.orange,"ellipse"); textBox(s,String(i+1),{left:698,top:252+i*78,width:36,height:36},{fontSize:17,bold:true,color:C.white,align:"center"}); textBox(s,x,{left:748,top:242+i*78,width:450,height:58},{fontSize:22}); });
    setNotes(s,[`Purpose: Compare the two sides of ${spec.title.toLowerCase()}.`,`Left side, ${spec.leftTitle}: ${spec.left.join(" ")}`,`Right side, ${spec.rightTitle}: ${spec.right.join(" ")}`,"Presenter cue: Explain the relationship between the columns rather than reading each line verbatim.","Audience question: Which responsibility is unclear or shared in your current environment?","Transition: Use the comparison to frame the next topic."]);
  } else if(spec.type==="end"){
    shape(s,{left:0,top:140,width:1280,height:580},C.navy);
    shape(s,{left:96,top:222,width:92,height:92},C.blue,"ellipse");
    textBox(s,"✓",{left:96,top:215,width:92,height:100},{fontSize:52,bold:true,color:C.white,align:"center"});
    textBox(s,spec.title,{left:230,top:210,width:900,height:90},{fontSize:43,bold:true,color:C.white});
    textBox(s,spec.subtitle,{left:232,top:320,width:880,height:55},{fontSize:25,color:"#CDE9F7"});
    shape(s,{left:230,top:410,width:760,height:4},C.orange);
    textBox(s,"Review the key concepts before continuing.",{left:232,top:445,width:820,height:50},{fontSize:22,color:C.white});
    setNotes(s,[`Purpose: Close ${d.label}.`,`Recap: Ask learners to state one concept they can apply and one question that remains.`,`Next: ${spec.subtitle}`,"Presenter cue: Confirm the class is ready before moving to the next module."]);
  }
}

const referenceSha256=crypto.createHash("sha256").update(await fs.readFile(referencePath)).digest("hex");
for(const d of decks){
  const p=Presentation.create({slideSize});
  await coverSlide(p,d);
  let n=2;
  for(const spec of d.slides){ await contentSlide(p,d,spec,n++); }
  const stage=path.join(buildDir,d.file.replace(/\.pptx$/,"")); await fs.mkdir(stage,{recursive:true});
  const candidatePath=path.join(stage,"candidate.pptx");
  await (await PresentationFile.exportPptx(p)).save(candidatePath);
  const finalPath=path.join(outDir,d.file);
  await fs.rm(finalPath,{force:true});
  const receiptPath=path.join(stage,"validation-latest.json");
  await fs.rm(receiptPath,{force:true});
  const result=await finalizePresentation({
    workspaceDir,candidatePath,finalPath,pythonExecutable,
    integrityValidatorPath:path.join(skillDir,"container_tools","inspect_presentation_package_integrity.py"),
    layoutValidatorPath:path.join(skillDir,"container_tools","inspect_presentation_layout_geometry.py"),
    layoutArgs:["--expected-slide-size-emu","12192000,6858000","--validate-heading-fit"],
    explicitTotalSlideCount:p.slides.items.length,
    requiredNativeTableOwnerSlides:[],requiredNativeChartOwnerSlides:[],
    fontPolicy:{basis:"reference",families:[family],referencePath,referenceSha256},
    expectedSlideSizeEmu:"12192000,6858000",verifyArtifactToolImport:true,
    receiptPath
  });
  console.log(JSON.stringify({file:finalPath,slides:p.slides.items.length,result:result?.status??"ok"}));
}
