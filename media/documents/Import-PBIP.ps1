# Parameters 
$workspaceName = "EdTech_Workspace"
$pbipSemanticModelPath = "C:\Users\User\powerbidesktop_reports\ded903.SemanticModel"
$pbipReportPath = "C:\Users\User\powerbidesktop_reports\ded903.Report"
$currentPath = (Split-Path $MyInvocation.MyCommand.Definition -Parent)
Set-Location $currentPath

# Download modules and install
New-Item -ItemType Directory -Path ".\modules" -ErrorAction SilentlyContinue | Out-Null
@("https://raw.githubusercontent.com/microsoft/Analysis-Services/master/pbidevmode/fabricps-pbip/FabricPS-PBIP.psm1"
, "https://raw.githubusercontent.com/microsoft/Analysis-Services/master/pbidevmode/fabricps-pbip/FabricPS-PBIP.psd1") |% {
    Invoke-WebRequest -Uri $_ -OutFile ".\modules\$(Split-Path $_ -Leaf)"
}
if(-not (Get-Module Az.Accounts -ListAvailable)) { 
    Install-Module Az.Accounts -Scope CurrentUser -Force
}
Import-Module ".\modules\FabricPS-PBIP" -Force

# Authenticate
Set-FabricAuthToken -reset

# Ensure workspace exists
$workspaceId = New-FabricWorkspace  -name $workspaceName -skipErrorIfExists

# Import the semantic model and save the item id
$semanticModelImport = Import-FabricItem -workspaceId $workspaceId -path $pbipSemanticModelPath

# Import the report and ensure its binded to the previous imported report
$reportImport = Import-FabricItem -workspaceId $workspaceId -path $pbipReportPath -itemProperties @{"semanticModelId" = $semanticModelImport.Id}