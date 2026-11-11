@echo off
cd /d "E:\Projects\Fawadimraj Github\Fawadullah15"
echo Reconciling with remote repository...
git pull --rebase origin main
echo Pushing updated profile to main branch...
git push origin main
echo.
echo ===========================================
echo Success! Your profile is live on GitHub!
echo ===========================================
pause
