# Script de PowerShell para probar el webhook con imagen
# Usa el archivo JSON para evitar problemas de codificación

$webhookUrl = "http://localhost:8000/webhook"
$jsonFile = "test_image_payload.json"

Write-Host "🖼️ Probando webhook con mensaje de imagen..." -ForegroundColor Green

# Verificar que el archivo JSON existe
if (-not (Test-Path $jsonFile)) {
    Write-Host "❌ Error: No se encontró el archivo $jsonFile" -ForegroundColor Red
    exit 1
}

# Leer el contenido del archivo JSON
$jsonContent = Get-Content $jsonFile -Raw

Write-Host "📄 Contenido del JSON cargado correctamente" -ForegroundColor Yellow

try {
    # Enviar la solicitud POST
    $headers = @{
        "Content-Type" = "application/json"
    }
    
    $response = Invoke-RestMethod -Uri $webhookUrl -Method POST -Body $jsonContent -Headers $headers
    
    Write-Host "✅ Respuesta exitosa:" -ForegroundColor Green
    Write-Host ($response | ConvertTo-Json -Depth 10)
    
} catch {
    Write-Host "❌ Error en la solicitud:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $statusCode = $_.Exception.Response.StatusCode
        $statusDescription = $_.Exception.Response.StatusDescription
        Write-Host "Status Code: $statusCode - $statusDescription" -ForegroundColor Red
    }
}

Write-Host "`n🏁 Prueba completada" -ForegroundColor Cyan 