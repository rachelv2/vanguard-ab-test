import pandas as pd

def load_data(base_path="data/raw/"):
    """
    Loads and prepares all project datasets from .txt files.
    
    Returns:
        df_demo, df_web, df_experiment
    """
    
    # Load datasets
    df_demo = pd.read_csv(base_path + "df_final_demo.txt", sep=",")
    df_web_1 = pd.read_csv(base_path + "df_final_web_data_pt_1.txt", sep=",")
    df_web_2 = pd.read_csv(base_path + "df_final_web_data_pt_2.txt", sep=",")
    df_experiment = pd.read_csv(base_path + "df_final_experiment_clients.txt", sep=",")
    
    # Merge web datasets
    df_web = pd.concat([df_web_1, df_web_2], ignore_index=True)
    
    # Standardize column names
    df_demo.columns = df_demo.columns.str.lower().str.strip()
    df_web.columns = df_web.columns.str.lower().str.strip()
    df_experiment.columns = df_experiment.columns.str.lower().str.strip()
    
    print("Datasets loaded successfully:")
    print(f"Demo: {df_demo.shape}")
    print(f"Web: {df_web.shape}")
    print(f"Experiment: {df_experiment.shape}")
    
    return df_demo, df_web, df_experiment