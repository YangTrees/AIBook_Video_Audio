$ErrorActionPreference = 'Stop'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

function Read-DotEnv([string]$Path) {
    $values = @{}
    Get-Content -LiteralPath $Path -Encoding UTF8 | ForEach-Object {
        if ($_ -match '^([^#=]+)=(.*)$') {
            $values[$matches[1].Trim()] = $matches[2].Trim()
        }
    }
    return $values
}

function Convert-HexToBytes([string]$Hex) {
    $bytes = New-Object byte[] ($Hex.Length / 2)
    for ($i = 0; $i -lt $bytes.Length; $i++) {
        $bytes[$i] = [Convert]::ToByte($Hex.Substring($i * 2, 2), 16)
    }
    return $bytes
}

function ConvertFrom-UnicodeEscapes([string]$Text) {
    return [regex]::Replace($Text, '\\u([0-9a-fA-F]{4})', {
        param($match)
        [char][Convert]::ToInt32($match.Groups[1].Value, 16)
    })
}

$root = $PSScriptRoot
$config = Read-DotEnv (Join-Path $root '.env')
$baseUrl = $config.MINIMAX_BASE_URL.TrimEnd('/')
$headers = @{ Authorization = "Bearer $($config.MINIMAX_API_KEY)" }
$reference = Join-Path $root 'reference_audio\diandian_edge_clone_reference.mp3'
$voiceId = "AIBook_diandian_edge_$(Get-Date -Format 'yyyyMMddHHmmss')"

$uploadRaw = & curl.exe -sS -X POST "$baseUrl/v1/files/upload" `
    -H "Authorization: Bearer $($config.MINIMAX_API_KEY)" `
    -F 'purpose=voice_clone' -F "file=@$reference;type=audio/mpeg"
if ($LASTEXITCODE -ne 0) { throw 'Reference upload failed.' }
$upload = $uploadRaw | ConvertFrom-Json
if ($upload.base_resp.status_code -ne 0) {
    throw "Reference upload failed: $($upload.base_resp.status_msg)"
}

$clonePayload = @{
    file_id = [int64]$upload.file.file_id
    voice_id = $voiceId
    model = $config.MINIMAX_TTS_MODEL
    need_noise_reduction = $false
    need_volume_normalization = $true
    aigc_watermark = $false
}
$cloneJson = $clonePayload | ConvertTo-Json -Depth 5 -Compress
$clone = Invoke-RestMethod -Method Post -Uri "$baseUrl/v1/voice_clone" -Headers $headers `
    -ContentType 'application/json; charset=utf-8' `
    -Body ([Text.Encoding]::UTF8.GetBytes($cloneJson)) -TimeoutSec 90
if ($clone.base_resp.status_code -ne 0) {
    throw "Voice clone failed: $($clone.base_resp.status_msg)"
}

$sampleText = ConvertFrom-UnicodeEscapes '\u6ef4\u6ef4\uff0c\u626b\u63cf\u5b8c\u6210\uff01\u524d\u65b9\u53d1\u73b0\u4e00\u9897\u4f1a\u5531\u6b4c\u7684\u5c0f\u661f\u661f\u3002'
$ttsPayload = @{
    model = $config.MINIMAX_TTS_MODEL
    text = $sampleText
    stream = $false
    voice_setting = @{
        voice_id = $voiceId
        speed = 0.98
        vol = 1.0
        pitch = 1
        emotion = 'happy'
    }
    audio_setting = @{ sample_rate = 32000; bitrate = 128000; format = 'mp3'; channel = 1 }
    subtitle_enable = $false
    aigc_watermark = $false
}
$ttsJson = $ttsPayload | ConvertTo-Json -Depth 6 -Compress
$tts = Invoke-RestMethod -Method Post -Uri "$baseUrl/v1/t2a_v2" -Headers $headers `
    -ContentType 'application/json; charset=utf-8' `
    -Body ([Text.Encoding]::UTF8.GetBytes($ttsJson)) -TimeoutSec 90
if ($tts.base_resp.status_code -ne 0 -or $tts.data.status -ne 2) {
    throw "TTS failed: $($tts.base_resp.status_msg)"
}

$outputDir = Join-Path $root 'audio_output\cloned_samples'
New-Item -ItemType Directory -Force -Path $outputDir | Out-Null
$outputPath = Join-Path $outputDir 'diandian_edge_cloned.mp3'
[IO.File]::WriteAllBytes($outputPath, (Convert-HexToBytes ([string]$tts.data.audio)))

$result = [ordered]@{
    voice_id = $voiceId
    edge_voice = 'zh-CN-XiaoyiNeural'
    reference = $reference
    output = $outputPath
    minimax = @{ speed = 0.98; vol = 1.0; pitch = 1; emotion = 'happy' }
}
$result | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $root 'diandian_edge_clone.json') -Encoding UTF8
Write-Host "voice_id: $voiceId"
Write-Host "output: $outputPath"

