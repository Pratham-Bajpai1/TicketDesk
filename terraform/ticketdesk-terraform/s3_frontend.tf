# S3 Bucket for Static Frontend (Checklist #22)
resource "aws_s3_bucket" "frontend" {
  bucket        = "tkt-${var.owner_initials}-frontend-bucket"
  force_destroy = true
}

resource "aws_s3_bucket_public_access_block" "frontend_block" {
  bucket                  = aws_s3_bucket.frontend.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# S3 Bucket for Attachments (Checklist #20 & #23)
resource "aws_s3_bucket" "attachments" {
  bucket        = "tkt-${var.owner_initials}-attachments-bucket"
  force_destroy = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "attachments_enc" {
  bucket = aws_s3_bucket.attachments.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_cors_configuration" "attachments_cors" {
  bucket = aws_s3_bucket.attachments.id
  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["PUT", "POST", "GET", "HEAD"]
    allowed_origins = ["*"]
    expose_headers  = ["ETag"]
    max_age_seconds = 3000
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "frontend_enc" {
  bucket = aws_s3_bucket.frontend.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Copy index.html directly from S3 build bucket to avoid local Zscaler proxy issues
resource "aws_s3_object_copy" "frontend_index" {
  bucket     = aws_s3_bucket.frontend.id
  key        = "index.html"
  source     = "ticketdesk-build-artifacts-pratham/index.html"
  content_type = "text/html"

  # Ensures frontend bucket exists before attempting copy
  depends_on = [aws_s3_bucket.frontend]
}