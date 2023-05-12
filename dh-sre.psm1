function New-BulkGCPGroups {
<#
  .SYNOPSIS
  New-BulkGCPGroups creates one or more security groups under default OU 'OU=Google Cloud,OU=Groups,OU=Enterprise,DC=domain,DC=co,DC=uk',
  or in a different OU provided as parameter value.
  .DESCRIPTION
  This script uses the Active Directory module to create one or more
  security groups. It's necessary to update the 'mail' attribute of the groups because GCDS (Google
  Cloud Directory Sync - currently installed on GB-WAT-SVV-3559) will only sync groups with this
  attribute set. Indeed, GCP will name the cloud counterpart of the group following the local
  part of the email address (everything before the '@' sign).
  .PARAMETER BaseOU
  Accepts the path to an existing Active Directory organization unit in distinguished name format (http://bit.ly/2uMeXOe).
  It's at this point in the directory structure that the new organization unit will be created. If 
  an invalid OU is specified the script will display an error and stop. This is an optional parameter
  and if not set at run time will default to the current root OU for Google Cloud projects:
  >> OU=Google Cloud,OU=Groups,OU=Enterprise,DC=domain,DC=co,DC=uk
  .PARAMETER SourceFile
  Accepts a valid file containig data in the format mentioned below.Specifices the CSV of the new organization unit to create. 'universal-exports', for example:
  GroupName,Description,ManagedBy,ClientName
  coop-no-ap-gpu,Test group to test automation of bulk group creation,ausafa,dh-coop-no
  coop-no-dp-gpu,Test group to test automation of bulk group creation,ausafa,dh-coop-no
  crv-ap-gpu,Test group to test automation of bulk group creation,ausafa,dh-crv
  crv-dp-gpu,Test group to test automation of bulk group creation,ausafa,dh-crv
  
  This is a mandatory parameter and require valid file. If file not found script will throw error "New-BulkGCPGroups: Cannot validate argument on parameter 'SourceFile'. Source file does not exist".
  .EXAMPLE
  This example creates AD groups based on the CSV file provided:
  New-BulkGCPGroups -SourceFile .\samplegroups.csv
  .EXAMPLE
  This example creates AD groups based on the provided CSV file provided overriding the base OU:
  New-BulkGCPGroups -SourceFile .\samplegroups.csv -BaseOU 'OU=Google Cloud,OU=Groups,OU=Enterprise,DC=domain,DC=co,DC=uk'
#>
    [CmdletBinding()] # Decorator to allow verbose and debug parameters
    param (
        [Parameter(Mandatory = $true)]
        [ValidateScript({
            If(-not($_ | test-path)) {
                throw "Source file does not exist"
            }
            return $true
        })]
        [System.IO.FileInfo]$SourceFile,

        [Parameter(Mandatory = $false)]
        [ValidateNotNullOrEmpty()]
        [string]$BaseOU = 'OU=Google Cloud,OU=Groups,OU=Enterprise,DC=domain,DC=co,DC=uk'
    )
    BEGIN {
        $Module = 'ActiveDirectory'
        Write-Verbose "Loading dependency ($Module)..."
        if (Get-Module -ListAvailable -Verbose:$false | Where-Object -FilterScript { $_.Name -eq $Module }) {
            Import-Module -Name $Module -Verbose:$false
        }
        else {
            Write-Error "Module ($Module) not available. Exiting..."
            exit
        }
    }
    PROCESS {
        # Check domain controller and set one in Wat if needed
        try {
            Write-Host "Getting ADDomainController..."
            $DomainController = Get-ADDomainController -ErrorAction Stop | Select-Object Name -expandproperty Name
        }
        catch {
            Write-Host "Get-ADDomainController threw an error"
            Write-Host "Selecting a specific domain controller "
            $DomainController = 'gb-wat-svv-1100'
        }
        Write-Host "Selected domain controller is $DomainController ..."
    
        if (-not(Test-Path -Path "AD:\$BaseOU")) {
            Write-Error "The path to the base OU provided ($BaseOU) doesn't exist - please try again ..."
            exit
        }
    
    
        # Loop through each group attempt to create it
        $SourceCSV = Import-csv $SourceFile
        foreach ($Item in $SourceCSV) {
            $Parameters = @{
                Name            = "$($Item.GroupName)"
                Path            = "OU=$($Item.clientname),$BaseOU"
                GroupScope      = 'Global'
                GroupCategory   = 'Security'
                ManagedBy       = $item.ManagedBy
                Description     = $item.Description
                OtherAttributes = @{mail = "$($item.GroupName)@domain.com" }
                Server          = $DomainController
            }
            try {
                # Validating OU in which group attempt to create
                if (-not(Test-Path -Path "AD:\OU=$($Item.ClientName),$BaseOU")) {
                    Write-Warning "Client $($item.clientname) base OU doesn't exist - skipping it ..."
                }
                else {
                    Write-Host "Attempting to create group ["$($Item.GroupName)"] ..."
                    New-ADGroup @Parameters -ErrorAction Stop
                    Write-Host "Created group ["$($Item.GroupName)"]"
                }
            }
            catch {
                if ($_.exception.message -eq 'The specified group already exists') {
                    Write-Warning "The following group already exists ["$($Item.GroupName)"]. Skipping it's creation..."
                }
                else {
                    throw "Exception Message: $($_.Exception.Message)"
                }
            }
        }
    }
    END {}
}
