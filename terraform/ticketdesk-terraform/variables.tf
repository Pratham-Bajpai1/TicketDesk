variable "aws_region" {
    description = "AWS region"
    type        = string
    default     = "ap-southeast-1"
}

variable "project_name" {
    description = "Project name"
    type        = string
    default     = "ticketdesk"
}

variable "environment" {
    description = "Envrionment name"
    type        = string
    default     = "dev"
}

variable "owner_initials" {
    type    = string
    default = "pb"
}

variable "ecr_image_uri" {
    description = "ECR image URI for TicketDesk"
    type        = string
}