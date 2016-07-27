if (-not (Get-Command python -errorAction SilentlyContinue) -or -not ((python -V).StartsWith("Python 3"))) {

    Write-Host "Python version >= 3.5 is required !"
    Start-Process -Path "https://www.python.org/ftp/python/3.5.2/python-3.5.2.exe"

} else {

    if (-not (Test-Path .\venv\Scripts\python.exe)) {

        if (-not (Get-Command virtualenv -errorAction SilentlyContinue)) {
            Write-Host "Installing virtualenv with pip"
            pip.exe install virtualenv
        }
        Write-Host "Setting up a windows virtual environnement"
        virtualenv .\venv\

        Write-Host "Installing dependencies..."
        .\venv\Scripts\pip.exe install websocket-server
    }
    
    Write-Host "Starting server. CTRL+C to quit."
    .\venv\Scripts\python.exe start.py
}
