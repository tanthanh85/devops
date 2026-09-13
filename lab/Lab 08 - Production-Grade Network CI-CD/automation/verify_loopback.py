import os
import re
import time

from pyats.topology import loader

from common import desired_loopback, emit


def main():
    started = time.perf_counter()
    desired = None
    device = None
    try:
        desired = desired_loopback()
        testbed = loader.load({"testbed":{"name":"netbox-loopback"},"devices":{desired["device"]:{"os":"iosxe","type":"router","connections":{"cli":{"protocol":"ssh","ip":desired["management_ip"]}},"credentials":{"default":{"username":desired["username"],"password":desired["password"]}}}}})
        device = testbed.devices[desired["device"]]
        device.connect(log_stdout=False, learn_hostname=True)
        output = device.execute(f"show ip interface brief | include {desired['interface']}")
        pattern = rf"^{re.escape(desired['interface'])}\s+{re.escape(desired['ip'])}\s+\S+\s+\S+\s+up\s+up\s*$"
        if not re.search(pattern, output, re.MULTILINE | re.IGNORECASE):
            raise AssertionError("loopback address or up/up state did not match NetBox intent")
        emit("loopback_validation", "success", started, **{"deployment.environment":desired["environment"],"network.device.name":desired["device"],"network.device.address":desired["management_ip"],"network.interface.name":desired["interface"],"network.interface.ip":desired["address"],"network.interface.status":"up","network.protocol.status":"up","test.framework":"pyATS","test.assertion":"exact address and up/up state"})
    except Exception as exc:
        emit("loopback_validation", "failure", started, **{"deployment.environment":(desired or {}).get("environment",os.getenv("TARGET_ENVIRONMENT","unknown")),"network.device.name":(desired or {}).get("device","unknown"),"error.type":type(exc).__name__,"error.message":str(exc)[:200],"test.framework":"pyATS"})
        raise
    finally:
        if device and device.connected: device.disconnect()


if __name__ == "__main__": main()
