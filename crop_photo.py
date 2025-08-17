#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Photo Cropping Tool - Optimized Version
Automatically crop photos to target dimensions while preserving aspect ratio
"""

import cv2
import numpy as np
from pathlib import Path
import os
import json
import argparse
import sys

class PhotoCropper:
    def __init__(self, config_file="config.json"):
        if isinstance(config_file, dict):
            # Direct config dictionary provided
            self.config = config_file
        else:
            # Config file path provided
            self.config = self.load_config(config_file)
        self.face_detector = None
        self.load_model()
    
    def load_config(self, config_file):
        """Load configuration from JSON file with smart defaults"""
        # Default configuration
        default_config = {
            "photo_cropping": {
                "input_directories": ["."],
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
    
    def load_model(self):
        """Load face detection model"""
        try:
            if self.config["photo_cropping"]["face_detection"]["method"] == "dnn":
                model_path = self.config["photo_cropping"]["face_detection"]["model_path"]
                prototxt_path = self.config["photo_cropping"]["face_detection"]["prototxt_path"]
                
                # Handle PyInstaller bundled files
                if hasattr(sys, '_MEIPASS'):
                    # Running from PyInstaller bundle
                    base_path = Path(sys._MEIPASS)
                    model_path = base_path / model_path
                    prototxt_path = base_path / prototxt_path
                else:
                    # Running from source
                    model_path = Path(model_path)
                    prototxt_path = Path(prototxt_path)
                
                if os.path.exists(model_path) and os.path.exists(prototxt_path):
                    self.face_detector = cv2.dnn.readNet(str(model_path), str(prototxt_path))
                    print("✓ DNN face detector loaded successfully!")
                else:
                    print(f"✗ DNN model files not found")
                    print(f"  Model: {model_path}")
                    print(f"  Prototxt: {prototxt_path}")
            else:
                print("✗ Unsupported face detection method")
        except Exception as e:
            print(f"Error loading model: {e}")
    
    def detect_face(self, image):
        """Detect best face and return (x, y, w, h)."""
        if self.face_detector is None:
            return None

        try:
            H, W = image.shape[:2]
            blob = cv2.dnn.blobFromImage(image, 1.0, (300, 300),
                                         (104.0, 177.0, 123.0),
                                         swapRB=False, crop=False)
            self.face_detector.setInput(blob)
            det = self.face_detector.forward()

            th = float(self.config["photo_cropping"]["face_detection"].get("confidence_threshold", 0.5))

            candidates = []
            for i in range(det.shape[2]):
                conf = float(det[0, 0, i, 2])
                if conf < th:
                    continue

                # x1,y1,x2,y2 (normalized to 0~1), map back to pixels
                x1, y1, x2, y2 = det[0, 0, i, 3:7] * np.array([W, H, W, H])
                x1 = int(max(0, min(W - 1, x1)))
                y1 = int(max(0, min(H - 1, y1)))
                x2 = int(max(0, min(W - 1, x2)))
                y2 = int(max(0, min(H - 1, y2)))
                w = max(1, x2 - x1)
                h = max(1, y2 - y1)

                # Basic filtering: area and aspect ratio
                area = (w * h) / float(W * H)
                if area < 0.005 or area > 0.9:  # 0.5% to 90%
                    continue
                ar = w / float(h)
                if ar < 0.3 or ar > 2.5:  # 0.3 to 2.5
                    continue

                # Simplified filtering: keep reasonable detections
                candidates.append((conf, (x1, y1, w, h)))

            if not candidates:
                return None

            # Select highest confidence detection
            candidates.sort(key=lambda t: t[0], reverse=True)
            return candidates[0][1]

        except Exception as e:
            print(f"Error in face detection: {e}")
            return None
    
    def estimate_head_top(self, face_y: int, face_h: int, image_h: int, face_cy: int) -> float:
        """Estimate head top position with adaptive adjustment"""
        # Get hair ratio parameters from config
        hair_cfg = self.config["photo_cropping"]["cropping_parameters"]["hair_ratio"]
        base_hair_ratio = hair_cfg["base"]
        min_hair_ratio = hair_cfg["min"]
        max_hair_ratio = hair_cfg["max"]
        small_face_mult = hair_cfg["small_face_multiplier"]
        large_face_mult = hair_cfg["large_face_multiplier"]
        top_pos_mult = hair_cfg["top_position_multiplier"]
        bottom_pos_mult = hair_cfg["bottom_position_multiplier"]
        
        # Adjust based on face position in image
        face_position_ratio = face_cy / image_h
        
        # Adjust based on face size
        face_size_ratio = face_h / image_h
        
        if face_size_ratio < 0.3:
            # Small face, likely distant view
            hair_ratio = base_hair_ratio * small_face_mult
        elif face_size_ratio > 0.6:
            # Large face, likely close view
            hair_ratio = base_hair_ratio * large_face_mult
        else:
            # Standard size, adjust by position
            if face_position_ratio < 0.4:
                # Face near top, reduce hair height
                hair_ratio = base_hair_ratio * top_pos_mult
            elif face_position_ratio > 0.7:
                # Face near bottom, increase hair height
                hair_ratio = base_hair_ratio * bottom_pos_mult
            else:
                # Face centered, use standard ratio
                hair_ratio = base_hair_ratio
        
        # Limit hair ratio range
        hair_ratio = max(min_hair_ratio, min(hair_ratio, max_hair_ratio))
        
        head_top = face_y - hair_ratio * face_h
        
        # Safety check: if pushed too high, use conservative value
        if head_top < 0:
            conservative_ratio = min(0.2, face_h / image_h * 0.6)
            head_top = face_y - conservative_ratio * face_h
            head_top = max(0.0, head_top)
        
        return head_top

    def compute_crop_rect(self, image_w: int, image_h: int, face_rect, target_aspect: float = None) -> tuple:
        """Simplified crop rectangle calculation based on face detection"""
        assert face_rect is not None
        if target_aspect is None:
            cfg_dim = self.config["photo_cropping"]["output_dimensions"]
            target_aspect = cfg_dim["width"] / cfg_dim["height"]

        x, y, w, h = face_rect
        face_cx = x + w // 2
        face_cy = y + h // 2

        # Get cropping parameters from config
        crop_cfg = self.config["photo_cropping"]["cropping_parameters"]
        target_head_ratio = crop_cfg["target_head_ratio"]
        target_top_margin = crop_cfg["target_top_margin"]
        chin_extra_ratio = crop_cfg["chin_extra_ratio"]
        
        # Estimate head top and chin
        head_top = float(self.estimate_head_top(y, h, image_h, face_cy))
        head_top_inside = max(0.0, head_top)
        chin = min(float(image_h - 1), y + h + chin_extra_ratio * h)  # Chin extra space
        head_height = max(1.0, chin - head_top)   # Head height in pixels

        # Simple strategy: direct calculation based on face detection
        # Target: head occupies target_head_ratio% of crop, top margin target_top_margin%
        
        # Calculate target crop dimensions
        target_crop_h = head_height / target_head_ratio
        target_crop_w = target_crop_h * target_aspect
        
        # Calculate crop position
        crop_y = int(round(head_top_inside - target_top_margin * target_crop_h))
        crop_x = int(round(face_cx - target_crop_w / 2))
        
        # Ensure crop rectangle stays within image boundaries
        if crop_x < 0:
            crop_x = 0
        if crop_x + target_crop_w > image_w:
            target_crop_w = image_w
            target_crop_h = target_crop_w / target_aspect
            crop_x = 0
        
        if crop_y < 0:
            crop_y = 0
        if crop_y + target_crop_h > image_h:
            target_crop_h = image_h
            target_crop_w = target_crop_h * target_aspect
            crop_y = 0
            # Recalculate x position
            crop_x = int(round(face_cx - target_crop_w / 2))
            crop_x = max(0, min(crop_x, image_w - target_crop_w))
        
        return int(crop_x), int(crop_y), int(target_crop_w), int(target_crop_h)
    
    def crop_photo(self, image_path, output_path):
        """Crop a single photo with face detection"""
        try:
            # Check if file exists
            if not Path(image_path).exists():
                print(f"File not found: {image_path}")
                return False
            
            image = cv2.imread(str(image_path))
            if image is None:
                print(f"Failed to load image: {image_path}")
                return False

            target_w = int(self.config["photo_cropping"]["output_dimensions"]["width"])
            target_h = int(self.config["photo_cropping"]["output_dimensions"]["height"])
            target_aspect = target_w / target_h

            face_rect = self.detect_face(image)
            if face_rect is None:
                print(f"No face detected in {image_path.name}, skipping...")
                return False

            cx, cy, cw, ch = self.compute_crop_rect(
                image.shape[1], image.shape[0], face_rect, target_aspect
            )
            cropped = image[cy:cy+ch, cx:cx+cw]

            result = cv2.resize(cropped, (target_w, target_h))
            quality = int(self.config["photo_cropping"].get("quality", 95))
            cv2.imwrite(str(output_path), result, [int(cv2.IMWRITE_JPEG_QUALITY), quality])

            # Generate debug image
            if bool(self.config["photo_cropping"].get("debug", False)):
                dbg = image.copy()
                fx, fy, fw, fh = face_rect
                
                # Face rectangle (green)
                cv2.rectangle(dbg, (fx, fy), (fx+fw, fy+fh), (0,255,0), 2)
                
                # Crop rectangle (blue)
                cv2.rectangle(dbg, (cx, cy), (cx+cw, cy+ch), (255,0,0), 2)
                
                # Head top line (red)
                head_top_y = int(self.estimate_head_top(fy, fh, image.shape[0], fy + fh//2))
                cv2.line(dbg, (fx-10, head_top_y), (fx+fw+10, head_top_y), (0,0,255), 2)
                cv2.putText(dbg, "Head Top", (fx, head_top_y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1)
                
                # Chin line (yellow)
                chin_y = int(fy + fh + 0.12 * fh)
                cv2.line(dbg, (fx-10, chin_y), (fx+fw+10, chin_y), (0,255,255), 2)
                cv2.putText(dbg, "Chin", (fx, chin_y+15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,255), 1)
                
                # Face center point (purple)
                face_center_x = fx + fw//2
                face_center_y = fy + fh//2
                cv2.circle(dbg, (face_center_x, face_center_y), 5, (255,0,255), -1)
                cv2.putText(dbg, "Face Center", (face_center_x+10, face_center_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,255), 1)
                
                debug_path = output_path.parent / f"DEBUG_{output_path.stem}.jpg"
                cv2.imwrite(str(debug_path), dbg)
            
            return True
        except Exception as e:
            print(f"Error cropping {image_path}: {e}")
            return False
    
    def batch_crop(self, input_dirs=None, output_dir="cropped_photo"):
        """Batch crop photos from input directories"""
        if input_dirs is None:
            input_dirs = self.config["photo_cropping"]["input_directories"]
        
        # Create output directory
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        
        total_processed = 0
        total_success = 0
        
        for input_dir in input_dirs:
            input_path = Path(input_dir)
            if not input_path.exists():
                print(f"Directory not found: {input_dir}")
                continue
            
            print(f"Processing directory: {input_dir}")
            
            # Find all image files
            image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
            image_files = []
            
            for ext in image_extensions:
                image_files.extend(input_path.glob(f"*{ext}"))
                image_files.extend(input_path.glob(f"*{ext.upper()}"))
            
            total_files = len(image_files)
            for idx, image_file in enumerate(image_files, 1):
                if image_file.name.startswith('.'):
                    continue
                
                output_file = output_dir / f"{image_file.stem}.jpg"
                
                # Show progress
                progress = f"[{idx}/{total_files}]"
                print(f"  {progress} Processing: {image_file.name}...", end=" ")
                
                if self.crop_photo(image_file, output_file):
                    print(f"[DONE] {image_file.name} -> {output_file.name}")
                    total_success += 1
                else:
                    print(f"[FAIL] {image_file.name}")
                
                total_processed += 1
        
        print(f"\nBatch processing completed!")
        print(f"Total processed: {total_processed}")
        print(f"Successful: {total_success}")
        print(f"Failed: {total_processed - total_success}")
        print(f"Output directory: {output_dir}")
        
        return total_success > 0

def main():
    parser = argparse.ArgumentParser(description="Photo Cropping Tool - Optimized Version")
    parser.add_argument("--input", "-i", default=".", help="Input directory or file (default: current directory)")
    parser.add_argument("--config", "-c", default="config.json", help="Configuration file")
    parser.add_argument("--output", "-o", default="cropped_photo", help="Output directory")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("PHOTO CROPPING TOOL - OPTIMIZED VERSION")
    print("=" * 60)
    
    cropper = PhotoCropper(args.config)
    
    if cropper.face_detector is None:
        print("✗ Face detection model not loaded. Exiting.")
        return
    
    # Check if input is a file or directory
    input_path = Path(args.input)
    if input_path.is_file():
        # Single file processing
        output_path = Path(args.output) / f"{input_path.stem}.jpg"
        output_path.parent.mkdir(exist_ok=True)
        
        print(f"Processing single file: {input_path}")
        success = cropper.crop_photo(input_path, output_path)
        
        if success:
            print(f"✓ Single file processed successfully: {output_path}")
        else:
            print(f"✗ Single file processing failed")
    else:
        # Directory processing
        success = cropper.batch_crop([args.input])
    
    if success:
        print("\n✓ Photo cropping completed successfully!")
    else:
        print("\n✗ Photo cropping failed!")

if __name__ == "__main__":
    main()    