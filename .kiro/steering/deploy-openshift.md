---
inclusion: manual
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
oc get pods
oc get route app-route -o jsonpath='{.spec.host}'
```

## 7. View Logs

```bash
oc logs -f deployment/python-app
```

## Update Deployment

After code changes:

```bash
oc start-build app-build --follow
oc rollout restart deployment/python-app
```

## Configuration Updates

Edit database credentials in `oc/app-deployment.yml`, then:

```bash
oc apply -f oc/app-deployment.yml
oc rollout restart deployment/python-app
```
