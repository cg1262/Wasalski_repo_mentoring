# Jenkins - do czego służy i jak działa?

## Co to jest Jenkins?

Jenkins to **open-source server automatyzacji** używany do CI/CD (Continuous Integration/Continuous Deployment). To jeden z najstarszych i najpopularniejszych narzędzi DevOps.

### Główne cechy:
- 🔧 **Self-hosted** - instalujesz na własnych serwerach
- 🔌 **Plugin ecosystem** - tysiące pluginów
- 📝 **Pipeline as Code** - Jenkinsfile
- 🔄 **Distributed builds** - master-slave architecture
- 🌐 **Web interface** - graficzny interfejs użytkownika

## Architektura Jenkins

### Komponenty:
```
Jenkins Master (Controller)
├── Web UI
├── Job Scheduler
├── Plugin Manager
└── Build Queue

Jenkins Agents (Nodes)
├── Agent 1 (Linux)
├── Agent 2 (Windows)
├── Agent 3 (Docker)
└── Agent 4 (macOS)
```

### Master vs Agent:
- **Master**: Zarządza jobami, interfejs web, plugins
- **Agent**: Wykonuje build-y, może być na różnych maszynach/OS

## Instalacja Jenkins

### Docker (najłatwiejszy sposób):
```bash
# Pobierz i uruchom Jenkins
docker run -d \
  --name jenkins \
  -p 8080:8080 \
  -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  jenkins/jenkins:lts

# Sprawdź initial admin password
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

### Linux (Ubuntu/Debian):
```bash
# Dodaj klucz Jenkins
wget -q -O - https://pkg.jenkins.io/debian/jenkins.io.key | sudo apt-key add -

# Dodaj repository
echo deb https://pkg.jenkins.io/debian binary/ | sudo tee /etc/apt/sources.list.d/jenkins.list

# Instaluj
sudo apt update
sudo apt install openjdk-11-jdk jenkins

# Uruchom
sudo systemctl start jenkins
sudo systemctl enable jenkins

# Jenkins dostępny na http://localhost:8080
```

## Pierwszy Job - przykład

### 1. **Freestyle Project** (tradycyjny sposób):
```
1. New Item → Freestyle Project
2. Source Code Management → Git
   Repository URL: https://github.com/user/repo.git
3. Build Triggers → Poll SCM
   Schedule: H/5 * * * * (co 5 minut)
4. Build Steps → Execute shell:
   #!/bin/bash
   echo "Building project..."
   npm install
   npm test
   npm run build
5. Post-build Actions → Archive artifacts
   Files to archive: dist/**
```

### 2. **Pipeline Job** (nowoczesny sposób):
```groovy
// Jenkinsfile
pipeline {
    agent any
    
    stages {
        stage('Checkout') {
            steps {
                git 'https://github.com/user/repo.git'
            }
        }
        
        stage('Build') {
            steps {
                sh 'npm install'
                sh 'npm run build'
            }
        }
        
        stage('Test') {
            steps {
                sh 'npm test'
            }
            post {
                always {
                    junit 'test-results.xml'
                }
            }
        }
        
        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                sh 'npm run deploy'
            }
        }
    }
    
    post {
        success {
            emailext (
                subject: "Build Success: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
                body: "Build completed successfully!",
                to: "${env.CHANGE_AUTHOR_EMAIL}"
            )
        }
        failure {
            emailext (
                subject: "Build Failed: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
                body: "Build failed. Check console output.",
                to: "${env.CHANGE_AUTHOR_EMAIL}"
            )
        }
    }
}
```

## Zaawansowane Pipeline przykłady

### 1. **Multi-stage Pipeline z różnymi agentami**:
```groovy
pipeline {
    agent none
    
    stages {
        stage('Build') {
            agent {
                docker {
                    image 'node:16'
                    args '-v /var/run/docker.sock:/var/run/docker.sock'
                }
            }
            steps {
                sh 'npm install'
                sh 'npm run build'
                stash includes: 'dist/**', name: 'built-app'
            }
        }
        
        stage('Test') {
            parallel {
                stage('Unit Tests') {
                    agent {
                        label 'linux'
                    }
                    steps {
                        unstash 'built-app'
                        sh 'npm test'
                    }
                }
                
                stage('Integration Tests') {
                    agent {
                        label 'docker'
                    }
                    steps {
                        unstash 'built-app'
                        sh 'docker-compose -f docker-compose.test.yml up --abort-on-container-exit'
                    }
                }
                
                stage('Security Scan') {
                    agent any
                    steps {
                        sh 'npm audit'
                        sh 'snyk test'
                    }
                }
            }
        }
        
        stage('Deploy to Staging') {
            agent {
                label 'staging-server'
            }
            steps {
                unstash 'built-app'
                sh './deploy-staging.sh'
            }
        }
        
        stage('Manual Approval') {
            steps {
                input message: 'Deploy to production?', 
                      ok: 'Deploy',
                      submitterParameter: 'APPROVER'
            }
        }
        
        stage('Deploy to Production') {
            agent {
                label 'production-server'
            }
            steps {
                unstash 'built-app'
                sh './deploy-production.sh'
            }
        }
    }
}
```

### 2. **Parametrized Pipeline**:
```groovy
pipeline {
    agent any
    
    parameters {
        choice(
            name: 'ENVIRONMENT',
            choices: ['staging', 'production'],
            description: 'Choose deployment environment'
        )
        booleanParam(
            name: 'RUN_TESTS',
            defaultValue: true,
            description: 'Run tests before deployment'
        )
        string(
            name: 'BRANCH_NAME',
            defaultValue: 'main',
            description: 'Branch to deploy'
        )
    }
    
    stages {
        stage('Checkout') {
            steps {
                git branch: "${params.BRANCH_NAME}", 
                    url: 'https://github.com/user/repo.git'
            }
        }
        
        stage('Test') {
            when {
                expression { params.RUN_TESTS }
            }
            steps {
                sh 'npm test'
            }
        }
        
        stage('Deploy') {
            steps {
                script {
                    if (params.ENVIRONMENT == 'production') {
                        sh './deploy-prod.sh'
                    } else {
                        sh './deploy-staging.sh'
                    }
                }
            }
        }
    }
}
```

## Najważniejsze Pluginy

### Essential Plugins:
```groovy
// Pipeline plugins
plugins {
    id 'pipeline-stage-view' // Wizualizacja pipeline
    id 'blue-ocean'          // Nowoczesny UI
    id 'pipeline-graph-analysis' // Analiza pipeline
}

// Source Control
- Git Plugin
- GitHub Plugin
- GitLab Plugin
- Bitbucket Plugin

// Build Tools
- Maven Integration
- Gradle Plugin
- NodeJS Plugin
- Docker Plugin

// Testing & Quality
- JUnit Plugin
- Cobertura Plugin
- SonarQube Scanner
- Checkstyle Plugin

// Deployment
- SSH Plugin
- Kubernetes Plugin
- AWS Steps
- Azure CLI Plugin

// Notifications
- Email Extension
- Slack Notification
- Microsoft Teams Notification
```

### Przykład użycia pluginów w Pipeline:
```groovy
pipeline {
    agent any
    
    tools {
        nodejs '16.x'
        maven '3.8.1'
    }
    
    stages {
        stage('Quality Gate') {
            steps {
                // SonarQube analysis
                withSonarQubeEnv('SonarQube') {
                    sh 'mvn sonar:sonar'
                }
                
                // Wait for Quality Gate
                timeout(time: 1, unit: 'HOURS') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }
        
        stage('Docker Build') {
            steps {
                script {
                    def image = docker.build("myapp:${env.BUILD_NUMBER}")
                    docker.withRegistry('https://registry.hub.docker.com', 'docker-hub-credentials') {
                        image.push()
                        image.push("latest")
                    }
                }
            }
        }
        
        stage('Deploy to Kubernetes') {
            steps {
                kubernetesDeploy(
                    configs: 'k8s/*.yaml',
                    kubeconfigId: 'kubeconfig-credentials'
                )
            }
        }
    }
    
    post {
        always {
            // Slack notification
            slackSend(
                channel: '#deployments',
                color: currentBuild.result == 'SUCCESS' ? 'good' : 'danger',
                message: "Build ${currentBuild.result}: ${env.JOB_NAME} - ${env.BUILD_NUMBER}"
            )
        }
    }
}
```

## Jenkins Configuration as Code (JCasC)

### jenkins.yaml:
```yaml
jenkins:
  systemMessage: "Jenkins managed by Configuration as Code"
  numExecutors: 0
  mode: EXCLUSIVE
  
  securityRealm:
    local:
      allowsSignup: false
      users:
        - id: "admin"
          password: "${JENKINS_ADMIN_PASSWORD}"
          
  authorizationStrategy:
    roleBased:
      roles:
        global:
          - name: "admin"
            description: "Jenkins administrators"
            permissions:
              - "Overall/Administer"
            assignments:
              - "admin"
              
  clouds:
    - docker:
        name: "docker-cloud"
        dockerApi:
          dockerHost:
            uri: "unix:///var/run/docker.sock"
        templates:
          - labelString: "docker-agent"
            dockerTemplateBase:
              image: "jenkins/inbound-agent:latest"

jobs:
  - script: |
      pipelineJob('example-pipeline') {
        definition {
          cpsScm {
            scm {
              git {
                remote {
                  url('https://github.com/user/repo.git')
                }
                branch('*/main')
              }
            }
            scriptPath('Jenkinsfile')
          }
        }
      }

credentials:
  system:
    domainCredentials:
      - credentials:
          - usernamePassword:
              scope: GLOBAL
              id: "github-credentials"
              username: "${GITHUB_USERNAME}"
              password: "${GITHUB_TOKEN}"
```

## Monitoring i Performance

### Build Metrics:
```groovy
pipeline {
    agent any
    
    stages {
        stage('Build') {
            steps {
                script {
                    def startTime = System.currentTimeMillis()
                    
                    sh 'npm install'
                    sh 'npm run build'
                    
                    def duration = System.currentTimeMillis() - startTime
                    echo "Build took ${duration}ms"
                    
                    // Send metrics to monitoring system
                    httpRequest(
                        httpMode: 'POST',
                        url: 'http://metrics-server/api/metrics',
                        requestBody: """
                        {
                            "metric": "build_duration",
                            "value": ${duration},
                            "tags": {
                                "job": "${env.JOB_NAME}",
                                "build": "${env.BUILD_NUMBER}"
                            }
                        }
                        """
                    )
                }
            }
        }
    }
}
```

### Health checks:
```bash
# Jenkins health check endpoints
curl http://jenkins:8080/api/json?pretty=true
curl http://jenkins:8080/computer/api/json?pretty=true

# Plugin information
curl http://jenkins:8080/pluginManager/api/json?depth=1

# Build queue
curl http://jenkins:8080/queue/api/json?pretty=true
```

## Jenkins vs Konkurencja

| Feature | Jenkins | GitHub Actions | GitLab CI | Azure DevOps |
|---------|---------|----------------|-----------|---------------|
| **Hosting** | Self-hosted | Cloud | Cloud/Self | Cloud/Self |
| **Setup** | Complex | Easy | Medium | Medium |
| **Plugins** | 1800+ | Marketplace | Limited | Extensions |
| **Cost** | Free | Free tier | Free tier | Free tier |
| **Learning curve** | Steep | Easy | Medium | Medium |
| **Flexibility** | Maximum | High | Medium | High |
| **Enterprise** | Excellent | Good | Excellent | Excellent |

## Najlepsze praktyki

### 1. **Bezpieczeństwo**:
```groovy
// Używaj credentials
withCredentials([
    usernamePassword(credentialsId: 'db-credentials', 
                    usernameVariable: 'DB_USER', 
                    passwordVariable: 'DB_PASS')
]) {
    sh 'mysql -u $DB_USER -p$DB_PASS < schema.sql'
}

// Sandbox dla Pipeline scripts
// Enable "Use Groovy Sandbox" w job configuration

// RBAC - Role-Based Access Control
// Używaj Matrix Authorization Strategy
```

### 2. **Performance**:
```groovy
// Parallel execution
stage('Tests') {
    parallel {
        stage('Unit Tests') {
            steps { sh 'npm run test:unit' }
        }
        stage('Integration Tests') {
            steps { sh 'npm run test:integration' }
        }
        stage('E2E Tests') {
            steps { sh 'npm run test:e2e' }
        }
    }
}

// Stash/Unstash dla współdzielenia plików
stash includes: 'dist/**', name: 'built-files'
unstash 'built-files'

// Build retention
properties([
    buildDiscarder(
        logRotator(
            daysToKeepStr: '30',
            numToKeepStr: '100'
        )
    )
])
```

### 3. **Maintainability**:
```groovy
// Shared Library
@Library('my-shared-library') _

pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                buildNodeApp()  // Function from shared library
            }
        }
    }
}

// vars/buildNodeApp.groovy w shared library
def call() {
    sh 'npm install'
    sh 'npm run build'
    sh 'npm test'
}
```

## Backup i Disaster Recovery

### Backup Jenkins:
```bash
#!/bin/bash
# Backup script
JENKINS_HOME=/var/lib/jenkins
BACKUP_DIR=/backup/jenkins
DATE=$(date +%Y%m%d_%H%M%S)

# Stop Jenkins
sudo systemctl stop jenkins

# Create backup
tar -czf ${BACKUP_DIR}/jenkins_backup_${DATE}.tar.gz \
    ${JENKINS_HOME}/config.xml \
    ${JENKINS_HOME}/jobs/ \
    ${JENKINS_HOME}/plugins/ \
    ${JENKINS_HOME}/users/ \
    ${JENKINS_HOME}/secrets/

# Start Jenkins
sudo systemctl start jenkins

# Keep only last 7 backups
find ${BACKUP_DIR} -name "jenkins_backup_*.tar.gz" -mtime +7 -delete
```

### Restore:
```bash
# Stop Jenkins
sudo systemctl stop jenkins

# Restore from backup
cd /var/lib/jenkins
sudo tar -xzf /backup/jenkins/jenkins_backup_20240101_120000.tar.gz

# Fix permissions
sudo chown -R jenkins:jenkins /var/lib/jenkins

# Start Jenkins
sudo systemctl start jenkins
```

## Podsumowanie

### ✅ Używaj Jenkins gdy:
- Masz dedykowany zespół DevOps
- Potrzebujesz maksymalnej elastyczności
- Masz złożone wymagania CI/CD
- Chcesz pełną kontrolę nad infrastrukturą
- Masz budżet na maintenance

### ❌ Unikaj Jenkins gdy:
- Mały zespół bez doświadczenia DevOps
- Potrzebujesz szybkiego setup-u
- Preferujesz cloud-native rozwiązania
- Ograniczony budżet na infrastrukturę
- Proste wymagania CI/CD

**Jenkins = Maximum flexibility, Maximum complexity** 🛠️