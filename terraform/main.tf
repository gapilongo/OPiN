
provider "aws" {
  region = var.aws_region
}

# VPC Configuration
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"

  name = "opin-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["${var.aws_region}a", "${var.aws_region}b"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24"]

  enable_nat_gateway = true
  single_nat_gateway = true

  tags = {
    Environment = var.environment
    Project     = "OPiN"
  }
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "opin-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

# Application Load Balancer
module "alb" {
  source  = "terraform-aws-modules/alb/aws"
  version = "~> 6.0"

  name = "opin-alb"

  vpc_id          = module.vpc.vpc_id
  subnets         = module.vpc.public_subnets
  security_groups = [aws_security_group.alb.id]

  target_groups = [
    {
      name             = "opin-backend"
      backend_protocol = "HTTP"
      backend_port     = 8000
      target_type      = "ip"
      health_check = {
        path                = "/health"
        healthy_threshold   = 2
        unhealthy_threshold = 10
      }
    },
    {
      name             = "opin-frontend"
      backend_protocol = "HTTP"
      backend_port     = 3000
      target_type      = "ip"
      health_check = {
        path                = "/"
        healthy_threshold   = 2
        unhealthy_threshold = 10
      }
    }
  ]

  http_tcp_listeners = [
    {
      port               = 80
      protocol           = "HTTP"
      target_group_index = 0
    }
  ]
}

# ECS Services
resource "aws_ecs_service" "backend" {
  name            = "opin-backend"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.backend.arn
  desired_count   = 2

  network_configuration {
    subnets         = module.vpc.private_subnets
    security_groups = [aws_security_group.ecs_tasks.id]
  }

  load_balancer {
    target_group_arn = module.alb.target_group_arns[0]
    container_name   = "backend"
    container_port   = 8000
  }

  capacity_provider_strategy {
    capacity_provider = "FARGATE"
    weight           = 1
  }
}

resource "aws_ecs_service" "frontend" {
  name            = "opin-frontend"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.frontend.arn
  desired_count   = 2

  network_configuration {
    subnets         = module.vpc.private_subnets
    security_groups = [aws_security_group.ecs_tasks.id]
  }

  load_balancer {
    target_group_arn = module.alb.target_group_arns[1]
    container_name   = "frontend"
    container_port   = 3000
  }

  capacity_provider_strategy {
    capacity_provider = "FARGATE"
    weight           = 1
  }
}

# RDS Database
module "db" {
  source  = "terraform-aws-modules/rds/aws"
  version = "~> 3.0"

  identifier = "opin-db"

  engine               = "postgres"
  engine_version       = "13.4"
  family              = "postgres13"
  major_engine_version = "13"
  instance_class      = "db.t3.medium"

  allocated_storage     = 20
  max_allocated_storage = 100

  name     = "opindb"
  username = var.db_username
  password = var.db_password
  port     = 5432

  multi_az               = false
  subnet_ids             = module.vpc.private_subnets
  vpc_security_group_ids = [aws_security_group.rds.id]

  maintenance_window = "Mon:00:00-Mon:03:00"
  backup_window      = "03:00-06:00"

  backup_retention_period = 7
  skip_final_snapshot    = true

  tags = {
    Environment = var.environment
    Project     = "OPiN"}
}

# ElastiCache Redis
resource "aws_elasticache_cluster" "redis" {
  cluster_id           = "opin-redis"
  engine              = "redis"
  node_type           = "cache.t3.micro"
  num_cache_nodes     = 1
  parameter_group_name = "default.redis6.x"
  port                = 6379
  security_group_ids  = [aws_security_group.redis.id]
  subnet_group_name   = aws_elasticache_subnet_group.redis.name
}

resource "aws_elasticache_subnet_group" "redis" {
  name       = "opin-redis-subnet-group"
  subnet_ids = module.vpc.private_subnets
}

# MSK (Managed Streaming for Kafka)
resource "aws_msk_cluster" "kafka" {
  cluster_name           = "opin-kafka"
  kafka_version          = "2.8.1"
  number_of_broker_nodes = 2

  broker_node_group_info {
    instance_type = "kafka.t3.small"
    client_subnets = module.vpc.private_subnets
    storage_info {
      ebs_storage_info {
        volume_size = 20
      }
    }
    security_groups = [aws_security_group.kafka.id]
  }

  encryption_info {
    encryption_at_rest_kms_key_arn = aws_kms_key.kafka.arn
  }
}

# CloudWatch Log Groups
resource "aws_cloudwatch_log_group" "backend" {
  name              = "/ecs/opin-backend"
  retention_in_days = 30
}

resource "aws_cloudwatch_log_group" "frontend" {
  name              = "/ecs/opin-frontend"
  retention_in_days = 30
}

# Security Groups
resource "aws_security_group" "alb" {
  name        = "opin-alb-sg"
  description = "ALB Security Group"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "ecs_tasks" {
  name        = "opin-ecs-tasks-sg"
  description = "ECS Tasks Security Group"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port       = 0
    to_port         = 0
    protocol        = "-1"
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "rds" {
  name        = "opin-rds-sg"
  description = "RDS Security Group"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_tasks.id]
  }
}

resource "aws_security_group" "redis" {
  name        = "opin-redis-sg"
  description = "Redis Security Group"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_tasks.id]
  }
}

resource "aws_security_group" "kafka" {
  name        = "opin-kafka-sg"
  description = "Kafka Security Group"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port       = 9092
    to_port         = 9092
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_tasks.id]
  }
}

# KMS Keys
resource "aws_kms_key" "kafka" {
  description = "KMS key for Kafka encryption"
}

# S3 Buckets
resource "aws_s3_bucket" "logs" {
  bucket = "opin-logs-${var.environment}"
}

resource "aws_s3_bucket_versioning" "logs" {
  bucket = aws_s3_bucket.logs.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "logs" {
  bucket = aws_s3_bucket.logs.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Route53 DNS
resource "aws_route53_zone" "main" {
  name = var.domain_name
}

resource "aws_route53_record" "api" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "api.${var.domain_name}"
  type    = "A"

  alias {
    name                   = module.alb.lb_dns_name
    zone_id                = module.alb.lb_zone_id
    evaluate_target_health = true
  }
}

# Variables file
# File: terraform/variables.tf

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "domain_name" {
  description = "Domain name for the application"
  type        = string
}

variable "db_username" {
  description = "Database username"
  type        = string
  sensitive   = true
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

# Outputs file
# File: terraform/outputs.tf

output "alb_dns_name" {
  description = "DNS name of the load balancer"
  value       = module.alb.lb_dns_name
}

output "rds_endpoint" {
  description = "RDS instance endpoint"
  value       = module.db.db_instance_endpoint
  sensitive   = true
}

output "kafka_brokers" {
  description = "Kafka broker endpoints"
  value       = aws_msk_cluster.kafka.bootstrap_brokers
  sensitive   = true
}

output "redis_endpoint" {
  description = "Redis endpoint"
  value       = aws_elasticache_cluster.redis.cache_nodes[0].address
  sensitive   = true
}
Last edited 3 minute