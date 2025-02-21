
#!/bin/bash
set -e

# Configuration
ENVIRONMENT=${ENVIRONMENT:-"production"}
BACKUP_BUCKET="opin-backups-${ENVIRONMENT}"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

# Load environment variables
source .env.${ENVIRONMENT}

echo "Starting backup process for ${ENVIRONMENT}..."

# Backup PostgreSQL database
PGPASSWORD=${DATABASE_PASSWORD} pg_dump \
  -h ${DATABASE_HOST} \
  -U ${DATABASE_USER} \
  -d ${DATABASE_NAME} \
  -F c \
  -f /tmp/db-backup-${TIMESTAMP}.dump

# Upload database backup to S3
aws s3 cp /tmp/db-backup-${TIMESTAMP}.dump \
  s3://${BACKUP_BUCKET}/database/db-backup-${TIMESTAMP}.dump

# Backup Redis data
redis-cli -h ${REDIS_HOST} -p ${REDIS_PORT} \
  -a ${REDIS_PASSWORD} --rdb /tmp/redis-backup-${TIMESTAMP}.rdb

# Upload Redis backup to S3
aws s3 cp /tmp/redis-backup-${TIMESTAMP}.rdb \
  s3://${BACKUP_BUCKET}/redis/redis-backup-${TIMESTAMP}.rdb

# Cleanup temporary files
rm /tmp/db-backup-${TIMESTAMP}.dump
rm /tmp/redis-backup-${TIMESTAMP}.rdb

echo "Backup completed successfully!"

