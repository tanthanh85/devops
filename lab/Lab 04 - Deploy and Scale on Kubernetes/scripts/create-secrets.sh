#!/usr/bin/env bash
set -euo pipefail
namespace=network-devops
if kubectl -n "$namespace" get secret network-monitor-secrets >/dev/null 2>&1; then
  echo "network-monitor-secrets already exists; preserving the current database and encryption keys."
  exit 0
fi
mysql_database=network_monitor
mysql_user=network_app
mysql_password=$(openssl rand -hex 18)
mysql_root_password=$(openssl rand -hex 18)
flask_secret=$(openssl rand -hex 32)
database_url="mysql+pymysql://${mysql_user}:${mysql_password}@mysql:3306/${mysql_database}"
kubectl -n "$namespace" create secret generic network-monitor-secrets \
  --from-literal=MYSQL_PASSWORD="$mysql_password" \
  --from-literal=MYSQL_ROOT_PASSWORD="$mysql_root_password" \
  --from-literal=DATABASE_URL="$database_url" \
  --from-literal=FLASK_SECRET_KEY="$flask_secret" \
  --dry-run=client -o yaml | kubectl apply -f -
echo "Created network-monitor-secrets without writing values to disk."
