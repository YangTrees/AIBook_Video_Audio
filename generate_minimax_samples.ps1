$ErrorActionPreference = 'Stop'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

function Read-DotEnv {
    param([string]$Path)
    $values = @{}
    Get-Content -LiteralPath $Path -Encoding UTF8 | ForEach-Object {
        if ($_ -match '^([^#=]+)=(.*)$') {
            $values[$matches[1].Trim()] = $matches[2].Trim()
        }
    }
    return $values
}

function Convert-HexToBytes {
    param([string]$Hex)
    $bytes = New-Object byte[] ($Hex.Length / 2)
    for ($i = 0; $i -lt $bytes.Length; $i++) {
        $bytes[$i] = [Convert]::ToByte($Hex.Substring($i * 2, 2), 16)
    }
    return $bytes
}

$root = $PSScriptRoot
$envValues = Read-DotEnv (Join-Path $root '.env')
$roles = Get-Content -LiteralPath (Join-Path $root 'voices.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$outputDir = Join-Path $root 'audio_output\role_samples'
New-Item -ItemType Directory -Force -Path $outputDir | Out-Null

$headers = @{ Authorization = "Bearer $($envValues.MINIMAX_API_KEY)" }
$uri = "$($envValues.MINIMAX_BASE_URL.TrimEnd('/'))/v1/t2a_v2"

foreach ($roleName in @('tuantuan', 'diandian', 'narrator')) {
    $role = $roles.$roleName
    $payload = @{
        model = $envValues.MINIMAX_TTS_MODEL
        text = $role.sample_text
        stream = $false
        voice_setting = @{
            voice_id = $role.minimax.voice_id
            speed = $role.minimax.speed
            vol = $role.minimax.vol
            pitch = $role.minimax.pitch
            emotion = $role.minimax.emotion
        }
        audio_setting = @{
            sample_rate = 32000
            bitrate = 128000
            format = 'mp3'
            channel = 1
        }
        subtitle_enable = $false
        aigc_watermark = $false
    }

    $json = $payload | ConvertTo-Json -Depth 6 -Compress
    $body = [Text.Encoding]::UTF8.GetBytes($json)
    $response = Invoke-RestMethod -Method Post -Uri $uri -Headers $headers `
        -ContentType 'application/json; charset=utf-8' -Body $body -TimeoutSec 60

    if ($response.base_resp.status_code -ne 0 -or $response.data.status -ne 2) {
        throw "$($role.display_name) generation failed: $($response.base_resp.status_msg)"
    }

    $audio = Convert-HexToBytes ([string]$response.data.audio)
    $outputPath = Join-Path $outputDir "$roleName.mp3"
    [IO.File]::WriteAllBytes($outputPath, $audio)
    Write-Host "$roleName`: $outputPath"
}
