# DB Subnet Group (Spans both Private Subnets)
resource "aws_db_subnet_group" "main" {
  name       = "tkt-${var.owner_initials}-db-subnet-group"
  subnet_ids = [aws_subnet.private_1.id, aws_subnet.private_2.id]

  tags = {
    Name = "tkt-${var.owner_initials}-db-subnet-group"
  }
}

# Database Security Group (Accepts traffic ONLY from ECS SG on port 5432)
resource "aws_security_group" "db_sg" {
  name        = "tkt-${var.owner_initials}-db-sg"
  description = "Allow inbound PostgreSQL traffic ONLY from ECS SG"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_sg.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Generate Random Password for RDS Admin
resource "random_password" "db_password" {
  length  = 16
  special = false
}

# Create AWS Secrets Manager Secret
resource "aws_secretsmanager_secret" "db_secret" {
  name                    = "tkt-${var.owner_initials}-db-credentials"
  recovery_window_in_days = 0
}

# Private RDS PostgreSQL Instance
resource "aws_db_instance" "postgres" {
  identifier             = "tkt-${var.owner_initials}-postgres"
  engine                 = "postgres"
  engine_version         = "15"
  instance_class         = "db.t4g.micro"
  allocated_storage      = 20

  db_name                = "ticketdesk"
  username               = "postgres"
  password               = random_password.db_password.result

  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.db_sg.id]

  publicly_accessible    = false
  skip_final_snapshot    = true

  storage_encrypted         = true
  backup_retention_period   = 1
  delete_automated_backups  = true
}

# Store JSON Secret Object in Secrets Manager
resource "aws_secretsmanager_secret_version" "db_secret_val" {
  secret_id = aws_secretsmanager_secret.db_secret.id
  secret_string = jsonencode({
    engine   = "postgres"
    host     = aws_db_instance.postgres.address
    port     = aws_db_instance.postgres.port
    dbname   = aws_db_instance.postgres.db_name
    username = aws_db_instance.postgres.username
    password = random_password.db_password.result
    url      = "postgresql://${aws_db_instance.postgres.username}:${random_password.db_password.result}@${aws_db_instance.postgres.address}:${aws_db_instance.postgres.port}/${aws_db_instance.postgres.db_name}"
  })
}