from mdf_util import mdf, get_data_source

def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

def color_filter(hex_color_value, color_tolerance):
    # color_tolerance = 0.20
    rgb_color_value = hex_to_rgb(hex_color_value)
    
    flt = (((mdf['COL_R'] >= rgb_color_value[0]/255.0 - color_tolerance) &
    (mdf['COL_R'] <= rgb_color_value[0]/255.0 + color_tolerance)) &
    ((mdf['COL_G'] >= rgb_color_value[1]/255.0 - color_tolerance) &
    (mdf['COL_G'] <= rgb_color_value[1]/255.0 + color_tolerance)) &
    ((mdf['COL_B'] >= rgb_color_value[2]/255.0 - color_tolerance) &
    (mdf['COL_B'] <= rgb_color_value[2]/255.0 + color_tolerance)))
    return flt