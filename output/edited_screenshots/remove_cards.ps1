Add-Type -AssemblyName System.Drawing

$ErrorActionPreference = "Stop"
$root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$outDir = Join-Path $root "output\edited_screenshots"
$oneDrive = $env:OneDrive
if (-not $oneDrive) { $oneDrive = $env:OneDriveConsumer }
if (-not $oneDrive) { $oneDrive = Join-Path $env:USERPROFILE "OneDrive" }
$screenshotDir = Get-ChildItem -LiteralPath $oneDrive -Directory -Recurse -Filter "Screenshots" |
  Where-Object { (Get-ChildItem -LiteralPath $_.FullName -Filter "*.png" | Select-Object -First 1) } |
  Select-Object -First 1 -ExpandProperty FullName
if (-not $screenshotDir) {
  throw "Screenshots folder was not found under $oneDrive"
}

function Find-Shot($key) {
  $file = Get-ChildItem -LiteralPath $screenshotDir -Filter "*.png" |
    Where-Object { $_.Name -like "*$key*" } |
    Select-Object -First 1
  if (-not $file) {
    throw "Screenshot with key $key was not found in $screenshotDir"
  }
  return $file.FullName
}

$shots = @(
  @{
    Input = Find-Shot "133450"
    Output = "screenshot-133450-cards-removed.png"
    SpineX = 915
    Polygons = @(
      @(@(420,226),@(1244,250),@(1255,798),@(420,754)),
      @(@(1328,454),@(1631,486),@(1640,842),@(1326,813)),
      @(@(605,773),@(1168,806),@(1168,912),@(604,912)),
      @(@(470,874),@(564,874),@(566,912),@(471,912))
    )
  },
  @{
    Input = Find-Shot "133501"
    Output = "screenshot-133501-cards-removed.png"
    SpineX = 820
    Polygons = @(
      @(@(169,75),@(895,37),@(897,644),@(169,574)),
      @(@(1054,263),@(1667,334),@(1663,814),@(1052,744)),
      @(@(166,0),@(314,0),@(315,75),@(166,76)),
      @(@(1583,0),@(1839,0),@(1839,78),@(1582,79)),
      @(@(1713,542),@(1839,518),@(1839,831),@(1712,837))
    )
  },
  @{
    Input = Find-Shot "133518"
    Output = "screenshot-133518-cards-removed.png"
    SpineX = 835
    Polygons = @(
      @(@(148,58),@(671,10),@(673,628),@(148,539)),
      @(@(857,250),@(1628,303),@(1653,832),@(858,833)),
      @(@(775,0),@(1130,0),@(1130,257),@(774,258)),
      @(@(1350,0),@(1570,0),@(1570,80),@(1350,80))
    )
  },
  @{
    Input = Find-Shot "133527"
    Output = "screenshot-133527-cards-removed.png"
    SpineX = 900
    Polygons = @(
      @(@(539,202),@(1327,221),@(1328,743),@(539,676)),
      @(@(1400,450),@(1665,483),@(1665,869),@(1400,895)),
      @(@(258,41),@(441,102),@(441,519),@(258,480)),
      @(@(884,672),@(1358,653),@(1358,912),@(884,912)),
      @(@(1334,0),@(1556,0),@(1555,78),@(1334,78))
    )
  },
  @{
    Input = Find-Shot "133541"
    Output = "screenshot-133541-cards-removed.png"
    SpineX = 880
    Polygons = @(
      @(@(236,105),@(846,51),@(846,657),@(236,577)),
      @(@(1012,283),@(1711,336),@(1711,870),@(1012,870)),
      @(@(330,13),@(676,0),@(676,95),@(330,105)),
      @(@(160,0),@(236,0),@(236,421),@(160,421))
    )
  }
)

function New-PathFromPolygons($polygons) {
  $path = New-Object System.Drawing.Drawing2D.GraphicsPath
  foreach ($poly in $polygons) {
    $points = New-Object System.Drawing.PointF[] $poly.Count
    for ($i = 0; $i -lt $poly.Count; $i++) {
      $points[$i] = New-Object System.Drawing.PointF([float]$poly[$i][0], [float]$poly[$i][1])
    }
    $path.AddPolygon($points)
  }
  return $path
}

function Draw-Vertebra($g, [float]$x, [float]$y, [float]$scale, [float]$angle, [float]$alpha) {
  $state = $g.Save()
  $g.TranslateTransform($x, $y)
  $g.RotateTransform($angle)
  $g.ScaleTransform($scale, $scale)

  $bodyPath = New-Object System.Drawing.Drawing2D.GraphicsPath
  $bodyPath.AddEllipse(-72, -29, 144, 58)
  $brush = New-Object System.Drawing.Drawing2D.PathGradientBrush($bodyPath)
  $brush.CenterColor = [System.Drawing.Color]::FromArgb([int](145 * $alpha), 150, 205, 225)
  $brush.SurroundColors = @([System.Drawing.Color]::FromArgb([int](28 * $alpha), 2, 7, 12))
  $g.FillPath($brush, $bodyPath)
  $brush.Dispose()
  $bodyPath.Dispose()

  $dark = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb([int](150 * $alpha), 6, 10, 22))
  $g.FillEllipse($dark, -30, -12, 60, 24)
  $dark.Dispose()

  $cyan = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb([int](96 * $alpha), 70, 225, 245), 4)
  $mag = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb([int](76 * $alpha), 230, 72, 220), 3)
  $g.DrawEllipse($cyan, -76, -31, 152, 62)
  $g.DrawBezier($mag, -80, 6, -42, -30, 42, 31, 86, -4)
  $cyan.Dispose()
  $mag.Dispose()

  $g.Restore($state)
}

foreach ($shot in $shots) {
  $bitmap = [System.Drawing.Bitmap]::FromFile($shot.Input)
  $g = [System.Drawing.Graphics]::FromImage($bitmap)
  $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
  $g.CompositingQuality = [System.Drawing.Drawing2D.CompositingQuality]::HighQuality

  $maskPath = New-PathFromPolygons $shot.Polygons
  $g.SetClip($maskPath)

  $rect = New-Object System.Drawing.Rectangle(0, 0, $bitmap.Width, $bitmap.Height)
  $bg = New-Object System.Drawing.Drawing2D.LinearGradientBrush(
    $rect,
    [System.Drawing.Color]::FromArgb(168, 1, 8, 10),
    [System.Drawing.Color]::FromArgb(154, 8, 16, 26),
    35
  )
  $g.FillRectangle($bg, $rect)
  $bg.Dispose()

  $rand = New-Object System.Random(4242 + [int]$shot.SpineX)
  for ($y = -40; $y -lt ($bitmap.Height + 70); $y += 54) {
    $cx = [float]($shot.SpineX + [Math]::Sin($y * 0.018) * 34 + ($rand.NextDouble() - 0.5) * 18)
    $scale = [float](0.82 + $rand.NextDouble() * 0.22)
    $angle = [float]([Math]::Sin($y * 0.011) * 13)
    Draw-Vertebra $g $cx ([float]$y) $scale $angle 0.46
  }

  $colors = @(
    [System.Drawing.Color]::FromArgb(150, 35, 215, 255),
    [System.Drawing.Color]::FromArgb(125, 232, 67, 214),
    [System.Drawing.Color]::FromArgb(115, 44, 255, 140),
    [System.Drawing.Color]::FromArgb(112, 112, 78, 255)
  )
  for ($i = 0; $i -lt 520; $i++) {
    $x = [float]($shot.SpineX + ($rand.NextDouble() - 0.5) * 650)
    $y = [float]($rand.NextDouble() * $bitmap.Height)
    $r = [float](1 + $rand.NextDouble() * 4.5)
    $brush = New-Object System.Drawing.SolidBrush($colors[$rand.Next(0, $colors.Count)])
    $g.FillEllipse($brush, $x - $r, $y - $r, $r * 2, $r * 2)
    $brush.Dispose()
  }

  $veil = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(22, 0, 8, 10))
  $g.FillRectangle($veil, $rect)
  $veil.Dispose()

  $g.ResetClip()
  $maskPath.Dispose()
  $g.Dispose()

  $outPath = Join-Path $outDir $shot.Output
  $bitmap.Save($outPath, [System.Drawing.Imaging.ImageFormat]::Png)
  $bitmap.Dispose()
  Write-Output $outPath
}
