

#!/bin/bash
set -e

# Check environment argument
if [ -z "$1" ]; then
  echo "Please specify environment (dev/staging/prod)"
  exit 1
fi

ENV=$1
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$SCRIPT_DIR/.."

# Load environment variables
source "$PROJECT_ROOT/config/$ENV.env"

# Initialize Terraform
cd "$PROJECT_ROOT/terraform"
terraform init

# Apply Terraform configuration
terraform apply -var-file="$ENV.tfvars" -auto-approve

# Update ECS services
aws ecs update-service --cluster opin-cluster --service opin-backend --force-new-deployment
aws ecs update-service --cluster opin-cluster --service opin-frontend --force-new-deployment

# Wait for services to stabilize
aws ecs wait services-stable --cluster opin-cluster --services opin-backend opin-frontend

echo "Deployment to $ENV completed successfully"

# File: config/dev.env

# AWS Configuration
AWS_REGION=us-east-1
ENVIRONMENT=dev
DOMAIN_NAME=dev.opin.example.com

# Database Configuration
DB_USERNAME=opin_dev
DB_PASSWORD=your_secure_password_here

# Application Configuration
API_URL=https://api.dev.opin.example.com
DEBUG=true
LOG_LEVEL=debug

# File: config/staging.env

# AWS Configuration
AWS_REGION=us-east-1
ENVIRONMENT=staging
DOMAIN_NAME=staging.opin.example.com

# Database Configuration
DB_USERNAME=opin_staging
DB_PASSWORD=your_secure_password_here

# Application Configuration
API_URL=https://api.staging.opin.example.com
DEBUG=false
LOG_LEVEL=info

# File: config/prod.env

# AWS Configuration
AWS_REGION=us-east-1
ENVIRONMENT=prod
DOMAIN_NAME=opin.example.com

# Database Configuration
DB_USERNAME=opin_prod
DB_PASSWORD=your_secure_password_here

# Application Configuration
API_URL=https://api.opin.example.com
DEBUG=false
LOG_LEVEL=info

# File: scripts/backup.sh

#!/bin/bash
set -e

# Check environment argument
if [ -z "$1" ]; then
  echo "Please specify environment (dev/staging/prod)"
  exit 1
fi

ENV=$1
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/$ENV/$TIMESTAMP"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup RDS database
aws rds create-db-snapshot \
  --db-instance-identifier "opin-$ENV" \
  --db-snapshot-identifier "opin-$ENV-$TIMESTAMP"

# Backup Redis (if needed)
# Add Redis backup logic here

# Backup application data
aws s3 sync "s3://opin-$ENV-data" "$BACKUP_DIR/data"

echo "Backup completed: $BACKUP_DIR"

# File: scripts/monitoring.sh

#!/bin/bash
set -e

# Check environment argument
if [ -z "$1" ]; then
  echo "Please specify environment (dev/staging/prod)"
  exit 1
fi

ENV=$1

# Create CloudWatch dashboard
aws cloudwatch put-dashboard \
  --dashboard-name "OPiN-$ENV" \
  --dashboard-body file://monitoring/dashboard.json

# Create alarms
aws cloudwatch put-metric-alarm \
  --alarm-name "OPiN-$ENV-CPU-High" \
  --alarm-description "CPU utilization high" \
  --metric-name CPUUtilization \
  --namespace AWS/ECS \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2 \
  --alarm-actions "arn:aws:sns:us-east-1:123456789012:OPiN-Alerts"

# File: monitoring/dashboard.json

{
  "widgets": [
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AWS/ECS", "CPUUtilization", "ServiceName", "opin-backend"],
          ["AWS/ECS", "CPUUtilization", "ServiceName", "opin-frontend"]
        ],
        "period": 300,
        "stat": "Average",
        "region": "us-east-1",
        "title": "CPU Utilization"
      }
    },
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AWS/ECS", "MemoryUtilization", "ServiceName", "opin-backend"],
          ["AWS/ECS", "MemoryUtilization", "ServiceName", "opin-frontend"]
        ],
        "period": 300,
        "stat": "Average",
        "region": "us-east-1",
        "title": "Memory Utilization"
      }
    },
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AWS/ApplicationELB", "RequestCount", "LoadBalancer", "opin-alb"]
        ],
        "period": 300,
        "stat": "Sum",
        "region": "us-east-1",
        "title": "Request Count"
      }
    }
  ]
}