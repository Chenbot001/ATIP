import pandas as pd
import os
import sys
from collections import Counter
from typing import Optional, List, Dict, Any, Tuple

def load_csv_data(csv_filepath: str) -> pd.DataFrame:
    """
    Load CSV data into a pandas DataFrame.
    
    Args:
        csv_filepath (str): Path to the CSV file to load
        
    Returns:
        pd.DataFrame: Loaded DataFrame
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file is not a CSV
    """
    try:
        if not os.path.exists(csv_filepath):
            raise FileNotFoundError(f"File '{csv_filepath}' not found.")
        
        if not csv_filepath.lower().endswith('.csv'):
            raise ValueError(f"File '{csv_filepath}' is not a CSV file.")
        
        df = pd.read_csv(csv_filepath)
        print(f"✓ Successfully loaded CSV file: {csv_filepath}")
        print(f"  Shape: {df.shape[0]} rows, {df.shape[1]} columns")
        return df
        
    except Exception as e:
        print(f"Error loading CSV file: {str(e)}")
        raise

def get_columns(df: pd.DataFrame) -> List[str]:
    """Get list of all column names in the DataFrame."""
    return list(df.columns)

def column_exists(df: pd.DataFrame, column_name: str) -> bool:
    """Check if a column exists in the DataFrame."""
    return column_name in df.columns

def remove_column(df: pd.DataFrame, column_name: str, save_to_file: bool = False, filepath: Optional[str] = None) -> Tuple[pd.DataFrame, bool]:
    """
    Remove a specified column from the DataFrame.
    
    Args:
        df (pd.DataFrame): DataFrame to modify
        column_name (str): Name of the column to remove
        save_to_file (bool): Whether to save changes back to a file
        filepath (str): File path to save to (required if save_to_file is True)
        
    Returns:
        Tuple[pd.DataFrame, bool]: (modified_dataframe, success_status)
    """
    try:
        if not column_exists(df, column_name):
            print(f"Warning: '{column_name}' column not found in the DataFrame.")
            print(f"Available columns: {get_columns(df)}")
            return df, False
        
        # Remove the specified column
        print(f"Removing '{column_name}' column...")
        modified_df = df.drop(columns=[column_name])
        
        if save_to_file:
            if filepath is None:
                print("Error: filepath is required when save_to_file is True")
                return df, False
            
            # Save the modified dataframe back to the file
            modified_df.to_csv(filepath, index=False)
            print(f"✓ Successfully removed '{column_name}' column and saved to {filepath}")
        
        print(f"Remaining columns: {get_columns(modified_df)}")
        return modified_df, True
        
    except Exception as e:
        print(f"Error removing column: {str(e)}")
        return df, False

def check_column_uniqueness(df: pd.DataFrame, column_name: str) -> Tuple[bool, Dict[str, int]]:
    """
    Check if a column contains all unique values.
    
    Args:
        df (pd.DataFrame): DataFrame to check
        column_name (str): Name of the column to check
        
    Returns:
        Tuple[bool, Dict[str, int]]: (is_unique, duplicates_dict)
    """
    try:
        if not column_exists(df, column_name):
            print(f"Error: Column '{column_name}' not found in the DataFrame.")
            print(f"Available columns: {get_columns(df)}")
            return False, {}
        
        # Get the column values
        column_values = df[column_name]
        
        # Count occurrences of each value
        value_counts = Counter(column_values)
        
        # Find duplicates (values that appear more than once)
        duplicates = {value: count for value, count in value_counts.items() if count > 1}
        
        if not duplicates:
            print(f"✓ Column '{column_name}' contains all unique values.")
            return True, {}
        else:
            print(f"✗ Column '{column_name}' contains duplicate values:")
            print(f"  Found {len(duplicates)} unique values with duplicates")
            print(f"  Total rows with duplicates: {sum(duplicates.values()) - len(duplicates)}")
            print("\nDuplicate values and their counts:")
            
            # Print duplicates in order of appearance in the file
            for value, count in duplicates.items():
                print(f"  '{value}': appears {count} times")
                
                # Find and print the row indices where this value appears
                duplicate_indices = df[df[column_name] == value].index.tolist()
                print(f"    Row indices: {duplicate_indices}")
            
            return False, duplicates
            
    except Exception as e:
        print(f"Error checking column uniqueness: {e}")
        return False, {}

def get_column_info(df: pd.DataFrame, column_name: str) -> Dict[str, Any]:
    """
    Get comprehensive information about a column.
    
    Args:
        df (pd.DataFrame): DataFrame to analyze
        column_name (str): Name of the column to analyze
        
    Returns:
        Dict[str, Any]: Dictionary containing column information
    """
    try:
        if not column_exists(df, column_name):
            return {"error": f"Column '{column_name}' not found"}
        
        column_data = df[column_name]
        
        info = {
            "column_name": column_name,
            "data_type": str(column_data.dtype),
            "total_rows": len(column_data),
            "non_null_count": column_data.count(),
            "null_count": column_data.isnull().sum(),
            "null_percentage": (column_data.isnull().sum() / len(column_data)) * 100,
            "unique_values": column_data.nunique(),
            "is_unique": column_data.is_unique,
            "sample_values": column_data.dropna().head(5).tolist()
        }
        
        # Add numeric-specific info if applicable
        if pd.api.types.is_numeric_dtype(column_data):
            info.update({
                "min_value": column_data.min(),
                "max_value": column_data.max(),
                "mean_value": column_data.mean(),
                "median_value": column_data.median(),
                "std_deviation": column_data.std()
            })
        
        return info
        
    except Exception as e:
        return {"error": f"Error analyzing column: {str(e)}"}

def print_column_info(df: pd.DataFrame, column_name: str) -> None:
    """Print formatted information about a column."""
    info = get_column_info(df, column_name)
    
    if "error" in info:
        print(f"Error: {info['error']}")
        return
    
    print(f"\nColumn Information for '{column_name}':")
    print("=" * 50)
    print(f"Data Type: {info['data_type']}")
    print(f"Total Rows: {info['total_rows']}")
    print(f"Non-null Count: {info['non_null_count']}")
    print(f"Null Count: {info['null_count']} ({info['null_percentage']:.2f}%)")
    print(f"Unique Values: {info['unique_values']}")
    print(f"Is Unique: {info['is_unique']}")
    
    if "min_value" in info:
        print(f"Min Value: {info['min_value']}")
        print(f"Max Value: {info['max_value']}")
        print(f"Mean Value: {info['mean_value']:.2f}")
        print(f"Median Value: {info['median_value']}")
        print(f"Standard Deviation: {info['std_deviation']:.2f}")
    
    print(f"Sample Values: {info['sample_values']}")

def save_dataframe(df: pd.DataFrame, filepath: str) -> bool:
    """Save DataFrame to a CSV file."""
    try:
        df.to_csv(filepath, index=False)
        print(f"✓ DataFrame saved to {filepath}")
        return True
    except Exception as e:
        print(f"Error saving DataFrame: {str(e)}")
        return False

def analyze_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Get comprehensive information about the entire DataFrame.
    
    Args:
        df (pd.DataFrame): DataFrame to analyze
        
    Returns:
        Dict[str, Any]: Dictionary containing DataFrame information
    """
    try:
        info = {
            "shape": df.shape,
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "columns": list(df.columns),
            "data_types": df.dtypes.to_dict(),
            "memory_usage": df.memory_usage(deep=True).sum(),
            "null_counts": df.isnull().sum().to_dict(),
            "null_percentages": (df.isnull().sum() / len(df) * 100).to_dict(),
            "duplicate_rows": df.duplicated().sum(),
            "duplicate_percentage": (df.duplicated().sum() / len(df)) * 100
        }
        
        return info
        
    except Exception as e:
        return {"error": f"Error analyzing DataFrame: {str(e)}"}

def print_dataframe_summary(df: pd.DataFrame) -> None:
    """Print a formatted summary of the DataFrame."""
    info = analyze_dataframe(df)
    
    if "error" in info:
        print(f"Error: {info['error']}")
        return
    
    print(f"\nDataFrame Summary:")
    print("=" * 50)
    print(f"Shape: {info['shape'][0]} rows × {info['shape'][1]} columns")
    print(f"Memory Usage: {info['memory_usage'] / 1024:.2f} KB")
    print(f"Duplicate Rows: {info['duplicate_rows']} ({info['duplicate_percentage']:.2f}%)")
    
    print(f"\nColumns ({info['total_columns']}):")
    for col in info['columns']:
        null_pct = info['null_percentages'][col]
        dtype = info['data_types'][col]
        print(f"  {col}: {dtype} (null: {null_pct:.1f}%)")

# Configuration for main function examples
DEFAULT_CONFIG = {
    'csv_filepath': 'data/paper_info.csv',
    'column_name': 's2_id',
    'operation': 'check_uniqueness'  # 'check_uniqueness', 'remove_column', 'column_info', 'dataframe_summary'
}

def main():
    """
    Main function demonstrating usage of the utility functions.
    Modify DEFAULT_CONFIG to change behavior.
    """
    config = DEFAULT_CONFIG
    csv_filepath = config['csv_filepath']
    column_name = config['column_name']
    operation = config['operation']
    
    print(f"CSV Utils - File: {csv_filepath}")
    print("=" * 60)
    
    try:
        # Load the DataFrame
        df = load_csv_data(csv_filepath)
        
        if operation == 'check_uniqueness':
            print(f"Checking uniqueness of column '{column_name}'")
            is_unique, duplicates = check_column_uniqueness(df, column_name)
            
            if is_unique:
                print("\nResult: Column contains all unique values ✓")
            else:
                print("\nResult: Column contains duplicate values ✗")
                
        elif operation == 'remove_column':
            print(f"Removing column '{column_name}'")
            modified_df, success = remove_column(df, column_name, save_to_file=True, filepath=csv_filepath)
            if success:
                print("Column removal completed successfully ✓")
            else:
                print("Column removal failed ✗")
                
        elif operation == 'column_info':
            print(f"Getting information for column '{column_name}'")
            print_column_info(df, column_name)
            
        elif operation == 'dataframe_summary':
            print("Getting DataFrame summary")
            print_dataframe_summary(df)
            
        else:
            print(f"Unknown operation: {operation}")
            print("Available operations: check_uniqueness, remove_column, column_info, dataframe_summary")
            
    except Exception as e:
        print(f"Error in main execution: {str(e)}")

if __name__ == "__main__":
    main() 