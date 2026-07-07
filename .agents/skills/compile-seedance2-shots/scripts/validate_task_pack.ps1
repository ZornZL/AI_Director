param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$InputPath
)

$ErrorActionPreference = 'Stop'

$rootRequired = @(
    'project_id', 'model_profile', 'source_lock', 'production_assumptions',
    'bibles', 'assets', 'asset_generation_tasks', 'shots'
)

$shotRequired = @(
    'shot_id', 'source_ids', 'purpose', 'duration_seconds', 'aspect_ratio',
    'input_mode', 'references', 'keyframes', 'first_frame', 'camera', 'blocking',
    'performance', 'audio', 'voice_continuity', 'timeline', 'edit_handles', 'lighting_environment', 'end_frame',
    'continuity_from', 'negative_constraints', 'prompt', 'acceptance', 'fallback'
)

$validModes = @('text', 'image', 'audio', 'video', 'mixed')
function Decode-Unicode {
    param([string]$Value)
    return [regex]::Unescape($Value)
}

$forbiddenShorthand = @(
    (Decode-Unicode '\u540c\u4e0a'),
    (Decode-Unicode '\u6cbf\u7528\u4e0a\u4e00\u955c'),
    (Decode-Unicode '\u6cbf\u7528\u524d\u6587'),
    (Decode-Unicode '\u5176\u4ed6\u4e0d\u53d8'),
    (Decode-Unicode '\u5176\u4f59\u4e0d\u53d8'),
    (Decode-Unicode '\u7565')
)
$errors = [System.Collections.Generic.List[string]]::new()
$warnings = [System.Collections.Generic.List[string]]::new()

function Has-Property {
    param($Object, [string]$Name)
    return $null -ne $Object -and $null -ne $Object.PSObject.Properties[$Name]
}

function Is-NonEmpty {
    param($Value)
    if ($null -eq $Value) { return $false }
    if ($Value -is [string]) { return -not [string]::IsNullOrWhiteSpace($Value) }
    if ($Value -is [System.Collections.ICollection]) { return $Value.Count -gt 0 }
    return $true
}

try {
    $resolvedPath = (Resolve-Path -LiteralPath $InputPath).Path
    $data = Get-Content -Raw -Encoding UTF8 -LiteralPath $resolvedPath | ConvertFrom-Json
} catch {
    Write-Output (@{ shots = 0; errors = @("cannot read JSON: $($_.Exception.Message)"); warnings = @() } | ConvertTo-Json -Depth 6)
    exit 1
}

foreach ($field in $rootRequired) {
    if (-not (Has-Property $data $field)) {
        $errors.Add("missing project field: $field")
    }
}

if (Has-Property $data 'tasks' -or Has-Property $data 'clips') {
    $errors.Add("use only the top-level 'shots' array; tasks/clips are not allowed")
}

if (-not (Has-Property $data 'shots') -or $null -eq $data.shots -or @($data.shots).Count -eq 0) {
    $errors.Add('shots must be a non-empty array')
}

$limits = @{ image = 9; audio = 3; video = 3 }
if (Has-Property $data 'model_profile' -and Has-Property $data.model_profile 'reference_limits') {
    foreach ($kind in @('image', 'audio', 'video')) {
        if (Has-Property $data.model_profile.reference_limits $kind) {
            $limits[$kind] = [int]$data.model_profile.reference_limits.$kind
        }
    }
} else {
    $warnings.Add('model_profile.reference_limits is missing; using baseline limits image=9, audio=3, video=3')
}

$seenIds = @{}
$shotIndex = 0
foreach ($shot in @($data.shots)) {
    $shotIndex++
    $label = "shot $shotIndex"

    foreach ($field in $shotRequired) {
        if (-not (Has-Property $shot $field)) {
            $errors.Add("${label}: missing $field")
        } elseif ($field -notin @('references', 'continuity_from') -and -not (Is-NonEmpty $shot.$field)) {
            $errors.Add("${label}: empty $field")
        }
    }

    if (Has-Property $shot 'shot_id') {
        $shotId = [string]$shot.shot_id
        if ($seenIds.ContainsKey($shotId)) {
            $errors.Add("${label}: duplicate shot_id $shotId")
        } else {
            $seenIds[$shotId] = $true
        }
    }

    if (Has-Property $shot 'duration_seconds') {
        $duration = $shot.duration_seconds
        if ($duration -isnot [int] -and $duration -isnot [long] -and $duration -isnot [double] -and $duration -isnot [decimal]) {
            $errors.Add("${label}: duration_seconds must be numeric")
        } elseif ($duration -lt 4 -or $duration -gt 15) {
            $errors.Add("${label}: duration_seconds must be between 4 and 15")
        }
    }

    if (Has-Property $shot 'input_mode') {
        $inputMode = [string]$shot.input_mode
        if ($inputMode -notin $validModes) {
            $errors.Add("${label}: invalid input_mode")
        }
    }

    if (Has-Property $shot 'references') {
        $counts = @{ image = 0; audio = 0; video = 0 }
        foreach ($reference in @($shot.references)) {
            if (-not (Has-Property $reference 'asset_id') -or -not (Is-NonEmpty $reference.asset_id) -or
                -not (Has-Property $reference 'type') -or -not (Is-NonEmpty $reference.type) -or
                -not (Has-Property $reference 'purpose') -or -not (Is-NonEmpty $reference.purpose)) {
                $errors.Add("${label}: each reference requires asset_id, type and purpose")
                continue
            }
            if ($counts.ContainsKey([string]$reference.type)) {
                $counts[[string]$reference.type]++
            }
        }
        foreach ($kind in @('image', 'audio', 'video')) {
            if ($counts[$kind] -gt $limits[$kind]) {
                $errors.Add("${label}: $kind references exceed project limit $($limits[$kind])")
            }
        }
    }

    if (Has-Property $shot 'audio' -and $null -ne $shot.audio -and Has-Property $shot.audio 'dialogue' -and (Is-NonEmpty $shot.audio.dialogue)) {
        foreach ($field in @('speaker', 'addressee')) {
            if (-not (Has-Property $shot.audio $field) -or -not (Is-NonEmpty $shot.audio.$field)) {
                $errors.Add("${label}: dialogue requires audio.$field")
            }
        }
        foreach ($field in @('lip_sync', 'non_speakers_closed_mouth')) {
            if (-not (Has-Property $shot.audio $field) -or $shot.audio.$field -ne $true) {
                $errors.Add("${label}: dialogue requires audio.$field=true")
            }
        }
    }

    if (Has-Property $shot 'keyframes') {
        if (-not (Has-Property $shot.keyframes 'first') -or
            -not (Has-Property $shot.keyframes.first 'prompt') -or -not (Is-NonEmpty $shot.keyframes.first.prompt) -or
            -not (Has-Property $shot.keyframes.first 'acceptance') -or -not (Is-NonEmpty $shot.keyframes.first.acceptance)) {
            $errors.Add("${label}: keyframes.first requires prompt and acceptance")
        }
    }

    if (Has-Property $shot 'timeline') {
        $timelineItems = @($shot.timeline)
        if ($timelineItems.Count -eq 0) {
            $errors.Add("${label}: timeline must be a non-empty array")
        } elseif ((Has-Property $shot 'duration_seconds') -and $shot.duration_seconds -le 10 -and $timelineItems.Count -gt 6) {
            $warnings.Add("${label}: probable action overload")
        }
    }

    if (Has-Property $shot 'edit_handles') {
        foreach ($field in @('head_seconds', 'tail_seconds')) {
            if (-not (Has-Property $shot.edit_handles $field)) {
                $errors.Add("${label}: edit_handles.$field is required")
            } else {
                $value = $shot.edit_handles.$field
                if ($value -isnot [int] -and $value -isnot [long] -and $value -isnot [double] -and $value -isnot [decimal]) {
                    $errors.Add("${label}: edit_handles.$field must be numeric")
                }
            }
        }
        foreach ($field in @('head_state', 'tail_state', 'cut_note')) {
            if (-not (Has-Property $shot.edit_handles $field) -or -not (Is-NonEmpty $shot.edit_handles.$field)) {
                $errors.Add("${label}: edit_handles.$field is required")
            }
        }
        if ((Has-Property $shot.edit_handles 'tail_seconds') -and $shot.edit_handles.tail_seconds -lt 0.2) {
            $warnings.Add("${label}: tail edit handle is shorter than 0.2s")
        }
    }

    if (Has-Property $shot 'prompt') {
        $prompt = [string]$shot.prompt
        $requiredMarkers = @(
            (Decode-Unicode '\u3010\u4efb\u52a1\u4e0e\u65f6\u957f\u3011'),
            (Decode-Unicode '\u3010\u9996\u5e27\u3011'),
            (Decode-Unicode '\u3010\u6444\u5f71\u3011'),
            (Decode-Unicode '\u3010\u9010\u79d2\u65f6\u95f4\u8f74\u3011'),
            (Decode-Unicode '\u3010\u526a\u8f91\u624b\u67c4\u3011'),
            (Decode-Unicode '\u3010\u5c3e\u5e27\u3011'),
            (Decode-Unicode '\u3010\u7981\u6b62\u3011')
        )
        foreach ($marker in $requiredMarkers) {
            if (-not $prompt.Contains($marker)) {
                $warnings.Add("${label}: prompt missing marker $marker")
            }
        }
        foreach ($phrase in $forbiddenShorthand) {
            if ($prompt.Contains($phrase)) {
                $errors.Add("${label}: prompt contains non-self-contained shorthand '$phrase'")
            }
        }
    }
}

$result = @{
    shots = if (Has-Property $data 'shots') { @($data.shots).Count } else { 0 }
    errors = @($errors)
    warnings = @($warnings)
}

Write-Output ($result | ConvertTo-Json -Depth 8)
if ($errors.Count -gt 0) { exit 1 }
exit 0
