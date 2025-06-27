# GitHub Actions - co to jest i jak działa?

## Co to jest GitHub Actions?

GitHub Actions to **platforma CI/CD** (Continuous Integration/Continuous Deployment) wbudowana w GitHub, która pozwala na automatyzację procesów deweloperskich.

### Główne cechy:
- 🤖 **Automatyzacja** - uruchamia się automatycznie na zdarzenia
- 🔗 **Integracja** - bezpośrednio w GitHub
- 🌐 **Cloud-based** - działa na serwerach GitHub
- 💰 **Free tier** - darmowe minuty dla repozytoriów publicznych
- 🔧 **Konfigurowalne** - pliki YAML

## Podstawowe pojęcia

### Struktura GitHub Actions:
```
Repository
├── .github/
│   └── workflows/
│       ├── ci.yml          # Workflow CI
│       ├── deploy.yml      # Workflow deployment
│       └── tests.yml       # Workflow testów
```

### Elementy składowe:
- **Workflow** - pełny proces automatyzacji
- **Job** - grupa kroków wykonywanych na tym samym runnerze
- **Step** - pojedynczy krok (np. uruchomienie komendy)
- **Action** - gotowy komponent do użycia
- **Runner** - maszyna wykonująca workflow

## Pierwszy workflow - przykład

### Podstawowy CI dla projektu Python:
```yaml
# .github/workflows/ci.yml
name: CI Pipeline                    # Nazwa workflow

on:                                 # Kiedy uruchomić
  push:                            # Po push do repo
    branches: [ main, develop ]    # Na tych branchach
  pull_request:                    # Przy pull request
    branches: [ main ]

jobs:                              # Zadania do wykonania
  test:                           # Nazwa job-a
    runs-on: ubuntu-latest        # System operacyjny
    
    strategy:                     # Matryca - testuj na różnych wersjach
      matrix:
        python-version: [3.8, 3.9, '3.10', 3.11]
    
    steps:                        # Kroki do wykonania
    - name: Checkout code         # Pobierz kod
      uses: actions/checkout@v4
      
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov
        
    - name: Run tests
      run: |
        pytest --cov=src --cov-report=xml
        
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

## Typy zdarzeń (triggers)

### Push i Pull Request:
```yaml
on:
  push:
    branches: [ main, develop ]
    paths: [ 'src/**', 'tests/**' ]  # Tylko gdy zmienią się te ścieżki
  pull_request:
    branches: [ main ]
    types: [opened, synchronize, reopened]
```

### Harmonogram (Cron):
```yaml
on:
  schedule:
    - cron: '0 2 * * *'  # Codziennie o 2:00 UTC
    - cron: '0 8 * * 1'  # Każdy poniedziałek o 8:00
```

### Ręczne uruchomienie:
```yaml
on:
  workflow_dispatch:     # Przycisk "Run workflow" w GitHub UI
    inputs:
      environment:
        description: 'Environment to deploy'
        required: true
        default: 'staging'
        type: choice
        options:
        - staging
        - production
```

### Inne zdarzenia:
```yaml
on:
  release:
    types: [published]   # Gdy utworzysz release
  issues:
    types: [opened]      # Gdy ktoś otworzy issue
  workflow_run:          # Po zakończeniu innego workflow
    workflows: ["CI"]
    types: [completed]
```

## Przykłady praktycznych workflow

### 1. **Node.js CI/CD**:
```yaml
name: Node.js CI/CD

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        node-version: [16.x, 18.x, 20.x]
        
    steps:
    - uses: actions/checkout@v4
    
    - name: Use Node.js ${{ matrix.node-version }}
      uses: actions/setup-node@v3
      with:
        node-version: ${{ matrix.node-version }}
        cache: 'npm'
    
    - name: Install dependencies
      run: npm ci
      
    - name: Run linter
      run: npm run lint
      
    - name: Run tests
      run: npm test
      
    - name: Build
      run: npm run build
      
  deploy:
    needs: test                    # Uruchom tylko po pomyślnych testach
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'  # Tylko na main branch
    
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-node@v3
      with:
        node-version: '18.x'
        cache: 'npm'
        
    - run: npm ci
    - run: npm run build
    
    - name: Deploy to Netlify
      uses: nwtgck/actions-netlify@v2.0
      with:
        publish-dir: './dist'
        production-branch: main
      env:
        NETLIFY_AUTH_TOKEN: ${{ secrets.NETLIFY_AUTH_TOKEN }}
        NETLIFY_SITE_ID: ${{ secrets.NETLIFY_SITE_ID }}
```

### 2. **Docker Build i Push**:
```yaml
name: Docker Build and Push

on:
  push:
    branches: [ main ]
    tags: [ 'v*' ]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
      
    steps:
    - name: Checkout
      uses: actions/checkout@v4
      
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
          type=ref,event=pr
          type=semver,pattern={{version}}
          
    - name: Build and push
      uses: docker/build-push-action@v4
      with:
        context: .
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
```

### 3. **Multi-stage deployment**:
```yaml
name: Deploy to Staging and Production

on:
  push:
    branches: [ main ]

jobs:
  deploy-staging:
    runs-on: ubuntu-latest
    environment: staging
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Deploy to staging
      run: |
        echo "Deploying to staging..."
        # Twoje komendy deployment
        
  deploy-production:
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment: production
    if: github.event_name == 'push'
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Deploy to production
      run: |
        echo "Deploying to production..."
        # Twoje komendy deployment
```

## Secrets i Environment Variables

### Ustawienie secrets:
1. Repository Settings → Secrets and variables → Actions
2. Dodaj secrets (np. API keys, hasła)

### Użycie w workflow:
```yaml
steps:
- name: Deploy
  env:
    API_KEY: ${{ secrets.API_KEY }}
    DATABASE_URL: ${{ secrets.DATABASE_URL }}
    NODE_ENV: production
  run: |
    echo "Deploying with API_KEY: ${API_KEY:0:5}..." # Pokaż tylko pierwsze 5 znaków
```

### Environment-specific secrets:
```yaml
jobs:
  deploy:
    environment: production  # Używa secrets z environment "production"
    steps:
    - name: Deploy
      env:
        API_KEY: ${{ secrets.PROD_API_KEY }}
```

## Gotowe Actions (Marketplace)

### Popularne Actions:
```yaml
steps:
# Pobieranie kodu
- uses: actions/checkout@v4

# Setup języków
- uses: actions/setup-python@v4
- uses: actions/setup-node@v3
- uses: actions/setup-java@v3
- uses: actions/setup-go@v4

# Cache dependencies
- uses: actions/cache@v3
  with:
    path: ~/.npm
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}

# Upload artifacts
- uses: actions/upload-artifact@v3
  with:
    name: build-files
    path: dist/

# Download artifacts
- uses: actions/download-artifact@v3
  with:
    name: build-files

# Slack notifications
- uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

## Zaawansowane funkcje

### Matrix builds:
```yaml
strategy:
  matrix:
    os: [ubuntu-latest, windows-latest, macos-latest]
    python-version: [3.8, 3.9, '3.10']
    include:
      - os: ubuntu-latest
        python-version: 3.11
    exclude:
      - os: windows-latest
        python-version: 3.8
```

### Conditional steps:
```yaml
steps:
- name: Run only on main branch
  if: github.ref == 'refs/heads/main'
  run: echo "This is main branch"
  
- name: Run only on PR
  if: github.event_name == 'pull_request'
  run: echo "This is a PR"
  
- name: Run only on success
  if: success()
  run: echo "Previous steps succeeded"
  
- name: Run always (even on failure)
  if: always()
  run: echo "This always runs"
```

### Reusable workflows:
```yaml
# .github/workflows/reusable-deploy.yml
on:
  workflow_call:
    inputs:
      environment:
        required: true
        type: string
    secrets:
      api-key:
        required: true

jobs:
  deploy:
    environment: ${{ inputs.environment }}
    runs-on: ubuntu-latest
    steps:
    - name: Deploy
      env:
        API_KEY: ${{ secrets.api-key }}
      run: echo "Deploying to ${{ inputs.environment }}"
```

```yaml
# Użycie reusable workflow
jobs:
  deploy-staging:
    uses: ./.github/workflows/reusable-deploy.yml
    with:
      environment: staging
    secrets:
      api-key: ${{ secrets.STAGING_API_KEY }}
```

## Monitoring i debugging

### Logi i status:
```yaml
steps:
- name: Debug info
  run: |
    echo "Event: ${{ github.event_name }}"
    echo "Branch: ${{ github.ref }}"
    echo "Commit: ${{ github.sha }}"
    echo "Actor: ${{ github.actor }}"
    
- name: List files
  run: ls -la
  
- name: Environment variables
  run: env | sort
```

### Artifacts dla debugowania:
```yaml
- name: Upload logs
  if: failure()
  uses: actions/upload-artifact@v3
  with:
    name: debug-logs
    path: |
      *.log
      coverage/
```

## Koszty i limity

### GitHub Free:
- 🔓 **Publiczne repos**: Unlimited
- 🔒 **Prywatne repos**: 2000 minut/miesiąc
- 💾 **Storage**: 500 MB

### GitHub Pro/Team/Enterprise:
- 📈 **Więcej minut** - 3000/10000+ minut
- 🏃‍♂️ **Self-hosted runners** - własne maszyny
- 🔧 **Zaawansowane funkcje**

### Optymalizacja kosztów:
```yaml
# Używaj cache dla dependencies
- uses: actions/cache@v3
  
# Uruchamiaj tylko gdy potrzeba
on:
  push:
    paths: ['src/**', 'tests/**']
    
# Anuluj poprzednie runny
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

## Porównanie z konkurencją

| Feature | GitHub Actions | Jenkins | GitLab CI | Azure DevOps |
|---------|----------------|---------|-----------|---------------|
| **Hosting** | GitHub cloud | Self-hosted | GitLab/Self | Azure cloud |
| **Setup** | Zero config | Complex | Medium | Medium |
| **Marketplace** | Huge | Plugins | Limited | Extensions |
| **Cost** | Free tier | Free | Free tier | Free tier |
| **Integration** | GitHub native | Universal | GitLab native | Azure native |

## Najlepsze praktyki

### 1. **Bezpieczeństwo**:
```yaml
# Używaj pinned versions
- uses: actions/checkout@8f4b7c84ec53a9bb0b3c7b7f5a2b1c3d4e5f6789
# Zamiast: - uses: actions/checkout@v4

# Ogranicz permissions
permissions:
  contents: read
  packages: write
```

### 2. **Wydajność**:
```yaml
# Cache dependencies
- uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}

# Fail fast
strategy:
  fail-fast: true
```

### 3. **Maintainability**:
```yaml
# Używaj environment variables
env:
  NODE_VERSION: '18.x'
  PYTHON_VERSION: '3.10'

# Composite actions dla powtarzalnych kroków
```

GitHub Actions to potężne narzędzie do automatyzacji - idealne do CI/CD, testowania i deploymentu! 🚀