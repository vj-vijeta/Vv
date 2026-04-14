import pandas as pd
import os

ASSET_DIR = "/Users/vijeta/Downloads/vasanth valley/Asset"

def validate():
    print("--- Validating Student Data ---")
    student_path = os.path.join(ASSET_DIR, "Asset student data.csv")
    if not os.path.exists(student_path):
        print(f"Error: {student_path} not found")
        return
    
    df = pd.read_csv(student_path)
    df.columns = [c.replace('\ufeff', '') for c in df.columns]
    print(f"Loaded {len(df)} rows of student data.")
    print(f"Subjects: {df['Subject'].unique()}")
    print(f"Average Percentile: {df['Percentile'].mean():.2f}")
    
    print("\n--- Validating Skill Data (English) ---")
    eng_path = os.path.join(ASSET_DIR, "Skill Performance -eng.csv")
    if os.path.exists(eng_path):
        sdf = pd.read_csv(eng_path)
        sdf.columns = [c.replace('\ufeff', '') for c in sdf.columns]
        print(f"Loaded {len(sdf)} skill rows for English.")
        school_col = "Vasant Valley School, New Delhi"
        if school_col in sdf.columns:
            top_skill = sdf.loc[sdf[school_col].idxmax(), 'SKILL_NAME']
            print(f"Top Skill: {top_skill}")
        else:
            print(f"Column '{school_col}' not found in Skill data.")
            print(f"Available columns: {sdf.columns.tolist()}")

if __name__ == "__main__":
    validate()
