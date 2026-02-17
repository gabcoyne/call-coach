terraform {
  backend "gcs" {
    bucket = "prefect-sbx-terraform-state"
    prefix = "call-coach"
  }
}
