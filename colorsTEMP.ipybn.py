import pandas as pd
speciesFile = currentDir + 'NWspecies060222.xlsx'
speciesTable = pd.read_excel(speciesFile,sheet_name = "species")

speciesTable.head()
