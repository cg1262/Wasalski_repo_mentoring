# Jak dobrze stworzyć swoją aplikację - architektura, technologie, deployment

## Architektura aplikacji - wybór i planowanie

### 1. **Typy architektur**

#### Monolityczna architektura:
```
Single Application
├── Frontend Layer
├── Business Logic Layer  
├── Data Access Layer
└── Database

Zalety:
✅ Prostota developmentu
✅ Łatwe testowanie
✅ Szybki start
✅ Atomic deployments

Wady:
❌ Trudność skalowania
❌ Technology lock-in
❌ Duże team coordination issues
❌ Long deployment cycles
```

#### Microservices architektura:
```
System
├── User Service (Node.js)
├── Order Service (Python)
├── Payment Service (Java)
├── Notification Service (Go)
├── API Gateway
├── Service Discovery
└── Shared Database per Service

Zalety:
✅ Niezależne skalowanie
✅ Technology diversity
✅ Team autonomy
✅ Fault isolation

Wady:
❌ Complexity overhead
❌ Network latency
❌ Data consistency challenges
❌ Monitoring complexity
```

#### Serverless/Function-as-a-Service:
```
Event-Driven Functions
├── AWS Lambda / Azure Functions
├── API Gateway
├── Event Sources (SQS, EventBridge)
├── Managed Databases
└── CDN + Static Hosting

Zalety:
✅ Zero server management
✅ Automatic scaling
✅ Pay-per-execution
✅ Built-in high availability

Wady:
❌ Vendor lock-in
❌ Cold start latency
❌ Limited execution time
❌ Complex debugging
```

### 2. **Wybór architektury według przypadku**

```python
def choose_architecture(requirements):
    """
    Pomoc w wyborze architektury
    """
    
    # Small team, simple app
    if (requirements.get('team_size', 0) <= 3 and 
        requirements.get('complexity', 'low') == 'low'):
        return "Monolith - Start simple, evolve later"
    
    # High scale, multiple teams
    if (requirements.get('scale', 'medium') == 'high' and 
        requirements.get('team_size', 0) > 10):
        return "Microservices - Organizational scaling"
    
    # Event-driven, variable load
    if (requirements.get('load_pattern') == 'variable' and
        requirements.get('event_driven') == True):
        return "Serverless - Cost effective, auto-scaling"
    
    # Rapid prototyping
    if requirements.get('stage') == 'prototype':
        return "Serverless or Simple Monolith"
    
    # Enterprise, compliance heavy
    if requirements.get('compliance', False):
        return "Monolith or Modular Monolith - Easier compliance"
    
    return "Start with Monolith, evolve to Microservices"

# Przykłady
startup_reqs = {
    'team_size': 2,
    'complexity': 'low', 
    'stage': 'prototype'
}

enterprise_reqs = {
    'team_size': 50,
    'scale': 'high',
    'compliance': True
}

print("Startup:", choose_architecture(startup_reqs))
print("Enterprise:", choose_architecture(enterprise_reqs))
```

## Stack technologiczny

### 1. **Backend - wybór języka i frameworka**

#### Python - Django/FastAPI:
```python
# FastAPI example - modern, fast, type hints
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import asyncio

app = FastAPI(title="My App API", version="1.0.0")

class User(BaseModel):
    id: Optional[int] = None
    name: str
    email: str
    age: Optional[int] = None

class UserRepository:
    def __init__(self):
        self.users = []
        self.next_id = 1
    
    async def create_user(self, user: User) -> User:
        user.id = self.next_id
        self.next_id += 1
        self.users.append(user)
        return user
    
    async def get_users(self) -> List[User]:
        return self.users
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        return next((u for u in self.users if u.id == user_id), None)

# Dependency injection
user_repo = UserRepository()

@app.post("/users/", response_model=User, status_code=201)
async def create_user(user: User):
    """Create new user"""
    return await user_repo.create_user(user)

@app.get("/users/", response_model=List[User])
async def get_users():
    """Get all users"""
    return await user_repo.get_users()

@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int):
    """Get user by ID"""
    user = await user_repo.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Middleware for logging
@app.middleware("http")
async def log_requests(request, call_next):
    import time
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    print(f"{request.method} {request.url} - {response.status_code} ({process_time:.3f}s)")
    return response

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": "2024-01-15T10:30:00Z"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

#### Node.js - Express/NestJS:
```javascript
// Express.js example - flexible, lightweight
const express = require('express');
const helmet = require('helmet');
const cors = require('cors');
const rateLimit = require('express-rate-limit');

const app = express();

// Middleware
app.use(helmet()); // Security headers
app.use(cors()); // CORS handling
app.use(express.json({ limit: '10mb' }));

// Rate limiting
const limiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100 // limit each IP to 100 requests per windowMs
});
app.use('/api/', limiter);

// Simple in-memory store (use database in production)
let users = [];
let nextId = 1;

// Routes
app.post('/api/users', (req, res) => {
    try {
        const { name, email, age } = req.body;
        
        // Validation
        if (!name || !email) {
            return res.status(400).json({ 
                error: 'Name and email are required' 
            });
        }
        
        const user = {
            id: nextId++,
            name,
            email,
            age: age || null,
            createdAt: new Date().toISOString()
        };
        
        users.push(user);
        res.status(201).json(user);
        
    } catch (error) {
        res.status(500).json({ error: 'Internal server error' });
    }
});

app.get('/api/users', (req, res) => {
    const { page = 1, limit = 10 } = req.query;
    const startIndex = (page - 1) * limit;
    const endIndex = page * limit;
    
    const paginatedUsers = users.slice(startIndex, endIndex);
    
    res.json({
        users: paginatedUsers,
        pagination: {
            page: parseInt(page),
            limit: parseInt(limit),
            total: users.length,
            totalPages: Math.ceil(users.length / limit)
        }
    });
});

app.get('/api/users/:id', (req, res) => {
    const userId = parseInt(req.params.id);
    const user = users.find(u => u.id === userId);
    
    if (!user) {
        return res.status(404).json({ error: 'User not found' });
    }
    
    res.json(user);
});

// Error handling middleware
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).json({ error: 'Something went wrong!' });
});

// 404 handler
app.use('*', (req, res) => {
    res.status(404).json({ error: 'Route not found' });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
```

### 2. **Frontend - React/Vue/Angular**

#### React + TypeScript przykład:
```tsx
// Modern React with TypeScript, hooks, and best practices
import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

// Types
interface User {
  id: number;
  name: string;
  email: string;
  age?: number;
}

interface ApiResponse<T> {
  data: T;
  error?: string;
  loading: boolean;
}

// Custom hook for API calls
function useApi<T>(url: string): ApiResponse<T | null> {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError('');
        const response = await axios.get(url);
        setData(response.data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [url]);

  return { data, error, loading };
}

// User component
const UserCard: React.FC<{ user: User }> = ({ user }) => {
  return (
    <div className="user-card">
      <h3>{user.name}</h3>
      <p>Email: {user.email}</p>
      {user.age && <p>Age: {user.age}</p>}
    </div>
  );
};

// Main App component
const App: React.FC = () => {
  const { data: users, error, loading } = useApi<User[]>('/api/users');
  const [newUser, setNewUser] = useState({ name: '', email: '', age: '' });
  const [submitLoading, setSubmitLoading] = useState(false);

  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitLoading(true);

    try {
      const userData = {
        name: newUser.name,
        email: newUser.email,
        age: newUser.age ? parseInt(newUser.age) : undefined
      };

      await axios.post('/api/users', userData);
      
      // Reset form
      setNewUser({ name: '', email: '', age: '' });
      
      // Refresh user list (in real app, might update state directly)
      window.location.reload();
      
    } catch (err) {
      console.error('Error creating user:', err);
    } finally {
      setSubmitLoading(false);
    }
  }, [newUser]);

  if (loading) return <div>Loading users...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div className="app">
      <h1>User Management</h1>
      
      {/* Add User Form */}
      <form onSubmit={handleSubmit} className="user-form">
        <h2>Add New User</h2>
        <input
          type="text"
          placeholder="Name"
          value={newUser.name}
          onChange={(e) => setNewUser(prev => ({ ...prev, name: e.target.value }))}
          required
        />
        <input
          type="email"
          placeholder="Email"
          value={newUser.email}
          onChange={(e) => setNewUser(prev => ({ ...prev, email: e.target.value }))}
          required
        />
        <input
          type="number"
          placeholder="Age (optional)"
          value={newUser.age}
          onChange={(e) => setNewUser(prev => ({ ...prev, age: e.target.value }))}
        />
        <button type="submit" disabled={submitLoading}>
          {submitLoading ? 'Adding...' : 'Add User'}
        </button>
      </form>

      {/* Users List */}
      <div className="users-list">
        <h2>Users ({users?.length || 0})</h2>
        {users && users.length > 0 ? (
          users.map(user => (
            <UserCard key={user.id} user={user} />
          ))
        ) : (
          <p>No users found</p>
        )}
      </div>
    </div>
  );
};

export default App;
```

### 3. **Baza danych - wybór i konfiguracja**

#### PostgreSQL setup:
```sql
-- Database schema design
-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    age INTEGER CHECK (age > 0 AND age < 150),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);

-- Update trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Sample data
INSERT INTO users (name, email, age) VALUES 
('John Doe', 'john@example.com', 30),
('Jane Smith', 'jane@example.com', 25),
('Bob Johnson', 'bob@example.com', 35);
```

#### Database connection (Python):
```python
import asyncpg
import asyncio
from typing import List, Optional
import os

class DatabaseManager:
    def __init__(self):
        self.pool = None
        
    async def initialize(self):
        """Initialize connection pool"""
        DATABASE_URL = os.getenv(
            'DATABASE_URL', 
            'postgresql://user:password@localhost:5432/myapp'
        )
        
        self.pool = await asyncpg.create_pool(
            DATABASE_URL,
            min_size=1,
            max_size=10,
            command_timeout=60
        )
        
    async def close(self):
        """Close connection pool"""
        if self.pool:
            await self.pool.close()
    
    async def create_user(self, name: str, email: str, age: Optional[int] = None) -> dict:
        """Create new user"""
        async with self.pool.acquire() as connection:
            query = """
                INSERT INTO users (name, email, age) 
                VALUES ($1, $2, $3) 
                RETURNING id, name, email, age, created_at
            """
            row = await connection.fetchrow(query, name, email, age)
            return dict(row)
    
    async def get_users(self, limit: int = 100, offset: int = 0) -> List[dict]:
        """Get users with pagination"""
        async with self.pool.acquire() as connection:
            query = """
                SELECT id, name, email, age, created_at 
                FROM users 
                ORDER BY created_at DESC 
                LIMIT $1 OFFSET $2
            """
            rows = await connection.fetch(query, limit, offset)
            return [dict(row) for row in rows]
    
    async def get_user_by_id(self, user_id: int) -> Optional[dict]:
        """Get user by ID"""
        async with self.pool.acquire() as connection:
            query = "SELECT * FROM users WHERE id = $1"
            row = await connection.fetchrow(query, user_id)
            return dict(row) if row else None
    
    async def update_user(self, user_id: int, **fields) -> Optional[dict]:
        """Update user fields"""
        if not fields:
            return None
            
        set_clause = ", ".join([f"{k} = ${i+2}" for i, k in enumerate(fields.keys())])
        query = f"""
            UPDATE users 
            SET {set_clause}
            WHERE id = $1 
            RETURNING *
        """
        
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow(query, user_id, *fields.values())
            return dict(row) if row else None
    
    async def delete_user(self, user_id: int) -> bool:
        """Delete user"""
        async with self.pool.acquire() as connection:
            query = "DELETE FROM users WHERE id = $1"
            result = await connection.execute(query, user_id)
            return result == "DELETE 1"

# Usage example
async def main():
    db = DatabaseManager()
    await db.initialize()
    
    try:
        # Create user
        user = await db.create_user("Alice", "alice@example.com", 28)
        print(f"Created user: {user}")
        
        # Get users
        users = await db.get_users(limit=10)
        print(f"Users: {users}")
        
        # Update user
        updated = await db.update_user(user['id'], age=29)
        print(f"Updated user: {updated}")
        
    finally:
        await db.close()

# asyncio.run(main())
```

## Deployment strategies

### 1. **Docker containerization**

#### Dockerfile best practices:
```dockerfile
# Multi-stage build for Python app
FROM python:3.11-slim as builder

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (for layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser

# Copy installed packages from builder
COPY --from=builder /root/.local /home/appuser/.local

# Set PATH to include user's local bin
ENV PATH=/home/appuser/.local/bin:$PATH

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Start application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Docker Compose for development:
```yaml
# docker-compose.yml
version: '3.8'

services:
  # Application
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/myapp
      - REDIS_URL=redis://redis:6379
      - ENV=development
    depends_on:
      - db
      - redis
    volumes:
      - .:/app  # Hot reload for development
    restart: unless-stopped

  # Database
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    restart: unless-stopped

  # Redis for caching/sessions
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    restart: unless-stopped

  # Nginx reverse proxy
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - app
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:

networks:
  default:
    driver: bridge
```

### 2. **CI/CD Pipeline**

#### GitHub Actions workflow:
```yaml
# .github/workflows/deploy.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        cache: 'pip'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run linting
      run: |
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        black --check .
        isort --check-only .
    
    - name: Run tests
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
      run: |
        pytest --cov=. --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

  build-and-push:
    needs: test
    runs-on: ubuntu-latest
    if: github.event_name == 'push'
    
    permissions:
      contents: read
      packages: write
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Log in to Container Registry
      uses: docker/login-action@v2
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v4
      with:
        images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
        tags: |
          type=ref,event=branch
          type=sha,prefix={{branch}}-
    
    - name: Build and push Docker image
      uses: docker/build-push-action@v4
      with:
        context: .
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}

  deploy-staging:
    needs: build-and-push
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/develop'
    environment: staging
    
    steps:
    - name: Deploy to staging
      run: |
        echo "Deploying to staging environment"
        # Add actual deployment commands here
        # e.g., kubectl, terraform, ansible, etc.

  deploy-production:
    needs: build-and-push
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment: production
    
    steps:
    - name: Deploy to production
      run: |
        echo "Deploying to production environment"
        # Add actual deployment commands here
```

### 3. **Cloud deployment options**

#### AWS deployment z Terraform:
```hcl
# main.tf
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Variables
variable "app_name" {
  description = "Application name"
  type        = string
  default     = "myapp"
}

variable "environment" {
  description = "Environment (dev/staging/prod)"
  type        = string
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

# VPC
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "${var.app_name}-vpc"
    Environment = var.environment
  }
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "${var.app_name}-igw"
  }
}

# Subnets
resource "aws_subnet" "public" {
  count = 2

  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.${count.index + 1}.0/24"
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true

  tags = {
    Name = "${var.app_name}-public-${count.index + 1}"
  }
}

resource "aws_subnet" "private" {
  count = 2

  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.${count.index + 10}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name = "${var.app_name}-private-${count.index + 1}"
  }
}

# Data source for AZs
data "aws_availability_zones" "available" {
  state = "available"
}

# Route table
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name = "${var.app_name}-public-rt"
  }
}

resource "aws_route_table_association" "public" {
  count = length(aws_subnet.public)

  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# Security Group
resource "aws_security_group" "app" {
  name_prefix = "${var.app_name}-app-"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.app_name}-app-sg"
  }
}

# Application Load Balancer
resource "aws_lb" "main" {
  name               = "${var.app_name}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.app.id]
  subnets            = aws_subnet.public[*].id

  enable_deletion_protection = false

  tags = {
    Name = "${var.app_name}-alb"
  }
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "${var.app_name}-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = {
    Name = "${var.app_name}-cluster"
  }
}

# ECS Task Definition
resource "aws_ecs_task_definition" "app" {
  family                   = "${var.app_name}-task"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn

  container_definitions = jsonencode([
    {
      name  = var.app_name
      image = "your-registry/your-app:latest"
      
      portMappings = [
        {
          containerPort = 8000
          protocol      = "tcp"
        }
      ]
      
      environment = [
        {
          name  = "ENV"
          value = var.environment
        }
      ]
      
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/${var.app_name}"
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])

  tags = {
    Name = "${var.app_name}-task"
  }
}

# ECS Service
resource "aws_ecs_service" "app" {
  name            = "${var.app_name}-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = 2
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.app.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.app.arn
    container_name   = var.app_name
    container_port   = 8000
  }

  depends_on = [aws_lb_listener.app]

  tags = {
    Name = "${var.app_name}-service"
  }
}

# IAM Role for ECS execution
resource "aws_iam_role" "ecs_execution_role" {
  name = "${var.app_name}-ecs-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_execution_role_policy" {
  role       = aws_iam_role.ecs_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# Outputs
output "load_balancer_dns" {
  description = "DNS name of the load balancer"
  value       = aws_lb.main.dns_name
}

output "cluster_name" {
  description = "Name of the ECS cluster"
  value       = aws_ecs_cluster.main.name
}
```

## Security best practices

### 1. **Authentication i Authorization**

```python
# JWT authentication example
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import secrets

app = FastAPI()
security = HTTPBearer()

# Security configuration
SECRET_KEY = secrets.token_urlsafe(32)  # Use environment variable in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthManager:
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)
    
    def create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    def verify_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

auth_manager = AuthManager()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Extract user from JWT token"""
    payload = auth_manager.verify_token(credentials.credentials)
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    return {"user_id": user_id, "payload": payload}

# Protected endpoint
@app.get("/protected")
async def protected_route(current_user = Depends(get_current_user)):
    return {"message": f"Hello user {current_user['user_id']}", "user": current_user}

# Login endpoint
@app.post("/login")
async def login(username: str, password: str):
    # In production, verify against database
    if username == "admin" and password == "secret":
        access_token = auth_manager.create_access_token(
            data={"sub": username, "role": "admin"}
        )
        return {"access_token": access_token, "token_type": "bearer"}
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password"
    )
```

### 2. **Environment configuration**

```python
# config.py - Environment-based configuration
import os
from typing import Optional
from pydantic import BaseSettings

class Settings(BaseSettings):
    # Application
    app_name: str = "MyApp"
    debug: bool = False
    secret_key: str
    
    # Database
    database_url: str
    database_pool_size: int = 5
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # Authentication
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30
    
    # Email
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    
    # AWS (if using)
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: str = "us-east-1"
    
    # Monitoring
    sentry_dsn: Optional[str] = None
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Environment-specific configurations
class DevelopmentSettings(Settings):
    debug: bool = True
    log_level: str = "DEBUG"

class ProductionSettings(Settings):
    debug: bool = False
    log_level: str = "WARNING"

class TestingSettings(Settings):
    debug: bool = True
    database_url: str = "sqlite:///./test.db"

def get_settings() -> Settings:
    env = os.getenv("ENV", "development").lower()
    
    if env == "production":
        return ProductionSettings()
    elif env == "testing":
        return TestingSettings()
    else:
        return DevelopmentSettings()

settings = get_settings()
```

### 3. **Monitoring i logging**

```python
# monitoring.py
import logging
import time
import psutil
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import Request, Response
import structlog

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')
ACTIVE_CONNECTIONS = Gauge('active_connections', 'Active database connections')
MEMORY_USAGE = Gauge('memory_usage_bytes', 'Memory usage in bytes')

# Structured logging setup
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

class MonitoringMiddleware:
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)
            start_time = time.time()
            
            # Process request
            response = await self.app(scope, receive, send)
            
            # Record metrics
            duration = time.time() - start_time
            REQUEST_DURATION.observe(duration)
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=request.url.path,
                status=response.status_code if hasattr(response, 'status_code') else 200
            ).inc()
            
            # Log request
            logger.info(
                "HTTP request",
                method=request.method,
                path=request.url.path,
                duration=duration,
                status_code=response.status_code if hasattr(response, 'status_code') else 200
            )
            
            return response
        
        return await self.app(scope, receive, send)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check with system metrics"""
    
    # Update system metrics
    MEMORY_USAGE.set(psutil.virtual_memory().used)
    
    # Check database connection
    try:
        # Attempt database query
        db_healthy = True
    except Exception:
        db_healthy = False
    
    status = "healthy" if db_healthy else "unhealthy"
    
    return {
        "status": status,
        "timestamp": time.time(),
        "version": "1.0.0",
        "checks": {
            "database": "ok" if db_healthy else "error",
            "memory_usage_mb": psutil.virtual_memory().used / 1024 / 1024,
            "cpu_percent": psutil.cpu_percent()
        }
    }

# Metrics endpoint for Prometheus
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type="text/plain")
```

## Podsumowanie - Decision Framework

### 1. **Architektura według rozmiaru zespołu**:

| Team Size | Recommended Architecture | Reasoning |
|-----------|-------------------------|-----------|
| 1-3 developers | Monolith | Simple, fast development |
| 4-10 developers | Modular Monolith | Organized but simple |
| 10+ developers | Microservices | Team autonomy |
| Variable/Contract | Serverless | No infrastructure management |

### 2. **Technology stack według przypadku**:

| Use Case | Backend | Frontend | Database | Deployment |
|----------|---------|----------|----------|------------|
| **Startup MVP** | FastAPI/Express | React/Vue | PostgreSQL | Docker + Cloud |
| **Enterprise** | Spring/Django | Angular | PostgreSQL/Oracle | Kubernetes |
| **High Traffic** | Go/Rust | React | PostgreSQL + Redis | Microservices |
| **Real-time** | Node.js/Go | React + WebSocket | Redis + PostgreSQL | Docker |

### 3. **Deployment według budżetu**:

| Budget | Option | Pros | Cons |
|--------|--------|------|------|
| **Low** | VPS + Docker | Cheap, simple | Manual scaling |
| **Medium** | Cloud PaaS | Managed, scalable | Vendor lock-in |
| **High** | Kubernetes | Ultimate flexibility | Complex management |

### ✅ **Final Checklist**:
- ✅ **Start simple** - można zawsze rozbudować
- ✅ **Security first** - uwierzytelnianie, autoryzacja, HTTPS
- ✅ **Monitor everything** - logi, metryki, health checks
- ✅ **Automate deployment** - CI/CD, infrastructure as code
- ✅ **Document architecture** - decision records, API docs
- ✅ **Plan for scale** - ale nie przedwcześnie optymalizuj
- ✅ **Test thoroughly** - unit, integration, e2e tests

**Remember: Perfect is the enemy of good - ship early, iterate fast!** 🚀