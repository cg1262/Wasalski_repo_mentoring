# SAS URL - co to jest?

## Co to jest SAS URL?

SAS URL (Shared Access Signature URL) to **bezpieczny sposób udzielania czasowego dostępu** do zasobów w Azure Storage bez udostępniania kluczy konta. 

### Główne cechy:
- 🔐 **Czasowy dostęp** - można ustawić czas wygaśnięcia
- 🎯 **Granularne uprawnienia** - read, write, delete, list
- 📍 **Ograniczony zasięg** - konkretne kontenery, pliki lub tabele
- 🛡️ **Bezpieczny** - nie wymaga udostępniania kluczy storage account
- 🌐 **Uniwersalny** - działa z HTTP/HTTPS requests

## Typy SAS

### 1. **Account SAS**:
```
Dostęp do wielu usług w storage account:
├── Blob storage
├── File storage  
├── Queue storage
└── Table storage
```

### 2. **Service SAS**:
```
Dostęp do konkretnej usługi:
├── Blob service only
├── File service only
├── Queue service only
└── Table service only
```

### 3. **User Delegation SAS** (zalecane):
```
Uwierzytelnianie przez Azure AD:
├── Bazuje na Azure AD credentials
├── Większe bezpieczeństwo
├── Można odwołać przez Azure AD
└── Audit trail w Azure AD
```

## Tworzenie SAS URL

### 1. **Azure Portal**:

```
1. Idź do Storage Account
2. Wybierz Container/Blob
3. Kliknij "Generate SAS"
4. Ustaw:
   - Permissions (Read, Write, Delete, List)
   - Start/Expiry time
   - Allowed IP addresses (optional)
   - Allowed protocols (HTTPS only)
5. Kliknij "Generate SAS URL"
```

### 2. **Azure CLI**:

```bash
# Generate SAS for container
az storage container generate-sas \
    --account-name mystorageaccount \
    --name mycontainer \
    --permissions rwdl \
    --expiry 2024-12-31T23:59:59Z \
    --https-only

# Generate SAS for specific blob
az storage blob generate-sas \
    --account-name mystorageaccount \
    --container-name mycontainer \
    --name myfile.txt \
    --permissions rw \
    --expiry 2024-02-15T23:59:59Z \
    --https-only

# Generate Account SAS
az storage account generate-sas \
    --account-name mystorageaccount \
    --account-key YOUR_ACCOUNT_KEY \
    --services b \
    --resource-types sco \
    --permissions rwdlacup \
    --expiry 2024-12-31T23:59:59Z \
    --https-only
```

### 3. **PowerShell**:

```powershell
# Connect to Azure
Connect-AzAccount

# Set context
$ctx = (Get-AzStorageAccount -ResourceGroupName "myRG" -Name "mystorageaccount").Context

# Generate container SAS
$containerSAS = New-AzStorageContainerSASToken -Context $ctx -Container "mycontainer" -Permission rwdl -ExpiryTime (Get-Date).AddDays(30)

# Generate blob SAS
$blobSAS = New-AzStorageBlobSASToken -Context $ctx -Container "mycontainer" -Blob "myfile.txt" -Permission rw -ExpiryTime (Get-Date).AddHours(24)

# Full URL
$blobURL = (Get-AzStorageBlob -Context $ctx -Container "mycontainer" -Blob "myfile.txt").ICloudBlob.StorageUri.PrimaryUri.ToString() + $blobSAS

Write-Host "SAS URL: $blobURL"
```

### 4. **Python SDK**:

```python
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta
import os

# Connection string
connection_string = "DefaultEndpointsProtocol=https;AccountName=mystorageaccount;AccountKey=...;EndpointSuffix=core.windows.net"

# Initialize client
blob_service_client = BlobServiceClient.from_connection_string(connection_string)

def generate_sas_url(account_name, account_key, container_name, blob_name, hours=24):
    """Generate SAS URL for a blob"""
    
    # Calculate expiry time
    expiry_time = datetime.utcnow() + timedelta(hours=hours)
    
    # Define permissions
    permissions = BlobSasPermissions(read=True, write=True, delete=False)
    
    # Generate SAS token
    sas_token = generate_blob_sas(
        account_name=account_name,
        container_name=container_name,
        blob_name=blob_name,
        account_key=account_key,
        permission=permissions,
        expiry=expiry_time,
        protocol="https"
    )
    
    # Construct full URL
    blob_url = f"https://{account_name}.blob.core.windows.net/{container_name}/{blob_name}?{sas_token}"
    
    return blob_url, sas_token

# Example usage
account_name = "mystorageaccount" 
account_key = "your_account_key"
container_name = "documents"
blob_name = "report.pdf"

sas_url, sas_token = generate_sas_url(account_name, account_key, container_name, blob_name, hours=48)

print(f"SAS URL: {sas_url}")
print(f"Expires in 48 hours")
```

### 5. **C# .NET**:

```csharp
using Azure.Storage.Blobs;
using Azure.Storage.Sas;
using System;

public class SasUrlGenerator
{
    private readonly BlobServiceClient _blobServiceClient;
    
    public SasUrlGenerator(string connectionString)
    {
        _blobServiceClient = new BlobServiceClient(connectionString);
    }
    
    public string GenerateBlobSasUrl(string containerName, string blobName, int hoursValid = 24)
    {
        // Get blob client
        var blobClient = _blobServiceClient
            .GetBlobContainerClient(containerName)
            .GetBlobClient(blobName);
        
        // Check if we can generate SAS (need account key)
        if (!blobClient.CanGenerateSasUri)
        {
            throw new InvalidOperationException("Cannot generate SAS URL. Ensure you're using account key authentication.");
        }
        
        // Create SAS permissions
        var sasBuilder = new BlobSasBuilder
        {
            BlobContainerName = containerName,
            BlobName = blobName,
            Resource = "b", // blob
            ExpiresOn = DateTimeOffset.UtcNow.AddHours(hoursValid)
        };
        
        // Set permissions
        sasBuilder.SetPermissions(BlobSasPermissions.Read | BlobSasPermissions.Write);
        
        // Generate SAS URL
        var sasUrl = blobClient.GenerateSasUri(sasBuilder);
        
        return sasUrl.ToString();
    }
    
    public string GenerateContainerSasUrl(string containerName, int hoursValid = 24)
    {
        var containerClient = _blobServiceClient.GetBlobContainerClient(containerName);
        
        if (!containerClient.CanGenerateSasUri)
        {
            throw new InvalidOperationException("Cannot generate SAS URL.");
        }
        
        var sasBuilder = new BlobSasBuilder
        {
            BlobContainerName = containerName,
            Resource = "c", // container
            ExpiresOn = DateTimeOffset.UtcNow.AddHours(hoursValid)
        };
        
        sasBuilder.SetPermissions(
            BlobContainerSasPermissions.Read | 
            BlobContainerSasPermissions.Write | 
            BlobContainerSasPermissions.List
        );
        
        return containerClient.GenerateSasUri(sasBuilder).ToString();
    }
}

// Usage
var sasGenerator = new SasUrlGenerator("your_connection_string");

// Generate blob SAS URL
string blobSasUrl = sasGenerator.GenerateBlobSasUrl("documents", "report.pdf", 48);
Console.WriteLine($"Blob SAS URL: {blobSasUrl}");

// Generate container SAS URL
string containerSasUrl = sasGenerator.GenerateContainerSasUrl("documents", 24);
Console.WriteLine($"Container SAS URL: {containerSasUrl}");
```

## Practical examples

### 1. **File upload through web application**:

```python
from flask import Flask, request, render_template, jsonify
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta
import uuid

app = Flask(__name__)

class FileUploadService:
    def __init__(self, connection_string):
        self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        self.container_name = "uploads"
    
    def generate_upload_sas(self, file_extension, hours=1):
        """Generate SAS URL for file upload"""
        
        # Generate unique filename
        filename = f"{uuid.uuid4()}.{file_extension}"
        
        # Create SAS with write permissions
        expiry_time = datetime.utcnow() + timedelta(hours=hours)
        permissions = BlobSasPermissions(write=True, create=True)
        
        sas_token = generate_blob_sas(
            account_name=self.blob_service_client.account_name,
            container_name=self.container_name,
            blob_name=filename,
            account_key=self.blob_service_client.credential.account_key,
            permission=permissions,
            expiry=expiry_time
        )
        
        upload_url = f"https://{self.blob_service_client.account_name}.blob.core.windows.net/{self.container_name}/{filename}?{sas_token}"
        
        return {
            "upload_url": upload_url,
            "filename": filename,
            "expires_at": expiry_time.isoformat()
        }
    
    def generate_download_sas(self, filename, hours=24):
        """Generate SAS URL for file download"""
        
        expiry_time = datetime.utcnow() + timedelta(hours=hours)
        permissions = BlobSasPermissions(read=True)
        
        sas_token = generate_blob_sas(
            account_name=self.blob_service_client.account_name,
            container_name=self.container_name,
            blob_name=filename,
            account_key=self.blob_service_client.credential.account_key,
            permission=permissions,
            expiry=expiry_time
        )
        
        download_url = f"https://{self.blob_service_client.account_name}.blob.core.windows.net/{self.container_name}/{filename}?{sas_token}"
        
        return {
            "download_url": download_url,
            "expires_at": expiry_time.isoformat()
        }

# Initialize service
upload_service = FileUploadService("your_connection_string")

@app.route('/upload/request', methods=['POST'])
def request_upload():
    """Request SAS URL for file upload"""
    data = request.get_json()
    file_extension = data.get('file_extension', 'txt')
    
    try:
        sas_info = upload_service.generate_upload_sas(file_extension)
        return jsonify({
            "success": True,
            "upload_url": sas_info["upload_url"],
            "filename": sas_info["filename"],
            "expires_at": sas_info["expires_at"]
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """Generate download SAS URL"""
    try:
        sas_info = upload_service.generate_download_sas(filename)
        return jsonify({
            "success": True,
            "download_url": sas_info["download_url"],
            "expires_at": sas_info["expires_at"]
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

### 2. **JavaScript client-side upload**:

```javascript
// Client-side file upload using SAS URL
class FileUploader {
    constructor(apiBaseUrl) {
        this.apiBaseUrl = apiBaseUrl;
    }
    
    async uploadFile(file) {
        try {
            // Step 1: Request SAS URL from your API
            const uploadRequest = await fetch(`${this.apiBaseUrl}/upload/request`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    file_extension: file.name.split('.').pop()
                })
            });
            
            const uploadInfo = await uploadRequest.json();
            
            if (!uploadInfo.success) {
                throw new Error(uploadInfo.error);
            }
            
            // Step 2: Upload directly to Azure Storage using SAS URL
            const uploadResponse = await fetch(uploadInfo.upload_url, {
                method: 'PUT',
                headers: {
                    'x-ms-blob-type': 'BlockBlob',
                    'Content-Type': file.type
                },
                body: file
            });
            
            if (!uploadResponse.ok) {
                throw new Error(`Upload failed: ${uploadResponse.statusText}`);
            }
            
            return {
                success: true,
                filename: uploadInfo.filename,
                uploadUrl: uploadInfo.upload_url
            };
            
        } catch (error) {
            console.error('Upload error:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }
    
    // Progress tracking
    async uploadFileWithProgress(file, onProgress) {
        return new Promise(async (resolve, reject) => {
            try {
                // Get SAS URL
                const uploadRequest = await fetch(`${this.apiBaseUrl}/upload/request`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ file_extension: file.name.split('.').pop() })
                });
                
                const uploadInfo = await uploadRequest.json();
                
                // Upload with progress
                const xhr = new XMLHttpRequest();
                
                xhr.upload.addEventListener('progress', (e) => {
                    if (e.lengthComputable) {
                        const percentComplete = (e.loaded / e.total) * 100;
                        onProgress(percentComplete);
                    }
                });
                
                xhr.addEventListener('load', () => {
                    if (xhr.status >= 200 && xhr.status < 300) {
                        resolve({
                            success: true,
                            filename: uploadInfo.filename
                        });
                    } else {
                        reject(new Error(`Upload failed: ${xhr.statusText}`));
                    }
                });
                
                xhr.addEventListener('error', () => {
                    reject(new Error('Upload failed'));
                });
                
                xhr.open('PUT', uploadInfo.upload_url);
                xhr.setRequestHeader('x-ms-blob-type', 'BlockBlob');
                xhr.setRequestHeader('Content-Type', file.type);
                xhr.send(file);
                
            } catch (error) {
                reject(error);
            }
        });
    }
}

// Usage
const uploader = new FileUploader('https://your-api.com');

// Simple upload
document.getElementById('fileInput').addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (file) {
        const result = await uploader.uploadFile(file);
        if (result.success) {
            console.log('File uploaded successfully:', result.filename);
        } else {
            console.error('Upload failed:', result.error);
        }
    }
});

// Upload with progress
document.getElementById('fileInputProgress').addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (file) {
        const progressBar = document.getElementById('progressBar');
        
        try {
            const result = await uploader.uploadFileWithProgress(file, (progress) => {
                progressBar.style.width = `${progress}%`;
                progressBar.textContent = `${Math.round(progress)}%`;
            });
            
            console.log('Upload completed:', result);
        } catch (error) {
            console.error('Upload error:', error);
        }
    }
});
```

### 3. **Batch operations with SAS**:

```python
from azure.storage.blob import BlobServiceClient, generate_account_sas, ResourceTypes, AccountSasPermissions
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from datetime import datetime, timedelta

class BatchFileManager:
    def __init__(self, account_name, account_key):
        self.account_name = account_name
        self.account_key = account_key
        self.connection_string = f"DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={account_key};EndpointSuffix=core.windows.net"
        self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
    
    def generate_account_sas(self, hours=24):
        """Generate account-level SAS for batch operations"""
        
        expiry_time = datetime.utcnow() + timedelta(hours=hours)
        
        sas_token = generate_account_sas(
            account_name=self.account_name,
            account_key=self.account_key,
            resource_types=ResourceTypes(service=True, container=True, object=True),
            permission=AccountSasPermissions(read=True, write=True, delete=True, list=True),
            expiry=expiry_time
        )
        
        return sas_token
    
    def batch_upload_files(self, container_name, files_to_upload, max_workers=5):
        """Upload multiple files concurrently using SAS"""
        
        sas_token = self.generate_account_sas()
        base_url = f"https://{self.account_name}.blob.core.windows.net"
        
        def upload_single_file(file_info):
            local_path, blob_name = file_info
            
            try:
                # Construct SAS URL
                url = f"{base_url}/{container_name}/{blob_name}?{sas_token}"
                
                # Upload file
                with open(local_path, 'rb') as file_data:
                    response = requests.put(
                        url,
                        data=file_data,
                        headers={'x-ms-blob-type': 'BlockBlob'}
                    )
                
                if response.status_code in [200, 201]:
                    return {"success": True, "blob_name": blob_name}
                else:
                    return {"success": False, "blob_name": blob_name, "error": response.text}
                    
            except Exception as e:
                return {"success": False, "blob_name": blob_name, "error": str(e)}
        
        # Execute uploads in parallel
        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_file = {
                executor.submit(upload_single_file, file_info): file_info 
                for file_info in files_to_upload
            }
            
            for future in as_completed(future_to_file):
                result = future.result()
                results.append(result)
                
                if result["success"]:
                    print(f"✅ Uploaded: {result['blob_name']}")
                else:
                    print(f"❌ Failed: {result['blob_name']} - {result['error']}")
        
        return results
    
    def batch_download_files(self, container_name, blobs_to_download, download_dir, max_workers=5):
        """Download multiple files concurrently using SAS"""
        
        sas_token = self.generate_account_sas()
        base_url = f"https://{self.account_name}.blob.core.windows.net"
        
        def download_single_file(blob_name):
            try:
                # Construct SAS URL
                url = f"{base_url}/{container_name}/{blob_name}?{sas_token}"
                
                # Download file
                response = requests.get(url)
                
                if response.status_code == 200:
                    # Save to local file
                    local_path = f"{download_dir}/{blob_name}"
                    with open(local_path, 'wb') as local_file:
                        local_file.write(response.content)
                    
                    return {"success": True, "blob_name": blob_name, "local_path": local_path}
                else:
                    return {"success": False, "blob_name": blob_name, "error": response.text}
                    
            except Exception as e:
                return {"success": False, "blob_name": blob_name, "error": str(e)}
        
        # Execute downloads in parallel
        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_blob = {
                executor.submit(download_single_file, blob_name): blob_name 
                for blob_name in blobs_to_download
            }
            
            for future in as_completed(future_to_blob):
                result = future.result()
                results.append(result)
                
                if result["success"]:
                    print(f"✅ Downloaded: {result['blob_name']} -> {result['local_path']}")
                else:
                    print(f"❌ Failed: {result['blob_name']} - {result['error']}")
        
        return results

# Example usage
file_manager = BatchFileManager("mystorageaccount", "your_account_key")

# Batch upload
files_to_upload = [
    ("./local/file1.txt", "uploads/file1.txt"),
    ("./local/file2.pdf", "uploads/file2.pdf"),
    ("./local/file3.jpg", "uploads/file3.jpg")
]

upload_results = file_manager.batch_upload_files("documents", files_to_upload)

# Batch download  
blobs_to_download = ["uploads/file1.txt", "uploads/file2.pdf", "uploads/file3.jpg"]
download_results = file_manager.batch_download_files("documents", blobs_to_download, "./downloads")
```

## Security best practices

### 1. **SAS URL security**:

```python
import ipaddress
from datetime import datetime, timedelta

class SecureSasGenerator:
    def __init__(self, account_name, account_key):
        self.account_name = account_name
        self.account_key = account_key
    
    def generate_secure_sas(self, container_name, blob_name, 
                           client_ip=None, hours=1, permissions="r"):
        """Generate SAS with security constraints"""
        
        from azure.storage.blob import generate_blob_sas, BlobSasPermissions
        
        # Minimal expiry time
        expiry_time = datetime.utcnow() + timedelta(hours=min(hours, 24))
        
        # Convert permissions string to enum
        perm_mapping = {
            'r': BlobSasPermissions(read=True),
            'w': BlobSasPermissions(write=True),
            'rw': BlobSasPermissions(read=True, write=True),
            'd': BlobSasPermissions(delete=True)
        }
        
        permissions_obj = perm_mapping.get(permissions, BlobSasPermissions(read=True))
        
        # Generate SAS with constraints
        sas_token = generate_blob_sas(
            account_name=self.account_name,
            container_name=container_name,
            blob_name=blob_name,
            account_key=self.account_key,
            permission=permissions_obj,
            expiry=expiry_time,
            start=datetime.utcnow() - timedelta(minutes=5),  # 5 min buffer for clock skew
            protocol="https",  # HTTPS only
            ip=client_ip  # IP restriction if provided
        )
        
        return {
            "sas_token": sas_token,
            "full_url": f"https://{self.account_name}.blob.core.windows.net/{container_name}/{blob_name}?{sas_token}",
            "expires_at": expiry_time,
            "permissions": permissions,
            "client_ip": client_ip
        }
    
    def validate_sas_request(self, user_ip, allowed_ips=None):
        """Validate SAS request based on IP"""
        
        if not allowed_ips:
            return True
        
        user_ip_obj = ipaddress.ip_address(user_ip)
        
        for allowed_ip in allowed_ips:
            if '/' in allowed_ip:  # CIDR notation
                if user_ip_obj in ipaddress.ip_network(allowed_ip):
                    return True
            else:  # Single IP
                if user_ip_obj == ipaddress.ip_address(allowed_ip):
                    return True
        
        return False
    
    def audit_sas_usage(self, sas_info, user_ip, user_agent=None):
        """Log SAS usage for audit"""
        
        import logging
        
        logger = logging.getLogger("sas_audit")
        logger.info(f"SAS_ACCESS - IP: {user_ip} "
                   f"URL: {sas_info['full_url'][:50]}... "
                   f"Permissions: {sas_info['permissions']} "
                   f"UserAgent: {user_agent}")

# Example usage with Flask
from flask import Flask, request, jsonify
import ipaddress

app = Flask(__name__)
secure_sas = SecureSasGenerator("mystorageaccount", "your_account_key")

@app.route('/secure-download/<path:blob_path>')
def secure_download(blob_path):
    """Generate secure SAS URL for download"""
    
    user_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ['REMOTE_ADDR'])
    user_agent = request.headers.get('User-Agent', '')
    
    # Define allowed IP ranges (example)
    allowed_ips = ["192.168.1.0/24", "10.0.0.0/8"]
    
    # Validate IP
    if not secure_sas.validate_sas_request(user_ip, allowed_ips):
        return jsonify({"error": "Access denied from this IP"}), 403
    
    try:
        # Generate secure SAS
        container_name, blob_name = blob_path.split('/', 1)
        
        sas_info = secure_sas.generate_secure_sas(
            container_name=container_name,
            blob_name=blob_name,
            client_ip=user_ip,
            hours=1,
            permissions="r"
        )
        
        # Audit the access
        secure_sas.audit_sas_usage(sas_info, user_ip, user_agent)
        
        return jsonify({
            "download_url": sas_info["full_url"],
            "expires_at": sas_info["expires_at"].isoformat(),
            "valid_for_ip": user_ip
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

### 2. **SAS rotation and management**:

```python
from datetime import datetime, timedelta
import hashlib
import json

class SasTokenManager:
    def __init__(self, account_name, account_key):
        self.account_name = account_name
        self.account_key = account_key
        self.active_tokens = {}  # In production, use Redis or database
    
    def generate_managed_sas(self, resource_path, permissions="r", hours=24, user_id=None):
        """Generate SAS with tracking and rotation capability"""
        
        from azure.storage.blob import generate_blob_sas, BlobSasPermissions
        
        # Create unique token ID
        token_data = f"{resource_path}:{permissions}:{user_id}:{datetime.utcnow()}"
        token_id = hashlib.md5(token_data.encode()).hexdigest()
        
        # Parse resource path
        parts = resource_path.split('/')
        container_name = parts[0]
        blob_name = '/'.join(parts[1:]) if len(parts) > 1 else ""
        
        # Generate SAS
        expiry_time = datetime.utcnow() + timedelta(hours=hours)
        
        perm_mapping = {
            'r': BlobSasPermissions(read=True),
            'w': BlobSasPermissions(write=True),
            'rw': BlobSasPermissions(read=True, write=True)
        }
        permissions_obj = perm_mapping.get(permissions, BlobSasPermissions(read=True))
        
        sas_token = generate_blob_sas(
            account_name=self.account_name,
            container_name=container_name,
            blob_name=blob_name,
            account_key=self.account_key,
            permission=permissions_obj,
            expiry=expiry_time,
            protocol="https"
        )
        
        # Store token metadata
        self.active_tokens[token_id] = {
            "resource_path": resource_path,
            "permissions": permissions,
            "user_id": user_id,
            "created_at": datetime.utcnow(),
            "expires_at": expiry_time,
            "sas_token": sas_token,
            "revoked": False,
            "usage_count": 0
        }
        
        full_url = f"https://{self.account_name}.blob.core.windows.net/{resource_path}?{sas_token}"
        
        return {
            "token_id": token_id,
            "url": full_url,
            "expires_at": expiry_time
        }
    
    def revoke_token(self, token_id):
        """Revoke a SAS token"""
        if token_id in self.active_tokens:
            self.active_tokens[token_id]["revoked"] = True
            return True
        return False
    
    def is_token_valid(self, token_id):
        """Check if token is still valid"""
        if token_id not in self.active_tokens:
            return False
        
        token_info = self.active_tokens[token_id]
        
        if token_info["revoked"]:
            return False
        
        if datetime.utcnow() > token_info["expires_at"]:
            return False
        
        return True
    
    def track_usage(self, token_id):
        """Track token usage"""
        if token_id in self.active_tokens:
            self.active_tokens[token_id]["usage_count"] += 1
    
    def get_token_stats(self):
        """Get statistics about active tokens"""
        total_tokens = len(self.active_tokens)
        active_tokens = sum(1 for t in self.active_tokens.values() 
                           if not t["revoked"] and datetime.utcnow() <= t["expires_at"])
        revoked_tokens = sum(1 for t in self.active_tokens.values() if t["revoked"])
        expired_tokens = sum(1 for t in self.active_tokens.values() 
                           if not t["revoked"] and datetime.utcnow() > t["expires_at"])
        
        return {
            "total_tokens": total_tokens,
            "active_tokens": active_tokens,
            "revoked_tokens": revoked_tokens,
            "expired_tokens": expired_tokens
        }
    
    def cleanup_expired_tokens(self):
        """Remove expired token metadata"""
        now = datetime.utcnow()
        expired_tokens = [
            token_id for token_id, token_info in self.active_tokens.items()
            if now > token_info["expires_at"] + timedelta(hours=24)  # Grace period
        ]
        
        for token_id in expired_tokens:
            del self.active_tokens[token_id]
        
        return len(expired_tokens)

# Example usage
token_manager = SasTokenManager("mystorageaccount", "your_account_key")

# Generate managed SAS
token_info = token_manager.generate_managed_sas(
    resource_path="documents/reports/monthly_report.pdf",
    permissions="r",
    hours=24,
    user_id="user123"
)

print(f"Generated token: {token_info['token_id']}")
print(f"URL: {token_info['url']}")

# Track usage
token_manager.track_usage(token_info['token_id'])

# Check validity
is_valid = token_manager.is_token_valid(token_info['token_id'])
print(f"Token valid: {is_valid}")

# Get stats
stats = token_manager.get_token_stats()
print(f"Token stats: {stats}")

# Revoke if needed
# token_manager.revoke_token(token_info['token_id'])
```

## Monitoring i troubleshooting

### 1. **SAS monitoring dashboard**:

```python
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
import seaborn as sns

class SasMonitoringDashboard:
    def __init__(self, token_manager):
        self.token_manager = token_manager
    
    def generate_usage_report(self):
        """Generate comprehensive usage report"""
        
        if not self.token_manager.active_tokens:
            return "No tokens to analyze"
        
        # Convert tokens to DataFrame for analysis
        token_data = []
        for token_id, token_info in self.token_manager.active_tokens.items():
            token_data.append({
                "token_id": token_id,
                "resource_path": token_info["resource_path"],
                "permissions": token_info["permissions"],
                "user_id": token_info["user_id"],
                "created_at": token_info["created_at"],
                "expires_at": token_info["expires_at"],
                "revoked": token_info["revoked"],
                "usage_count": token_info["usage_count"],
                "days_to_expiry": (token_info["expires_at"] - datetime.utcnow()).days
            })
        
        df = pd.DataFrame(token_data)
        
        # Generate report
        report = {
            "summary": {
                "total_tokens": len(df),
                "active_tokens": len(df[~df["revoked"] & (df["days_to_expiry"] > 0)]),
                "most_used_resource": df.loc[df["usage_count"].idxmax(), "resource_path"],
                "most_active_user": df.groupby("user_id")["usage_count"].sum().idxmax()
            },
            "by_permissions": df.groupby("permissions").size().to_dict(),
            "by_user": df.groupby("user_id")["usage_count"].sum().to_dict(),
            "expiring_soon": df[df["days_to_expiry"].between(0, 1)]["resource_path"].tolist()
        }
        
        return report
    
    def plot_usage_analytics(self):
        """Create visualization of SAS usage"""
        
        token_data = []
        for token_info in self.token_manager.active_tokens.values():
            token_data.append({
                "permissions": token_info["permissions"],
                "usage_count": token_info["usage_count"],
                "user_id": token_info["user_id"],
                "days_active": (datetime.utcnow() - token_info["created_at"]).days,
                "status": "revoked" if token_info["revoked"] else "active"
            })
        
        if not token_data:
            print("No data to visualize")
            return
        
        df = pd.DataFrame(token_data)
        
        # Create subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Usage by permissions
        df.groupby("permissions")["usage_count"].sum().plot(kind="bar", ax=axes[0,0])
        axes[0,0].set_title("Usage by Permissions")
        axes[0,0].set_ylabel("Total Usage Count")
        
        # Usage by user
        top_users = df.groupby("user_id")["usage_count"].sum().nlargest(10)
        top_users.plot(kind="bar", ax=axes[0,1])
        axes[0,1].set_title("Top 10 Users by Usage")
        axes[0,1].set_ylabel("Total Usage Count")
        
        # Status distribution
        df["status"].value_counts().plot(kind="pie", ax=axes[1,0], autopct='%1.1f%%')
        axes[1,0].set_title("Token Status Distribution")
        
        # Usage vs Days Active
        axes[1,1].scatter(df["days_active"], df["usage_count"])
        axes[1,1].set_xlabel("Days Active")
        axes[1,1].set_ylabel("Usage Count")
        axes[1,1].set_title("Usage vs Token Age")
        
        plt.tight_layout()
        plt.savefig("sas_usage_analytics.png")
        plt.show()
    
    def security_audit_report(self):
        """Generate security-focused audit report"""
        
        issues = []
        recommendations = []
        
        for token_id, token_info in self.token_manager.active_tokens.items():
            # Check for long-lived tokens
            token_age = datetime.utcnow() - token_info["created_at"]
            if token_age.days > 30:
                issues.append(f"Long-lived token {token_id[:8]} (age: {token_age.days} days)")
            
            # Check for unused tokens
            if token_info["usage_count"] == 0 and token_age.days > 7:
                issues.append(f"Unused token {token_id[:8]} (created {token_age.days} days ago)")
            
            # Check for write permissions
            if 'w' in token_info["permissions"]:
                issues.append(f"Write permissions granted to token {token_id[:8]}")
        
        # Generate recommendations
        if len(self.token_manager.active_tokens) > 100:
            recommendations.append("Consider implementing token cleanup policy")
        
        write_tokens = sum(1 for t in self.token_manager.active_tokens.values() 
                          if 'w' in t["permissions"])
        if write_tokens > 10:
            recommendations.append("Review write permission grants - consider more restrictive permissions")
        
        return {
            "security_issues": issues,
            "recommendations": recommendations,
            "audit_timestamp": datetime.utcnow().isoformat()
        }

# Example usage
dashboard = SasMonitoringDashboard(token_manager)

# Generate reports
usage_report = dashboard.generate_usage_report()
print("Usage Report:", usage_report)

security_report = dashboard.security_audit_report()
print("Security Report:", security_report)

# Generate visualizations (if you have matplotlib)
# dashboard.plot_usage_analytics()
```

## Podsumowanie

### ✅ Używaj SAS URL gdy:
- Temporary access potrzebny
- Third-party integrations
- Client-side file uploads
- Granular permissions required
- No backend authentication możliwe

### 🔧 Best Practices:
- ✅ **Minimal permissions** - tylko to co potrzebne
- ✅ **Short expiry times** - maksymalnie 24h dla write
- ✅ **HTTPS only** - zawsze enforce SSL
- ✅ **IP restrictions** - gdy możliwe
- ✅ **Monitor usage** - audit logs i metrics
- ✅ **Token rotation** - regular refresh
- ✅ **User Delegation SAS** - preferuj nad Account SAS

### ❌ Unikaj:
- Długoterminowych SAS tokens
- Broad permissions (rwdl all)
- Hardcoding SAS w aplikacjach
- Sharing SAS URLs w plain text
- Brak monitoring użycia

**SAS URL = Secure, temporary, granular access to Azure Storage** 🔐