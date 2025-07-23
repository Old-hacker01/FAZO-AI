#!/usr/bin/env python3
import os
import sys
import time
import requests
from PIL import Image, ImageOps, ImageFilter, ImageEnhance
import numpy as np
import argparse
import subprocess
from datetime import datetime
import platform

# Check if running on Termux or Kali Linux
IS_TERMUX = "termux" in os.environ.get("PREFIX", "")
IS_KALI = platform.system() == "Linux" and "kali" in platform.release().lower()

# Configuration
CONFIG = {
    "telegram_link": "https://t.me/mr_nobody",
    "whatsapp_link": "https://wa.me/+255675007732",
    "youtube_link": "https://youtube.com/fazo_28",
    "twitter_link": "https://twitter.com/Fazo28_tz",
    "api_key": "your_stable_diffusion_api_key",
    "output_dir": "output",
    "max_image_size": (1024, 1024),
    "default_model": "stable-diffusion-xl-1024-v1-0"
}

# ASCII Art and Banner
BANNER = """
\033[1;35m
  ______      _          ___   ___ 
 |  ____|    | |        | \ \ / / |
 | |__ __ _ __| |_      | |\ V /| |
 |  __/ _` / _` \ \ /\ / / | > < | |
 | | | (_| | (_| |\ V  V /  |/ . \| |
 |_|  \__,_|\__,_| \_/\_/   /_/ \_\_|
\033[0m
\033[1;36mFazo-AI: Advanced AI Image Generation & Editing Tool\033[0m
\033[1;33mVersion 1.0 | For Kali Linux & Termux\033[0m
"""

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def display_banner():
    clear_screen()
    print(BANNER)
    print("\033[1;32mSocial Links:\033[0m")
    print(f"\033[1;34mTelegram: {CONFIG['telegram_link']}\033[0m")
    print(f"\033[1;32mWhatsApp: {CONFIG['whatsapp_link']}\033[0m")
    print(f"\033[1;31mYouTube: {CONFIG['youtube_link']}\033[0m")
    print(f"\033[1;33mGitHub: {CONFIG['github_link']}\033[0m")
    print(f"\033[1;36mTwitter: {CONFIG['twitter_link']}\033[0m")
    print("-" * 50)

def check_dependencies():
    required = ['Pillow', 'numpy', 'requests']
    missing = []
    
    for package in required:
        try:
            __import__(package.lower())
        except ImportError:
            missing.append(package)
    
    if missing:
        print("\033[1;31mMissing dependencies:\033[0m")
        for dep in missing:
            print(f"- {dep}")
        print("\nInstall them with: pip install " + " ".join(missing))
        sys.exit(1)

def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

def generate_image(prompt, model=CONFIG['default_model'], negative_prompt="", width=512, height=512, samples=1):
    """Generate image using Stable Diffusion API"""
    try:
        url = "https://stablediffusionapi.com/api/v3/text2img"
        
        payload = {
            "key": CONFIG['api_key'],
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "width": str(width),
            "height": str(height),
            "samples": str(samples),
            "num_inference_steps": "20",
            "safety_checker": "yes",
            "enhance_prompt": "yes",
            "seed": None,
            "guidance_scale": 7.5,
            "multi_lingual": "no",
            "panorama": "no",
            "self_attention": "no",
            "upscale": "no",
            "model": model
        }
        
        headers = {'Content-Type': 'application/json'}
        
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        
        if data['status'] == 'success':
            image_url = data['output'][0] if isinstance(data['output'], list) else data['output']
            image_response = requests.get(image_url)
            image_response.raise_for_status()
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"generated_{timestamp}.png"
            output_path = os.path.join(CONFIG['output_dir'], "generated", filename)
            
            with open(output_path, 'wb') as f:
                f.write(image_response.content)
            
            return output_path
        else:
            print(f"\033[1;31mError: {data.get('message', 'Unknown error')}\033[0m")
            return None
            
    except Exception as e:
        print(f"\033[1;31mError generating image: {str(e)}\033[0m")
        return None

def edit_image(image_path, operations):
    """Apply various editing operations to an image"""
    try:
        with Image.open(image_path) as img:
            original_mode = img.mode
            
            # Convert to RGB if not already (for compatibility with filters)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Apply operations
            for op in operations:
                if op == 'grayscale':
                    img = ImageOps.grayscale(img)
                elif op == 'invert':
                    img = ImageOps.invert(img)
                elif op == 'mirror':
                    img = ImageOps.mirror(img)
                elif op == 'flip':
                    img = ImageOps.flip(img)
                elif op == 'blur':
                    img = img.filter(ImageFilter.BLUR)
                elif op == 'contour':
                    img = img.filter(ImageFilter.CONTOUR)
                elif op == 'detail':
                    img = img.filter(ImageFilter.DETAIL)
                elif op == 'edge_enhance':
                    img = img.filter(ImageFilter.EDGE_ENHANCE)
                elif op == 'emboss':
                    img = img.filter(ImageFilter.EMBOSS)
                elif op == 'sharpen':
                    img = img.filter(ImageFilter.SHARPEN)
                elif op == 'smooth':
                    img = img.filter(ImageFilter.SMOOTH)
                elif op.startswith('brightness'):
                    factor = float(op.split(':')[1])
                    enhancer = ImageEnhance.Brightness(img)
                    img = enhancer.enhance(factor)
                elif op.startswith('contrast'):
                    factor = float(op.split(':')[1])
                    enhancer = ImageEnhance.Contrast(img)
                    img = enhancer.enhance(factor)
                elif op.startswith('color'):
                    factor = float(op.split(':')[1])
                    enhancer = ImageEnhance.Color(img)
                    img = enhancer.enhance(factor)
                elif op.startswith('resize'):
                    width, height = map(int, op.split(':')[1].split('x'))
                    img = img.resize((width, height), Image.LANCZOS)
                elif op.startswith('rotate'):
                    degrees = float(op.split(':')[1])
                    img = img.rotate(degrees, expand=True)
            
            # Convert back to original mode if needed
            if original_mode != 'RGB' and original_mode != img.mode:
                img = img.convert(original_mode)
            
            # Save edited image
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"edited_{os.path.basename(image_path)}"
            output_path = os.path.join(CONFIG['output_dir'], "edited", filename)
            
            img.save(output_path)
            return output_path
            
    except Exception as e:
        print(f"\033[1;31mError editing image: {str(e)}\033[0m")
        return None

def upscale_image(image_path, scale=2):
    """Upscale image using ESRGAN"""
    try:
        from ISR.models import RDN
        from ISR.models import RRDN
        
        # Load the model
        model = RDN(weights='noise-cancel')
        
        # Load and preprocess the image
        img = Image.open(image_path)
        lr_img = np.array(img)
        
        # Generate super-resolution version
        sr_img = model.predict(lr_img)
        
        # Convert back to PIL Image
        result = Image.fromarray(sr_img)
        
        # Save the result
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"upscaled_{os.path.basename(image_path)}"
        output_path = os.path.join(CONFIG['output_dir'], "upscaled", filename)
        
        result.save(output_path)
        return output_path
        
    except ImportError:
        print("\033[1;33mESRGAN not installed. Using simple resize instead.\033[0m")
        with Image.open(image_path) as img:
            width, height = img.size
            new_size = (width * scale, height * scale)
            img = img.resize(new_size, Image.LANCZOS)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"upscaled_{os.path.basename(image_path)}"
            output_path = os.path.join(CONFIG['output_dir'], "upscaled", filename)
            
            img.save(output_path)
            return output_path
            
    except Exception as e:
        print(f"\033[1;31mError upscaling image: {str(e)}\033[0m")
        return None

def show_image(image_path):
    """Display image using available viewer"""
    try:
        if IS_TERMUX:
            subprocess.run(["termux-open", image_path])
        elif IS_KALI:
            subprocess.run(["xdg-open", image_path])
        else:
            img = Image.open(image_path)
            img.show()
    except Exception as e:
        print(f"\033[1;31mError displaying image: {str(e)}\033[0m")

def main_menu():
    """Display main menu and handle user input"""
    while True:
        display_banner()
        print("\033[1;34mMain Menu:\033[0m")
        print("1. Generate Image from Text Prompt")
        print("2. Edit Existing Image")
        print("3. Upscale Image")
        print("4. Batch Process Images")
        print("5. Open Social Links")
        print("6. Exit")
        
        choice = input("\n\033[1;36mSelect an option (1-6): \033[0m")
        
        if choice == '1':
            text_to_image_menu()
        elif choice == '2':
            edit_image_menu()
        elif choice == '3':
            upscale_image_menu()
        elif choice == '4':
            batch_process_menu()
        elif choice == '5':
            open_social_links()
        elif choice == '6':
            print("\033[1;32mThank you for using Fazo-AI!\033[0m")
            sys.exit(0)
        else:
            print("\033[1;31mInvalid choice. Please try again.\033[0m")
            time.sleep(1)

def text_to_image_menu():
    """Menu for generating images from text prompts"""
    display_banner()
    print("\033[1;34mText to Image Generation\033[0m")
    
    prompt = input("\nEnter your prompt: ")
    if not prompt:
        print("\033[1;31mPrompt cannot be empty!\033[0m")
        time.sleep(1)
        return
    
    negative_prompt = input("Enter negative prompt (things to avoid, optional): ")
    width = input("Width (default 512): ") or "512"
    height = input("Height (default 512): ") or "512"
    
    try:
        width = int(width)
        height = int(height)
    except ValueError:
        print("\033[1;31mInvalid dimensions. Using default 512x512.\033[0m")
        width, height = 512, 512
    
    print("\n\033[1;33mGenerating image... Please wait.\033[0m")
    
    image_path = generate_image(
        prompt=prompt,
        negative_prompt=negative_prompt,
        width=width,
        height=height
    )
    
    if image_path:
        print(f"\033[1;32mImage generated successfully: {image_path}\033[0m")
        show_image(image_path)
    else:
        print("\033[1;31mFailed to generate image.\033[0m")
    
    input("\nPress Enter to continue...")

def edit_image_menu():
    """Menu for editing existing images"""
    display_banner()
    print("\033[1;34mImage Editing\033[0m")
    
    image_path = input("\nEnter path to image: ").strip()
    if not os.path.isfile(image_path):
        print("\033[1;31mFile not found!\033[0m")
        time.sleep(1)
        return
    
    print("\nAvailable editing operations:")
    print("1. Convert to Grayscale")
    print("2. Invert Colors")
    print("3. Mirror Image")
    print("4. Flip Image")
    print("5. Apply Blur")
    print("6. Apply Contour Effect")
    print("7. Enhance Details")
    print("8. Enhance Edges")
    print("9. Apply Emboss Effect")
    print("10. Sharpen Image")
    print("11. Smooth Image")
    print("12. Adjust Brightness")
    print("13. Adjust Contrast")
    print("14. Adjust Color")
    print("15. Resize Image")
    print("16. Rotate Image")
    
    choices = input("\nSelect operations (comma-separated, e.g., 1,3,5): ").strip().split(',')
    operations = []
    
    for choice in choices:
        choice = choice.strip()
        if choice == '1':
            operations.append('grayscale')
        elif choice == '2':
            operations.append('invert')
        elif choice == '3':
            operations.append('mirror')
        elif choice == '4':
            operations.append('flip')
        elif choice == '5':
            operations.append('blur')
        elif choice == '6':
            operations.append('contour')
        elif choice == '7':
            operations.append('detail')
        elif choice == '8':
            operations.append('edge_enhance')
        elif choice == '9':
            operations.append('emboss')
        elif choice == '10':
            operations.append('sharpen')
        elif choice == '11':
            operations.append('smooth')
        elif choice == '12':
            factor = input("Enter brightness factor (0.1-2.0, 1.0=normal): ") or "1.0"
            operations.append(f'brightness:{factor}')
        elif choice == '13':
            factor = input("Enter contrast factor (0.1-2.0, 1.0=normal): ") or "1.0"
            operations.append(f'contrast:{factor}')
        elif choice == '14':
            factor = input("Enter color factor (0.1-2.0, 1.0=normal): ") or "1.0"
            operations.append(f'color:{factor}')
        elif choice == '15':
            width = input("Enter new width: ")
            height = input("Enter new height: ")
            operations.append(f'resize:{width}x{height}')
        elif choice == '16':
            degrees = input("Enter rotation degrees: ") or "90"
            operations.append(f'rotate:{degrees}')
    
    print("\n\033[1;33mEditing image... Please wait.\033[0m")
    edited_path = edit_image(image_path, operations)
    
    if edited_path:
        print(f"\033[1;32mImage edited successfully: {edited_path}\033[0m")
        show_image(edited_path)
    else:
        print("\033[1;31mFailed to edit image.\033[0m")
    
    input("\nPress Enter to continue...")

def upscale_image_menu():
    """Menu for upscaling images"""
    display_banner()
    print("\033[1;34mImage Upscaling\033[0m")
    
    image_path = input("\nEnter path to image: ").strip()
    if not os.path.isfile(image_path):
        print("\033[1;31mFile not found!\033[0m")
        time.sleep(1)
        return
    
    scale = input("Enter scale factor (2-4, default 2): ") or "2"
    
    try:
        scale = int(scale)
        if scale < 2 or scale > 4:
            print("\033[1;31mScale must be between 2 and 4. Using 2.\033[0m")
            scale = 2
    except ValueError:
        print("\033[1;31mInvalid scale. Using 2.\033[0m")
        scale = 2
    
    print("\n\033[1;33mUpscaling image... Please wait.\033[0m")
    upscaled_path = upscale_image(image_path, scale)
    
    if upscaled_path:
        print(f"\033[1;32mImage upscaled successfully: {upscaled_path}\033[0m")
        show_image(upscaled_path)
    else:
        print("\033[1;31mFailed to upscale image.\033[0m")
    
    input("\nPress Enter to continue...")

def batch_process_menu():
    """Menu for batch processing images"""
    display_banner()
    print("\033[1;34mBatch Image Processing\033[0m")
    
    input_dir = input("\nEnter directory containing images: ").strip()
    if not os.path.isdir(input_dir):
        print("\033[1;31mDirectory not found!\033[0m")
        time.sleep(1)
        return
    
    print("\nAvailable batch operations:")
    print("1. Convert to Grayscale")
    print("2. Resize")
    print("3. Apply Watermark")
    print("4. Rename sequentially")
    
    choice = input("\nSelect operation: ").strip()
    
    if choice == '1':
        operations = ['grayscale']
    elif choice == '2':
        width = input("Enter new width: ")
        height = input("Enter new height: ")
        operations = [f'resize:{width}x{height}']
    elif choice == '3':
        watermark_path = input("Enter path to watermark image: ").strip()
        if not os.path.isfile(watermark_path):
            print("\033[1;31mWatermark image not found!\033[0m")
            time.sleep(1)
            return
        operations = [f'watermark:{watermark_path}']
    elif choice == '4':
        prefix = input("Enter filename prefix: ") or "image"
        operations = [f'rename:{prefix}']
    else:
        print("\033[1;31mInvalid choice.\033[0m")
        time.sleep(1)
        return
    
    print("\n\033[1;33mProcessing images... Please wait.\033[0m")
    
    processed_count = 0
    for filename in os.listdir(input_dir):
        try:
            filepath = os.path.join(input_dir, filename)
            if os.path.isfile(filepath) and filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                edited_path = edit_image(filepath, operations)
                if edited_path:
                    processed_count += 1
        except Exception as e:
            print(f"\033[1;31mError processing {filename}: {str(e)}\033[0m")
    
    print(f"\033[1;32mProcessed {processed_count} images successfully.\033[0m")
    input("\nPress Enter to continue...")

def open_social_links():
    """Open social media links in browser"""
    display_banner()
    print("\033[1;34mSocial Media Links\033[0m")
    
    print("\n1. Telegram")
    print("2. WhatsApp")
    print("3. YouTube")
    print("4. GitHub")
    print("5. Twitter")
    print("6. Back to Main Menu")
    
    choice = input("\nSelect platform to open (1-6): ").strip()
    
    if choice == '1':
        url = CONFIG['telegram_link']
    elif choice == '2':
        url = CONFIG['whatsapp_link']
    elif choice == '3':
        url = CONFIG['youtube_link']
    elif choice == '4':
        url = CONFIG['github_link']
    elif choice == '5':
        url = CONFIG['twitter_link']
    elif choice == '6':
        return
    else:
        print("\033[1;31mInvalid choice.\033[0m")
        time.sleep(1)
        return
    
    try:
        if IS_TERMUX:
            subprocess.run(["termux-open-url", url])
        elif IS_KALI:
            subprocess.run(["xdg-open", url])
        else:
            import webbrowser
            webbrowser.open(url)
    except Exception as e:
        print(f"\033[1;31mError opening link: {str(e)}\033[0m")
    
    input("\nPress Enter to continue...")

if __name__ == "__main__":
    # Initialize directories
    create_directory(CONFIG['output_dir'])
    create_directory(os.path.join(CONFIG['output_dir'], "generated"))
    create_directory(os.path.join(CONFIG['output_dir'], "edited"))
    create_directory(os.path.join(CONFIG['output_dir'], "upscaled"))
    
    # Check dependencies
    check_dependencies()
    
    # Start application
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\033[1;31mOperation cancelled by user.\033[0m")
        sys.exit(0)
    except Exception as e:
        print(f"\033[1;31mAn error occurred: {str(e)}\033[0m")
        sys.exit(1)
