import pandas as pd

from artefact.data import DATA_DIR


def load_csv(name: str) -> pd.DataFrame:
    df = pd.read_csv(
        DATA_DIR / f"desafio_tecnico_ai_eng - {name}.csv", skipinitialspace=True
    )
    df.columns = df.columns.str.strip()
    for column in df.columns:
        if pd.api.types.is_string_dtype(df[column]):
            df[column] = df[column].str.strip().replace("", pd.NA)
    return df
