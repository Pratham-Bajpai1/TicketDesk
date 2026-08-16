# OpenID Connect Provider for GitHub Actions
resource "aws_iam_openid_connect_provider" "github" {
  url             = "https://token.actions.githubusercontent.com"
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = ["6938fd4d98bab03faadb97b34396831e3780aea1", "1c58a2168627f9c908a8b0a7128d96a484382570"]
}

# IAM Role assumed by GitHub Actions
resource "aws_iam_role" "github_actions_role" {
  name = "tkt-${var.owner_initials}-github-actions-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRoleWithWebIdentity"
        Effect = "Allow"
        Principal = {
          Federated = aws_iam_openid_connect_provider.github.arn
        }
        Condition = {
          StringEquals = {
            "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
          }
          StringLike = {
            # Strictly restrict deployment role access to ONLY your repository on the main branch
            "token.actions.githubusercontent.com:sub" = "repo:Pratham-Bajpai1/Ticketdesk:ref:refs/heads/main"
          }
        }
      }
    ]
  })
}

# Grant ECR & ECS Deployment Permissions to the Role
resource "aws_iam_role_policy" "github_actions_policy" {
  name = "tkt-${var.owner_initials}-github-actions-policy"
  role = aws_iam_role.github_actions_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload",
          "ecr:PutImage"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "ecs:DescribeTaskDefinition",
          "ecs:RegisterTaskDefinition",
          "ecs:UpdateService",
          "ecs:DescribeServices",
          "ecs:DescribeTasks",
          "ecs:ListTasks"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = "iam:PassRole"
        Resource = "*"
      }
    ]
  })
}

output "github_actions_role_arn" {
  value       = aws_iam_role.github_actions_role.arn
  description = "IAM Role ARN to put into GitHub Secret AWS_ROLE_TO_ASSUME"
}
