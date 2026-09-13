#!/usr/bin/env sh
set -eu
: "${CI_API_V4_URL:?}"
: "${CI_PROJECT_ID:?}"
: "${CI_PIPELINE_ID:?}"
: "${CI_JOB_TOKEN:?}"
learner_id="$(python3 -c 'import json,re; v=json.load(open("intent.json"))["learner_id"]; assert re.fullmatch(r"L(?:0[1-9]|1[0-9]|20)",v); print(v.lower())')"
state_url="${CI_API_V4_URL}/projects/${CI_PROJECT_ID}/terraform/state/cml-${learner_id}-${CI_PIPELINE_ID}"
export TF_HTTP_ADDRESS="$state_url"
export TF_HTTP_LOCK_ADDRESS="${state_url}/lock"
export TF_HTTP_UNLOCK_ADDRESS="${state_url}/lock"
export TF_HTTP_LOCK_METHOD=POST
export TF_HTTP_UNLOCK_METHOD=DELETE
export TF_HTTP_RETRY_WAIT_MIN=5
export TF_HTTP_USERNAME=gitlab-ci-token
export TF_HTTP_PASSWORD="$CI_JOB_TOKEN"
terraform -chdir="${TF_ROOT}" init -input=false
