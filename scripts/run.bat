@echo off
chcp 65001 > nul
cls
echo.
echo ========================================
echo    SEO关键词挖掘工具集
echo ========================================
echo.
echo 请选择要使用的工具:
echo.
echo [1] 热词发现工具 - 自动发现当前热门话题
echo [2] 关键词挖掘工具 - 深入挖掘特定关键词
echo [3] 退出
echo.
echo ========================================
echo.

set /p choice="请输入选择 (1/2/3): "

if "%choice%"=="1" goto trend
if "%choice%"=="2" goto keyword
if "%choice%"=="3" goto end
echo 无效选择，请重新运行
pause
goto end

:trend
echo.
echo 启动热词发现工具...
python trending-finder.py
pause
goto end

:keyword
echo.
echo 启动关键词挖掘工具...
python keyword-digger.py
pause
goto end

:end
exit
