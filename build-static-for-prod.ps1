cd ..\futsal-sim-fe\
npm run build
dir .\build | where {$_.extension -in ".json",".png",".ico",".txt",".svg"} | Move-Item -Destination .\build\static
Remove-Item -Path ..\Django-StyleGuide-Example\build -Recurse -ErrorAction SilentlyContinue
Move-Item -Path .\build -Destination ..\Django-StyleGuide-Example\build
cd ..\Django-Styleguide-Example
Remove-Item -Path .\staticfiles -Recurse -ErrorAction SilentlyContinue
.\venv\Scripts\activate.ps1
python manage.py collectstatic