#!/usr/bin/env bash
# Build, push and deploy the Cert Compliance Chat app to SPCS.
# Run from the app/ directory.
set -euo pipefail

ACCOUNT_REGISTRY="sfsenorthamerica-dhall-aws1.registry.snowflakecomputing.com"
REPO_PATH="comcast_cyber_demo/cert_security/app_repo"
IMAGE_NAME="cert-chat"
TAG="latest"
FULL_IMAGE="${ACCOUNT_REGISTRY}/${REPO_PATH}/${IMAGE_NAME}:${TAG}"

echo "==> Building image ${FULL_IMAGE}"
docker build --platform linux/amd64 -t "${FULL_IMAGE}" .

echo "==> Logging in to Snowflake registry"
snow spcs image-registry login

echo "==> Pushing image"
docker push "${FULL_IMAGE}"

echo "==> Creating service in Snowflake"
snow sql -q "
CREATE SERVICE IF NOT EXISTS COMCAST_CYBER_DEMO.CERT_SECURITY.CERT_CHAT_SERVICE
  IN COMPUTE POOL COMCAST_CERT_APP_POOL
  FROM SPECIFICATION \$\$
$(cat service_spec.yaml)
\$\$;

SHOW ENDPOINTS IN SERVICE COMCAST_CYBER_DEMO.CERT_SECURITY.CERT_CHAT_SERVICE;
"

echo "Done. Wait ~2 min for the public endpoint to come online, then check 'SHOW ENDPOINTS IN SERVICE ...' to grab the URL."
