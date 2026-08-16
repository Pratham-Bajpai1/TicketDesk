resource "aws_vpc" "main" {
    cidr_block           = "10.0.0.0/16"
    enable_dns_hostnames = true
    enable_dns_support   = true

    tags = {
        Name = "tkt-${var.owner_initials}-vpc"
    }
}

resource "aws_internet_gateway" "igw" {
    vpc_id = aws_vpc.main.id
}

resource "aws_subnet" "public_1" {
    vpc_id                  = aws_vpc.main.id
    cidr_block              = "10.0.1.0/24"
    availability_zone       = "${var.aws_region}a"
    map_public_ip_on_launch = true

    tags = {
        Name = "tkt-${var.owner_initials}-pub-1"
    }
}

resource "aws_subnet" "public_2" {
    vpc_id                  = aws_vpc.main.id
    cidr_block              = "10.0.2.0/24"
    availability_zone       = "${var.aws_region}b"
    map_public_ip_on_launch = true

    tags = {
        Name = "tkt-${var.owner_initials}-pub-2"
    }
}

resource "aws_subnet" "private_1" {
    vpc_id                  = aws_vpc.main.id
    cidr_block              = "10.0.10.0/24"
    availability_zone       = "${var.aws_region}a"

    tags = {
        Name = "tkt-${var.owner_initials}-priv-1"
    }
}

resource "aws_subnet" "private_2" {
    vpc_id                  = aws_vpc.main.id
    cidr_block              = "10.0.20.0/24"
    availability_zone       = "${var.aws_region}b"

    tags = {
        Name = "tkt-${var.owner_initials}-priv-2"
    }
}

resource "aws_eip" "nat" {
    domain = "vpc"
}

resource "aws_nat_gateway" "nat" {
    allocation_id = aws_eip.nat.id
    subnet_id     = aws_subnet.public_1.id
}

resource "aws_route_table" "public" {
    vpc_id = aws_vpc.main.id
    route {
        cidr_block = "0.0.0.0/0"
        gateway_id = aws_internet_gateway.igw.id
    }
}

resource "aws_route_table_association" "pub_1" {
    subnet_id      = aws_subnet.public_1.id 
    route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "pub_2" {
    subnet_id      = aws_subnet.public_2.id 
    route_table_id = aws_route_table.public.id
}

resource "aws_route_table" "private" {
    vpc_id = aws_vpc.main.id
    route {
        cidr_block     = "0.0.0.0/0"
        nat_gateway_id = aws_nat_gateway.nat.id
    }
}

resource "aws_route_table_association" "priv_1" {
    subnet_id      = aws_subnet.private_1.id 
    route_table_id = aws_route_table.private.id
}

resource "aws_route_table_association" "priv_2" {
    subnet_id      = aws_subnet.private_2.id 
    route_table_id = aws_route_table.private.id
}