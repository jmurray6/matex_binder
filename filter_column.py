import os
from plot_util import (
    get_mat_count,
    create_source,
    plot_fig,
    get_texture_image_path,
    logger,
    FRAME_PATH
)
from color_util import color_filter
from mdf_util import mdf, get_data_source
import panel as pn
import pandas as pd
from CONSTANTS import column_axis_dict

BLANK_AXES_DICT = {"x": None, "y": None}

class SliderGroup:

    def __init__(self, name, min_value, max_value, step):
        self.name = name
        self.title = f"#### {name.upper()}"
        self.min_value = min_value
        self.max_value = max_value
        self.step = step
        self.apply = pn.widgets.Checkbox(width=5)
        self.min_slider = pn.widgets.FloatSlider(
            name='Min',
            start=min_value,
            end=max_value,
            step=step,
            value=min_value
            )
        self.max_slider = pn.widgets.FloatSlider(
            name='Max',
            start=min_value,
            end=max_value,
            step=step,
            value=max_value
            )
        self.column = pn.Column(
            pn.Row(self.apply, self.title),
            self.min_slider,
            self.max_slider,
            css_classes=['panel-widget-box'],
            margin=10
            )

    def reset(self):
        self.min_slider.value = 0 # self.min_value
        self.max_slider.value = 1 # self.max_value
        self.apply.value = False

class PresetButton:

    def __init__(self, name, on_click):
        self.name = name
        self.on_click = on_click
        self.button = pn.widgets.Button(name=name)
        self.button.on_click(on_click)

class FiltersColumn:

    def __init__(self, pn_row_fig, pn_row_results):
        self.header_row = pn.Row("### FILTERS", ".")
        self.filters = pn.Column(
            self.header_row,
            sizing_mode='stretch_both',
            height_policy='max',
            css_classes=['vertical-widget-box']
            )
        # self.filterUtils = pn.Column(sizing_mode='stretch_both', height_policy='max')
        self.pn_row_fig = pn_row_fig
        self.pn_row_results = pn_row_results
        self.source = None
        self.data_objects = None

        self.metalness_slider_group = SliderGroup("metalness", 0, 1, 0.01)

        self.roughness_slider_group = SliderGroup("roughness", 0, 1, 0.01)

        # self.entityTypeDropdown = pn.widgets.Select(name='Entity Type', options=entityTypeList)
        # self.entityTypeApply = pn.widgets.Checkbox(width=5)
        # self.entitySelectorRow = pn.Row(self.entityTypeApply, self.entityTypeDropdown)

        self.has_texture_dropdown = pn.widgets.Select(name="Has Texture", options=[True, False])
        self.has_texture_apply = pn.widgets.Checkbox(width=5)
        self.has_texture_row = pn.Row(
            self.has_texture_apply,
            self.has_texture_dropdown,
            css_classes=['panel-widget-box'],
            margin=10
            )

        self.keyword_search_box = pn.widgets.TextInput(name='Keyword 1', value='Enter Keywords Here')
        self.keyword_apply = pn.widgets.Checkbox(width=5)
        self.add_keyword_button = pn.widgets.Button(name='Add Keyword')
        self.extra_keyword_buttons = []
        self.keyword_row = pn.Column(
            pn.Row(self.keyword_apply, self.keyword_search_box),
            pn.Row(self.add_keyword_button),
            css_classes=['panel-widget-box'],
            margin=10
            )

        # product search box
        self.product_search_box = pn.widgets.TextInput(name='Product Search', value='Enter Keywords Here')
        self.product_apply = pn.widgets.Checkbox(width=5)
        self.product_row = pn.Column(
            pn.Row(self.product_apply, self.product_search_box),
            css_classes=['panel-widget-box'],
            margin=10
            )

        self.color_picker = pn.widgets.ColorPicker(name='Color Picker')
        self.color_apply = pn.widgets.Checkbox(width=5)
        self.color_tolerance_slider = pn.widgets.FloatSlider(
            name='Color Tolerance',
            start=0,
            end=1,
            step=0.01,
            value=0.05
            )
        self.color_row = pn.Column(
            pn.Row(self.color_apply, self.color_picker), 
            pn.Row(self.color_tolerance_slider), 
            css_classes=['panel-widget-box'], 
            margin=10
            )

        self.x_axis_dropdown = pn.widgets.Select(name='X Axis', options=list(column_axis_dict.keys()))
        self.x_axis_apply = pn.widgets.Checkbox(width=5)
        self.x_axis_row = pn.Column(
            pn.Row(self.x_axis_apply, self.x_axis_dropdown),
            css_classes=['panel-widget-box'],
            margin=10
            )

        self.y_axis_dropdown = pn.widgets.Select(name='Y Axis', options=list(column_axis_dict.keys()))
        self.y_axis_apply = pn.widgets.Checkbox(width=5)
        self.y_axis_row = pn.Column(
            pn.Row(self.y_axis_apply, self.y_axis_dropdown), 
            css_classes=['panel-widget-box'], 
            margin=10
            )

        self.run_button = pn.widgets.Button(name='APPLY')
        self.clear_filters_button = pn.widgets.Button(name='CLEAR FILTERS')
        self.filter_utils_column = pn.Column(
            self.run_button,
            self.clear_filters_button,
            css_classes=['panel-widget-box'],
            margin=10
            )

        self.preset_button_1 = PresetButton("Madison Texture", self.apply_preset_1)
        self.preset_button_2 = PresetButton("Preset 2", self.apply_preset_2)
        self.preset_button_3 = PresetButton("Preset 3", self.apply_preset_3)
        self.preset_button_4 = PresetButton("Preset 4", self.apply_preset_4)

        self.preset_column = pn.Column(
            "#### PRESETS",
            self.preset_button_1.button,
            self.preset_button_2.button,
            self.preset_button_3.button,
            self.preset_button_4.button,
            css_classes=['panel-widget-box'],
            margin=10
            )

        self.the_rest_column = pn.Column(
            self.keyword_row,
            self.product_row,
            self.has_texture_row,
            self.color_row,
            self.x_axis_row,
            self.y_axis_row
            )

        self.fig = None
        self.create_column()
        self.apply_filters(None)

    def create_column(self): # need to clear everything. essentially reinitialize all components
        component_list = [
                # self.metalnessRow,
                self.metalness_slider_group.column,
                self.roughness_slider_group.column,
                # self.roughnessRow,
                # self.keyword_row,
                # # self.entitySelectorRow,
                # self.has_texture_row,
                # self.color_row,
                # self.x_axis_row,
                # self.y_axis_row,
                self.the_rest_column,
                self.filter_utils_column,
                self.preset_column,
                pn.pane.Markdown(".")
        ]

        for component in component_list:
            self.filters.append(component)

    def add_keyword_row(self, event):
        extra_keyword_button_id = len(self.extra_keyword_buttons)
        if extra_keyword_button_id > 4:
            return True
        search_box_title = f"Keyword {extra_keyword_button_id+2}"

        this_checkbox = pn.widgets.Checkbox(width=5)
        this_search_box = pn.widgets.TextInput(name=search_box_title, value='Enter Keywords Here')
        this_row = pn.Row(this_checkbox, this_search_box)

        keyword_button_dict = {
            "id": extra_keyword_button_id,
            "checkbox": this_checkbox,
            "keyword_search_box": this_search_box,
            "row": this_row
        }
        self.extra_keyword_buttons.append(keyword_button_dict)
        self.keyword_row.append(this_row)


    def apply_filters(self, event):
        flt = pd.Series([True]*len(mdf), index=mdf.index)

        if self.metalness_slider_group.apply.value:
            flt = flt & (mdf['metalness'] >= self.metalness_slider_group.min_slider.value) \
            & (mdf['metalness'] <= self.metalness_slider_group.max_slider.value)
        if self.roughness_slider_group.apply.value:
            flt = flt & (mdf['roughness'] >= self.roughness_slider_group.min_slider.value) \
            & (mdf['roughness'] <= self.roughness_slider_group.max_slider.value)
        if self.keyword_apply.value:
            flt = flt & (mdf['description_lower'].str.contains(self.keyword_search_box.value.lower()))
        if self.product_apply.value:
            flt = flt & (mdf['product_string_lower'].str.contains(self.product_search_box.value.lower()))
        # if self.entityTypeApply.value:
        #     flt = flt & (mdf["entity_type_string"].str.contains(self.entityTypeDropdown.value))
        if self.color_apply.value:
            flt = flt & (color_filter(self.color_picker.value, self.color_tolerance_slider.value))
        if self.has_texture_apply.value:
            flt = flt & (mdf["hasTexture"] == self.has_texture_dropdown.value)
        for extra_keyword_button in self.extra_keyword_buttons:
            if extra_keyword_button.get("checkbox").value:
                flt = flt & (mdf['description_lower'].str.contains(extra_keyword_button.get("keyword_search_box").value.lower()))
        axes_dict = {"x": None, "y": None}
        if self.x_axis_apply.value:
            axes_dict["x"] = column_axis_dict.get(self.x_axis_dropdown.value)
        if self.y_axis_apply.value:
            axes_dict["y"] = column_axis_dict.get(self.y_axis_dropdown.value)
        

        self.plot_with_filters(flt, axes_dict)
    
    def clear_filters(self, event):
        # self.metalnessApply.value = False
        self.metalness_slider_group.reset()
        self.roughness_slider_group.reset()
        # self.roughnessApply.value = False
        self.keyword_apply.value = False
        self.keyword_search_box.value = 'Enter Keywords Here'
        for extra_keyword_button in self.extra_keyword_buttons:
            self.keyword_row.remove(extra_keyword_button.get("row"))
        self.extra_keyword_buttons = []
        self.has_texture_apply.value = False
        self.color_apply.value = False
        self.x_axis_apply.value = False
        self.y_axis_apply.value = False
        

    def clear_filters_and_plot(self, event):
        flt = pd.Series([True]*len(mdf), index=mdf.index)
        self.clear_filters(None)
        self.plot_with_filters(flt, BLANK_AXES_DICT)
    
    def plot_with_filters(self, flt, axes_dict):
        self.header_row[-1] = (get_mat_count(flt.sum()))
        data_objects = self.get_data_objects()
        self.source = create_source(data_objects["mdf"])
        self.source.selected.on_change('indices', self.select)
        self.pn_row_fig.clear()
        x_axis = axes_dict.get("x")
        y_axis = axes_dict.get("y")
        self.pn_row_fig.append(pn.pane.Bokeh(plot_fig(self.source, flt, x_axis, y_axis)))
        
    def get_data_objects(self):
        if not self.data_objects:
            self.data_objects = {'mdf':get_data_source()}
        return self.data_objects
        
    def select(self, attr, old, new):
        if len(new) > 0:
            new_x = new[0]
        else:
            self.pn_row_results.clear()
            return True

        pane_list = []
        self.pn_row_results.clear()
        for val in new:
            try:
                frame_image_path = f"{os.path.join(FRAME_PATH, self.source.data['p_name'][val])}.png"
                frame_image_row = pn.pane.PNG(frame_image_path, width=417, height=167)
            except Exception as e:
                print(f"frame image row error: {e}")

            # if self.source.data['hasTexture']:
            # texture_image_row = pn.pane.PNG(get_texture_image_path(self.source.data['p_name'][val]), width=952, height=952) if self.source.data['p_hasTexture'][val]==True else None
            
            try:
                texture_image_row = pn.pane.PNG(
                    get_texture_image_path(
                        self.source.data['p_name'][val]
                    ),
                    width=300,
                    height=300
                    ) if self.source.data['p_hasTexture'][val]==True else None
            except Exception as e:
                print("texture_image_row error: ", e)
                texture_image_row = None
            # textureImagePath = f"{os.path.join(texturesPath), self.source.data['p_name'][val])}.png"
            logger.info(f"path: {frame_image_path}")
            pane_list.append(pn.Column(pn.pane.Markdown(f"""
            | Name | {self.source.data['p_name'][val]} |
            | ----------- | ----------- |
            | (r,g,b) | ({self.source.data['cR'][val]}, {self.source.data['cG'][val]}, {self.source.data['cB'][val]}) |
            | texture | {self.source.data['p_url_tex'][val]} |
            | product | {self.source.data['p_product'][val]} |
            """, style={'border': "2px solid black"}),
            frame_image_row,
            texture_image_row))
        for pane in pane_list:
            self.pn_row_results.append(pane)
    
    def apply_preset_1(self, event):
        self.clear_filters(None)

        self.has_texture_apply.value = True

        self.keyword_apply.value = True
        self.keyword_search_box.value = "madison"
        self.apply_filters(None)

    def apply_preset_2(self, event):
        self.clear_filters(None)

        self.metalness_slider_group.apply.value = True
        self.metalness_slider_group.min_slider.value = 0.2
        self.metalness_slider_group.max_slider.value = 0.8

        self.roughness_slider_group.apply.value = True
        self.roughness_slider_group.min_slider.value = 0.1
        self.roughness_slider_group.max_slider.value = 0.4

        self.keyword_apply.value = True
        self.keyword_search_box.value = "acetate"

        self.apply_filters(None)

    def apply_preset_3(self, event):
        self.clear_filters(None)

        self.metalness_slider_group.apply.value = True
        self.metalness_slider_group.min_slider.value = 0
        self.metalness_slider_group.max_slider.value = 0.5

        self.roughness_slider_group.apply.value = True
        self.roughness_slider_group.min_slider.value = 0.1
        self.roughness_slider_group.max_slider.value = 0.4

        self.keyword_apply.value = True
        self.keyword_search_box.value = "hugo boss"

        self.apply_filters(None)
    
    def apply_preset_4(self, event):
        self.clear_filters(None)
        self.metalness_slider_group.apply.value = True
        self.metalness_slider_group.min_slider.value = 0
        self.metalness_slider_group.max_slider.value = 0.8

        self.keyword_apply.value = True
        self.keyword_search_box.value = "gold"
        self.apply_filters(None)



        # flt = flt & (mdf['metalness'] >= self.metalness_slider_group.min_slider.value) & (mdf['metalness'] <= self.metalness_slider_group.max_slider.value)
        # self.plot_with_filters(flt, BLANK_AXES_DICT)

    