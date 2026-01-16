from PIL import Image, ImageDraw
import os

def crop_to_circle(image_path, output_path):
    print(f"Processing {image_path}...")
    try:
        img = Image.open(image_path).convert("RGBA")
    except Exception as e:
        print(f"Error opening image: {e}")
        return

    # Analyze the image to find the bounding box of non-background pixels
    # We assume the background is uniform and pick the top-left pixel color
    width, height = img.size
    pixels = img.load()
    bg_color = pixels[0, 0]
    print(f"Background color detected: {bg_color}")
    
    # Simple color distance check
    def is_different(c1, c2, tolerance=20):
        return sum(abs(p1 - p2) for p1, p2 in zip(c1, c2)) > tolerance * 3

    # Find boundaries
    min_x, min_y = width, height
    max_x, max_y = 0, 0
    found = False

    for y in range(height):
        for x in range(width):
            if is_different(pixels[x, y], bg_color):
                if x < min_x: min_x = x
                if x > max_x: max_x = x
                if y < min_y: min_y = y
                if y > max_y: max_y = y
                found = True

    if not found:
        print("No non-background pixels found!")
        return

    # Calculate center and radius
    w = max_x - min_x
    h = max_y - min_y
    diameter = max(w, h)
    
    center_x = (min_x + max_x) // 2
    center_y = (min_y + max_y) // 2
    
    # Expand slightly
    radius = (diameter // 2) + 2
    
    # Create cropped square image
    left = center_x - radius
    top = center_y - radius
    right = center_x + radius
    bottom = center_y + radius
    
    cropped = img.crop((left, top, right, bottom))
    
    # Create circular mask
    mask_size = (radius * 2, radius * 2)
    mask_img = Image.new('L', mask_size, 0)
    draw = ImageDraw.Draw(mask_img)
    draw.ellipse((0, 0) + mask_size, fill=255)
    
    # Apply mask
    output = Image.new('RGBA', mask_size, (0, 0, 0, 0))
    output.paste(cropped, (0, 0), mask_img)
    
    output.save(output_path, "PNG")
    print(f"Saved cropped logo to {output_path}")

# Run
input_path = "/Users/arturmartirosyan/telegram-bot-platform/miniapp/public/taskbot-source.png"
output_path = "/Users/arturmartirosyan/telegram-bot-platform/miniapp/public/taskbot-logo.png"
crop_to_circle(input_path, output_path)
