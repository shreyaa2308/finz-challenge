import pandas as pd

def read_excel_file(file_path: str):
    workbook = pd.ExcelFile(file_path)
    return {
        "sheet_names": workbook.sheet_names
    }

def read_bank_transactions(file_path: str):
    df = pd.read_excel(
        file_path,
        sheet_name="Raw Bank Transactions"
    )
    df = df.where(pd.notnull(df), None)
    return df.to_dict(orient="records")