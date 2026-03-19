#!/bin/bash
INGRESS_NAME="ingresscontroller.operator.openshift.io/default"

printf "==========================================================\n"
printf "INGRESS CONTROLLER CONFIGURATION: %s\n" "$INGRESS_NAME"
printf "==========================================================\n"

# Get the Policy
POLICY=$(oc get "$INGRESS_NAME" -n openshift-ingress-operator -o jsonpath='{.spec.endpointPublishingStrategy.nodePort.externalTrafficPolicy}')
printf "Traffic Policy:  %s\n" "$POLICY"

# Get the Ports
HTTP_PORT=$(oc get "$INGRESS_NAME" -n openshift-ingress-operator -o jsonpath='{.status.endpointPublishingStrategy.nodePort.protocolMetadata[?(@.protocol=="http")].nodePort}')
HTTPS_PORT=$(oc get "$INGRESS_NAME" -n openshift-ingress-operator -o jsonpath='{.status.endpointPublishingStrategy.nodePort.protocolMetadata[?(@.protocol=="https")].nodePort}')

printf "HTTP NodePort:   %s\n" "$HTTP_PORT"
printf "HTTPS NodePort:  %s\n" "$HTTPS_PORT"

# Check Pod Placement
printf "\nRouter Pod Placement:\n"
oc get pods -n openshift-ingress -l ingresscontroller.operator.openshift.io/deployment-ingresscontroller=default -o wide