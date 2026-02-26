# Certificate Configuration Guide (Edge Termination)

This guide explains how to configure HTTPS for your public-facing URL using **Edge Termination**. This means OpenShift terminates the SSL at the router, and internal cluster traffic remains HTTP.

## Certificate Overview

- **Server Certificate**: `uat-hybridcloud_krungsri_com_1458327455.crt`
- **Private Key**: `uat-hyb/uat-hyb.key`
- **CA Chain**: `DigiCertCA.crt` and `TrustedRoot.crt`

## 1. Configure OpenShift Route

To enable https for your application:

### Option A: Via YAML Manifest (Recommended)

Update your route in `oc/app-deployment.yml`:

```yaml
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: app-route
spec:
  to:
    kind: Service
    name: app-service
  port:
    targetPort: 5000
  tls:
    termination: edge
    certificate: |
      -----BEGIN CERTIFICATE-----
      # Content from certs/uat-hybridcloud_krungsri_com_1458327455.crt
      -----END CERTIFICATE-----
    key: |
      -----BEGIN EC PRIVATE KEY-----
      # Content from certs/uat-hyb/uat-hyb.key
      -----END EC PRIVATE KEY-----
    caCertificate: |
      -----BEGIN CERTIFICATE-----
      # Content from certs/TrustedRoot.crt
      -----END CERTIFICATE-----
```

### Option B: Via command line

```bash
oc create route edge app-route \
    --service=app-service \
    --cert=" certs/uat-hybridcloud_krungsri_com_1458327455.crt" \
    --key=" certs/uat-hyb/uat-hyb.key" \
    --ca-cert=" certs/TrustedRoot.crt"
```

## 2. Verify Internal Connectivity

Since you are using **Edge Termination**, the application itself doesn't need to be aware of SSL:

1. The Flask app will continue to run on `http://0.0.0.0:5000`.
2. Internal pods can reach the app via `http://app-service:5000`.
3. External users will access the app via `https://your-route-url`.
