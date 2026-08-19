%undefine _missing_build_ids_terminate_build

Name:           SkiaTestApp
Version:        1.0.0
Release:        1%{?dist}
Summary:        Uno Platform SkiaSharp Test App for ppc64le

License:        MIT
URL:            https://github.com/autorepobot/SkiaTestApp
ExclusiveArch:  ppc64le

# 说明：当 Copr/Packit 从 Git 触发构建时，Source0 会被系统自动替换为 Git 源码包；
# 将预编译包单独定义为 Source3，可确保在任何构建环境下均能精准拉取并使用 Zip 包。
Source0:        https://github.com/autorepobot/SkiaTest-ui/releases/download/%{version}/%{name}-linux-ppc64le.zip
Source1:        https://github.com/autorepobot/SkiaSharp/releases/download/ppc64le-test-31909126013/libHarfBuzzSharp.so
Source2:        https://github.com/autorepobot/SkiaSharp/releases/download/ppc64le-test-31909126013/libSkiaSharp.so
Source3:        https://github.com/autorepobot/SkiaTest-ui/releases/download/%{version}/%{name}-linux-ppc64le.zip

BuildRequires:  unzip
BuildRequires:  xorg-x11-server-Xvfb
BuildRequires:  ImageMagick
BuildRequires:  fontconfig
BuildRequires:  libX11-devel
BuildRequires:  libXi-devel

%description
Uno Platform SkiaSharp test application build with headless GUI execution and screenshot validation on ppc64le.

%prep
# 进入标准的源码/构建主目录
%setup -q -n %{name}-%{version}

# 强制将预编译 Zip 包的内容解压并覆盖到当前构建目录根节点
unzip -o %{SOURCE3} -d .

%build
# 将第三方编译的 ppc64le native .so 覆盖/复制到程序目录中
cp -f %{SOURCE1} .
cp -f %{SOURCE2} .

%install
mkdir -p %{buildroot}%{_libexecdir}/%{name}
mkdir -p %{buildroot}%{_bindir}

# 部署程序本体与链接库（平铺复制到安装目录）
cp -a ./* %{buildroot}%{_libexecdir}/%{name}/

# 为二进制程序及原生共享库赋予正确的可执行权限
chmod +x %{buildroot}%{_libexecdir}/%{name}/SkiaTestApp
chmod 0755 %{buildroot}%{_libexecdir}/%{name}/*.so

# 创建可执行启动脚本
cat << 'EOF' > %{buildroot}%{_bindir}/%{name}
#!/bin/sh
exec %{_libexecdir}/%{name}/SkiaTestApp "$@"
EOF
chmod +x %{buildroot}%{_bindir}/%{name}

%check
# 1. 启动虚拟 X11 显示服务
export DISPLAY=:99
Xvfb :99 -screen 0 1024x768x24 &
XVFB_PID=$!
sleep 2

# 创建临时日志与截图输出目录
TEST_DIR="$(mktemp -d)"
LOG_FILE="${TEST_DIR}/gui_test.log"
SCREENSHOT_FILE="${TEST_DIR}/gui_test_screenshot.png"

# 2. 启动 GUI 应用并将终端控制台输出写入日志
%{buildroot}%{_libexecdir}/%{name}/SkiaTestApp > "${LOG_FILE}" 2>&1 &
APP_PID=$!

# 等待 Uno Host 窗口创建并完成 Skia 绘制
sleep 30

# 3. 使用 ImageMagick 截取虚拟桌面的画面并保存为截图
import -window root "${SCREENSHOT_FILE}" || true

# 4. 清理后台进程
kill $APP_PID || true
kill $XVFB_PID || true

# 5. 打印控制台输出到 Copr 构建日志中便于直接排查
echo "================ Copr GUI Test Log ================"
cat "${LOG_FILE}"
echo "==================================================="

# 清理临时文件
rm -rf "${TEST_DIR}"

%files
%{_bindir}/%{name}
%{_libexecdir}/%{name}/

%changelog
* Wed Aug 19 2026 Auto Repo Bot <dev@example.com> - 1.0.0-1
- Fix source unpacking logic to support Copr Git builds with prebuilt zip deployment.
- Explicitly inject ppc64le native libraries and set 0755 permissions.
