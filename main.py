import integrations.richart_wholesale_club.ingestion as ing

if __name__ == "__main__":
    df = ing.process_csv_files(100)
    ing.process_api_calls(df, 50, len(df))