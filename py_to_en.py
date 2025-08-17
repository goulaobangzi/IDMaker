#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chinese Name to English (Pinyin) Converter
Convert Chinese names to English (Pinyin) format
"""

from pypinyin import pinyin, Style
import re
import argparse
import json
from pathlib import Path

def convert_chinese_name(chinese_name, config=None):
    """
    Convert Chinese name to English (Pinyin) format
    
    Args:
        chinese_name (str): Chinese name string
        config (dict): Configuration dictionary (optional)
        
    Returns:
        str: English name in format "FirstName LastName"
    """
    if not chinese_name or not chinese_name.strip():
        return ""
    
    # Get configuration parameters
    if config and "name_conversion" in config:
        name_cfg = config["name_conversion"]
        pinyin_style = name_cfg.get("pinyin_style", "normal")
        name_format = name_cfg.get("name_format", "givenname_surname")
        fallback_to_original = name_cfg.get("fallback_to_original", True)
    else:
        # Default values
        pinyin_style = "normal"
        name_format = "givenname_surname"
        fallback_to_original = True
    
    # Remove extra spaces and special characters
    chinese_name = re.sub(r'[^\u4e00-\u9fff\s]', '', chinese_name.strip())
    
    if not chinese_name:
        return ""
    
    # Convert to pinyin
    try:
        # Map pinyin style string to Style enum
        style_map = {
            "normal": Style.NORMAL,
            "first_letter": Style.FIRST_LETTER,
            "tone": Style.TONE,
            "tone2": Style.TONE2
        }
        style = style_map.get(pinyin_style, Style.NORMAL)
        
        pinyin_list = pinyin(chinese_name, style=style)
        
        if len(pinyin_list) == 1:
            # Single character name
            return pinyin_list[0][0].capitalize()
        elif len(pinyin_list) >= 2:
            # First character is surname, rest are given name
            surname = pinyin_list[0][0]  # 姓
            given_name_parts = [p[0] for p in pinyin_list[1:]]  # 名（除第一个字外的所有字）
            given_name = ''.join(given_name_parts)  # 将名字部分连接起来
            
            # Format based on configuration
            if name_format == "surname_givenname":
                # Format: Surname GivenName (姓 名)
                return f"{surname.capitalize()} {given_name.capitalize()}"
            else:
                # Default: GivenName Surname (名 姓)
                return f"{given_name.capitalize()} {surname.capitalize()}"
        else:
            return chinese_name if fallback_to_original else ""
            
    except Exception as e:
        print(f"Error converting name '{chinese_name}': {e}")
        return chinese_name if fallback_to_original else ""

def convert_name_list(name_list):
    """
    Convert a list of Chinese names to English
    
    Args:
        name_list (list): List of Chinese names
        
    Returns:
        list: List of English names
    """
    if not name_list:
        return []
    
    english_names = []
    for name in name_list:
        english_name = convert_chinese_name(name)
        if english_name:
            english_names.append(english_name)
    
    return english_names

def batch_convert_names(input_file, output_file):
    """Batch convert names from a text file"""
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            names = [line.strip() for line in f if line.strip()]
        
        english_names = convert_name_list(names)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for name in english_names:
                f.write(name + '\n')
        
        print(f"✓ Converted {len(english_names)} names")
        print(f"✓ Output saved to: {output_file}")
        
        return True
    except Exception as e:
        print(f"✗ Error in batch conversion: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Chinese Name to English Converter")
    parser.add_argument("--name", "-n", help="Single Chinese name to convert")
    parser.add_argument("--input", "-i", help="Input file with names (one per line)")
    parser.add_argument("--output", "-o", default="converted_names.txt", help="Output file for batch conversion")
    parser.add_argument("--interactive", "-t", action="store_true", help="Interactive mode")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("CHINESE NAME TO ENGLISH CONVERTER")
    print("=" * 60)
    
    if args.name:
        # Convert single name
        english_name = convert_chinese_name(args.name)
        print(f"'{args.name}' -> '{english_name}'")
    
    elif args.input:
        # Batch conversion from file
        if not Path(args.input).exists():
            print(f"✗ Input file not found: {args.input}")
            return
        
        success = batch_convert_names(args.input, args.output)
        if success:
            print("\n✓ Batch conversion completed successfully!")
        else:
            print("\n✗ Batch conversion failed!")
    
    elif args.interactive:
        # Interactive mode
        print("\n" + "=" * 40)
        print("Interactive Mode (Enter 'quit' to exit)")
        print("=" * 40)
        
        while True:
            user_input = input("\nEnter Chinese name: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            
            if user_input:
                english_name = convert_chinese_name(user_input)
                print(f"English: {english_name}")
            else:
                print("Please enter a valid name.")
    
    else:
        print("Please provide --name or --input. Use --help for options.")
        return

if __name__ == "__main__":
    main() 