# Script to create GitHub repository
# You'll need a GitHub Personal Access Token with 'repo' scope
# Get one at: https://github.com/settings/tokens

param(
    [Parameter(Mandatory=$true)]
    [string]$GitHubToken,
    
    [string]$RepoName = "transformer-questions",
    [switch]$Private = $false
)

$headers = @{
    "Accept" = "application/vnd.github.v3+json"
    "Authorization" = "token $GitHubToken"
}

$body = @{
    name = $RepoName
    private = $Private
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "https://api.github.com/user/repos" -Method Post -Headers $headers -Body $body -ContentType "application/json"
    Write-Host "Repository created successfully!" -ForegroundColor Green
    Write-Host "Repository URL: $($response.html_url)" -ForegroundColor Cyan
    
    # Add remote and push
    git remote add origin $response.clone_url
    Write-Host "Remote 'origin' added: $($response.clone_url)" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "  git add ."
    Write-Host "  git commit -m 'Initial commit'"
    Write-Host "  git branch -M main"
    Write-Host "  git push -u origin main"
} catch {
    Write-Host "Error creating repository: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response.StatusCode -eq 401) {
        Write-Host "Authentication failed. Please check your GitHub token." -ForegroundColor Red
    }
}

