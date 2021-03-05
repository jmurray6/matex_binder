import pandas as pd

def safe_concat(x):
    if isinstance(x,list):
        return ' '.join(x)
    else:
        return ''

mdf = pd.read_pickle('./data/materials.pkl')
mdf["description_lower"] = mdf["material"].apply(lambda x: x.lower())
mdf["entity_type_string"] = mdf["entity"].apply(safe_concat)
mdf["shader_string"] = mdf["shader"].apply(safe_concat)
mdf["product_string"] = mdf["product"].apply(lambda x: safe_concat(x))
mdf["product_string_lower"] = mdf["product"].apply(lambda x: safe_concat(x).lower())
mdf["hasTexture"] = mdf['path'].apply(lambda x: False if len(x)<1 else True)
entityTypeList = sorted(mdf.entity.dropna().explode().unique())


def get_data_source():
    return mdf