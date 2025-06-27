# Terraform - o co chodzi?

## Co to jest Terraform?

Terraform to **Infrastructure as Code (IaC)** narzędzie od HashiCorp, które pozwala definiować, tworzyć i zarządzać infrastrukturą chmurową za pomocą kodu.

### Główne cechy:
- 📝 **Deklaratywny** - opisujesz co chcesz, nie jak to zrobić
- 🌐 **Multi-cloud** - AWS, Azure, GCP, VMware i setki innych
- 🔄 **Plan & Apply** - zobaczysz zmiany przed wdrożeniem
- 📊 **State management** - śledzi stan infrastruktury
- 🔄 **Idempotent** - możesz uruchamiać wielokrotnie bezpiecznie

## Podstawowe pojęcia

### Terraform workflow:
```
1. Write     → Piszesz konfigurację (.tf files)
2. Plan      → terraform plan (podgląd zmian)
3. Apply     → terraform apply (wdróż zmiany)
4. Destroy   → terraform destroy (usuń infrastrukturę)
```

### Składnia HCL (HashiCorp Configuration Language):
```hcl
# Podstawowa struktura
resource "aws_instance" "example" {
  ami           = "ami-0c55b159cbfafe1d0"
  instance_type = "t2.micro"
  
  tags = {
    Name = "ExampleInstance"
  }
}

# Zmienne
variable "instance_type" {
  description = "Type of EC2 instance"
  type        = string
  default     = "t2.micro"
}

# Output
output "instance_ip" {
  value = aws_instance.example.public_ip
}
```

## Pierwszy projekt - AWS EC2 instance

### 1. **main.tf**:
```hcl
# Konfiguracja providera
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  required_version = ">= 1.5"
}

# Provider AWS
provider "aws" {
  region = var.aws_region
}

# Data source - pobierz najnowsze Ubuntu AMI
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# Security Group
resource "aws_security_group" "web_sg" {
  name_prefix = "web-security-group"
  description = "Security group for web server"

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # W produkcji ogranicz to!
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "WebSecurityGroup"
  }
}

# EC2 Instance
resource "aws_instance" "web_server" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type         = var.instance_type
  vpc_security_group_ids = [aws_security_group.web_sg.id]
  key_name              = var.key_pair_name

  user_data = <<-EOF
              #!/bin/bash
              apt-get update
              apt-get install -y nginx
              systemctl start nginx
              systemctl enable nginx
              echo "<h1>Hello from Terraform!</h1>" > /var/www/html/index.html
              EOF

  tags = {
    Name        = "WebServer"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# Elastic IP
resource "aws_eip" "web_server_eip" {
  instance = aws_instance.web_server.id
  domain   = "vpc"

  tags = {
    Name = "WebServerEIP"
  }
}
```

### 2. **variables.tf**:
```hcl
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "eu-west-1"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t2.micro"
  
  validation {
    condition = contains([
      "t2.micro", "t2.small", "t2.medium",
      "t3.micro", "t3.small", "t3.medium"
    ], var.instance_type)
    error_message = "Instance type must be a valid t2 or t3 type."
  }
}

variable "key_pair_name" {
  description = "Name of the AWS key pair for SSH access"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "development"
}
```

### 3. **outputs.tf**:
```hcl
output "instance_id" {
  description = "ID of the EC2 instance"
  value       = aws_instance.web_server.id
}

output "instance_public_ip" {
  description = "Public IP address of the EC2 instance"
  value       = aws_eip.web_server_eip.public_ip
}

output "instance_public_dns" {
  description = "Public DNS name of the EC2 instance"
  value       = aws_instance.web_server.public_dns
}

output "security_group_id" {
  description = "ID of the security group"
  value       = aws_security_group.web_sg.id
}
```

### 4. **terraform.tfvars**:
```hcl
aws_region     = "eu-west-1"
instance_type  = "t2.micro"
key_pair_name  = "my-key-pair"  # Musi istnieć w AWS
environment    = "development"
```

## Uruchomienie projektu

### Podstawowe komendy:
```bash
# 1. Inicjalizacja - pobierz providery
terraform init

# 2. Walidacja konfiguracji
terraform validate

# 3. Formatowanie kodu
terraform fmt

# 4. Plan - zobacz co się zmieni
terraform plan

# 5. Zastosuj zmiany
terraform apply

# 6. Pokaż stan
terraform show

# 7. Lista zasobów
terraform state list

# 8. Zniszcz infrastrukturę
terraform destroy
```

### Przykład output:
```bash
$ terraform plan

Terraform will perform the following actions:

  # aws_eip.web_server_eip will be created
  + resource "aws_eip" "web_server_eip" {
      + allocation_id        = (known after apply)
      + domain               = "vpc"
      + id                   = (known after apply)
      + instance             = (known after apply)
      + public_ip            = (known after apply)
    }

  # aws_instance.web_server will be created
  + resource "aws_instance" "web_server" {
      + ami                    = "ami-0c55b159cbfafe1d0"
      + instance_type          = "t2.micro"
      + id                     = (known after apply)
      + public_ip              = (known after apply)
    }

Plan: 2 to add, 0 to change, 0 to destroy.
```

## Zaawansowane przykłady

### 1. **Moduły** - reusable components:
```hcl
# modules/vpc/main.tf
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = var.vpc_name
  }
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "${var.vpc_name}-igw"
  }
}

resource "aws_subnet" "public" {
  count = length(var.public_subnet_cidrs)

  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.public_subnet_cidrs[count.index]
  availability_zone       = var.availability_zones[count.index]
  map_public_ip_on_launch = true

  tags = {
    Name = "${var.vpc_name}-public-${count.index + 1}"
  }
}
```

```hcl
# Użycie modułu
module "vpc" {
  source = "./modules/vpc"

  vpc_name             = "my-vpc"
  vpc_cidr            = "10.0.0.0/16"
  public_subnet_cidrs = ["10.0.1.0/24", "10.0.2.0/24"]
  availability_zones  = ["eu-west-1a", "eu-west-1b"]
}

# Odwołanie do output z modułu
resource "aws_instance" "app" {
  subnet_id = module.vpc.public_subnet_ids[0]
  # ...
}
```

### 2. **Remote State** - współdzielony stan:
```hcl
# backend.tf
terraform {
  backend "s3" {
    bucket         = "my-terraform-state-bucket"
    key            = "prod/terraform.tfstate"
    region         = "eu-west-1"
    dynamodb_table = "terraform-locks"
    encrypt        = true
  }
}

# Data source z innego state
data "terraform_remote_state" "vpc" {
  backend = "s3"
  config = {
    bucket = "my-terraform-state-bucket"
    key    = "vpc/terraform.tfstate"
    region = "eu-west-1"
  }
}

# Użyj danych z innego projektu
resource "aws_instance" "app" {
  subnet_id = data.terraform_remote_state.vpc.outputs.private_subnet_id
}
```

### 3. **Multi-environment** setup:
```hcl
# environments/dev/main.tf
module "infrastructure" {
  source = "../../modules/infrastructure"

  environment         = "dev"
  instance_type      = "t2.micro"
  min_size           = 1
  max_size           = 2
  database_instance  = "db.t3.micro"
}

# environments/prod/main.tf
module "infrastructure" {
  source = "../../modules/infrastructure"

  environment         = "prod"
  instance_type      = "t3.medium"
  min_size           = 3
  max_size           = 10
  database_instance  = "db.r5.large"
}
```

## Multi-Cloud przykład

### AWS + Azure + GCP:
```hcl
# Providery
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
}

# AWS
provider "aws" {
  region = "eu-west-1"
}

resource "aws_s3_bucket" "app_storage" {
  bucket = "my-app-storage-aws"
}

# Azure
provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "main" {
  name     = "my-app-rg"
  location = "West Europe"
}

resource "azurerm_storage_account" "app_storage" {
  name                     = "myappstorageazure"
  resource_group_name      = azurerm_resource_group.main.name
  location                = azurerm_resource_group.main.location
  account_tier            = "Standard"
  account_replication_type = "LRS"
}

# Google Cloud
provider "google" {
  project = "my-project-id"
  region  = "europe-west1"
}

resource "google_storage_bucket" "app_storage" {
  name     = "my-app-storage-gcp"
  location = "EU"
}
```

## State Management

### Importowanie istniejących zasobów:
```bash
# Import AWS EC2 instance
terraform import aws_instance.example i-1234567890abcdef0

# Import Azure Resource Group
terraform import azurerm_resource_group.example /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/example
```

### State operacje:
```bash
# Lista zasobów w state
terraform state list

# Szczegóły konkretnego zasobu
terraform state show aws_instance.web_server

# Usuń zasób ze state (nie usuwa rzeczywistego zasobu!)
terraform state rm aws_instance.old_server

# Przenies zasób w state
terraform state mv aws_instance.old aws_instance.new

# Backup state
cp terraform.tfstate terraform.tfstate.backup
```

## Testowanie Terraform

### 1. **Terraform Validate & Plan**:
```bash
#!/bin/bash
# test.sh
set -e

echo "Validating Terraform configuration..."
terraform validate

echo "Checking format..."
terraform fmt -check

echo "Planning deployment..."
terraform plan -out=tfplan

echo "All tests passed!"
```

### 2. **Terratest** (Go):
```go
// test/terraform_test.go
package test

import (
    "testing"
    "github.com/gruntwork-io/terratest/modules/terraform"
    "github.com/stretchr/testify/assert"
)

func TestTerraformExample(t *testing.T) {
    terraformOptions := &terraform.Options{
        TerraformDir: "../",
        Vars: map[string]interface{}{
            "instance_type": "t2.micro",
            "environment":   "test",
        },
    }

    defer terraform.Destroy(t, terraformOptions)
    
    terraform.InitAndApply(t, terraformOptions)
    
    instanceId := terraform.Output(t, terraformOptions, "instance_id")
    assert.NotEmpty(t, instanceId)
}
```

### 3. **Policy as Code** (Sentinel):
```hcl
# policy/restrict-instance-types.sentinel
import "tfplan/v2" as tfplan

allowed_types = ["t2.micro", "t2.small"]

main = rule {
    all tfplan.resource_changes as _, changes {
        changes.mode is "managed" and
        changes.type is "aws_instance" and
        changes.change.after.instance_type in allowed_types
    }
}
```

## Best Practices

### 1. **Struktura projektu**:
```
terraform-project/
├── modules/
│   ├── vpc/
│   ├── compute/
│   └── database/
├── environments/
│   ├── dev/
│   ├── staging/
│   └── prod/
├── policies/
├── scripts/
└── README.md
```

### 2. **Naming conventions**:
```hcl
# Resource naming
resource "aws_instance" "web_server" {}      # snake_case
resource "aws_s3_bucket" "app_data" {}

# Variable naming
variable "vpc_cidr_block" {}
variable "environment_name" {}

# Tags
tags = {
  Name        = "WebServer"
  Environment = var.environment
  Project     = "MyApp" 
  ManagedBy   = "Terraform"
  Owner       = "DevOps"
}
```

### 3. **Security**:
```hcl
# Nie commituj secrets do repo!
variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

# Używaj AWS Secrets Manager
data "aws_secretsmanager_secret_version" "db_password" {
  secret_id = "prod/database/password"
}

# Encrypt state
terraform {
  backend "s3" {
    bucket  = "terraform-state"
    key     = "prod/terraform.tfstate"
    region  = "eu-west-1"
    encrypt = true                    # ✅ Encrypt!
    
    dynamodb_table = "terraform-locks"
  }
}
```

## Terraform vs Konkurencja

| Narzędzie | Podejście | Providers | Learning Curve |
|-----------|-----------|-----------|----------------|
| **Terraform** | Deklaratywny | 1000+ | Medium |
| **CloudFormation** | Deklaratywny | AWS only | Medium |
| **Pulumi** | Programmatic | Multi-cloud | High |
| **Ansible** | Procedural | Multi-cloud | Low |
| **ARM Templates** | Deklaratywny | Azure only | Medium |

## Podsumowanie

### ✅ Używaj Terraform gdy:
- Chcesz Infrastructure as Code
- Potrzebujesz multi-cloud
- Masz zespół DevOps
- Chcesz version control infrastruktury
- Potrzebujesz powtarzalnych deploymentów

### ❌ Unikaj Terraform gdy:
- Bardzo prosta infrastruktura
- Brak doświadczenia z IaC
- Tylko ręczne zarządzanie
- Jednorazowe projekty

**Terraform = Infrastructure as Code made simple!** 🏗️