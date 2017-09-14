import unreal_engine as ue
from unreal_engine import SWindow, SBox, SPythonComboBox, STextBlock, SBorder, SVerticalBox, SEditableTextBox, SHorizontalBox, SButton, SPythonListView
from unreal_engine.enums import EHorizontalAlignment, EVerticalAlignment
from unreal_engine import FLinearColor
from unreal_engine.structs import SlateColor, Margin
import xmlrpc.client
from unreal_engine.classes import ActorComponent
from collections import Counter
from unreal_engine.classes import Material
from ast import literal_eval


import sys

print('version :', sys.version)
world = ue.get_editor_world()


def get_mbu_product():
	print("get_mbu_product")
	actors = world.all_actors()
	
	#print("",[ a.get_actor_component_by_type('StaticMesh') for a in actors])
	mbu_actors = filter(lambda a : len(a.tags)>1 and a.tags[0]=='mbu', actors)
	print("=====>",mbu_actors)
	return [a.get_property('ref') for a in mbu_actors]


url = 'http://pos.agiloc.org:9090'
db = '00mbu_test'
username = 'admin'
password = 'MBU@ao2017'
 
common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
print('version',common.version())

uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))


def get_projects():
	imported= False  
	leads= models.execute_kw(
	db, uid,password, 'crm.lead', 'search_read',
	[[['is_blender_lead','=',True]]], {'fields': ['id','name','create_date']})
	return leads


projects= [str((p['id'],p['name'])) for p in get_projects()]


class DynamicComboBox:

    def __init__(self, items):
        self.box = SBox(height_override=100, min_desired_width=400)
        self.items = items
        self.build_combo_box()
        self.combo_box.set_selected_item(self.items[0])

    def get_widget(self):
        return self.box

    def generate_combo_box_widget(self, item):
        return STextBlock(text=item)

    def append(self, item, committed):
        if item and item not in self.items:
            self.items.append(item)
            self.build_combo_box()
            self.combo_box.set_selected_item(item)

    def get_current_item(self):
        return self.combo_box.get_selected_item()

    def build_combo_box(self):
        self.combo_box = SPythonComboBox(options_source=self.items, on_generate_widget=self.generate_combo_box_widget, content=STextBlock(text=self.get_current_item))
        self.box.set_content(self.combo_box)


class ListView:

    def __init__(self, items):
        self.box = SBox(height_override=100, min_desired_width=400)
        self.items = items
        self.build_list_view()
        self.combo_box.set_selected_item(self.items[0])

    def get_widget(self):
        return self.box

    def generate_list_view_widget(self, item):
        return STextBlock(text=item)

    def append(self, item, committed):
        if item and item not in self.items:
            self.items.append(item)
            self.build_combo_box()
            self.combo_box.set_selected_item(item)

    def get_current_item(self):
        return self.combo_box.get_selected_item()

    def build_list_view(self):
        self.list_view = SPythonListView(list_items=self.items, on_generate_widget=self.generate_list_view_widget)
        self.box.set_content(self.combo_box)

dynamic_combo_box = DynamicComboBox(projects)

list_view = ListView(projects)

def update_prd_odoo():
	lead_id = literal_eval(dynamic_combo_box.get_current_item())
	print ('dynamic_combo_box',lead_id[0])
	print('products :', dict(Counter(get_mbu_product())))
	odoo_context={'blender_select':{'name':'blabla','blender_file':'test','products':dict(Counter(get_mbu_product()))}}
	print(odoo_context) 
	leads= models.execute_kw(db, uid, password, 'crm.lead.blender.model', 'save_last_blender_model',[lead_id[0], odoo_context])



# the final backslash is required for the 'pretty syntax'
SWindow(client_size=(1024, 576), title='DynamicComboBox')\
(
    SBorder(color_and_opacity=FLinearColor(1, 1, 1, 1), border_background_color=SlateColor(SpecifiedColor=FLinearColor(1, 1, 1, 1)))
    (
        SBox(h_align=EHorizontalAlignment.HAlign_Center, v_align=EVerticalAlignment.VAlign_Center)
        (
            SBorder(color_and_opacity=FLinearColor(1, 1, 1, 1), border_background_color=SlateColor(SpecifiedColor=FLinearColor(1, 1, 1, 1)))
            (
             				SVerticalBox()
                (
                                      dynamic_combo_box.get_widget()
                )
(list_view.get_widget())
                (
                    SHorizontalBox()(
                        SButton(text='Upload', on_clicked=update_prd_odoo),
                        fill_width=0.2
                    )
                )
            )
        )
    )
)
