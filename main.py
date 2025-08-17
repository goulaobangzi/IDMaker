#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main Workflow Script for ID Card Generation
Integrates photo cropping and ID card generation modules
"""

import os
import sys
import argparse
import re
import json
from pathlib import Path
from typing import List, Tuple, Optional
import shutil

# Import core modules
from crop_photo import PhotoCropper
from make_id import IDCardGenerator
from py_to_en import convert_chinese_name

class MainWorkflow:
    def __init__(self, config_file: str = "config.json"):
        """Initialize the main workflow with unified configuration file"""
        self.config_file = config_file
        self.config = self.load_unified_config()
        self.photo_cropper = None
        self.id_generator = None
        
        # Output directories will be set dynamically based on input path
        self.crop_dir = None
        self.id_dir = None
        
        # Statistics
        self.stats = {
            "total_photos": 0,
            "crop_success": 0,
            "crop_failed": 0,
            "id_success": 0,
            "id_failed": 0
        }
    
    def load_unified_config(self):
        """Load unified configuration file with fallback to defaults"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                print(f"✓ Loaded configuration from: {self.config_file}")
                return config
        except Exception as e:
            print(f"Warning: Could not load config file '{self.config_file}': {e}")
            print("Using default configuration")
            return self.get_default_config()
    
    def get_default_config(self):
        """Get default configuration when no config file is available"""
        return {
            "photo_cropping": {
                "output_dimensions": {"width": 360, "height": 450},
                "face_detection": {
                    "method": "dnn",
                    "confidence_threshold": 0.5,
                    "model_path": "dnn_models/res10_300x300_ssd_iter_140000.caffemodel",
                    "prototxt_path": "dnn_models/deploy.prototxt"
                },
                "quality": 95,
                "debug": False,
                "cropping_parameters": {
                    "target_head_ratio": 0.75,
                    "target_top_margin": 0.08,
                    "chin_extra_ratio": 0.12,
                    "hair_ratio": {
                        "base": 0.25,
                        "min": 0.15,
                        "max": 0.35,
                        "small_face_multiplier": 1.1,
                        "large_face_multiplier": 0.6,
                        "top_position_multiplier": 0.6,
                        "bottom_position_multiplier": 1.0
                    }
                }
            },
            "id_card_generation": {
                "template_directory": "id_template",
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
            },
            "name_conversion": {
                "pinyin_style": "normal",
                "name_format": "givenname_surname",
                "fallback_to_original": True
            },
            "main_workflow": {
                "default_template": "Student",
                "output_directories": {
                    "crop": "crop",
                    "id": "ID"
                },
                "supported_formats": [".jpg", ".jpeg", ".png", ".bmp"],
                "recursive_search": False,
                "auto_clean": False
            }
        }
    
    def initialize_modules(self) -> bool:
        """Initialize photo cropper and ID generator modules"""
        try:
            print("Initializing modules...")
            
            # Initialize photo cropper with unified config
            self.photo_cropper = PhotoCropper()
            # Merge photo cropper config with our unified config
            self.photo_cropper.config = self.photo_cropper._merge_config(
                self.photo_cropper.config, 
                self.config
            )
            if self.photo_cropper.face_detector is None:
                print("✗ Error: DNN face detection model not loaded!")
                print("Please check if the model files exist in dnn_models/ directory")
                return False
            
            # Initialize ID generator with unified config (but don't load template yet)
            self.id_generator = IDCardGenerator()
            # Merge ID generator config with our unified config
            self.id_generator.config = self.id_generator._merge_config(
                self.id_generator.config, 
                self.config
            )
            # Don't check template here - it will be loaded when user selects it
            
            print("✓ All modules initialized successfully!")
            return True
            
        except Exception as e:
            print(f"✗ Error initializing modules: {e}")
            return False
    
    def setup_directories(self, input_path: str, clean: bool = False):
        """Setup output directories based on input path, optionally cleaning them first"""
        # Determine output directories based on input path
        input_path_obj = Path(input_path.replace('\\', '/'))
        
        if input_path_obj.is_file():
            # Single file: create crop/ and ID/ in the same directory as the file
            base_dir = input_path_obj.parent
        elif input_path_obj.is_dir():
            # Directory: create crop/ and ID/ inside the input directory
            base_dir = input_path_obj
        else:
            # If input_path doesn't exist, use current directory
            base_dir = Path('.')
        
        # Set output directories
        self.crop_dir = base_dir / "crop"
        self.id_dir = base_dir / "ID"
        
        if clean:
            print("Removing output directories...")
            # Remove both the main directories and any subdirectories that might exist
            if self.crop_dir.exists():
                print(f"  Deleting directory: {self.crop_dir}")
                shutil.rmtree(self.crop_dir)
            if self.id_dir.exists():
                print(f"  Deleting directory: {self.id_dir}")
                shutil.rmtree(self.id_dir)
            
            # Also remove any crop/ and ID/ directories in current directory if we're not already targeting them
            if base_dir != Path('.'):
                current_crop = Path('.') / "crop"
                current_id = Path('.') / "ID"
                if current_crop.exists():
                    print(f"  Deleting directory: {current_crop}")
                    shutil.rmtree(current_crop)
                if current_id.exists():
                    print(f"  Deleting directory: {current_id}")
                    shutil.rmtree(current_id)
        
        # Create directories
        self.crop_dir.mkdir(exist_ok=True)
        self.id_dir.mkdir(exist_ok=True)
        print(f"✓ Output directories ready: {self.crop_dir}, {self.id_dir}")
    
    def get_output_directories_for_photo(self, photo_path: Path) -> Tuple[Path, Path]:
        """Get output directories for a specific photo based on its location"""
        # Get the directory containing the photo
        photo_dir = photo_path.parent
        
        # Create crop and ID directories in the same directory as the photo
        crop_dir = photo_dir / "crop"
        id_dir = photo_dir / "ID"
        
        # Create directories if they don't exist
        # Note: Directories should already exist from setup_directories if clean=True
        crop_dir.mkdir(exist_ok=True)
        id_dir.mkdir(exist_ok=True)
        
        return crop_dir, id_dir
    
    def is_chinese_filename(self, filename: str) -> bool:
        """Check if filename contains Chinese characters"""
        return any('\u4e00' <= ch <= '\u9fff' for ch in filename)
    
    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename by removing/replacing illegal characters"""
        # Remove Windows illegal characters: \ / : * ? " < > |
        illegal_chars = r'[\\/:*?"<>|]'
        sanitized = re.sub(illegal_chars, '_', filename)
        # Remove leading/trailing spaces and dots
        sanitized = sanitized.strip(' .')
        return sanitized if sanitized else "unnamed"
    
    def generate_unique_filename(self, base_name: str, extension: str = ".jpg") -> str:
        """Generate filename - will overwrite existing files"""
        return f"{base_name}{extension}"
    
    def find_photos(self, input_path: str, recursive: bool = False) -> List[Path]:
        """Find all photo files in the input path"""
        # Normalize path separators for cross-platform compatibility
        input_path = Path(input_path.replace('\\', '/'))
        photos = []
        
        # Define directories to exclude (program files and output directories)
        exclude_dirs = {'id_template', 'dnn_models', 'crop', 'ID'}
        
        if input_path.is_file():
            # Single file
            if self.is_photo_file(input_path):
                photos.append(input_path)
        elif input_path.is_dir():
            # Directory
            if recursive:
                # Recursive search with exclusion
                for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp']:
                    for photo_path in input_path.rglob(ext):
                        # Check if photo is in excluded directory
                        if not any(exclude_dir in photo_path.parts for exclude_dir in exclude_dirs):
                            photos.append(photo_path)
            else:
                # Non-recursive search
                for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp']:
                    photos.extend(input_path.glob(ext))
        else:
            # If input_path doesn't exist, try current directory
            print(f"Input path '{input_path}' not found, searching current directory...")
            current_dir = Path('.')
            if recursive:
                # Recursive search in current directory with exclusion
                for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp']:
                    for photo_path in current_dir.rglob(ext):
                        # Check if photo is in excluded directory
                        if not any(exclude_dir in photo_path.parts for exclude_dir in exclude_dirs):
                            photos.append(photo_path)
            else:
                # Non-recursive search in current directory
                for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp']:
                    photos.extend(current_dir.glob(ext))
        
        # Sort photos for consistent processing order
        photos.sort()
        return photos
    
    def is_photo_file(self, file_path: Path) -> bool:
        """Check if file is a supported photo format"""
        return file_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp']
    
    def process_photo_cropping(self, photo_path: Path) -> Optional[Path]:
        """Process single photo cropping"""
        try:
            # Get output directories for this specific photo
            crop_dir, id_dir = self.get_output_directories_for_photo(photo_path)
            
            # Determine output filename
            stem = photo_path.stem
            if self.is_chinese_filename(stem):
                # Convert Chinese name to English with config
                english_name = convert_chinese_name(stem, self.config)
                if english_name:
                    stem = english_name
                    print(f"  Converted '{photo_path.stem}' → '{english_name}'")
                else:
                    print(f"  Warning: Could not convert Chinese name '{photo_path.stem}'")
            
            # Sanitize filename
            clean_stem = self.sanitize_filename(stem)
            output_filename = self.generate_unique_filename(clean_stem)
            output_path = crop_dir / output_filename
            
            # Crop photo (silent success, only show failures)
            success = self.photo_cropper.crop_photo(photo_path, output_path)
            
            if success:
                return output_path
            else:
                print(f"  ✗ Cropping failed: {photo_path.name}")
                return None
                
        except Exception as e:
            print(f"  ✗ Error processing {photo_path.name}: {e}")
            return None
    
    def process_id_generation(self, cropped_photo_path: Path, template: str) -> bool:
        """Process single ID card generation"""
        try:
            # Get output directories for this specific photo (use original photo path)
            # We need to find the original photo path from the cropped photo path
            # The cropped photo is in a crop/ subdirectory, so we go up one level
            original_photo_dir = cropped_photo_path.parent.parent
            id_dir = original_photo_dir / "ID"
            id_dir.mkdir(exist_ok=True)
            
            # Generate ID card filename
            stem = cropped_photo_path.stem
            output_filename = f"{template}_{stem}.jpg"
            output_path = id_dir / output_filename
            
            # Generate ID card (silent success, only show failures)
            # Template should already be loaded
            
            # Create ID card
            success = self.id_generator.create_id_card(cropped_photo_path, stem, template_type=template)
            if success is not None:
                # Save ID card
                self.id_generator.save_id_card(success, output_path)
                return True
            else:
                print(f"  ✗ ID card generation failed: {cropped_photo_path.name}")
                return False
                
        except Exception as e:
            import traceback
            print(f"  ✗ Error generating ID card for {cropped_photo_path.name}: {e}")
            print(f"  Error details: {traceback.format_exc()}")
            return False
    
    def run_workflow(self, input_path: str, template: str = "Student", 
                    no_recursive: bool = False, clean: bool = False, verbose: bool = False, auto: bool = False, withparent: bool = False) -> int:
        """Run the complete workflow"""
        print("=" * 60)
        print("ID Card Generation Workflow")
        print("=" * 60)
        
        # Setup
        if not self.initialize_modules():
            return 2  # Model loading failed
        
        # Find photos first - default to recursive search
        recursive = not no_recursive
        photos = self.find_photos(input_path, recursive)
        if not photos:
            print("✗ No photo files found")
            print("Searched in:", input_path if input_path != "." else "current directory")
            if not recursive:
                print("Search was non-recursive. Use --no-recursive (-n) to disable recursive search.")
            return 1  # No photos found
        
        # Setup directories only after finding photos
        self.setup_directories(input_path, clean)
        
        self.stats["total_photos"] = len(photos)
        print(f"\nFound {len(photos)} photo(s) to process")
        
        # Phase 1: Photo Cropping
        print(f"\n{'='*20} PHASE 1: PHOTO CROPPING {'='*20}")
        
        # Warning and confirmation before cropping
        if not auto:
            # ANSI color codes for Windows and Unix
            RED = '\033[91m'
            YELLOW = '\033[93m'
            BOLD = '\033[1m'
            UNDERLINE = '\033[4m'
            RESET = '\033[0m'
            
            print(f"\n{RED}{BOLD}{'='*20} ⚠️  IMPORTANT NAMING REQUIREMENT ⚠️  {'='*20}{RESET}")
            print(f"{YELLOW}{BOLD}Before proceeding with photo cropping, please ensure:{RESET}")
            print(f"{YELLOW}• Photos are named with {BOLD}FIRST NAME{RESET}{YELLOW}, {BOLD}SPACE{RESET}{YELLOW}, {BOLD}LAST NAME{RESET}{YELLOW} (e.g., 'John Smith.jpg')")
            print(f"• For Chinese names, use {BOLD}normal Chinese characters{RESET}{YELLOW} (e.g., '张三.jpg')")
            print(f"• The system will automatically convert Chinese names to Pinyin{RESET}")
            print(f"{RED}{BOLD}{'='*20} ⚠️  IMPORTANT NAMING REQUIREMENT ⚠️  {'='*20}{RESET}")
            
            while True:
                response = input("Are your photos properly named and ready for cropping? (y/n): ").lower().strip()
                if response in ['y', 'yes']:
                    print("✓ Starting photo cropping process...")
                    break
                elif response in ['n', 'no']:
                    print("✗ Please prepare your photos with proper naming first.")
                    print("Workflow will exit. Please run again when ready.")
                    return 1  # Exit with error code
                else:
                    print("Please enter 'y' for yes or 'n' for no.")
        else:
            print("✓ Auto mode: Skipping naming requirement confirmation")
            print("✓ Starting photo cropping process...")
        
        cropped_photos = []
        failed_crops = []
        
        if verbose:
            # Verbose mode: show each file processing
            for i, photo_path in enumerate(photos, 1):
                print(f"\r[{i}/{len(photos)}] Processing: {photo_path.name}...", end="", flush=True)
                
                cropped_path = self.process_photo_cropping(photo_path)
                if cropped_path:
                    cropped_photos.append(cropped_path)
                    self.stats["crop_success"] += 1
                    print(" ✓")
                else:
                    failed_crops.append(photo_path)
                    self.stats["crop_failed"] += 1
                    print(" ✗")
            print()  # New line after progress
        else:
            # Normal mode: show progress bar
            print("Processing photos: ", end="", flush=True)
            for i, photo_path in enumerate(photos, 1):
                # Show progress bar
                progress = int((i / len(photos)) * 40)
                bar = "█" * progress + "░" * (40 - progress)
                print(f"\rProcessing photos: [{bar}] {i}/{len(photos)}", end="", flush=True)
                
                cropped_path = self.process_photo_cropping(photo_path)
                if cropped_path:
                    cropped_photos.append(cropped_path)
                    self.stats["crop_success"] += 1
                else:
                    failed_crops.append(photo_path)
                    self.stats["crop_failed"] += 1
                    # Show failure immediately
                    print(f"\n✗ Failed to crop: {photo_path.name}")
            
            print()  # New line after progress
        
        # Check cropping results
        if self.stats["crop_success"] == 0:
            print(f"\n✗ All {self.stats['total_photos']} photos failed cropping")
            return 3  # All cropping failed
        
        print(f"\n✓ Cropping completed: {self.stats['crop_success']}/{self.stats['total_photos']} successful")
        
        # User review of cropped photos
        if not auto:
            print(f"\n{'='*20} USER REVIEW {'='*20}")
            print(f"Please check the cropped photos in: {self.crop_dir}")
            print("Review the cropping results and ensure they meet your requirements.")
            input("Press Enter to continue to ID card generation...")
        else:
            print(f"\n✓ Auto mode: Skipping user review of cropped photos")
        
        # Phase 2: ID Card Generation
        print(f"\n{'='*20} PHASE 2: ID CARD GENERATION {'='*20}")
        
        # Ask user to select template
        if not auto:
            selected_template = self.select_template()
            if not selected_template:
                print("✗ No template selected. Exiting.")
                return 5  # Template selection failed
            print(f"Selected template: {selected_template}")
        else:
            # Auto mode: use template from command line arguments
            selected_template = template
            print(f"✓ Auto mode: Using template: {selected_template}")
        
        # Generate ID cards with selected template
        failed_ids = []
        
        # Load template once before processing
        self.id_generator.load_template(selected_template)
        if self.id_generator.template is None:
            print(f"✗ Failed to load template: {selected_template}")
            return 5  # Template loading failed
        
        if verbose:
            # Verbose mode: show each file processing
            for i, cropped_photo in enumerate(cropped_photos, 1):
                print(f"\r[{i}/{len(cropped_photos)}] Generating ID card for: {cropped_photo.name}...", end="", flush=True)
                
                success = self.process_id_generation(cropped_photo, selected_template)
                if success:
                    self.stats["id_success"] += 1
                    print(" ✓")
                else:
                    failed_ids.append(cropped_photo)
                    self.stats["id_failed"] += 1
                    print(" ✗")
            print()  # New line after progress
        else:
            # Normal mode: show progress bar
            print("Generating ID cards: ", end="", flush=True)
            for i, cropped_photo in enumerate(cropped_photos, 1):
                # Show progress bar
                progress = int((i / len(cropped_photos)) * 40)
                bar = "█" * progress + "░" * (40 - progress)
                print(f"\rGenerating ID cards: [{bar}] {i}/{len(cropped_photos)}", end="", flush=True)
                
                success = self.process_id_generation(cropped_photo, selected_template)
                if success:
                    self.stats["id_success"] += 1
                else:
                    failed_ids.append(cropped_photo)
                    self.stats["id_failed"] += 1
                    # Show failure immediately
                    print(f"\n✗ Failed to generate ID: {cropped_photo.name}")
            
            print()  # New line after progress
        
        # Ask if user wants to generate parent cards
        if selected_template.lower() == "student":
            if not auto:
                generate_parent = self.ask_generate_parent()
            else:
                # Auto mode: generate parent cards only if --withparent is specified
                generate_parent = withparent
                if withparent:
                    print("✓ Auto mode: Will generate Parent ID cards for students")
                else:
                    print("✓ Auto mode: Skipping Parent ID card generation (use --withparent to enable)")
            
            if generate_parent:
                print(f"\n{'='*20} GENERATING PARENT ID CARDS {'='*20}")
                parent_success = 0
                failed_parents = []
                
                # Load Parent template before processing
                self.id_generator.load_template("Parent")
                if self.id_generator.template is None:
                    print(f"✗ Failed to load Parent template")
                    print("Skipping Parent ID card generation")
                else:
                    print("✓ Parent template loaded successfully!")
                    
                    if verbose:
                        # Verbose mode: show each file processing
                        for i, cropped_photo in enumerate(cropped_photos, 1):
                            print(f"\r[{i}/{len(cropped_photos)}] Generating Parent ID card for: {cropped_photo.name}...", end="", flush=True)
                            
                            success = self.process_id_generation(cropped_photo, "Parent")
                            if success:
                                parent_success += 1
                                print(" ✓")
                            else:
                                failed_parents.append(cropped_photo)
                                print(" ✗")
                        
                        print()  # New line after progress
                    else:
                        # Normal mode: show progress bar
                        print("Generating Parent ID cards: ", end="", flush=True)
                        for i, cropped_photo in enumerate(cropped_photos, 1):
                            # Show progress bar
                            progress = int((i / len(cropped_photos)) * 40)
                            bar = "█" * progress + "░" * (40 - progress)
                            print(f"\rGenerating Parent ID cards: [{bar}] {i}/{len(cropped_photos)}", end="", flush=True)
                            
                            success = self.process_id_generation(cropped_photo, "Parent")
                            if success:
                                parent_success += 1
                            else:
                                failed_parents.append(cropped_photo)
                                # Show failure immediately
                                print(f"\n✗ Failed to generate Parent ID: {cropped_photo.name}")
                        
                        print()  # New line after progress
                    
                    print(f"✓ Parent ID cards generated: {parent_success}/{len(cropped_photos)}")
        
        # Final summary
        print(f"\n{'='*20} WORKFLOW SUMMARY {'='*20}")
        print(f"Total photos processed: {self.stats['total_photos']}")
        print(f"Photos cropped successfully: {self.stats['crop_success']}")
        print(f"Photos cropped failed: {self.stats['crop_failed']}")
        print(f"ID cards generated successfully: {self.stats['id_success']}")
        print(f"ID cards generation failed: {self.stats['id_failed']}")
        print(f"Output directories: {self.crop_dir}, {self.id_dir}")
        
        # Show failed files for manual processing
        if failed_crops:
            print(f"\n{'='*20} FAILED CROPS - MANUAL PROCESSING NEEDED {'='*20}")
            for i, failed_photo in enumerate(failed_crops, 1):
                print(f"{i}. {failed_photo}")
        
        if failed_ids:
            print(f"\n{'='*20} FAILED ID GENERATIONS - MANUAL PROCESSING NEEDED {'='*20}")
            for i, failed_photo in enumerate(failed_ids, 1):
                print(f"{i}. {failed_photo}")
        
        if 'failed_parents' in locals() and failed_parents:
            print(f"\n{'='*20} FAILED PARENT ID GENERATIONS - MANUAL PROCESSING NEEDED {'='*20}")
            for i, failed_photo in enumerate(failed_parents, 1):
                print(f"{i}. {failed_photo}")
        
        if self.stats["id_success"] == 0:
            print(f"\n✗ All ID card generation failed")
            return 4  # ID generation failed
        
        print(f"\n✓ Workflow completed successfully!")
        return 0  # Success
    
    def select_template(self) -> str:
        """Let user select ID card template"""
        print("\nPlease select ID card template:")
        print("1. Student")
        print("2. Staff") 
        print("3. Contractor")
        print("4. Resident")
        
        while True:
            try:
                choice = input("Enter your choice (1-4): ").strip()
                if choice == "1":
                    return "Student"
                elif choice == "2":
                    return "Staff"
                elif choice == "3":
                    return "Contractor"
                elif choice == "4":
                    return "Resident"
                else:
                    print("Invalid choice. Please enter 1, 2, 3, or 4.")
            except KeyboardInterrupt:
                print("\nOperation cancelled by user.")
                return None
            except Exception as e:
                print(f"Error: {e}")
                return None
    
    def ask_generate_parent(self) -> bool:
        """Ask user if they want to generate parent ID cards"""
        print("\nDo you want to generate Parent ID cards as well?")
        print("(This is useful when processing student photos)")
        
        while True:
            try:
                response = input("Generate Parent ID cards? (y/n): ").strip().lower()
                if response in ['y', 'yes', '是']:
                    return True
                elif response in ['n', 'no', '否']:
                    return False
                else:
                    print("Please enter 'y' for yes or 'n' for no.")
            except KeyboardInterrupt:
                print("\nOperation cancelled by user.")
                return False
            except Exception as e:
                print(f"Error: {e}")
                return False

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="ID Card Generation Workflow - Integrates photo cropping and ID card generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                                    # Process current directory
  python main.py --input "photos/"                  # Process photos directory
  python main.py --input "photos/" --template Staff # With Staff template
  python main.py --input "photo.jpg" --clean       # Single file with clean
  python main.py --input "photos/" --auto          # Auto mode, skip all prompts
  python main.py --input "photos/" --auto --template Staff      # Auto mode with Staff template
  python main.py --input "photos/" --auto --template Student --withparent  # Auto mode with Parent cards
        """
    )
    
    parser.add_argument(
        "--input",
        default=".",
        help="Input directory or file (default: current directory)"
    )
    
    parser.add_argument(
        "--no-recursive",
        action="store_true",
        help="Disable recursive search (default: recursive search enabled)"
    )
    
    parser.add_argument(
        "--template",
        default="Student",
        choices=["Student", "Staff", "Parent", "Resident", "Contractor"],
        help="ID card template (default: Student) - Note: Will be overridden by interactive selection"
    )
    
    parser.add_argument(
        "--config",
        default="config.json",
        help="Unified configuration file (default: config.json)"
    )
    
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Delete existing crop/ and ID/ directories before processing"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output - show detailed processing information"
    )
    
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Auto mode - skip all interactive prompts and generate ID cards directly"
    )
    
    parser.add_argument(
        "--withparent",
        action="store_true",
        help="Generate Parent ID cards when using Student template (auto mode only)"
    )
    
    args = parser.parse_args()
    
    # Create and run workflow
    workflow = MainWorkflow(args.config)
    exit_code = workflow.run_workflow(
        input_path=args.input,
        template=args.template,
        no_recursive=args.no_recursive,
        clean=args.clean,
        verbose=args.verbose,
        auto=args.auto,
        withparent=args.withparent
    )
    
    # Don't auto-close window, wait for user input
    if exit_code == 0:
        print(f"\n{'='*60}")
        print("✓ Workflow completed successfully!")
        if not args.auto:
            print("Press Enter to close the window...")
        else:
            print("Auto mode: Window will close automatically...")
    else:
        print(f"\n{'='*60}")
        print("✗ Workflow completed with errors!")
        if not args.auto:
            print("Press Enter to close the window...")
        else:
            print("Auto mode: Window will close automatically...")
    
    if not args.auto:
        try:
            input()
        except KeyboardInterrupt:
            print("\nWindow closing...")
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main() 