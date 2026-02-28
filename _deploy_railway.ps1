$env:RAILWAY_TOKEN = "99b4ca31-6c98-4a36-85f9-3ed4f50b6c43"

Write-Host "Testing Railway auth..."
npx @railway/cli whoami

Write-Host "`nLinking to project zealous-radiance (71bce21a-ef1c-46b3-a54b-7bde6002ba86)..."
npx @railway/cli link --project 71bce21a-ef1c-46b3-a54b-7bde6002ba86

Write-Host "`nDeploying backend..."
npx @railway/cli up --detach
