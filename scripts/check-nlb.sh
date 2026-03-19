#!/bin/bash

# ==========================================================
# CONFIGURATION
# ==========================================================
PROFILE="app-poc"
REGION="ap-southeast-7"
LB_DNS="hybrid-cloud-nlb-680b81437b61b55f.elb.ap-southeast-7.amazonaws.com"

# The ports you identified
TARGET_PORTS=(32150 30837)

# Disable the AWS pager
export AWS_PAGER=""

printf "==========================================================\n"
printf "STEP 1: AWS TARGET GROUP HEALTH CHECK\n"
printf "==========================================================\n"

LB_ARN=$(aws elbv2 describe-load-balancers --profile "$PROFILE" --region "$REGION" \
    --query "LoadBalancers[?DNSName=='$LB_DNS'].LoadBalancerArn" \
    --output text)

# Find Target Groups matching your specific ports
for PORT in "${TARGET_PORTS[@]}"; do
    printf "\n>>> Checking AWS Target Group for Port: %s\n" "$PORT"
    TG_ARN=$(aws elbv2 describe-target-groups --profile "$PROFILE" --region "$REGION" \
        --load-balancer-arn "$LB_ARN" \
        --query "TargetGroups[?Port==\`$PORT\`].TargetGroupArn" --output text)

    if [[ -z "$TG_ARN" || "$TG_ARN" == "None" ]]; then
        printf "    [!] ALERT: No AWS Target Group found listening on port %s\n" "$PORT"
    else
        aws elbv2 describe-target-health --profile "$PROFILE" --region "$REGION" \
            --target-group-arn "$TG_ARN" \
            --query "TargetHealthDescriptions[*].{ID:Target.Id, Status:TargetHealth.State, Reason:TargetHealth.Description}" \
            --output table
    fi
done

printf "\n==========================================================\n"
printf "STEP 2: OPENSHIFT SERVICE MAPPING\n"
printf "==========================================================\n"

for NP in "${TARGET_PORTS[@]}"; do
    printf "--- Analyzing NodePort: %s ---\n" "$NP"
    
    # Locate Service by Port
    SVC_DATA=$(oc get svc -A -o json | jq -r ".items[] | select(.spec.ports[].nodePort == $NP) | .metadata.namespace + \" \" + .metadata.name" 2>/dev/null)
    
    if [[ -z "$SVC_DATA" ]]; then
        printf "    [!] ERROR: Port %s is NOT assigned to any Service in OpenShift.\n" "$NP"
    else
        echo "$SVC_DATA" | while read -r NS SVC; do
            printf "    [+] Found: %s / %s\n" "$NS" "$SVC"
            
            # Check for Endpoints (The "Sometimes" culprit)
            EP_COUNT=$(oc get endpoints "$SVC" -n "$NS" -o jsonpath='{range .subsets[*]}{.addresses[*].ip}{" "}{end}' | wc -w)
            printf "    [+] Ready Pods: %s\n" "$EP_COUNT"
            
            if [ "$EP_COUNT" -eq 0 ]; then
                printf "    [CRITICAL] Service exists but has NO running pods!\n"
            fi

            # Check Traffic Policy
            POLICY=$(oc get svc "$SVC" -n "$NS" -o jsonpath='{.spec.externalTrafficPolicy}')
            printf "    [+] Policy: %s\n" "$POLICY"

            # Check Pod status and which Node they are on
            SELECTOR=$(oc get svc "$SVC" -n "$NS" -o jsonpath='{.spec.selector}' | jq -r 'to_entries | .[0].key + "=" + .[0].value')
            oc get pods -n "$NS" -l "$SELECTOR" -o wide | sed 's/^/      /'
        done
    fi
done

printf "\n==========================================================\n"
printf "STEP 3: CONNECTIVITY TEST\n"
printf "==========================================================\n"

for i in {1..5}; do
    # Testing Port 443 (Standard for OCP Routes)
    printf "Request #%s: " "$i"
    curl -I -k -s --connect-timeout 2 -o /dev/null \
        -w "HTTP %{http_code} | Time: %{time_total}s\n" \
        "https://$LB_DNS"
done

printf "\nTroubleshooting Complete.\n"
