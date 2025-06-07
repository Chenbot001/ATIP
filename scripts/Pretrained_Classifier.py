#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ACL Paper Track Classification using Pretrained Models
=====================================================

This script uses pretrained BERT and SciBERT models without fine-tuning to classify 
ACL research papers into their respective tracks based on their titles and abstracts.
It evaluates the performance of these models on the ACL25_ThemeData dataset.

Author: Eric Chen & GitHub Copilot
Date: June 8, 2025
"""

# I. Imports - All necessary libraries
import os
import json
import numpy as np
import pandas as pd
import torch
import seaborn as sns
import matplotlib.pyplot as plt
from tqdm import tqdm
from sklearn.metrics import (
    accuracy_score, 
    precision_recall_fscore_support, 
    confusion_matrix
)
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.neighbors import KNeighborsClassifier
from transformers import (
    AutoTokenizer, 
    AutoModel
)
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

# Check for GPU availability
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

def load_data(csv_path):
    """
    Load data from CSV file
    
    Args:
        csv_path (str): Path to the CSV file
        
    Returns:
        tuple: DataFrame, label encoder, unique labels
    """
    print(f"Loading data from {csv_path}...")
    # Load data
    df = pd.read_csv(csv_path)
    
    # Check for required columns
    required_columns = ['Title', 'Track Theme']
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Required column '{col}' not found in the dataset")
    
    # Check if abstract column is available
    has_abstract = 'abstract' in df.columns
    
    # Create text_input column
    if has_abstract:
        # Combine title and abstract, handle missing abstracts
        df['text_input'] = df.apply(
            lambda x: x['Title'] + ' [SEP] ' + str(x['abstract']) 
            if pd.notna(x['abstract']) else x['Title'],
            axis=1
        )
    else:
        df['text_input'] = df['Title']
    
    # Encode labels
    le = LabelEncoder()
    df['label_id'] = le.fit_transform(df['Track Theme'])
    unique_labels = le.classes_
    
    print(f"Found {len(unique_labels)} unique tracks.")
    
    return df, le, unique_labels

def compute_metrics(y_true, y_pred):
    """
    Compute evaluation metrics for the model
    
    Args:
        y_true: True labels
        y_pred: Predicted labels
        
    Returns:
        dict: Dictionary of metrics including micro/macro F1 scores
    """
    # Calculate metrics
    accuracy = accuracy_score(y_true, y_pred)
    
    # Calculate macro metrics
    precision_macro, recall_macro, f1_macro, _ = precision_recall_fscore_support(
        y_true, y_pred, average='macro', zero_division=0
    )
    
    # Calculate micro metrics
    precision_micro, recall_micro, f1_micro, _ = precision_recall_fscore_support(
        y_true, y_pred, average='micro', zero_division=0
    )
    
    # Calculate weighted metrics
    precision_weighted, recall_weighted, f1_weighted, _ = precision_recall_fscore_support(
        y_true, y_pred, average='weighted', zero_division=0
    )
    
    # Return metrics dictionary
    return {
        'accuracy': accuracy,
        'precision_macro': precision_macro,
        'recall_macro': recall_macro,
        'f1_macro': f1_macro,
        'precision_micro': precision_micro,
        'recall_micro': recall_micro,
        'f1_micro': f1_micro,
        'precision_weighted': precision_weighted,
        'recall_weighted': recall_weighted,
        'f1_weighted': f1_weighted
    }

def plot_confusion_matrix(y_true, y_pred, labels, model_name):
    """
    Computes, plots, and saves the confusion matrix
    
    Args:
        y_true: True labels
        y_pred: Predicted labels
        labels: List of label names
        model_name: Name of the model (for saving the figure)
    """
    print(f"\nGenerating confusion matrix for {model_name}...")
    
    # Compute the confusion matrix
    cm = confusion_matrix(y_true, y_pred)

    # Plot the confusion matrix using seaborn
    plt.figure(figsize=(18, 15))  # Adjust size for better readability
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=labels, yticklabels=labels)
    
    plt.title(f'Confusion Matrix - {model_name}', fontsize=20)
    plt.ylabel('True Label', fontsize=16)
    plt.xlabel('Predicted Label', fontsize=16)
    plt.xticks(rotation=45, ha="right", fontsize=12)
    plt.yticks(rotation=0, fontsize=12)
    plt.tight_layout()  # Adjust layout to make sure labels fit

    # Save the figure to a file
    output_path = f"confusion_matrix_{model_name.lower().replace(' ', '_')}.png"
    plt.savefig(output_path)
    print(f"Confusion matrix plot saved to {output_path}")
    
    # Close the figure to free memory
    plt.close()

def extract_embeddings(texts, model, tokenizer, max_length=512):
    """
    Extract embeddings from a pretrained model
    
    Args:
        texts (list): List of text inputs
        model: Pretrained model
        tokenizer: Tokenizer for the model
        max_length (int): Maximum sequence length
        
    Returns:
        np.ndarray: Array of embeddings
    """
    embeddings = []
    batch_size = 8  # Process in small batches to avoid memory issues
    
    # Process texts in batches
    for i in tqdm(range(0, len(texts), batch_size), desc=f"Extracting embeddings"):
        batch_texts = texts[i:i + batch_size]
        
        # Tokenize
        inputs = tokenizer(
            batch_texts,
            padding=True,
            truncation=True,
            max_length=max_length,
            return_tensors='pt'
        ).to(device)
        
        # Get embeddings
        with torch.no_grad():
            outputs = model(**inputs)
            # Use the [CLS] token embedding as the sentence embedding
            batch_embeddings = outputs.last_hidden_state[:, 0, :].cpu().numpy()
        
        embeddings.extend(batch_embeddings)
    
    return np.array(embeddings)

def classify_with_pretrained_model(model_name, model_path, df, label_encoder):
    """
    Classify papers using pretrained embeddings and a simple classifier
    
    Args:
        model_name (str): Name of the model for reporting
        model_path (str): Path or name of the pretrained model
        df (pd.DataFrame): DataFrame with the data
        label_encoder (LabelEncoder): Fitted label encoder
        
    Returns:
        dict: Dictionary of metrics
    """
    print(f"\n===== Evaluating {model_name} =====")
    
    # Split data
    train_df, test_df = train_test_split(
        df, test_size=0.2, random_state=42, stratify=df['label_id']
    )
    
    # Load model and tokenizer
    print(f"Loading {model_name} model and tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModel.from_pretrained(model_path).to(device)
    
    # Extract embeddings
    print("Extracting embeddings for training data...")
    train_embeddings = extract_embeddings(
        train_df['text_input'].tolist(), model, tokenizer
    )
    
    print("Extracting embeddings for test data...")
    test_embeddings = extract_embeddings(
        test_df['text_input'].tolist(), model, tokenizer
    )
    
    # Train a simple classifier on top of the embeddings
    print("Training a logistic regression classifier on embeddings...")
    classifier = LogisticRegression(
        max_iter=1000, class_weight='balanced', n_jobs=-1
    )
    classifier.fit(train_embeddings, train_df['label_id'])
    
    # Predict
    print("Making predictions...")
    test_pred = classifier.predict(test_embeddings)
    
    # Compute metrics
    metrics = compute_metrics(test_df['label_id'], test_pred)
    
    # Plot confusion matrix
    plot_confusion_matrix(
        test_df['label_id'], 
        test_pred,
        label_encoder.classes_,
        model_name
    )
    
    return metrics, test_df['label_id'], test_pred

def classify_with_tfidf(df, label_encoder):
    """
    Classify papers using TF-IDF and a simple classifier as baseline
    
    Args:
        df (pd.DataFrame): DataFrame with the data
        label_encoder (LabelEncoder): Fitted label encoder
        
    Returns:
        dict: Dictionary of metrics
    """
    print("\n===== Evaluating TF-IDF Baseline =====")
    
    # Split data
    train_df, test_df = train_test_split(
        df, test_size=0.2, random_state=42, stratify=df['label_id']
    )
    
    # Extract TF-IDF features
    print("Extracting TF-IDF features...")
    tfidf = TfidfVectorizer(
        max_features=10000,
        stop_words='english'
    )
    
    train_features = tfidf.fit_transform(train_df['text_input'])
    test_features = tfidf.transform(test_df['text_input'])
    
    # Train a simple classifier
    print("Training a logistic regression classifier on TF-IDF features...")
    classifier = LogisticRegression(
        max_iter=1000, class_weight='balanced', n_jobs=-1
    )
    classifier.fit(train_features, train_df['label_id'])
    
    # Predict
    print("Making predictions...")
    test_pred = classifier.predict(test_features)
    
    # Compute metrics
    metrics = compute_metrics(test_df['label_id'], test_pred)
    
    # Plot confusion matrix
    plot_confusion_matrix(
        test_df['label_id'], 
        test_pred,
        label_encoder.classes_,
        "TF-IDF Baseline"
    )
    
    return metrics, test_df['label_id'], test_pred

def print_metrics(metrics, model_name):
    """
    Print metrics in a formatted way
    
    Args:
        metrics (dict): Dictionary of metrics
        model_name (str): Name of the model
    """
    print(f"\n===== {model_name} Performance Metrics =====")
    print(f"Accuracy: {metrics['accuracy']:.4f}")
    print(f"Micro-F1 Score: {metrics['f1_micro']:.4f}")
    print(f"Macro-F1 Score: {metrics['f1_macro']:.4f}")
    print(f"Weighted-F1 Score: {metrics['f1_weighted']:.4f}")
    print("==================================\n")
    
    # Print detailed metrics
    # print(f"Detailed {model_name} metrics:")
    # for key, value in metrics.items():
    #     print(f"  {key}: {value:.4f}")

def main():
    """
    Main function to run the evaluation
    """
    # Path to data
    data_path = "C:\\Eric\\Projects\\AI_Researcher_Network\\data\\ACL25_ThemeData.csv"
    
    # Load data
    df, label_encoder, unique_labels = load_data(data_path)
    
    # Get metrics for TF-IDF baseline
    tfidf_metrics, _, _ = classify_with_tfidf(df, label_encoder)
    print_metrics(tfidf_metrics, "TF-IDF Baseline")
    
    # Get metrics for BERT
    bert_metrics, _, _ = classify_with_pretrained_model(
        "BERT", "bert-base-uncased", df, label_encoder
    )
    print_metrics(bert_metrics, "BERT")
    
    # Get metrics for SciBERT
    scibert_metrics, _, _ = classify_with_pretrained_model(
        "SciBERT", "allenai/scibert_scivocab_uncased", df, label_encoder
    )
    print_metrics(scibert_metrics, "SciBERT")
    
    # Compare models
    print("\n===== Model Comparison =====")
    comparison_metrics = ['accuracy', 'f1_micro', 'f1_macro', 'f1_weighted']
    models = {
        "TF-IDF": tfidf_metrics,
        "BERT": bert_metrics,
        "SciBERT": scibert_metrics
    }
    
    comparison_df = pd.DataFrame({
        model_name: [metrics[m] for m in comparison_metrics]
        for model_name, metrics in models.items()
    }, index=comparison_metrics)
    
    print(comparison_df)
    
    # Plot comparison
    plt.figure(figsize=(10, 6))
    comparison_df.plot(kind='bar', ax=plt.gca())
    plt.title('Model Comparison', fontsize=16)
    plt.ylabel('Score', fontsize=14)
    plt.xlabel('Metric', fontsize=14)
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig('model_comparison.png')
    print("Model comparison chart saved to 'model_comparison.png'")

if __name__ == "__main__":
    main()
