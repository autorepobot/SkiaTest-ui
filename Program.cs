using System;
using Uno.UI.Hosting;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using SkiaSharp;
using SkiaSharp.Views.WindowsUI;

namespace SkiaTestApp;

public class Program
{
    [STAThread]
    public static void Main(string[] args)
    {
        Console.WriteLine("[TEST] Starting Uno Platform Linux FrameBuffer Host...");
        
        var host = UnoPlatformHostBuilder.Create()
            .App(() => new App())
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

        // 创建一个 SkiaSharp 专用绘图画布，用于测试底层引擎渲染
        var skiaCanvas = new SKXamlCanvas();
        skiaCanvas.PaintSurface += (s, e) =>
        {
            var canvas = e.Surface.Canvas;
            
            // 1. 测试画布清屏与底色填充
            canvas.Clear(SKColors.DarkSlateBlue);
            
            // 2. 测试 SkiaSharp 矢量图形绘制（画一个矩形）
            using var rectPaint = new SKPaint
            {
                Color = SKColors.Crimson,
                Style = SKPaintStyle.Fill,
                IsAntialias = true
            };
            canvas.DrawRoundRect(new SKRect(50, 50, 450, 200), 20, 20, rectPaint);

            // 3. 测试 SkiaSharp 文字渲染
            using var textPaint = new SKPaint
            {
                Color = SKColors.White,
                TextSize = 32,
                IsAntialias = true
            };
            canvas.DrawText("SkiaSharp Engine Active!", 80, 120, textPaint);
            
            Console.WriteLine("[TEST] SUCCESS: SkiaSharp PaintSurface Event Executed!");
        };

        var window = new Window();
        window.Content = new Grid
        {
            Children =
            {
                skiaCanvas, // 将 Skia 画布作为底层渲染组件
                new TextBlock
                {
                    Text = "Uno Platform FrameBuffer Mode",
                    HorizontalAlignment = HorizontalAlignment.Center,
                    VerticalAlignment = VerticalAlignment.Bottom,
                    Margin = new Thickness(0, 0, 0, 40),
                    FontSize = 18
                }
            }
        };
        
        window.Activate();
        Console.WriteLine("[TEST] SUCCESS: FrameBuffer Initialized and Rendered without Exceptions!");
    }
}
