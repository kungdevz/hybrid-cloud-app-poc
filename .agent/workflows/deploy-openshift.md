---
description: Deploy application to Red Hat OpenShift
---

# OpenShift Deployment Workflow

## Prerequisites

- `oc` CLI installed and logged in
- Access to OpenShift cluster (ROSA)

## 1. Login to OpenShift

```bash
oc login https://api.your-cluster.openshiftapps.com --token=<your-token>
```

## 2. Create/Select Project

```bash
oc project ks-hybrid-cloud-poc
# or create new:
oc new-project ks-hybrid-cloud-poc
```

## 3. Apply Build Configuration

// turbo

```bash
oc apply -f oc/buildconfig.yml
```

This creates:

- ImageStream: `app`
- BuildConfig: `app-build` (pulls from GitHub, builds Containerfile)

## 4. Start the Build

```bash
oc start-build app-build --follow
```

## 5. Deploy the Application

// turbo

```bash
oc apply -f oc/app-deployment.yml
```

This creates:

- ConfigMap: `app-config` (database connection)
- Service: `app-service` (port 5000)
- Deployment: `python-app`
- Route: `app-route` (public URL)

## 6. Verify Deployment

```bash
# Check pod status
oc get pods

# Get route URL
oc get route app-route -o jsonpath='{.spec.host}'
```

## 7. View Logs

```bash
oc logs -f deployment/python-app
```

## Update Deployment

After code changes:

```bash
# Trigger new build
oc start-build app-build --follow

# Rollout new deployment
oc rollout restart deployment/python-app
```

## Configuration Updates

Edit database credentials in `oc/app-deployment.yml`:

```yaml
data:
  DATABASE_URI: "your-connection-string"
  DATABASE_PASSWORD: "your-password"
```

Then apply:

```bash
oc apply -f oc/app-deployment.yml
oc rollout restart deployment/python-app
```
