resource "aws_ecs_cluster" "main" {
    name = "tkt-${var.owner_initials}-cluster"
}

resource "aws_iam_role" "ecs_execution_role" {
    name = "tkt-${var.owner_initials}-ecs-exec-role"

    assume_role_policy = jsonencode({
        Version = "2012-10-17"
        Statement = [{
            Action    = "sts:AssumeRole"
            Effect    = "Allow"  
            Principal = { Service = "ecs-tasks.amazonaws.com" }
        }]
    })
}

resource "aws_iam_role_policy_attachment" "ecs_exec_policy" {
    role       = aws_iam_role.ecs_execution_role.name
    policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_cloudwatch_log_group" "ecs" {
  name              = "/ecs/tkt-${var.owner_initials}"
  retention_in_days = 7
}

resource "aws_ecs_task_definition" "app" {
    family                   = "tkt-${var.owner_initials}-task"
    network_mode             = "awsvpc"
    requires_compatibilities = ["FARGATE"]
    cpu                      = "256"
    memory                   = "512"
    execution_role_arn       = aws_iam_role.ecs_execution_role.arn
    task_role_arn            = aws_iam_role.ecs_task_role.arn

    container_definitions = jsonencode([
        {
            name      = "ticketdesk-api"
            image     = var.ecr_image_uri
            essential = true

            portMappings = [
                {
                    containerPort = 8000
                    hostPort      = 8000
                    protocol      = "tcp"
                }
            ]

            secrets = [
                {
                    name      = "DATABASE_URL"
                    valueFrom = "${aws_secretsmanager_secret.db_secret.arn}:url::"
                }
            ]

            environment = [
              {
                name  = "ATTACHMENTS_BUCKET"
                value = aws_s3_bucket.attachments.id
              },
              {
                name  = "AWS_REGION"
                value = var.aws_region
              },
              {
                name  = "AWS_DEFAULT_REGION"
                value = var.aws_region
              }
            ]

            logConfiguration = {
                logDriver = "awslogs"
                options = {
                    awslogs-group         = aws_cloudwatch_log_group.ecs.name
                    awslogs-region        = var.aws_region
                    awslogs-stream-prefix = "ecs"
                }
            }
        }
    ])
}

# Task Role (S3 Permissions for presigned URLs)
resource "aws_iam_role" "ecs_task_role" {
  name = "tkt-${var.owner_initials}-ecs-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
    }]
  })
}

resource "aws_iam_policy" "ecs_s3_policy" {
  name = "tkt-${var.owner_initials}-ecs-s3-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = ["s3:ListBucket"]
        Resource = aws_s3_bucket.attachments.arn
      },
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject"
        ]
        Resource = "${aws_s3_bucket.attachments.arn}/*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_s3_attach" {
  role       = aws_iam_role.ecs_task_role.name
  policy_arn = aws_iam_policy.ecs_s3_policy.arn
}

resource "aws_ecs_service" "main" {
  name            = "tkt-${var.owner_initials}-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = [aws_subnet.private_1.id, aws_subnet.private_2.id]
    security_groups  = [aws_security_group.ecs_sg.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.app.arn
    container_name   = "ticketdesk-api"
    container_port   = 8000
  }

  depends_on = [
    aws_lb_listener.http
  ]
}

# IAM Policy allowing ECS Task Execution Role to read Secrets Manager
resource "aws_iam_policy" "secrets_policy" {
  name        = "tkt-${var.owner_initials}-secrets-policy"
  description = "Allow ECS execution role to retrieve DB credentials"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["secretsmanager:GetSecretValue"]
      Resource = [aws_secretsmanager_secret.db_secret.arn]
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_secrets_attach" {
  role       = aws_iam_role.ecs_execution_role.name
  policy_arn = aws_iam_policy.secrets_policy.arn
}

resource "aws_iam_policy" "ssm_policy" {
  name = "tkt-${var.owner_initials}-ssm-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "ssm:GetParameter",
        "ssm:GetParameters"
      ]
      Resource = "*"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_ssm_attach" {
  role       = aws_iam_role.ecs_execution_role.name
  policy_arn = aws_iam_policy.ssm_policy.arn
}