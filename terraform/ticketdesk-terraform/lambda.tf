# IAM Role for Lambda
resource "aws_iam_role" "lambda_role" {
  name = "tkt-${var.owner_initials}-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

# Basic Lambda CloudWatch Execution Policy Attachment
resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Policy allowing Lambda to Read/Write from Attachments Bucket
resource "aws_iam_policy" "lambda_s3_policy" {
  name = "tkt-${var.owner_initials}-lambda-s3-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["s3:GetObject", "s3:PutObject"]
      Resource = ["${aws_s3_bucket.attachments.arn}/*"]
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_s3_attach" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_s3_policy.arn
}

# Lambda Function Definition
resource "aws_lambda_function" "thumbnail" {
  filename         = "lambda_thumbnail.zip"
  function_name    = "tkt-${var.owner_initials}-thumbnail-generator"
  role             = aws_iam_role.lambda_role.arn
  handler          = "handler.lambda_handler"
  runtime          = "python3.10"
  source_code_hash = filebase64sha256("lambda_thumbnail.zip")
  timeout          = 30
  memory_size      = 256

  environment {
    variables = {
      ATTACHMENTS_BUCKET = aws_s3_bucket.attachments.id
    }
  }
}

# Grant S3 Service Permission to Invoke Lambda
resource "aws_lambda_permission" "allow_s3" {
  statement_id  = "AllowExecutionFromS3"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.thumbnail.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.attachments.arn
}

# Trigger Lambda on S3 Object Creation inside attachments/
resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = aws_s3_bucket.attachments.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.thumbnail.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "attachments/"
  }

  depends_on = [aws_lambda_permission.allow_s3]
}