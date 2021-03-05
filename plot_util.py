import sys
import logging
import os
import json
import matplotlib.pyplot as plt
import panel as pn
import numpy as np
from bokeh.plotting import figure, ColumnDataSource
from bokeh.models import (
    HoverTool,
    WheelZoomTool,
    CDSView,
    BooleanFilter,
    Title
)
from CONSTANTS import column_axis_dict

logging.basicConfig(
    level=logging.INFO,
    format='[{%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(filename='tmp6a.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('LOGGER_NAME')
FRAME_PATH = "./frameImages"
TEXTURES_PATH = "./textures"

def get_texture_image_path(name):
    with open(f"{os.path.join(TEXTURES_PATH, name)}.json") as json_file:
        data = json.load(json_file)
        texture_image = data.get("path")
    texture_image_path = os.path.join(TEXTURES_PATH, texture_image)
    if "pvr" in texture_image_path:
        file_without_extension = texture_image_path.rsplit(".", 1)[0]
        print("looking for alternative for: ", texture_image_path)
        for extension in [".png", ".jpg"]:
            file_with_new_extension = f"{file_without_extension}{extension}"
            if os.path.exists(file_with_new_extension):
                print("existence for ", file_with_new_extension)
                print("original: ", texture_image_path)
                return file_with_new_extension
    else:
        return texture_image_path

    return None

def fillna_and_add_boolean(df,colname,default_value):
    df = df.copy()
    if colname in df.columns:
        df['has__'+colname] = (df[colname].isna()==False)
        df[colname] = df[colname].fillna(default_value)
    return df

def fillna_and_onehot(df,colname,default_value):
    df = df.copy()
    if colname in df.columns:
        df[colname] = df[colname].fillna(default_value)
        # replace with onehot
        df = pd.concat([df,pd.get_dummies(df[colname],prefix=colname+'__')],axis=1)
        df = df.drop(columns=[colname],axis=1)

    return df

def create_source(mdf):
    line_color = np.array(['black']*mdf.shape[0])
    line_color[mdf.hasTexture]='red'
    ret = ColumnDataSource(
            data=dict(
                x=mdf['ML_X'],
                y=mdf['ML_Y'],
                cR=mdf['COL_R'],
                cG=mdf['COL_G'],
                cB=mdf['COL_B'],
                #c=pd.concat([mdf['COL_R'],mdf['COL_G'],mdf['COL_B']],axis=1).values,
                #c=np.array(list(map(rgb_to_hex,pd.concat([mdf['COL_R'],mdf['COL_G'],mdf['COL_B']],axis=1).values))),
                c=mdf['hex'].apply(lambda s: '#'+s), # fill color
                p_name=mdf['material'],
                # Props
                p_alpha = mdf['alpha'],
                p_diffuse_intensity = mdf['diffuse_intensity' ],
                p_metalness = mdf['metalness'],
                p_reflection_intensity = mdf['reflection_intensity' ],
                p_roughness = mdf['roughness' ],
                p_mask_for_luminance = mdf['mask_for_luminance'],
                p_luminance_offset = mdf['luminance_offset' ],
                p_transparency_mode = mdf['transparency_mode' ],
                p_base_alpha = mdf['base_alpha'],
                p_black_point = mdf['black_point' ],
                p_luminance_coefficients = mdf['luminance_coefficients' ],
                p_surface_alpha = mdf['surface_alpha' ],
                p_white_point = mdf['white_point'],
                p_transparencyMode = mdf['transparencyMode' ],
                p_reflection_intesnity = mdf['reflection_intesnity' ],
                p_hasHex = mdf['hasHex' ],
                p_hasTexture = mdf['hasTexture'],
                p_line_color = line_color,
                p_url_tex = mdf['path'],
                p_product = mdf['product_string']
            )
        )

    return ret

def plot_fig(source, flt, x_axis, y_axis):
    hover = HoverTool(
            tooltips=[
                ("name", "@p_name"),
                ("index", "$index"),
               ("(x,y)", "($x, $y)"),
                ("(r,g,b)","(@cR, @cG, @cB)"),
#                 Props
                ("alpha", "@p_alpha"),
                ("diffuse_intensity", "@p_diffuse_intensity"),
                ("metalness", "@p_metalness"),
                ("reflection_intensity", "@p_reflection_intensity"),
                ("roughness", "@p_roughness"),
                ("mask_for_luminance", "@p_mask_for_luminance"),
                ("luminance_offset", "@p_luminance_offset"),
                ("transparency_mode", "@p_transparency_mode"),
                ("base_alpha", "@p_base_alpha"),
                ("black_point", "@p_black_point"),
                ("luminance_coefficients", "@p_luminance_coefficients"),
                ("surface_alpha", "@p_surface_alpha"),
                ("white_point", "@p_white_point"),
                ("transparencyMode", "@p_transparencyMode"),
                ("reflection_intesnity", "@p_reflection_intesnity"),
                ("hasHex", "@p_hasHex"),
                ("hasTexture", "@p_hasTexture"),
                ("url_tex", "@p_url_tex")
            ]
        )

    pw = 900
    ph = 684

    p = figure(
            title="MATERIAL EXPLORER", toolbar_location="above",
            tools=[
                'pan',
                'box_zoom',
                'wheel_zoom',
                'box_select',
                'tap',
                'save',
                'reset',
                hover,
                'lasso_select'
            ],
            plot_width=pw, plot_height=ph
    )

    view = CDSView(source=source, filters=[BooleanFilter(flt)])

    if x_axis:
        p.add_layout(
            Title(
                text=list(column_axis_dict.keys())[list(column_axis_dict.values()).index(x_axis)],
                align="center"),
                "below"
            )
    else:
        x_axis = "x"

    if y_axis:
        p.add_layout(
            Title(
                text=list(column_axis_dict.keys())[list(column_axis_dict.values()).index(y_axis)],
                align="center"),
                "left"
            )
    else:
        y_axis = "y"

    p.circle(
        x_axis,
        y_axis,
        fill_color='c',
        line_color='p_line_color',
        size=10,
        source=source,
        view=view
        ) # fill color is weird

    # style
    p.title.align = "left"
    p.title.text_font_size = "25px"

    # defaults
    p.toolbar.active_scroll = p.select_one(WheelZoomTool)

    return p

def plot_hist(mdf, flt, field):
    mdf[field].hist(bins=20, label="original")
    mdf[field][flt].hist(bins=20, label="filter")
    plt.legend()
    plt.title(field)

def get_mat_count(frame_count):
    """ desc """
    return pn.Column(pn.pane.Markdown(f"""Showing **{frame_count}** Materials"""))
