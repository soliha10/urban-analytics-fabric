# %%
%pip install -q semantic-link-labs

# %%
import sempy.fabric as fabric
from sempy_labs import create_semantic_model_from_bim, get_semantic_model_bim, refresh_semantic_model
from sempy_labs.report import clone_report

WORKSPACE = "ws_urban_analytics"
SOURCE_MODEL = "sm_urban_analytics"
IMPORT_MODEL = "sm_urban_analytics_import"
SOURCE_REPORT = "rpt_urban_analytics"
PUBLIC_REPORT = "rpt_urban_analytics_public"


# %%
def import_query(entity):
    item = f'[Schema="{entity.get("schemaName", "dbo")}", Item="{entity["entityName"]}"]'
    return f'let Source = {entity["expressionSource"]}, Data = Source{{{item}}}[Data] in Data'


def import_partition(partition):
    return {"name": partition["name"], "mode": "import", "source": {"type": "m", "expression": import_query(partition["source"])}}


def to_import_table(table):
    return {**table, "partitions": [import_partition(partition) for partition in table["partitions"]]}


def to_import_model(bim):
    model = bim["model"]
    return {**bim, "model": {**model, "tables": [to_import_table(table) for table in model["tables"]]}}


def item_exists(name, item_type):
    items = fabric.list_items(type=item_type, workspace=WORKSPACE)
    return name in set(items["Display Name"])


# %%
if not item_exists(IMPORT_MODEL, "SemanticModel"):
    create_semantic_model_from_bim(IMPORT_MODEL, to_import_model(get_semantic_model_bim(SOURCE_MODEL, WORKSPACE)), WORKSPACE)
print(f"{IMPORT_MODEL}: import-mode copy of {SOURCE_MODEL}")

# %%
refresh_semantic_model(dataset=IMPORT_MODEL, workspace=WORKSPACE)
if not item_exists(PUBLIC_REPORT, "Report"):
    clone_report(SOURCE_REPORT, PUBLIC_REPORT, workspace=WORKSPACE, target_dataset=IMPORT_MODEL)
print(f"{PUBLIC_REPORT} -> {IMPORT_MODEL}")
