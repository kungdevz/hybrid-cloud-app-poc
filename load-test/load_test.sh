#!/bin/bash

URL=$1
CONCURRENCY=10
DURATION=300 # 5 minutes

if [ -z "$URL" ]; then
  echo "Usage: $0 <url>"
  exit 1
fi

echo "Starting load test on $URL with $CONCURRENCY concurrent threads for $DURATION seconds..."

end_time=$((SECONDS + DURATION))

while [ $SECONDS -lt $end_time ]; do
  for i in $(seq 1 $CONCURRENCY); do
    curl -s -o /dev/null -w "%{http_code}\n" "$URL/users" &
  done
  wait
done

echo "Load test finished."
