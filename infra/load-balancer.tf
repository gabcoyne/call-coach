# =============================================================================
# Load Balancer with IAP for Cloud Run Services
# =============================================================================
#
# This configuration creates a Global External Application Load Balancer
# with Identity-Aware Proxy (IAP) to provide authenticated access to
# Cloud Run services for users in the prefect.io domain.

# =============================================================================
# Serverless NEGs (Network Endpoint Groups) for Cloud Run
# =============================================================================

resource "google_compute_region_network_endpoint_group" "frontend_neg" {
  name                  = "call-coach-frontend-neg"
  network_endpoint_type = "SERVERLESS"
  region                = var.region
  project               = var.project_id

  cloud_run {
    service = module.frontend_service.service_name
  }
}

resource "google_compute_region_network_endpoint_group" "api_neg" {
  name                  = "call-coach-api-neg"
  network_endpoint_type = "SERVERLESS"
  region                = var.region
  project               = var.project_id

  cloud_run {
    service = module.api_service.service_name
  }
}

# =============================================================================
# Backend Services
# =============================================================================

resource "google_compute_backend_service" "frontend" {
  name     = "call-coach-frontend-backend"
  project  = var.project_id
  protocol = "HTTPS"
  # Note: timeout_sec not supported with serverless NEGs

  backend {
    group = google_compute_region_network_endpoint_group.frontend_neg.id
  }

  # Enable IAP
  iap {
    oauth2_client_id     = google_iap_client.call_coach.client_id
    oauth2_client_secret = google_iap_client.call_coach.secret
  }

  log_config {
    enable      = true
    sample_rate = 1.0
  }
}

resource "google_compute_backend_service" "api" {
  name     = "call-coach-api-backend"
  project  = var.project_id
  protocol = "HTTPS"
  # Note: timeout_sec not supported with serverless NEGs

  backend {
    group = google_compute_region_network_endpoint_group.api_neg.id
  }

  # Enable IAP for API as well
  iap {
    oauth2_client_id     = google_iap_client.call_coach.client_id
    oauth2_client_secret = google_iap_client.call_coach.secret
  }

  log_config {
    enable      = true
    sample_rate = 1.0
  }
}

# =============================================================================
# URL Map (routing rules)
# =============================================================================

resource "google_compute_url_map" "call_coach" {
  name            = "call-coach-url-map"
  project         = var.project_id
  default_service = google_compute_backend_service.frontend.id

  host_rule {
    hosts        = ["*"]
    path_matcher = "allpaths"
  }

  path_matcher {
    name            = "allpaths"
    default_service = google_compute_backend_service.frontend.id

    # Route backend API paths to the API service
    path_rule {
      paths   = ["/api/v1/*", "/health", "/tools/*"]
      service = google_compute_backend_service.api.id
    }
  }
}

# =============================================================================
# SSL Certificate (managed by Google)
# =============================================================================

resource "google_compute_managed_ssl_certificate" "call_coach" {
  name    = "call-coach-ssl-cert-v2"
  project = var.project_id

  managed {
    domains = [var.load_balancer_domain]
  }

  lifecycle {
    create_before_destroy = true
  }
}

# =============================================================================
# HTTPS Proxy
# =============================================================================

resource "google_compute_target_https_proxy" "call_coach" {
  name             = "call-coach-https-proxy"
  project          = var.project_id
  url_map          = google_compute_url_map.call_coach.id
  ssl_certificates = [google_compute_managed_ssl_certificate.call_coach.id]
}

# =============================================================================
# Global Forwarding Rule (external IP)
# =============================================================================

resource "google_compute_global_address" "call_coach" {
  name    = "call-coach-ip"
  project = var.project_id
}

resource "google_compute_global_forwarding_rule" "call_coach" {
  name                  = "call-coach-forwarding-rule"
  project               = var.project_id
  ip_address            = google_compute_global_address.call_coach.address
  ip_protocol           = "TCP"
  load_balancing_scheme = "EXTERNAL"
  port_range            = "443"
  target                = google_compute_target_https_proxy.call_coach.id
}

# =============================================================================
# HTTP to HTTPS Redirect
# =============================================================================

resource "google_compute_url_map" "https_redirect" {
  name    = "call-coach-https-redirect"
  project = var.project_id

  default_url_redirect {
    https_redirect         = true
    redirect_response_code = "MOVED_PERMANENTLY_DEFAULT"
    strip_query            = false
  }
}

resource "google_compute_target_http_proxy" "https_redirect" {
  name    = "call-coach-http-redirect-proxy"
  project = var.project_id
  url_map = google_compute_url_map.https_redirect.id
}

resource "google_compute_global_forwarding_rule" "https_redirect" {
  name                  = "call-coach-http-redirect"
  project               = var.project_id
  ip_address            = google_compute_global_address.call_coach.address
  ip_protocol           = "TCP"
  load_balancing_scheme = "EXTERNAL"
  port_range            = "80"
  target                = google_compute_target_http_proxy.https_redirect.id
}

# =============================================================================
# IAP Configuration
# =============================================================================

# IAP OAuth Client - requires OAuth consent screen to be "Internal"
resource "google_iap_client" "call_coach" {
  display_name = "Call Coach IAP Client"
  brand        = "projects/${var.project_id}/brands/${data.google_project.project.number}"
}

# IAP Web Backend Service IAM binding - allow prefect.io domain
resource "google_iap_web_backend_service_iam_member" "frontend_access" {
  project             = var.project_id
  web_backend_service = google_compute_backend_service.frontend.name
  role                = "roles/iap.httpsResourceAccessor"
  member              = "domain:prefect.io"
}

resource "google_iap_web_backend_service_iam_member" "api_access" {
  project             = var.project_id
  web_backend_service = google_compute_backend_service.api.name
  role                = "roles/iap.httpsResourceAccessor"
  member              = "domain:prefect.io"
}

# =============================================================================
# Outputs
# =============================================================================

output "load_balancer_ip" {
  description = "The IP address of the load balancer"
  value       = google_compute_global_address.call_coach.address
}

output "load_balancer_url" {
  description = "The URL to access the application (requires DNS setup)"
  value       = "https://${var.load_balancer_domain}"
}
