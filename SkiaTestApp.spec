Name:           SkiaTestApp
Version:        1.0.0
Release:        1%{?dist}
Summary:        Uno Platform SkiaSharp Test App for ppc64le

License:        MIT
URL:            https://github.com/autorepobot/SkiaTestApp
ExclusiveArch:  ppc64le

# 使用预编译好的 Zip 发布包
Source0:        https://github.com/autorepobot/SkiaTest-ui/releases/download/%{version}/%{name}-linux-ppc64le.zip
# 依赖的原生库定义为额外 Source
Source1:        https://github.com/autorepobot/SkiaSharp/releases/download/ppc64le-test-31909126013/libHarfBuzzSharp.so
Source2:        https://github.com/autorepobot/SkiaSharp/releases/download/ppc64le-test-31909126013/libSkiaSharp.so

BuildRequires:  unzip
BuildRequires:  xorg-x11-server-Xvfb
BuildRequires:  ImageMagick
BuildRequires:  fontconfig
BuildRequires:  libX11-devel
BuildRequires:  libXi-devel

%description
Uno Platform SkiaSharp test application build with headless GUI execution and screenshot validation on ppc64le.

%prep
# zip 包解压时没有顶层同名文件夹，使用 -c 创建解压目录
%setup -q -c -n %{name}-%{version}

%build
# 插入第三方编译的 native .so 到程序解压目录中
cp %{SOURCE1} .
cp %{SOURCE2} .

%install
mkdir -p %{buildroot}%{_libexecdir}/%{name}
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_docdir}/%{name}

# 部署程序本体与链接库
cp -a ./* %{buildroot}%{_libexecdir}/%{name}/

# 创建可执行启动脚本并赋予权限
cat << 'EOF' > %{buildroot}%{_bindir}/%{name}
#!/bin/sh
exec %{_libexecdir}/%{name}/SkiaTestApp "$@"
EOF
chmod +x %{buildroot}%{_bindir}/%{name}
chmod +x %{buildroot}%{_libexecdir}/%{name}/SkiaTestApp

%check
# 1. 启动虚拟 X11 显示服务
export DISPLAY=:99
Xvfb :99 -screen 0 1024x768x24 &
XVFB_PID=$!
sleep 2

DOC_DIR="%{buildroot}%{_docdir}/%{name}"
LOG_FILE="${DOC_DIR}/gui_test.log"
SCREENSHOT_FILE="${DOC_DIR}/gui_test_screenshot.png"

# 2. 启动 GUI 应用并将终端控制台输出写入日志
%{buildroot}%{_libexecdir}/%{name}/SkiaTestApp > "${LOG_FILE}" 2>&1 &
APP_PID=$!

# 等待 Uno Host 窗口创建并完成 Skia 绘制
sleep 5

# 3. 使用 ImageMagick 截取虚拟桌面的画面并保存为截图
import -window root "${SCREENSHOT_FILE}" || true

# 4. 清理后台进程
kill $APP_PID || true
kill $XVFB_PID || true

# 5. 打印控制台输出到 Copr 构建日志中便于直接排查
echo "================ Copr GUI Test Log ================"
cat "${LOG_FILE}"
echo "==================================================="

%files
%{_bindir}/%{name}
%{_libexecdir}/%{name}/
# 将日志与截图打入 RPM 包的文档目录 (/usr/share/doc/SkiaTestApp/)
%doc %{_docdir}/%{name}/

%changelog
* Wed Aug 19 2026 Auto Repo Bot <dev@example.com> - 1.0.0-1
- Switch to prebuilt zip source and inject custom native libraries for ppc64le.
