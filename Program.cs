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

        var host = UnoPlatformHostBuilder.Create()
            .App(() => new App())
            // 有图形会话（X11 或 Wayland 下的 XWayland）时优先使用，
            // 通过 $DISPLAY 环境变量探测可用性。
            .UseX11()
            // 没有窗口系统（纯 tty / 嵌入式无头设备，且内核暴露了 /dev/fb0）
            // 时的兜底方案。当前机器如果没有 /dev/fb0，这一项会被自动跳过。
            .UseLinuxFrameBuffer()
            .Build();

        host.Run();
    }
}

public class App : Application
{
    protected override void OnLaunched(LaunchActivatedEventArgs args)
    {
        Console.WriteLine("[TEST] Initializing Main Window...");

        // 【核心修复】必须先创建并 Activate() Window，
        // 让 X11XamlRootHost 先注册好，之后再创建任何依赖
        // DisplayInformation.GetForCurrentView() 的控件（比如 SKXamlCanvas）。
        // 之前的写法是先 new SKXamlCanvas() 再创建 Window，
        // 这时候还没有任何 root host，所以会抛
        // "X11DisplayInformationExtension couldn't find a X11XamlRootHost"。
        var window = new Window();
        window.Activate();

        Console.WriteLine("[TEST] Initializing Skia Canvas...");

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

        Console.WriteLine("[TEST] SUCCESS: Host Initialized and Rendered without Exceptions!");
    }
}
