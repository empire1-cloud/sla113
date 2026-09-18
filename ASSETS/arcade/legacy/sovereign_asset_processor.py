import os
from pathlib import Path
from rembg import remove
from PIL import Image
from io import BytesIO

def process_sovereign_assets(input_folder, output_folder):
    # Ensure output directory exists
    Path(output_folder).mkdir(parents=True, exist_ok=True)

    print(f"SLA113 // INITIALIZING POST-PROCESSING PIPELINE...")
    
    for filename in os.listdir(input_folder):
        if filename.endswith((".png", ".jpg", ".jpeg")):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, f"{Path(filename).stem}.webp")

            print(f"Processing: {filename} -> Extracting Alpha Layer...")

            try:
                # 1. Open the raw Vertex AI asset
                with open(input_path, 'rb') as i:
                    input_image = i.read()

                # 2. Remove background using AI
                output_image = remove(input_image)

                # 3. Convert to PIL for final Sovereign optimization
                img = Image.open(BytesIO(output_image)).convert("RGBA")  # Output from rembg
                
                # 4. Save the optimized WebP file
                img.save(output_path, "WEBP", method=6)

                print(f"Success: {filename} -> Saved as {output_path}")

            except Exception as e:
                print(f"Error processing {filename}: {e}")

# Define input and output folders for the Sovereign Asset Pipeline
input_folder = "path_to_input_assets"
output_folder = "path_to_output_assets"

process_sovereign_assets(input_folder, output_folder)