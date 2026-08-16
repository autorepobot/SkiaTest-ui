using System;
using System.Reflection;
using Uno.UI.Hosting;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using SkiaSharp;
using SkiaSharp.Views.Windows;

namespace SkiaTestApp;

public class Program
{
    [STAThread]
    public static void Main(string[] args)
    {
        Console.WriteLine("[TEST] Starting Uno Platform Skia Host...");

        // 【核心修复】显式加载 X11 与 Linux FrameBuffer 两个宿主程序集，
        // 确保反射扫描能成功发现它们（尤其是在裁剪/自包含发布场景下）。
        Assembly.Load("Uno.UI.Runtime.Skia.X11");
        Assembly.Load("Uno.UI.Runtime.Skia.Linux.FrameBuffer");

        // 打开 Host 选择阶段的调试日志，方便确认到底选中了哪个 host、
        // 以及某个 host 判定"不可用"的具体原因。
        App.ConfigureFilters();

        var host = UnoPlatformHostBuilder.Create()
            .App(() => new App())
            // 有图形会话（X11 或 Wayland 下的 XWayland）时优先使用，
            // 通过 $DISPLAY 环境变量探测可用性。
            .UseX11()
            // 没有窗口系统（纯 tty / 嵌入式无头设备，且内核暴露了 /dev/fb0）
            // 时的兜底方案。当前这台机器如果没有 /dev/fb0，这一项会被自动跳过。
            .UseLinuxFrameBuffer()
            .Build();

        host.Run();
    }
}

public class App : Application
{
    protected override void OnLaunched(LaunchActivatedEventArgs args)
    {
        Console.WriteLine("[TEST] Initializing Main Window & Skia Canvas...");

        var skiaCanvas = new SKXamlCanvas();
        skiaCanvas.PaintSurface += (s, e) =>
        {
            var canvas = e.Surface.Canvas;

            // 1. 测试画布清屏与底色填充
            canvas.Clear(SKColors.DarkSlateBlue);

            // 2. 测试 SkiaSharp 矢量图形绘制
            using var rectPaint = new SKPaint
            {
                Color = SKColors.Crimson,
                Style = SKPaintStyle.Fill,
                IsAntialias = true
            };
            canvas.DrawRoundRect(new SKRect(50, 50, 450, 200), 20, 20, rectPaint);

            // 3. 测试 SkiaSharp 文字渲染
            using var font = new SKFont(SKTypeface.Default, 32);
            using var textPaint = new SKPaint
            {
                Color = SKColors.White,
                IsAntialias = true
            };
            canvas.DrawText("SkiaSharp Engine Active!", 80, 120, SKTextAlign.Left, font, textPaint);

            Console.WriteLine("[TEST] SUCCESS: SkiaSharp PaintSurface Event Executed!");
        };

        var window = new Window();
        window.Content = new Grid
        {
            Children =
            {
                skiaCanvas,
                new TextBlock
                {
                    Text = "Uno Platform Skia Desktop Mode",
                    HorizontalAlignment = HorizontalAlignment.Center,
                    VerticalAlignment = VerticalAlignment.Bottom,
                    Margin = new Thickness(0, 0, 0, 40),
                    FontSize = 18
                }
            }
        };

        window.Activate();
        Console.WriteLine("[TEST] SUCCESS: Host Initialized and Rendered without Exceptions!");
    }

    // 打开 Skia Host 选择阶段的调试日志。
    // 需要在 Build() 之前调用，否则看不到 host 探测过程的日志。
    public static void ConfigureFilters()
    {
        Microsoft.Extensions.Logging.ILoggerFactory factory = Microsoft.Extensions.Logging.LoggerFactory.Create(builder =>
        {
            builder
                .SetMinimumLevel(Microsoft.Extensions.Logging.LogLevel.Debug)
                .AddFilter("Uno", Microsoft.Extensions.Logging.LogLevel.Debug)
                .AddConsole();
        });

        global::Uno.Extensions.LogExtensionPoint.AmbientLoggerFactory = factory;
    }
}
