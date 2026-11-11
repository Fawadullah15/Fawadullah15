@echo off
setlocal enabledelayedexpansion
title Pushing GitHub Profile...

cd /d "E:\Projects\Fawadimraj Github\Fawadullah15"
echo ========================================================
echo   Auto-Syncing Profile to https://github.com/Fawadullah15
echo ========================================================
echo.

echo 1. Staging any unstaged changes...
git add -A

echo 2. Committing local changes...
git commit -m "feat: complete GitHub personal branding and profile upgrade" 2>nul

echo 3. Reconciling with remote GitHub repository...
git pull --rebase -X theirs origin main 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Rebase fallback to merge...
    git pull --no-rebase origin main --strategy-option=theirs -m "merge: sync remote profile assets"
)

echo 4. Pushing to origin main...
git push origin main
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================================
    echo   SUCCESS: Your GitHub profile is now officially live!
    echo   Check it out: https://github.com/Fawadullah15
    echo ========================================================
) else (
    echo.
    echo Attempting force-with-lease to ensure remote sync...
    git push --force-with-lease origin main
)

echo.
timeout /t 5
