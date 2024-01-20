import pandas as pd


def get_sheet(spreadsheet_id: str, sheet_id: int) -> pd.DataFrame:
    url = f'https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=csv&gid={sheet_id}'
    return pd.read_csv(url)
