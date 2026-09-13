#!/usr/bin/env sh
set -eu

audit_emit() {
  action=$1 outcome=$2 message=$3 fields=${4:-"{}"}
  python3 ci/audit.py emit --action "$action" --outcome "$outcome" --message "$message" --fields-json "$fields"
}

audit_task() {
  task=$1
  shift
  started=$(date +%s)
  audit_emit "${task}_start" unknown "Starting ${task}"
  set +e
  "$@"
  result=$?
  set -e
  duration=$(( ($(date +%s) - started) * 1000 ))
  if [ "$result" -eq 0 ]; then outcome=success; else outcome=failure; fi
  python3 ci/audit.py emit --action "${task}_complete" --outcome "$outcome" --message "Completed ${task}" --duration-ms "$duration" --fields-json "{\"process.exit_code\":$result}"
  return "$result"
}

audit_job_start() {
  audit_emit job_start unknown "Pipeline job started"
  trap 'status=$?; trap - EXIT; audit_job_finish "$status"; exit "$status"' EXIT
}
audit_job_finish() {
  result=${1:-1}
  if [ "$result" -eq 0 ]; then outcome=success; else outcome=failure; fi
  audit_emit job_complete "$outcome" "Pipeline job completed" "{\"process.exit_code\":$result}"
}
