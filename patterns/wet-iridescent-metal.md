# Wet Iridescent Metal

Use for dark anatomical, spine, liquid-metal, or biomechanical objects that need to match neon/cyber references.

## Direction

- Base: very dark blue/steel/violet, not pure black.
- Highlights: cyan rim light, restrained magenta/purple oil-slick bands, small green accents.
- Surface feel: glossy wet reflections, high contrast, noisy speckles, dark recesses.

## Three.js Shader Notes

- Use Fresnel for cyan/magenta edge glow.
- Use world-position bands for slow oil-slick color variation.
- Keep magenta as highlights, not as the whole base.
- If the object becomes unreadable, raise cyan/steel midtones before raising global brightness.

## QA

- Compare against the final browser canvas, not only Blender or draft screenshots.
- If it reads as pink plastic, reduce magenta fill and darken the base.
- If it reads as black silhouette, increase steel-blue midtones and cyan rim.
