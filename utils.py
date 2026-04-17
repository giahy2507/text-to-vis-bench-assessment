from transformers import GPT2Tokenizer
from typing import List
import glob
import os
import nbformat
import tqdm
import pandas as pd
import json

# initialize GPT2 tokenizer
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")

def tokenize_text(text) -> List[str]:
    """
    Tokenize text using GPT2 tokenizer.
    
    Args:
        text (str): Input text string.
        
    Returns:
        List[str]: List of tokens.
    """
    tokens = tokenizer.encode(text, add_special_tokens=False)
    return [tokenizer.decode(tokens[i:i+1]) for i in range(len(tokens) - 1)]