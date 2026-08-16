resource "aws_lb" "main" {
    name               = "tkt-${var.owner_initials}-alb"
    internal           = false
    load_balancer_type = "application"
    security_groups    = [aws_security_group.alb_sg.id]
    subnets            = [aws_subnet.public_1.id, aws_subnet.public_2.id]
}

resource "aws_lb_target_group" "app" {
    name        = "tkt-${var.owner_initials}-tg"
    port        = 8000
    protocol    = "HTTP"
    vpc_id      = aws_vpc.main.id
    target_type = "ip"

    health_check {
        path                = "/health"
        healthy_threshold   = 2
        unhealthy_threshold = 3
        timeout             = 5
        interval            = 30
        matcher             = "200"
    }
}

resource "aws_lb_listener" "http" {
    load_balancer_arn = aws_lb.main.arn
    port              = 80
    protocol          = "HTTP"

    default_action {
        type             = "forward"
        target_group_arn = aws_lb_target_group.app.arn
    }
}