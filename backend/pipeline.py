from functions.services.entity_linker import *
from functions.services.extract_triples import *
from functions.services.graph_design import *
from functions.services.save_txt import *

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "data" / "csv" / "DBLP1_processed_.csv"

data = pd.read_csv(CSV_PATH, sep=";")

print("Data loaded successfully.")
data.head()

UniqueList3 = entity_linker(data)
triples_labels_df, listtripletslabel = extract_triples(UniqueList3)
# graph_design(UniqueList3, listtripletslabel, data)
# save_txt(data, triples_labels_df)

