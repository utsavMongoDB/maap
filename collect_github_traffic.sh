#!/bin/bash
# Script to collect GitHub traffic data for multiple repos and save as JSON
# Usage: bash collect_github_traffic.sh
source .env
OWNER="mongodb-partners"
REPOS=(
  "maap-framework"
  "maap-anthropic-qs"
  "maap-arcee-qs"
  "maap-meta-qs"
  "langchain-qs"
  "maap-cohere-qs"
  "maap-together-qs"
  "maap-confluent-qs"
  "maap-confluent-gcp-qs"
  "maap-temporal-qs"
)
GITHUB_TOKEN="$GITHUB_TOKEN"
OUTPUT_FILE="github_traffic_daily.json"

if [ -z "$GITHUB_TOKEN" ]; then
  echo "Error: GITHUB_TOKEN environment variable not set."
  exit 1
fi

TMP_FILE="github_traffic_daily_tmp.json"

# If OUTPUT_FILE exists, read previous data
if [ -f "$OUTPUT_FILE" ]; then
  PREV_DATA=$(cat "$OUTPUT_FILE")
else
  PREV_DATA="[]"
fi

# Get current timestamp
CURRENT_TIME=$(date -Iseconds)

echo "[" > "$TMP_FILE"
for i in "${!REPOS[@]}"; do
  REPO="${REPOS[$i]}"
  echo "Collecting data for $OWNER/$REPO..."
  DATA=$(curl -s -H "Authorization: token $GITHUB_TOKEN" -H "Accept: application/vnd.github.v3+json" \
    "https://api.github.com/repos/$OWNER/$REPO/traffic/views")
  CLONES=$(curl -s -H "Authorization: token $GITHUB_TOKEN" -H "Accept: application/vnd.github.v3+json" \
    "https://api.github.com/repos/$OWNER/$REPO/traffic/clones")

  # Get previous values for this repo
  PREV_REPO=$(echo "$PREV_DATA" | jq -c ".[] | select(.repository == \"$OWNER/$REPO\")")
  PREV_VIEWS=$(echo "$PREV_REPO" | jq ".views.count" 2>/dev/null)
  PREV_CLONES=$(echo "$PREV_REPO" | jq ".clones.count" 2>/dev/null)
  CUR_VIEWS=$(echo "$DATA" | jq ".count" 2>/dev/null)
  CUR_CLONES=$(echo "$CLONES" | jq ".count" 2>/dev/null)

  # Calculate delta and increment
  if [ -z "$PREV_VIEWS" ] || [ "$PREV_VIEWS" == "null" ]; then PREV_VIEWS=0; fi
  if [ -z "$PREV_CLONES" ] || [ "$PREV_CLONES" == "null" ]; then PREV_CLONES=0; fi
  if [ -z "$CUR_VIEWS" ] || [ "$CUR_VIEWS" == "null" ]; then CUR_VIEWS=0; fi
  if [ -z "$CUR_CLONES" ] || [ "$CUR_CLONES" == "null" ]; then CUR_CLONES=0; fi

  INC_VIEWS=$((CUR_VIEWS - PREV_VIEWS))
  INC_CLONES=$((CUR_CLONES - PREV_CLONES))
  TOTAL_VIEWS=$((PREV_VIEWS + INC_VIEWS))
  TOTAL_CLONES=$((PREV_CLONES + INC_CLONES))

  # Update views and clones JSON with incremented totals
  DATA=$(echo "$DATA" | jq ".count = $TOTAL_VIEWS")
  CLONES=$(echo "$CLONES" | jq ".count = $TOTAL_CLONES")

  REPO_JSON="{  \"repository\": \"$OWNER/$REPO\",  \"collected_at\": \"$(date -Iseconds)\",  \"views\": $DATA,  \"clones\": $CLONES}"
  echo "$REPO_JSON" >> "$TMP_FILE"
  if [ "$i" -lt $((${#REPOS[@]}-1)) ]; then
    echo "," >> "$TMP_FILE"
  fi
done
echo "]" >> "$TMP_FILE"

# Add timestamp to JSON file before finalizing
TMP_WITH_TIMESTAMP=$(cat "$TMP_FILE")
echo "{\"last_updated\": \"$CURRENT_TIME\", \"data\": $TMP_WITH_TIMESTAMP}" > "$OUTPUT_FILE"

echo "Data collection complete. Saved to $OUTPUT_FILE with timestamp: $CURRENT_TIME"
