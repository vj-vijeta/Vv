import pypdf
import pandas as pd
import re
import os

def extract_skill_trends(pdf_path, subject, grade):
    # This logic targets the 'Skill-based Summary' table in your ASSET MyBooks
    try:
        reader = pypdf.PdfReader(pdf_path)
        data = []
        for page in reader.pages:
            text = page.extract_text()
            if "Skill-based Summary" in text or "Performance on Skills" in text:
                # Regex to find: Skill Name followed by School % and National %
                # Note: Adjusting to capture 'Previous' vs 'Current' if present in the PDF table
                matches = re.findall(r"([A-Za-z\s,]+)\s+(\d+\.?\d*)%\s+(\d+\.?\d*)%", text)
                for match in matches:
                    data.append({
                        "Year": 2025,
                        "Grade": grade,
                        "Subject": subject,
                        "Skill": match[0].strip(),
                        "School_Score": float(match[1]),
                        "Nat_Score": float(match[2])
                    })
        return data
    except:
        return []

# Usage example to build your trends file
trends = extract_skill_trends("/combinepdf (1).pdf", "Maths", 8)
# pd.DataFrame(trends).to_csv("Asset/Skill_Trends.csv", index=False)