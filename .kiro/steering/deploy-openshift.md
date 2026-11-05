---
inclusion: manual
---

# OpenShift Deployment Workflow

Deploys the Flask app to OpenShift (ROSA) using the in-cluster BuildConfig
and the internal image registry. Covers the `production` profile, which
points the app at the external MSSQL database.

## Prerequisites

- `oc` CLI installed (tested with 4.22.0)
- Access to the OpenShift cluster (ROSA)

## Cluster Reference

| Item | Value |
|------|-------|
| API endpoint | `https://api.n0w7a5w8g3j0z4e.en6d.p3.openshiftapps.com:443` |
| Apps domain | `apps.rosa.n0w7a5w8g3j0z4e.en6d.p3.openshiftapps.com` |
| Project / namespace | `ks-hybrid-cloud-poc` |

## 1. Login to OpenShift

```bash
oc login https://api.n0w7a5w8g3j0z4e.en6d.p3.openshiftapps.com:443 \
  --username cluster-admin \
  --password <password>
```

Token-based login also works:

```bash
oc login https://api.n0w7a5w8g3j0z4e.en6d.p3.openshiftapps.com:443 --token=<your-token>
```

## 2. Create/Select Project

```bash
oc new-project ks-hybrid-cloud-poc
# or, if it already exists:
oc project ks-hybrid-cloud-poc
```

## 3. Apply Build Configuration

```bash
oc apply -f oc/buildconfig.yml -n ks-hybrid-cloud-poc
```

This creates:

- ImageStream: `app`
- BuildConfig: `app-build` (pulls from GitHub, builds `app/Containerfile`)

Note: the BuildConfig has a `ConfigChange` trigger, so creating it kicks off
`app-build-1` automatically. A manual `oc start-build` then queues
`app-build-2`; the first build is the one to follow.

## 4. Start / Follow the Build

```bash
oc start-build app-build -n ks-hybrid-cloud-poc
oc logs -f build/app-build-1 -n ks-hybrid-cloud-poc
```

Wait for `Push successful`. The image lands at
`image-registry.openshift-image-registry.svc:5000/ks-hybrid-cloud-poc/app:latest`.

## 5. Configure the `production` Profile

The `production` profile reads the database connection from environment
variables, NOT from `app/config.yaml` (that file is gitignored, so it is
**not** present in the image built from GitHub). Supply the connection via a
ConfigMap and a Secret.

IMPORTANT: Without `DATABASE_URI` set in `production`, the app crashes at
startup with `TypeError: not all arguments converted during string
formatting`, because `config.py` tries to interpolate an empty URI.

Create the ConfigMap (profile + DB URI, password left as the `%s` placeholder):

```bash
oc create configmap app-config \
  --from-literal=PROFILE=production \
  --from-literal=FLASK_APP=app.app \
  --from-literal=DATABASE_URI='mssql+pyodbc://hybrid_usr:%s@192.168.66.147:9677/hybrid_poc?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=yes&TrustServerCertificate=yes' \
  -n ks-hybrid-cloud-poc \
  --dry-run=client -o yaml | oc apply -f -
```

Create the Secret (DB password — never bake this into the image or ConfigMap):

```bash
oc create secret generic app-db-secret \
  --from-literal=DATABASE_PASSWORD='<db-password>' \
  -n ks-hybrid-cloud-poc \
  --dry-run=client -o yaml | oc apply -f -
```

## 6. Deploy the Application

```bash
oc apply -f oc/fix/app-service.yml -n ks-hybrid-cloud-poc
oc apply -f oc/fix/app-deployment.yml -n ks-hybrid-cloud-poc
```

`app-deployment.yml` loads env only from the `app-config` ConfigMap. Patch it
once to also load the DB password from the Secret:

```bash
oc patch deployment python-app -n ks-hybrid-cloud-poc --type=json \
  -p='[{"op":"add","path":"/spec/template/spec/containers/0/envFrom/-","value":{"secretRef":{"name":"app-db-secret"}}}]'
```

This creates:

- Service: `app-service` (ClusterIP, port 5000)
- Deployment: `python-app`

## 7. Expose with a Route

Simple edge-terminated route on the default cluster domain:

```bash
oc create route edge app-route --service=app-service --port=5000 -n ks-hybrid-cloud-poc
oc get route app-route -n ks-hybrid-cloud-poc -o jsonpath='{.spec.host}'
```

For the custom `uat-hybridcloud.krungsri.com` hostname with the DigiCert
certificate and the dedicated AWS NLB, use `oc/fix/app-route.yml` and
`oc/fix/ingresscontroller.yml` instead. Note: `oc/fix/ingresscontroller.yml`
still carries an old cluster's `domain`
(`poc.apps.rosa.r0r7f1m1d7w4r0m...`); update it to the current apps domain
before applying on this cluster.

## 8. Verify Deployment

```bash
oc rollout status deployment/python-app -n ks-hybrid-cloud-poc
oc get pods -l app=python-app -n ks-hybrid-cloud-poc
oc get route app-route -n ks-hybrid-cloud-poc -o jsonpath='{.spec.host}'
curl -sk -o /dev/null -w "HTTP %{http_code}\n" https://$(oc get route app-route -n ks-hybrid-cloud-poc -o jsonpath='{.spec.host}')/
```

Expect `HTTP 200` from `/`.

## 9. View Logs

```bash
oc logs -f deployment/python-app -n ks-hybrid-cloud-poc
```

## Update Deployment

After code changes:

```bash
oc start-build app-build -n ks-hybrid-cloud-poc --follow
oc rollout restart deployment/python-app -n ks-hybrid-cloud-poc
```

## Configuration Updates

To change the DB connection, update the ConfigMap/Secret from step 5, then:

```bash
oc rollout restart deployment/python-app -n ks-hybrid-cloud-poc
```

## Troubleshooting

- `TypeError: not all arguments converted during string formatting` in the
  pod log: `DATABASE_URI` is missing for the `production` profile. Set it in
  the `app-config` ConfigMap (step 5).
- `Login failed for user 'hybrid_usr' (18456)` in the pod log: the app reached
  the external MSSQL host (network is fine) but the DB rejected the
  credentials. Fix the password in `app-db-secret` or the user/grants on the
  SQL Server. The app still serves `/` even while DB login fails.
