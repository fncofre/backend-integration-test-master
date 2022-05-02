"""This is the main module.

This module imports ingestion, to run all the tasks.
Including .csv processing and API calls.

N_HIGHEST: The number of elements to process per branch
N_START: From which row of the df to start uploading products
N_END: In which row to stop uploading products
BRANCHES_NAMES: List with the names of the selected branchs
"""

import integrations.richart_wholesale_club.ingestion as ing

if __name__ == "__main__":
    N_HIGHEST = 100
    BRANCHES_NAMES = ['MM', 'RHSM']
    df = ing.process_csv_files(100, BRANCHES_NAMES)
    N_START = 0
    N_END = len(df)
    ing.process_api_calls(df, N_START, N_END)
