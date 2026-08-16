resource "aws_ssm_parameter" "app_env" {
  name  = "/tkt/${var.environment}/APP_ENV"
  type  = "String"
  value = var.environment
}

resource "aws_ssm_parameter" "db_host" {
  name  = "/tkt/${var.environment}/DB_HOST"
  type  = "String"
  value = aws_db_instance.postgres.address
}

resource "aws_ssm_parameter" "attachments_bucket" {
  name  = "/tkt/${var.environment}/ATTACHMENTS_BUCKET"
  type  = "String"
  value = aws_s3_bucket.attachments.id
}