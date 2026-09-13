#!/usr/bin/env python3
import json
import os
from pathlib import Path

from automation.common import vault_secret


cml = vault_secret("integrations/cml")
intent = json.loads(Path("intent.json").read_text(encoding="utf-8"))
learner_id = intent["learner_id"]
router = vault_secret(f"network/test/c8000v/{learner_id}")
values = {
    "pipeline_id": os.environ["CI_PIPELINE_ID"],
    "learner_id": learner_id,
    "cml_address": cml["address"],
    "cml_token": cml["token"],
    "cml_skip_verify": bool(cml.get("skip_verify", False)),
    "external_connector": cml.get("external_connector", "bridge0"),
    "node_definition": cml.get("node_definition", "cat8000v"),
    "image_definition": cml.get("image_definition") or None,
    "router_ip": router["management_ip"],
    "router_prefix_length": int(router["prefix_length"]),
    "router_gateway": router["gateway"],
    "router_username": router["username"],
    "router_password": router["password"],
    "router_ram_mb": int(cml.get("router_ram_mb", 4096)),
}
target = Path("terraform/cml-test/pipeline.auto.tfvars.json")
target.write_text(json.dumps(values), encoding="utf-8")
target.chmod(0o600)
print(json.dumps({"rendered": str(target), "pipeline_id": values["pipeline_id"], "learner_id": learner_id}))
