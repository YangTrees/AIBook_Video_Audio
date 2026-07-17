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

function ConvertFrom-UnicodeEscapes {
    param([string]$Text)
    return [regex]::Replace($Text, '\\u([0-9a-fA-F]{4})', {
        param($match)
        [char][Convert]::ToInt32($match.Groups[1].Value, 16)
    })
}

$root = $PSScriptRoot
$config = Read-DotEnv (Join-Path $root '.env')
$baseUrl = $config.MINIMAX_BASE_URL.TrimEnd('/')
$headers = @{ Authorization = "Bearer $($config.MINIMAX_API_KEY)" }
$stamp = Get-Date -Format 'yyyyMMddHHmmss'
$inputDir = Join-Path $root 'reference_audio'
$outputDir = Join-Path $root 'audio_output\cloned_samples'
New-Item -ItemType Directory -Force -Path $inputDir, $outputDir | Out-Null

$tuantuanSource = Join-Path $inputDir 'tuantuan_reference.mp3'
$diandianSource = Join-Path $inputDir 'diandian_reference.mp3'
$narratorSource = Join-Path $inputDir 'narrator_reference.mp3'

$roles = @(
    @{ key = 'tuantuan'; source = $tuantuanSource; text = '\u54c7\uff01\u70b9\u70b9\u5feb\u770b\uff0c\u90a3\u9897\u661f\u661f\u6b63\u5728\u5bf9\u6211\u4eec\u7728\u773c\u775b\u5462\uff01'; speed = 1.05; pitch = 1; emotion = 'happy' },
    @{ key = 'diandian'; source = $diandianSource; text = '\u6ef4\u6ef4\uff0c\u626b\u63cf\u5b8c\u6210\uff01\u524d\u65b9\u53d1\u73b0\u4e00\u9897\u4f1a\u5531\u6b4c\u7684\u5c0f\u661f\u661f\u3002'; speed = 0.98; pitch = 1; emotion = 'happy' },
    @{ key = 'narrator'; source = $narratorSource; text = '\u591c\u5e55\u8f7b\u8f7b\u843d\u4e0b\uff0c\u56e2\u56e2\u548c\u70b9\u70b9\u8e0f\u4e0a\u4e86\u4e00\u6bb5\u95ea\u95ea\u53d1\u5149\u7684\u65c5\u7a0b\u3002'; speed = 0.9; pitch = -1; emotion = 'calm' }
)

$manifest = [ordered]@{}
foreach ($role in $roles) {
    $mp3Path = Join-Path $inputDir "$($role.key)_reference.mp3"
    if ((Resolve-Path -LiteralPath $role.source).Path -ne (Resolve-Path -LiteralPath $mp3Path).Path) {
        Copy-Item -LiteralPath $role.source -Destination $mp3Path -Force
    }

    $uploadRaw = & curl.exe -sS -X POST "$baseUrl/v1/files/upload" `
        -H "Authorization: Bearer $($config.MINIMAX_API_KEY)" `
        -F 'purpose=voice_clone' -F "file=@$mp3Path;type=audio/mpeg"
    if ($LASTEXITCODE -ne 0) { throw "Upload failed for $($role.key)" }
    $upload = $uploadRaw | ConvertFrom-Json
    if ($upload.base_resp.status_code -ne 0) {
        throw "Upload failed for $($role.key): $($upload.base_resp.status_msg)"
    }

    $voiceId = "AIBook_$($role.key)_$stamp"
    $clonePayload = @{
        file_id = [int64]$upload.file.file_id
        voice_id = $voiceId
        model = $config.MINIMAX_TTS_MODEL
        need_noise_reduction = $true
        need_volume_normalization = $true
        aigc_watermark = $false
    }
    $cloneJson = $clonePayload | ConvertTo-Json -Depth 5 -Compress
    $clone = Invoke-RestMethod -Method Post -Uri "$baseUrl/v1/voice_clone" -Headers $headers `
        -ContentType 'application/json; charset=utf-8' -Body ([Text.Encoding]::UTF8.GetBytes($cloneJson)) -TimeoutSec 90
    if ($clone.base_resp.status_code -ne 0) {
        throw "Clone failed for $($role.key): $($clone.base_resp.status_msg)"
    }

    $ttsPayload = @{
        model = $config.MINIMAX_TTS_MODEL
        text = ConvertFrom-UnicodeEscapes $role.text
        stream = $false
        voice_setting = @{
            voice_id = $voiceId
            speed = $role.speed
            vol = 1.0
            pitch = $role.pitch
            emotion = $role.emotion
        }
        audio_setting = @{ sample_rate = 32000; bitrate = 128000; format = 'mp3'; channel = 1 }
        subtitle_enable = $false
        aigc_watermark = $false
    }
    $ttsJson = $ttsPayload | ConvertTo-Json -Depth 6 -Compress
    $tts = Invoke-RestMethod -Method Post -Uri "$baseUrl/v1/t2a_v2" -Headers $headers `
        -ContentType 'application/json; charset=utf-8' -Body ([Text.Encoding]::UTF8.GetBytes($ttsJson)) -TimeoutSec 90
    if ($tts.base_resp.status_code -ne 0 -or $tts.data.status -ne 2) {
        throw "TTS failed for $($role.key): $($tts.base_resp.status_msg)"
    }

    $outputPath = Join-Path $outputDir "$($role.key)_cloned.mp3"
    [IO.File]::WriteAllBytes($outputPath, (Convert-HexToBytes ([string]$tts.data.audio)))
    $manifest[$role.key] = @{ voice_id = $voiceId; source = $mp3Path; output = $outputPath }
    Write-Host "$($role.key): $voiceId"
}

$manifest | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $root 'cloned_voices.json') -Encoding UTF8
