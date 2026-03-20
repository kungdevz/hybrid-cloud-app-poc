#!/bin/bash

# --- CONFIGURATION ---
NAMESPACE="ks-hybrid-cloud-poc"
APP_NAME="app"
IMAGE_TAG="latest"

echo "🔍 Starting verification for $NAMESPACE/$APP_NAME:$IMAGE_TAG..."

# 1. Get the Local Digest from Podman
# We use 'index' or 'image' digest depending on how it was built
LOCAL_DIGEST=$(podman inspect --format='{{index .RepoDigests 0}}' ${APP_NAME}:${IMAGE_TAG} 2>/dev/null | cut -d'@' -f2)

if [ -z "$LOCAL_DIGEST" ]; then
    echo "❌ Error: Could not find image '$APP_NAME:$IMAGE_TAG' in local Podman."
    exit 1
fi

echo "🏠 Local Podman SHA:  $LOCAL_DIGEST"

# 2. Get the Remote Digest from OpenShift
# This queries the ImageStreamTag directly
REMOTE_REF=$(oc get istag/${APP_NAME}:${IMAGE_TAG} -n ${NAMESPACE} -o jsonpath='{.image.dockerImageReference}' 2>/dev/null)
REMOTE_DIGEST=$(echo $REMOTE_REF | cut -d'@' -f2)

if [ -z "$REMOTE_DIGEST" ]; then
    echo "❌ Error: Could not find image '$APP_NAME:$IMAGE_TAG' in OpenShift registry."
    exit 1
fi

echo "☁️  Remote Registry SHA: $REMOTE_DIGEST"

# 3. Compare the two
echo "---------------------------------------------------"
if [ "$LOCAL_DIGEST" == "$REMOTE_DIGEST" ]; then
    echo "✅ MATCH! The registry is running your latest build."
else
    echo "⚠️  MISMATCH! The registry has a different version."
    echo "Action: Run your podman push command again."
fi
