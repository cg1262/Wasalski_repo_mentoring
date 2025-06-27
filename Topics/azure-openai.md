# Azure OpenAI - podłączenie i działanie

## Co to jest Azure OpenAI?
Azure OpenAI to usługa Microsoft Azure, która umożliwia dostęp do zaawansowanych modeli sztucznej inteligencji OpenAI (takich jak GPT-4, GPT-3.5, DALL-E) przez chmurę Azure.

## Główne cechy:
- **Bezpieczeństwo**: Dane są przetwarzane w bezpiecznym środowisku Azure
- **Zgodność**: Spełnia standardy enterprise (GDPR, HIPAA)
- **Integracja**: Łatwa integracja z innymi usługami Azure
- **Kontrola**: Pełna kontrola nad danymi i modelami

## Jak się podłączyć?

### 1. Utworzenie zasobu Azure OpenAI
```bash
# Przez Azure CLI
az cognitiveservices account create \
  --name myOpenAIResource \
  --resource-group myResourceGroup \
  --kind OpenAI \
  --sku S0 \
  --location eastus
```

### 2. Pobieranie kluczy dostępu
- Endpoint URL
- API Key
- Deployment name

### 3. Przykład połączenia w Pythonie
```python
import openai
from openai import AzureOpenAI

# Konfiguracja
client = AzureOpenAI(
    api_key="your-api-key",
    api_version="2024-02-01",
    azure_endpoint="https://your-resource.openai.azure.com/"
)

# Przykład użycia
response = client.chat.completions.create(
    model="gpt-4",  # nazwa deployment
    messages=[
        {"role": "user", "content": "Witaj! Jak się masz?"}
    ],
    max_tokens=100
)

print(response.choices[0].message.content)
```

## Dostępne modele:
- **GPT-4**: Najnowszy model tekstowy
- **GPT-3.5**: Szybszy, tańszy model
- **DALL-E**: Generowanie obrazów
- **Whisper**: Rozpoznawanie mowy
- **Text-to-speech**: Synteza mowy

## Zalety Azure OpenAI vs OpenAI API:
- ✅ Większe bezpieczeństwo danych
- ✅ Zgodność z regulacjami korporacyjnymi
- ✅ Integracja z Azure
- ✅ SLA i wsparcie Microsoft
- ❌ Wyższe koszty
- ❌ Mniejsza dostępność niektórych modeli