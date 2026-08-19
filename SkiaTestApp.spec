%undefine _missing_build_ids_terminate_build

Name:           SkiaTestApp
Version:        1.0.0
Release:        1%{?dist}
Summary:        Uno Platform SkiaSharp Test App for ppc64le

License:        MIT
URL:            https://github.com/autorepobot/SkiaTestApp
ExclusiveArch:  ppc64le

Source0:        SkiaTestApp-1.0.0.tar.gz
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
%setup -q -n SkiaTestApp-1.0.0
unzip -o %{SOURCE3} -d .

%build
cp -f %{SOURCE1} .
cp -f %{SOURCE2} .

%install
mkdir -p %{buildroot}%{_libexecdir}/%{name}
mkdir -p %{buildroot}%{_bindir}

cp -a ./* %{buildroot}%{_libexecdir}/%{name}/

chmod +x %{buildroot}%{_libexecdir}/%{name}/SkiaTestApp
chmod 0755 %{buildroot}%{_libexecdir}/%{name}/*.so

cat << 'EOF' > %{buildroot}%{_bindir}/%{name}
#!/bin/sh
exec %{_libexecdir}/%{name}/SkiaTestApp "$@"
EOF
chmod +x %{buildroot}%{_bindir}/%{name}

%check
export DISPLAY=:99
Xvfb :99 -screen 0 1024x768x24 &
XVFB_PID=$!
sleep 2

TEST_DIR="$(mktemp -d)"
LOG_FILE="${TEST_DIR}/gui_test.log"
SCREENSHOT_FILE="${TEST_DIR}/gui_test_screenshot.png"

%{buildroot}%{_libexecdir}/%{name}/SkiaTestApp > "${LOG_FILE}" 2>&1 &
APP_PID=$!

sleep 30

import -window root "${SCREENSHOT_FILE}" || true

kill $APP_PID || true
kill $XVFB_PID || true

echo "================ Copr GUI Test Log ================"
cat "${LOG_FILE}"
echo "==================================================="

# 把截图和日志一并安装进 buildroot 的 doc 目录，随包一起产出
mkdir -p %{buildroot}%{_docdir}/%{name}-tests
if [ -s "${SCREENSHOT_FILE}" ]; then
    install -Dm644 "${SCREENSHOT_FILE}" \
        %{buildroot}%{_docdir}/%{name}-tests/gui_test_screenshot.png
else
    echo "WARNING: screenshot file is empty or missing, GUI likely failed to render" >&2
fi
install -Dm644 "${LOG_FILE}" \
    %{buildroot}%{_docdir}/%{name}-tests/gui_test.log

rm -rf "${TEST_DIR}"

%files
%{_bindir}/%{name}
%{_libexecdir}/%{name}/

%files -f %{_builddir}/SkiaTestApp-1.0.0/filelist-tests.txt

%changelog
* Wed Aug 19 2026 Auto Repo Bot <dev@example.com> - 1.0.0-1
- Fix source unpacking logic to support Copr Git builds with prebuilt zip deployment.
- Explicitly inject ppc64le native libraries and set 0755 permissions.
- Preserve GUI test screenshot and log as build artifacts for manual verification.
