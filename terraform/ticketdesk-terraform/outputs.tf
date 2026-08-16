output "aws_region" {
    value = var.aws_region
}

output "project_name" {
    value = var.project_name
}

output "alb_dns_name" {
    description = "Application Load Balancer URL"
    value       = "http://${aws_lb.main.dns_name}"
}