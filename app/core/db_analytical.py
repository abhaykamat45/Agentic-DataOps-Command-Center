import duckdb
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional
from app.config import settings

class AnalyticalDB:
    def __init__(self, parquet_dir: Optional[Path] = None):
        self._parquet_dir = parquet_dir

    @property
    def parquet_dir(self) -> Path:
        return self._parquet_dir or settings.PARQUET_DIR

    def get_connection(self) -> duckdb.DuckDBPyConnection:
        p_dir = self.parquet_dir
        p_dir.mkdir(parents=True, exist_ok=True)
        conn = duckdb.connect(database=":memory:")
        # Register parquet directory files as views
        for file in p_dir.glob("*.parquet"):
            table_name = file.stem
            conn.execute(f"CREATE VIEW {table_name} AS SELECT * FROM read_parquet('{file.as_posix()}')")
        return conn

    def query(self, sql: str) -> List[Dict[str, Any]]:
        """Run SQL query against registered Parquet views."""
        conn = self.get_connection()
        try:
            df = conn.execute(sql).df()
            return df.to_dict(orient="records")
        finally:
            conn.close()

    def query_df(self, sql: str) -> pd.DataFrame:
        """Run SQL query returning a Pandas DataFrame."""
        conn = self.get_connection()
        try:
            return conn.execute(sql).df()
        finally:
            conn.close()

    def get_table_schema(self, table_name: str) -> List[Dict[str, Any]]:
        """Fetch schema metadata for a parquet table."""
        file_path = self.parquet_dir / f"{table_name}.parquet"
        if not file_path.exists():
            raise FileNotFoundError(f"Table '{table_name}' does not exist as parquet.")
        
        conn = self.get_connection()
        try:
            df_desc = conn.execute(f"DESCRIBE SELECT * FROM read_parquet('{file_path.as_posix()}')").df()
            return df_desc.to_dict(orient="records")
        finally:
            conn.close()

    def save_dataframe_as_table(self, df: pd.DataFrame, table_name: str) -> str:
        """Save a pandas dataframe to Parquet storage."""
        file_path = self.parquet_dir / f"{table_name}.parquet"
        df.to_parquet(file_path, index=False)
        return str(file_path)

analytical_db = AnalyticalDB()
