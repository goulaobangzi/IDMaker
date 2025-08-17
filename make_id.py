#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ID Card Generator
Generate ID cards with photos and text
"""

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import json
import os
import argparse
from py_to_en import convert_chinese_name
import sys

class IDCardGenerator:
    def __init__(self, config_file="config.json"):
        if isinstance(config_file, dict):
            # Direct config dictionary provided
            self.config = config_file
        else:
            # Config file path provided
            self.config = self.load_config(config_file)
        self.template = None
        self.font = None
        self.load_template()
        self.load_font()
    
    def load_config(self, config_file):
        """Load configuration from JSON file"""
        # Default configuration
        default_config = {
            "id_card_generation": {
                "template_directory": "id_template",
                "output_directory": "output_id_cards",
                "templates": {
                    "contractor": "Contractor.png",
                    "resident": "Resident.png",
                    "staff": "Staff.png",
                    "student": "Student.png",
                    "parent": "Parent.png"
                },
                "photo_position": {"x": 175, "y": 659, "width": 288, "height": 350},
                "text_position": {
                    "name_origin": [175, 1040],
                    "max_width": 450,
                    "font_size": 42,
                    "line_spacing": 16
                },
                "font": {"path": "font.otf", "color": [17, 26, 65]},
                "output_format": "jpg",
                "quality": 95
            }
        }
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                # Deep merge user config with default config
                return self._merge_config(default_config, user_config)
        except Exception as e:
            print(f"Warning: Could not load config file '{config_file}': {e}")
            print("Using default configuration")
            return default_config
    
    def _merge_config(self, default_config, user_config):
        """Deep merge user config with default config"""
        if not isinstance(user_config, dict):
            return default_config
        
        result = default_config.copy()
        for key, value in user_config.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        return result
    
    def load_template(self, template_name="Student"):
        """Load ID card template"""
        try:
            gen_cfg = self.config.get("id_card_generation", {})
            template_dir = gen_cfg.get("template_directory", "id_template")
            # Support template mapping if provided
            templates_map = gen_cfg.get("templates", {})
            mapped = templates_map.get(template_name.lower()) if isinstance(template_name, str) else None
            template_file = mapped if mapped else f"{template_name}.png"
            
            # Handle PyInstaller bundled files
            if hasattr(sys, '_MEIPASS'):
                # Running from PyInstaller bundle
                base_path = Path(sys._MEIPASS)
                template_path = base_path / template_dir / template_file
            else:
                # Running from source
                template_path = Path(template_dir) / template_file
            
            if template_path.exists():
                pil_image = Image.open(str(template_path))
                pil_image = pil_image.convert('RGB')
                template_array = np.array(pil_image)
                self.template = cv2.cvtColor(template_array, cv2.COLOR_RGB2BGR)
                print(f"✓ Template '{template_name}' loaded successfully!")
            else:
                print(f"✗ Template not found: {template_path}")
                # List available templates
                if hasattr(sys, '_MEIPASS'):
                    base_path = Path(sys._MEIPASS)
                    template_dir_path = base_path / template_dir
                else:
                    template_dir_path = Path(template_dir)
                
                if template_dir_path.exists():
                    template_files = list(template_dir_path.glob("*.png"))
                    if template_files:
                        print(f"Available templates: {[f.stem for f in template_files]}")
        except Exception as e:
            print(f"Error loading template: {e}")
    
    def load_font(self):
        """Load font for text rendering"""
        try:
            gen_cfg = self.config.get("id_card_generation", {})
            font_path = gen_cfg.get("font", {}).get("path", "font.otf")
            # Use text_position.font_size for consistency with main app
            font_size = gen_cfg.get("text_position", {}).get("font_size", 42)
            
            # Handle PyInstaller bundled files
            if hasattr(sys, '_MEIPASS'):
                # Running from PyInstaller bundle
                base_path = Path(sys._MEIPASS)
                font_path = base_path / font_path
            else:
                font_path = Path(font_path)
            
            if os.path.exists(font_path):
                self.font = ImageFont.truetype(str(font_path), font_size)
                print("✓ Font loaded successfully!")
            else:
                print(f"✗ Font not found: {font_path}")
                # Try common fallback in project root
                fallback = "font.otf"
                if hasattr(sys, '_MEIPASS'):
                    fallback_path = base_path / fallback
                else:
                    fallback_path = Path(fallback)
                
                if os.path.exists(fallback_path):
                    self.font = ImageFont.truetype(str(fallback_path), font_size)
                    print("✓ Font loaded from project root!")
                else:
                    print("✗ No font file found, using default font")
                    self.font = ImageFont.load_default()
        except Exception as e:
            print(f"Error loading font: {e}")
            # Fallback to default font
            try:
                self.font = ImageFont.load_default()
                print("✓ Using default font as fallback")
            except Exception as e2:
                print(f"Error loading default font: {e2}")
    
    def get_template_path(self, template_name):
        """Get path to template by name"""
        template_dir = self.config["id_card_generation"]["template_directory"]
        template_path = Path(template_dir) / f"{template_name}.png"
        return template_path
    
    def create_id_card(self, photo_path, name, title="Student", id_number="", template_type="Student"):
        """Create ID card with photo and name text"""
        if self.template is None:
            print("✗ Template not loaded")
            return None
        if self.font is None:
            print("✗ Font not loaded")
            return None
        
        try:
            # Load photo
            photo = cv2.imread(str(photo_path))
            if photo is None:
                print(f"✗ Could not load photo: {photo_path}")
                return None
            
            gen_cfg = self.config.get("id_card_generation", {})
            photo_pos = gen_cfg.get("photo_position", {"x": 175, "y": 659, "width": 288, "height": 350})
            text_pos = gen_cfg.get("text_position", {})
            font_color = tuple(gen_cfg.get("font", {}).get("color", [17, 26, 65]))
            
            # Create result canvas from template
            result = self.template.copy()
            
            # Resize and place photo
            photo_resized = cv2.resize(photo, (photo_pos["width"], photo_pos["height"]))
            y1 = int(photo_pos["y"])
            y2 = int(photo_pos["y"] + photo_pos["height"])
            x1 = int(photo_pos["x"])
            x2 = int(photo_pos["x"] + photo_pos["width"])
            result[y1:y2, x1:x2] = photo_resized
            
            # Convert to PIL for text rendering
            result_rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(result_rgb)
            draw = ImageDraw.Draw(pil_image)
            
            # Process name (Chinese -> Pinyin GivenName Surname)
            is_chinese = any('\u4e00' <= ch <= '\u9fff' for ch in str(name))
            display_name = convert_chinese_name(name) if is_chinese else name
            
            # Wrap text
            start_x, start_y = text_pos.get("name_origin", [175, 1040])
            max_width = text_pos.get("max_width", 450)
            line_spacing = text_pos.get("line_spacing", 16)
            font_size = text_pos.get("font_size", 42)
            
            # Ensure font size reflects config if default font was used earlier
            if isinstance(self.font, ImageFont.FreeTypeFont):
                active_font = self.font
            else:
                active_font = ImageFont.load_default()
            
            lines = self.wrap_text(display_name, max_width, active_font)
            y_offset = start_y
            for line in lines:
                draw.text((start_x, y_offset), line, font=active_font, fill=font_color)
                y_offset += font_size + line_spacing
            
            # Back to OpenCV
            result_bgr = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            if result_bgr is not None and result_bgr.size > 0:
                return result_bgr
            else:
                print("✗ Failed to create ID card image")
                return None
        except Exception as e:
            import traceback
            print(f"Error creating ID card: {e}")
            print(f"Error details: {traceback.format_exc()}")
            return None
    
    def wrap_text(self, text, max_width, font):
        """Wrap text to fit within max_width using provided font"""
        words = text.split()
        lines = []
        current_line = ""
        for word in words:
            candidate = (current_line + " " + word).strip() if current_line else word
            try:
                bbox = font.getbbox(candidate)
                width = bbox[2] - bbox[0]
            except Exception:
                width = font.getsize(candidate)[0]
            if width <= max_width:
                current_line = candidate
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        return lines if lines else [text]
    
    def save_id_card(self, id_card, output_path):
        """Save ID card to file"""
        try:
            # Determine format and quality from config
            gen_cfg = self.config.get("id_card_generation", {})
            fmt = gen_cfg.get("output_format", "jpg").lower()
            quality = int(gen_cfg.get("quality", 95))
            output_path = Path(output_path)
            if output_path.suffix.lower() != f".{fmt}":
                output_path = output_path.with_suffix(f".{fmt}")
            
            if fmt in ("jpg", "jpeg"):
                cv2.imwrite(str(output_path), id_card, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
            else:
                cv2.imwrite(str(output_path), id_card)
            return True
        except Exception as e:
            print(f"Error saving ID card: {e}")
            return False
    
    def batch_generate(self, photo_dir, output_dir, template_type="Student"):
        """Batch generate ID cards from photos"""
        photo_path = Path(photo_dir)
        gen_cfg = self.config.get("id_card_generation", {})
        output_path = Path(output_dir) if output_dir else Path(gen_cfg.get("output_directory", "output_id_cards"))
        
        if not photo_path.exists():
            print(f"✗ Photo directory not found: {photo_dir}")
            return False
        
        output_path.mkdir(exist_ok=True)
        
        # Load template for requested type
        self.load_template(template_type)
        if self.template is None:
            return False
        
        # Gather photos
        exts = {".jpg", ".jpeg", ".png", ".bmp"}
        photo_files = [p for p in photo_path.glob("*") if p.suffix.lower() in exts]
        if not photo_files:
            print(f"✗ No photos found in {photo_dir}")
            return False
        
        print(f"Found {len(photo_files)} photos to process")
        success_count = 0
        for photo_file in photo_files:
            name = photo_file.stem
            # Convert Chinese to English if needed
            if any('\u4e00' <= ch <= '\u9fff' for ch in name):
                cn = convert_chinese_name(name)
                if cn:
                    name = cn
            
            id_card = self.create_id_card(photo_file, name, template_type=template_type)
            if id_card is not None:
                output_filename = f"{template_type.title()}_{name}"
                out_file = output_path / output_filename
                if self.save_id_card(id_card, out_file):
                    print(f"✓ Generated: {out_file.name}")
                    success_count += 1
                else:
                    print(f"✗ Failed to save: {output_filename}")
            else:
                print(f"✗ Failed to generate ID card for: {photo_file.name}")
        
        print(f"\nBatch generation completed!")
        print(f"Successfully generated: {success_count}/{len(photo_files)}")
        print(f"Output directory: {output_path}")
        return success_count > 0

def main():
    parser = argparse.ArgumentParser(description="ID Card Generator")
    parser.add_argument("--photo-dir", "-p", default="cropped_photo", help="Photo directory (default: cropped_photo)")
    parser.add_argument("--output-dir", "-o", default="output_id_cards", help="Output directory")
    parser.add_argument("--template", "-t", default="Student", help="Template type (Student, Staff, Parent, etc.)")
    parser.add_argument("--config", "-c", default="config.json", help="Configuration file")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("ID CARD GENERATOR")
    print("=" * 60)
    
    generator = IDCardGenerator(args.config)
    
    if generator.template is None or generator.font is None:
        print("✗ Required resources not loaded. Exiting.")
        return
    
    # Generate ID cards
    success = generator.batch_generate(args.photo_dir, args.output_dir, args.template)
    if success:
        print("\n✓ ID card generation completed successfully!")
    else:
        print("\n✗ ID card generation failed!")

if __name__ == "__main__":
    main() 