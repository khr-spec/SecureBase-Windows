# New-SecureBaseSupport.ps1
# Formål:
# Opretter en Support-OU, en global sikkerhedsgruppe og tre brugere
# i Active Directory. Scriptet kan køres flere gange uden at
# oprette duplikater.
#
# Krav:
# - Køres på DC01 som administrator
# - ActiveDirectory PowerShell-modulet skal være installeret

Import-Module ActiveDirectory

# Grundstier i Active Directory
$DomainDN = "DC=securebase,DC=local"
$BaseOU   = "OU=SecureBase,$DomainDN"
$SupportOU = "OU=Support,$BaseOU"
$GroupsOU  = "OU=Groups,$BaseOU"

# Gruppe, som Support-brugerne skal være medlem af
$GroupName = "GG_Support_Users"

# Brugere, som scriptet skal administrere
$Users = @(
    @{
        FirstName = "Nora"
        LastName  = "Hansen"
        Username  = "nhansen"
    },
    @{
        FirstName = "Oliver"
        LastName  = "Madsen"
        Username  = "omadsen"
    },
    @{
        FirstName = "Freja"
        LastName  = "Thomsen"
        Username  = "fthomsen"
    }
)

# Password læses interaktivt og gemmes derfor ikke i scriptet.
$TemporaryPassword = Read-Host "Indtast midlertidigt password til nye brugere" -AsSecureString

# Opret Support-OU, hvis den ikke allerede findes.
$ExistingOU = Get-ADOrganizationalUnit `
    -Filter "Name -eq 'Support'" `
    -SearchBase $BaseOU `
    -SearchScope OneLevel `
    -ErrorAction SilentlyContinue

if (-not $ExistingOU) {
    New-ADOrganizationalUnit `
        -Name "Support" `
        -Path $BaseOU `
        -ProtectedFromAccidentalDeletion $true

    Write-Host "[CREATED] OU Support"
}
else {
    Write-Host "[EXISTS] OU Support"
}

# Opret Support-gruppen, hvis den ikke allerede findes.
$ExistingGroup = Get-ADGroup `
    -Filter "SamAccountName -eq '$GroupName'" `
    -ErrorAction SilentlyContinue

if (-not $ExistingGroup) {
    New-ADGroup `
        -Name $GroupName `
        -SamAccountName $GroupName `
        -GroupScope Global `
        -GroupCategory Security `
        -Path $GroupsOU

    Write-Host "[CREATED] Group $GroupName"
}
else {
    Write-Host "[EXISTS] Group $GroupName"
}

# Opret brugerne og kontroller deres gruppemedlemskab.
foreach ($User in $Users) {

    $ExistingUser = Get-ADUser `
        -Filter "SamAccountName -eq '$($User.Username)'" `
        -ErrorAction SilentlyContinue

    if (-not $ExistingUser) {

        $FullName = "$($User.FirstName) $($User.LastName)"

        New-ADUser `
            -Name $FullName `
            -GivenName $User.FirstName `
            -Surname $User.LastName `
            -DisplayName $FullName `
            -SamAccountName $User.Username `
            -UserPrincipalName "$($User.Username)@securebase.local" `
            -Path $SupportOU `
            -AccountPassword $TemporaryPassword `
            -Enabled $true `
            -ChangePasswordAtLogon $true

        Write-Host "[CREATED] User $($User.Username)"
    }
    else {
        Write-Host "[EXISTS] User $($User.Username)"
    }

    # Tilføj kun brugeren til gruppen, hvis medlemskabet mangler.
    $IsMember = Get-ADGroupMember $GroupName |
        Where-Object { $_.SamAccountName -eq $User.Username }

    if (-not $IsMember) {
        Add-ADGroupMember `
            -Identity $GroupName `
            -Members $User.Username

        Write-Host "[ADDED] $($User.Username) -> $GroupName"
    }
    else {
        Write-Host "[EXISTS] $($User.Username) already member of $GroupName"
    }
}

Write-Host ""
Write-Host "SecureBase Support setup completed."
