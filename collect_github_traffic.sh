#!/bin/bash
# Script to collect GitHub traffic data for multiple repos and save as JSON
# Usage: bash collect_github_traffic.sh

# Source .env file if it exists
if [ -f ".env" ]; then
  source .env
  echo "Loaded environment variables from .env file"
else
  echo "No .env file found, using environment variables from system"
fi
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
  "ai-memory"
)

# Function to get start value for a repo
get_start_value() {
  local repo=$1
  case $repo in
    "maap-framework") echo 142 ;;
    "maap-anthropic-qs") echo 11 ;;
    "maap-arcee-qs") echo 2 ;;
    "maap-meta-qs") echo 6 ;;
    "langchain-qs") echo 18 ;;
    "maap-cohere-qs") echo 24 ;;
    "maap-together-qs") echo 2 ;;
    "maap-confluent-qs") echo 8 ;;
    "maap-confluent-gcp-qs") echo 2 ;;
    "maap-temporal-qs") echo 27 ;;
    "ai-memory") echo 164 ;;
    *) echo 0 ;;
  esac
}
OUTPUT_FILE="github_traffic_daily.json"

# Validate GitHub token
if [ -z "$GITHUB_TOKEN" ]; then
  echo "Error: GITHUB_TOKEN environment variable not set."
  exit 1
fi

echo "GitHub token is set, proceeding with data collection"

TMP_FILE="github_traffic_daily_tmp.json"

# If OUTPUT_FILE exists, read previous data
if [ -f "$OUTPUT_FILE" ]; then
  # Handle both the old format (array) and new format (object with data property)
  FIRST_CHAR=$(head -c 1 "$OUTPUT_FILE")
  if [ "$FIRST_CHAR" = "{" ]; then
    # New format with data property
    PREV_DATA=$(jq -r '.data' "$OUTPUT_FILE")
  else
    # Old format (direct array)
    PREV_DATA=$(cat "$OUTPUT_FILE")
  fi
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

  # Debug info about the JSON structure
  echo "Processing $OWNER/$REPO with PREV_DATA format:"
  echo "$PREV_DATA" | head -n 1
  
  # Get previous values for this repo with error handling
  PREV_REPO=$(echo "$PREV_DATA" | jq -c ".[] | select(.repository == \"$OWNER/$REPO\")" 2>/tmp/jq_error.log || echo "{}")
  if [ -s /tmp/jq_error.log ]; then
    echo "WARNING: jq error occurred when selecting repo data:"
    cat /tmp/jq_error.log
    echo "Creating empty repo data as fallback"
    PREV_REPO="{}"
  fi
  
  PREV_VIEWS=$(echo "$PREV_REPO" | jq ".views.count" 2>/dev/null || echo 0)
  PREV_CLONES=$(echo "$PREV_REPO" | jq ".clones.count" 2>/dev/null || echo 0)
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

  # Apply the start value for views
  START_VALUE=$(get_start_value "$REPO")
  TOTAL_VIEWS=$((TOTAL_VIEWS + START_VALUE))

  # Update views and clones JSON with incremented totals
  DATA=$(echo "$DATA" | jq ".count = $TOTAL_VIEWS")
  CLONES=$(echo "$CLONES" | jq ".count = $TOTAL_CLONES")

  START_VALUE=$(get_start_value "$REPO")
  REPO_JSON="{  \"repository\": \"$OWNER/$REPO\",  \"collected_at\": \"$(date -Iseconds)\",  \"views\": $DATA,  \"clones\": $CLONES,  \"start_value\": $START_VALUE}"
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
