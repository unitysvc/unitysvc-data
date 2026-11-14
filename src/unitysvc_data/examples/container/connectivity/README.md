+++
preset_name = "container_connectivity"
category = "connectivity_test"
mime_type = "python"
file = "connectivity.py"
description = "Pull and start a prepared container application and verify its health"
is_active = true
is_public = false
meta = { runtime = "docker", timeout = 180, container_timeout_seconds = 120, requirements = ["unitysvc-core>=0.3.10"] }
+++

# Container connectivity test

Container services require a connectivity test like other services. Add this
generic test to the listing's documents:

```json
{"Connectivity test": {"$doc_preset": "container_connectivity_v1"}}
```

Sellers may run the same script before upload using
`usvc seller specs run-tests <service> --category connectivity_test`. Each
container tier is tested independently. It is uploaded as a normal
`connectivity_test`, not a separate local-only document category. It pulls a
prepared digest-pinned image; it never runs `docker build`.

The script accepts `--manifest normalized.json --timeout 120`, or the equivalent
`USVC_CONTAINER_MANIFEST_JSON` / `USVC_CONTAINER_TIMEOUT_SECONDS` environment
variables. The seller harness compiles that manifest from the accepted core
format. A platform executor must supply the same input and Docker capability;
this preset does not add that backend execution infrastructure. It must run
where it can reach the Docker daemon's loopback-published ports.

The test pulls the images, starts every service/replica on a temporary network,
applies CPU/memory limits and checks HTTP/TCP/exec health. Ports publish only to
loopback with dynamically assigned host ports. Missing health uses TCP on the
first port, or running-process state without ports. Image-embedded Docker
HEALTHCHECK is disabled, matching Kubernetes behavior. Test resources carry a
unique label and are removed on success, failure and normal interruption.

Passing verifies this startup/health workflow. It does not certify Kubernetes
scheduling, gVisor, network policy, rolling updates or disk quotas. NVIDIA GPU
limits require Docker's GPU support; other extended resources are rejected.
Startup failures are reported without reproducing Kubernetes' restart loop.

Health defaults match the compute manifest: period 5s, timeout 2s, success 1,
failure 3, startup min(60s, deadline). The default execution budget is 180s:
120s for the test plus bounded cleanup. Images remain cached. Outputs contain
the verdict, not the full manifest or application environment.
