(Get-Content $args[0]) -replace 'pick 1735a9d', 'edit 1735a9d' | Set-Content $args[0]
