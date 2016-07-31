function Download-If-Not-Exists {
	for ($i=0; $i -lt $args.length; $i++) {
		if (-not (Test-Path $args[$i])) {
			Write-Host -ForegroundColor Yellow "File" $args[$i] "not found, downloading a template from github..."
			$args[$i] = $args[$i] -replace "\.\\", ""
			Invoke-WebRequest -Uri ("https://raw.githubusercontent.com/Julien00859/Bomberman/master/" + ($args[$i] -replace "\\", "/")) -OutFile $args[$i]
		}
	}
}

Set-Location $PSScriptRoot

if (-not (Get-Command python -errorAction SilentlyContinue) -or -not ((python -V).StartsWith("Python 3"))) {

    Write-Host "Python version >= 3.5 is required !" -ForegroundColor Yellow
    Start-Process -Path "https://www.python.org/ftp/python/3.5.2/python-3.5.2.exe"

} else {

    if (-not (Test-Path .\venv\Scripts\python.exe)) {

        if (-not (Get-Command virtualenv -errorAction SilentlyContinue)) {
            Write-Host "Installing virtualenv with pip" -ForegroundColor Yellow
            pip.exe install virtualenv
        }
        Write-Host "Setting up a windows virtual environnement" -ForegroundColor Yellow
        virtualenv.exe .\venv\

        Write-Host "Installing dependencies..." -ForegroundColor Yellow
        .\venv\Scripts\pip.exe install websocket-server
    }

    if (-not (Test-Path .\client\js\playground.js)) {
    	Write-Host -ForegroundColor Yellow "Library playground.js not found, downloading..."
    	Invoke-WebRequest -Uri https://raw.githubusercontent.com/rezoner/playground/master/build/playground.js -OutFile .\client\js\playground.js
    }

    if (-not (Test-Path .\settings\)) {
        Write-Host ".\settings package not found, creating one" -ForegroundColor Yellow
    	New-Item .\settings -type directory | Out-Null
		New-Item .\settings\__init__.py -type file | Out-Null
    }
    
    Download-If-Not-Exists .\settings\game_settings.py .\settings\server_settings.py .\settings\schema.sql

    Write-Host "Starting server. CTRL+C to quit."
    .\venv\Scripts\python.exe start.py
}
