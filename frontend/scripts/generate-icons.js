import sharp from 'sharp'
import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const logoPath = path.join(__dirname, '../../docs/images/logo_photo.svg')
const outputDir = path.join(__dirname, '../public')

// Ensure output directory exists
if (!fs.existsSync(outputDir)) {
  fs.mkdirSync(outputDir, { recursive: true })
}

// Icon sizes needed for PWA
const iconSizes = [
  { size: 64, name: 'pwa-64x64.png' },
  { size: 192, name: 'pwa-192x192.png' },
  { size: 512, name: 'pwa-512x512.png' },
  { size: 512, name: 'maskable-icon-512x512.png', maskable: true }
]

async function generateIcons() {
  try {
    // Read the SVG file
    const svgBuffer = fs.readFileSync(logoPath)
    
    for (const { size, name, maskable } of iconSizes) {
      const outputPath = path.join(outputDir, name)
      
      if (maskable) {
        // For maskable icons, add padding (about 10% on each side)
        const padding = Math.floor(size * 0.1)
        const iconSize = size - (padding * 2)
        
        // Create a white square with the icon in the center
        const icon = await sharp({
          create: {
            width: size,
            height: size,
            channels: 4,
            background: { r: 255, g: 255, b: 255, alpha: 1 }
          }
        })
        .composite([
          {
            input: await sharp(svgBuffer)
              .resize(iconSize, iconSize, { fit: 'contain', background: { r: 0, g: 0, b: 0, alpha: 0 } })
              .toBuffer(),
            left: padding,
            top: padding
          }
        ])
        .png()
        .toFile(outputPath)
        
        console.log(`Generated ${name} (${size}x${size} maskable)`)
      } else {
        // Regular icon - resize with padding for better appearance
        await sharp(svgBuffer)
          .resize(size, size, { fit: 'contain', background: { r: 255, g: 255, b: 255, alpha: 1 } })
          .png()
          .toFile(outputPath)
        
        console.log(`Generated ${name} (${size}x${size})`)
      }
    }
    
    console.log('All icons generated successfully!')
  } catch (error) {
    console.error('Error generating icons:', error)
    process.exit(1)
  }
}

generateIcons()

