/**
 * Cloud Monitoring Configuration
 *
 * Sets up alerting policies for Cloud Run services and jobs.
 */

# =============================================================================
# Notification Channel (Email)
# =============================================================================

resource "google_monitoring_notification_channel" "email" {
  count        = var.alert_email != "" ? 1 : 0
  display_name = "Call Coach Alerts Email"
  type         = "email"

  labels = {
    email_address = var.alert_email
  }

  enabled = true
}

# =============================================================================
# Alert Policy: API Error Rate > 5%
# =============================================================================

resource "google_monitoring_alert_policy" "api_error_rate" {
  display_name = "Call Coach API - High Error Rate"
  combiner     = "OR"

  conditions {
    display_name = "Error rate > 5% for 5 minutes"

    condition_threshold {
      filter = <<-EOT
        resource.type = "cloud_run_revision"
        AND resource.labels.service_name = "${module.api_service.service_name}"
        AND metric.type = "run.googleapis.com/request_count"
        AND metric.labels.response_code_class != "2xx"
      EOT

      comparison      = "COMPARISON_GT"
      threshold_value = 0.05
      duration        = "300s"

      aggregations {
        alignment_period     = "60s"
        per_series_aligner   = "ALIGN_RATE"
        cross_series_reducer = "REDUCE_SUM"
        group_by_fields      = ["resource.labels.service_name"]
      }

      trigger {
        count = 1
      }
    }
  }

  notification_channels = var.alert_email != "" ? [google_monitoring_notification_channel.email[0].name] : []

  alert_strategy {
    auto_close = "1800s" # 30 minutes
  }

  documentation {
    content   = "The Call Coach API is experiencing a high error rate (>5%). Check Cloud Run logs for details."
    mime_type = "text/markdown"
  }

  enabled = true
}

# =============================================================================
# Alert Policy: API Latency p95 > 2s
# =============================================================================

resource "google_monitoring_alert_policy" "api_latency" {
  display_name = "Call Coach API - High Latency"
  combiner     = "OR"

  conditions {
    display_name = "p95 latency > 2s for 5 minutes"

    condition_threshold {
      filter = <<-EOT
        resource.type = "cloud_run_revision"
        AND resource.labels.service_name = "${module.api_service.service_name}"
        AND metric.type = "run.googleapis.com/request_latencies"
      EOT

      comparison      = "COMPARISON_GT"
      threshold_value = 2000 # 2000ms = 2s
      duration        = "300s"

      aggregations {
        alignment_period     = "60s"
        per_series_aligner   = "ALIGN_PERCENTILE_95"
        cross_series_reducer = "REDUCE_MAX"
        group_by_fields      = ["resource.labels.service_name"]
      }

      trigger {
        count = 1
      }
    }
  }

  notification_channels = var.alert_email != "" ? [google_monitoring_notification_channel.email[0].name] : []

  alert_strategy {
    auto_close = "1800s"
  }

  documentation {
    content   = "The Call Coach API p95 latency is above 2 seconds. Check for slow queries or external API issues."
    mime_type = "text/markdown"
  }

  enabled = true
}

# =============================================================================
# Alert Policy: DLT Sync Job Failure
# =============================================================================

resource "google_monitoring_alert_policy" "dlt_job_failure" {
  display_name = "Call Coach DLT Sync - Job Failed"
  combiner     = "OR"

  conditions {
    display_name = "DLT sync job execution failed"

    condition_threshold {
      filter = <<-EOT
        resource.type = "cloud_run_job"
        AND resource.labels.job_name = "${module.dlt_sync_job.job_name}"
        AND metric.type = "run.googleapis.com/job/completed_execution_count"
        AND metric.labels.result = "failed"
      EOT

      comparison      = "COMPARISON_GT"
      threshold_value = 0
      duration        = "0s"

      aggregations {
        alignment_period     = "300s"
        per_series_aligner   = "ALIGN_SUM"
        cross_series_reducer = "REDUCE_SUM"
        group_by_fields      = ["resource.labels.job_name"]
      }

      trigger {
        count = 1
      }
    }
  }

  notification_channels = var.alert_email != "" ? [google_monitoring_notification_channel.email[0].name] : []

  alert_strategy {
    auto_close = "3600s" # 1 hour
  }

  documentation {
    content   = "The DLT sync job failed. Check Cloud Run job logs for error details. Data may not be synced from BigQuery."
    mime_type = "text/markdown"
  }

  enabled = true
}

# =============================================================================
# Alert Policy: Frontend Error Rate
# =============================================================================

resource "google_monitoring_alert_policy" "frontend_error_rate" {
  display_name = "Call Coach Frontend - High Error Rate"
  combiner     = "OR"

  conditions {
    display_name = "Error rate > 5% for 5 minutes"

    condition_threshold {
      filter = <<-EOT
        resource.type = "cloud_run_revision"
        AND resource.labels.service_name = "${module.frontend_service.service_name}"
        AND metric.type = "run.googleapis.com/request_count"
        AND metric.labels.response_code_class = "5xx"
      EOT

      comparison      = "COMPARISON_GT"
      threshold_value = 0.05
      duration        = "300s"

      aggregations {
        alignment_period     = "60s"
        per_series_aligner   = "ALIGN_RATE"
        cross_series_reducer = "REDUCE_SUM"
        group_by_fields      = ["resource.labels.service_name"]
      }

      trigger {
        count = 1
      }
    }
  }

  notification_channels = var.alert_email != "" ? [google_monitoring_notification_channel.email[0].name] : []

  alert_strategy {
    auto_close = "1800s"
  }

  documentation {
    content   = "The Call Coach Frontend is experiencing high 5xx error rate. Check Cloud Run logs and API connectivity."
    mime_type = "text/markdown"
  }

  enabled = true
}
