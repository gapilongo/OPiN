

# WAF Configuration
resource "aws_wafv2_web_acl" "main" {
  name        = "opin-waf-${var.environment}"
  description = "WAF for OPiN application"
  scope       = "REGIONAL"

  default_action {
    allow {}
  }

  # Rate limiting rule
  rule {
    name     = "RateLimit"
    priority = 1

    override_action {
      none {}
    }

    statement {
      rate_based_statement {
        limit              = 2000
        aggregate_key_type = "IP"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name               = "RateLimitRule"
      sampled_requests_enabled  = true
    }
  }

  # SQL Injection protection
  rule {
    name     = "SQLInjectionProtection"
    priority = 2

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesSQLiRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name               = "SQLInjectionProtectionRule"
      sampled_requests_enabled  = true
    }
  }

  # Common vulnerabilities protection
  rule {
    name     = "CommonVulnerabilities"
    priority = 3

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesCommonRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name               = "CommonVulnerabilitiesRule"
      sampled_requests_enabled  = true
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name               = "OPiNWAF"
    sampled_requests_enabled  = true
  }
}

# Associate WAF with ALB
resource "aws_wafv2_web_acl_association" "main" {
  resource_arn = module.alb.lb_arn
  web_acl_arn  = aws_wafv2_web_acl.main.arn
}

# SSL/TLS Certificate
resource "aws_acm_certificate" "main" {
  domain_name       = var.domain_name
  validation_method = "DNS"

  subject_alternative_names = [
    "*.${var.domain_name}"
  ]

  lifecycle {
    create_before_destroy = true
  }

  tags = {
    Environment = var.environment
    Project     = "OPiN"
  }
}

# Certificate validation
resource "aws_acm_certificate_validation" "main" {
  certificate_arn         = aws_acm_certificate.main.arn
  validation_record_fqdns = [for record in aws_route53_record.cert_validation : record.fqdn]
}

# DNS validation records
resource "aws_route53_record" "cert_validation" {
  for_each = {
    for dvo in aws_acm_certificate.main.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = aws_route53_zone.main.zone_id
}

# File: backend/app/middleware/security.py

from fastapi import FastAPI, Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
import secure

# Create security headers middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # CSP Headers
        csp = secure.ContentSecurityPolicy()
        csp.default_src("'self'")
        csp.script_src("'self'", "'unsafe-inline'", "'unsafe-eval'")
        csp.style_src("'self'", "'unsafe-inline'")
        csp.img_src("'self'", "data:", "https:")
        csp.font_src("'self'", "https:", "data:")
        csp.connect_src("'self'", "https:")
        
        # Add security headers
        secure_headers = secure.Secure()
        secure_headers.xssfilter.on()
        secure_headers.contenttype.nosniff()
        secure_headers.xframe.deny()
        secure_headers.referrer.no_referrer()
        secure_headers.hsts.include_subdomains().preload().max_age(31536000)
        secure_headers.csp = csp
        
        # Apply headers to response
        for header, value in secure_headers.headers().items():
            response.headers[header] = value
            
        return response

# Rate limiting middleware
class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: FastAPI,
        redis_client,
        rate_limit: int = 100,
        window: int = 60
    ):
        super().__init__(app)
        self.redis_client = redis_client
        self.rate_limit = rate_limit
        self.window = window

    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = request.client.host
        
        # Create Redis key
        key = f"rate_limit:{client_ip}"
        
        # Check rate limit
        requests = await self.redis_client.incr(key)
        if requests == 1:
            await self.redis_client.expire(key, self.window)
            
        if requests > self.rate_limit:
            return Response(
                content="Rate limit exceeded",
                status_code=429
            )
            
        return await call_next(request)

# File: backend/app/core/security.py (additional functions)

from cryptography.fernet import Fernet
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
encryption_key = Fernet.generate_key()
fernet = Fernet(encryption_key)

def encrypt_sensitive_data(data: str) -> str:
    """Encrypt sensitive data"""
    return fernet.encrypt(data.encode()).decode()

def decrypt_sensitive_data(encrypted_data: str) -> str:
    """Decrypt sensitive data"""
    return fernet.decrypt(encrypted_data.encode()).decode()

def create_access_token(
    data: dict,
    expires_delta: timedelta = timedelta(minutes=15)
) -> str:
    """Create JWT token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)

# Add these configurations to backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.ALLOWED_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    RateLimitMiddleware,
    redis_client=redis_client,
    rate_limit=settings.RATE_LIMIT_PER_MINUTE
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)