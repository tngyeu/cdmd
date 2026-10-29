# Start WordCraft Desktop MCP without keyboard/mouse automation.
$wcExecutable = 'C:\Program Files\WordCraft\wordcraft.exe'
if (-not (Test-Path -LiteralPath $wcExecutable)) { throw "WordCraft executable not found: $wcExecutable" }
$wcSocket = [System.Net.Sockets.TcpClient]::new()
try {
    $wcSocket.Connect('127.0.0.1', 7981)
    Write-Output 'Port 7981 is already open. Verify WordCraft with an MCP inspect_document call.'
} catch {
    Start-Process -FilePath $wcExecutable -ArgumentList '--control', '7981' | Out-Null
    Write-Output 'Started WordCraft with --control 7981. Verify using MCP inspect_document.'
} finally { $wcSocket.Dispose() }
