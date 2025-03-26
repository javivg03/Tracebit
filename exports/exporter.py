import pandas as pd

def export_to_excel(data_list, filename):
    df = pd.DataFrame(data_list)
    df.to_excel(filename, index=False)
