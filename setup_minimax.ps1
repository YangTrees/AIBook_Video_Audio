$ErrorActionPreference = 'Stop'

function ConvertFrom-SecureValue {
    param([Security.SecureString]$SecureValue)

    $ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($SecureValue)
    try {
        return [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
    }
    finally {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)
    }
}

$apiKey = ConvertFrom-SecureValue (Read-Host 'MinMax API Key (hidden)' -AsSecureString)
if ([string]::IsNullOrWhiteSpace($apiKey)) {
    throw 'API Key cannot be empty.'
}

$groupId = Read-Host 'MinMax Group ID (optional; press Enter to skip)'
$baseUrl = Read-Host 'Base URL [https://api.minimaxi.com]'
if ([string]::IsNullOrWhiteSpace($baseUrl)) {
    $baseUrl = 'https://api.minimaxi.com'
}

$model = Read-Host 'TTS model [speech-02-hd]'
if ([string]::IsNullOrWhiteSpace($model)) {
    $model = 'speech-02-hd'
}

$lines = @(
    "MINIMAX_API_KEY=$apiKey"
    "MINIMAX_GROUP_ID=$groupId"
    "MINIMAX_BASE_URL=$baseUrl"
    "MINIMAX_TTS_MODEL=$model"
)

[IO.File]::WriteAllLines((Join-Path $PSScriptRoot '.env'), $lines, [Text.UTF8Encoding]::new($false))
Write-Host 'Saved MinMax configuration to .env (excluded by .gitignore).'

