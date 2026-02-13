# Agentic Honey-Pot: Simple Test Script
# Run multiple pre-loaded scam messages and see results

param(
    [string]$ApiUrl = "https://yash1th005-agentic-honey-pot.hf.space/api/message",
    [string]$ApiKey = "agentic_honey_pot_2026"
)

Write-Host "`n========== AGENTIC HONEY-POT TESTER ==========" -ForegroundColor Yellow
Write-Host "API: $ApiUrl`n" -ForegroundColor Cyan

# Test messages
$tests = @(
    "URGENT! Your SBI account has been compromised. Send Rs 5000 to verify@sbi immediately.",
    "Call our helpline at 9876543210 for assistance.",
    "Your Amazon OTP is 123456. Share it to verify.",
    "Won Rs 50,000! Pay Rs 500 to winner@paytm to claim prize.",
    "Tax notice: Pay Rs 12,000 to taxdept@okaxis or call 8899776655"
)

$sessionId = "test-$(Get-Date -Format 'HHmmss')"
$history = @()
$totalDetected = 0

foreach ($msg in $tests) {
    Write-Host "Scammer: " -ForegroundColor Red -NoNewline
    Write-Host $msg

    $body = @{
        sessionId = $sessionId
        message = @{
            sender = "scammer"
            text = $msg
            timestamp = [DateTimeOffset]::Now.ToUnixTimeMilliseconds()
        }
        conversationHistory = $history
    } | ConvertTo-Json -Depth 10

    try {
        $response = Invoke-RestMethod -Uri $ApiUrl -Method POST `
            -Headers @{"x-api-key"=$ApiKey} `
            -Body $body -ContentType "application/json"

        Write-Host "Honeypot: " -ForegroundColor Green -NoNewline
        Write-Host $response.reply

        if ($response.scamDetected) {
            Write-Host "[DETECTED]" -ForegroundColor Green
            $totalDetected++
        } else {
            Write-Host "[MISSED]" -ForegroundColor Red
        }

        # Show extracted intel
        $intel = $response.extractedIntelligence
        if ($intel.phoneNumbers.Count -gt 0) { 
            Write-Host "  Phones: $($intel.phoneNumbers -join ', ')" -ForegroundColor Cyan
        }
        if ($intel.upiIds.Count -gt 0) {
            Write-Host "  UPIs: $($intel.upiIds -join ', ')" -ForegroundColor Cyan
        }
        if ($intel.amounts.Count -gt 0) {
            Write-Host "  Amounts: $($intel.amounts -join ', ')" -ForegroundColor Cyan
        }

        $history += @{sender="scammer"; text=$msg}
        $history += @{sender="user"; text=$response.reply}

    } catch {
        Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    }

    Write-Host ""
    Start-Sleep -Milliseconds 500
}

Write-Host "========================================" -ForegroundColor Yellow
Write-Host "Detection Rate: $totalDetected/$($tests.Count)" -ForegroundColor $(if ($totalDetected -eq $tests.Count) {"Green"} else {"Yellow"})
Write-Host "========================================`n" -ForegroundColor Yellow
