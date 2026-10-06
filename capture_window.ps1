param([Parameter(Mandatory=$true)][string]$Title,[Parameter(Mandatory=$true)][string]$OutFile)
Add-Type -AssemblyName System.Drawing
$source = @"
using System;
using System.Runtime.InteropServices;
public static class WinSnap {
 [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left; public int Top; public int Right; public int Bottom; }
 [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern IntPtr FindWindow(string cls, string title);
 [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
 [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h, IntPtr dc, uint flags);
}
"@
Add-Type -TypeDefinition $source
$proc=Get-Process | Where-Object { $_.MainWindowTitle -eq $Title } | Select-Object -First 1
if($null -eq $proc -or $proc.MainWindowHandle -eq 0){throw "Window not found: $Title"}
$handle=[IntPtr]$proc.MainWindowHandle
$rect=New-Object WinSnap+RECT
[void][WinSnap]::GetWindowRect($handle,[ref]$rect)
$width=$rect.Right-$rect.Left; $height=$rect.Bottom-$rect.Top
$bitmap=New-Object System.Drawing.Bitmap($width,$height)
$graphics=[System.Drawing.Graphics]::FromImage($bitmap)
$dc=$graphics.GetHdc()
$result=[WinSnap]::PrintWindow($handle,$dc,2)
$graphics.ReleaseHdc($dc)
if(-not $result){$graphics.CopyFromScreen($rect.Left,$rect.Top,0,0,[System.Drawing.Size]::new($width,$height))}
$bitmap.Save($OutFile,[System.Drawing.Imaging.ImageFormat]::Png)
$graphics.Dispose(); $bitmap.Dispose()
