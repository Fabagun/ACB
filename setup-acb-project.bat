@echo off
echo Setting up AzerothCore Builder project directory...

REM Create the new project directory
set PROJECT_DIR=C:\AzerothCore-Builder-Project
mkdir "%PROJECT_DIR%" 2>nul

echo Copying files to %PROJECT_DIR%...

REM Copy all documentation and project files
copy "ACB.py" "%PROJECT_DIR%\"
copy "README.md" "%PROJECT_DIR%\"
copy "LICENSE" "%PROJECT_DIR%\"
copy "CHANGELOG.md" "%PROJECT_DIR%\"
copy "CONTRIBUTING.md" "%PROJECT_DIR%\"
copy "setup.py" "%PROJECT_DIR%\"
copy "requirements.txt" "%PROJECT_DIR%\"
copy "requirements-dev.txt" "%PROJECT_DIR%\"
copy "*.md" "%PROJECT_DIR%\"
copy ".gitignore" "%PROJECT_DIR%\"

REM Copy directories
xcopy "icons" "%PROJECT_DIR%\icons\" /E /I /Y
xcopy ".github" "%PROJECT_DIR%\.github\" /E /I /Y

echo.
echo ✅ Project setup complete!
echo.
echo Next steps:
echo 1. Open GitHub Desktop
echo 2. Click "Add an Existing Repository from your Hard Drive"
echo 3. Browse to: %PROJECT_DIR%
echo 4. Click "Create repository" if prompted
echo 5. All files should now be visible in GitHub Desktop
echo.
echo Project location: %PROJECT_DIR%
pause