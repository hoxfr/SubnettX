$editorPath = Join-Path $PSScriptRoot "git_editor.ps1"
Set-Content -Path $editorPath -Value "(Get-Content `$args[0]) -replace 'pick 1735a9d', 'edit 1735a9d' | Set-Content `$args[0]"

$env:GIT_SEQUENCE_EDITOR = "powershell -ExecutionPolicy Bypass -File `"$editorPath`""
& "C:\Program Files\Git\cmd\git.exe" rebase -i HEAD~4
