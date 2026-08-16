using System;
using Uno.UI.Runtime.Skia.LinuxFrameBuffer;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;

namespace SkiaTestApp;

public class Program
{
    [STAThread]
    public static void Main(string[] args)
    {
        Console.WriteLine("[TEST] Starting Uno Platform Linux FrameBuffer Host...");
        var host = new FrameBufferHost(() => new App());
        host.Run();
    }
}

public class App : Application
{
    protected override void OnLaunched(LaunchActivatedEventArgs args)
    {
        Console.WriteLine("[TEST] Initializing Main Window & Skia Canvas...");
        var window = new Window();
        window.Content = new Grid
        {
            Children =
            {
                new TextBlock
                {
                    Text = "SkiaSharp / Uno FrameBuffer Rendered Successfully!",
                    HorizontalAlignment = HorizontalAlignment.Center,
                    VerticalAlignment = VerticalAlignment.Center,
                    FontSize = 24
                }
            }
        };
        window.Activate();
        Console.WriteLine("[TEST] SUCCESS: FrameBuffer Initialized and Rendered without Exceptions!");
    }
}
