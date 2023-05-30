import streamlit as st
import pickle
import pandas as pd
import re
from streamlit_player import st_player

st.set_page_config(
    page_title="OnlyRice------------------------------------",
    page_icon="🍲")

# CSS to inject contained in a string
hide_table_row_index = """
            <style>
            thead tr th:first-child {display:none}
            tbody th {display:none}
            </style>
            """
st.markdown(hide_table_row_index, unsafe_allow_html=True)

# Save into pickle
with open('category_recipe_dict.pickle', 'rb') as handle:
    category_recipe_dict = pickle.load(handle)

col1, col2, col3, col4 = st.columns([6,1,1,1])

with col1:
    st.header("幫你規劃你的")
with col2:
    st.button("早餐")
with col3:
    st.button("午餐")
with col4:
    st.button("晚餐")

### User Input Section
col1, col2 = st.columns([1,2])

with col1:
    N_people = st.number_input("幾人吃飯", min_value=1, max_value=9, value=1)

with col2:
    tmp_list = ["豬肉","花生"]
    choice = st.multiselect("避開:",tmp_list, default=["花生"])

###


cat_index = ["-1", "0", "1", "2", "3", "4", "5", "6", "7"]
cat_name = ['所有食譜', '蔬果', '海產', '肉類', '家禽', '小吃', '湯品', '鐵質豐富', '其他']
cat_name_dict = dict(zip(cat_index,cat_name))

# Create all tabs
tabs = st.tabs(cat_name)
tab_number_dict = dict()

for cat_i, tab in enumerate(tabs):
    
    cat = cat_index[cat_i]
    tab_number_dict[cat] = dict()

    with tab:
        

        for i in range(5):

            with st.container():
                col1, col2 = st.columns([1,5])

                with col1:
                    st.image(
                        category_recipe_dict[cat][i]["image_url"],
                        use_column_width = "auto"
                    )
                    tab_number_dict[cat][i] = st.number_input("幾人份", min_value=0, max_value=9, value=0,key=f"{cat}-{i}", label_visibility ="collapsed")

                with col2:
                    recipe_name = category_recipe_dict[cat][i]["recipe_name"]

                    with st.expander(recipe_name):
                        for key, df_table in category_recipe_dict[cat][i].items():
                            if key not in  ["recipe_name","image_url","video_url"]:
                                st.table(df_table)

                        video_url = category_recipe_dict[cat][i]["video_url"]
                        if video_url:
                            st_player(video_url, key = f"{cat}-{i}-video")



def extract_integer(string):
    try:
        integer = re.findall(r'\d+', string)[0]
        integer = int(integer) 
    except:
        integer = int(string) 

    return integer

def remove_bracket(text):

    text = text.split("（")[0]
    text = text.split("(")[0]
    
    return text

def update_health_summary(df_table, recipe_number):

    for index, row in df_table.iterrows():
        item = row["每一份"]
        value = row[""]

        if item in health_summary:
            health_summary[item] += extract_integer(value) * recipe_number
        else:
            health_summary[item] = extract_integer(value) * recipe_number

def update_ingredients_summary(df_table, recipe_number):

    for index, row in df_table.iterrows():

        item = remove_bracket(row["材料"]) + "(克)"
        value = row[""]

        if item in ingredients_summary:
            ingredients_summary[item] += extract_integer(value) * recipe_number
        else:
            ingredients_summary[item] =extract_integer(value) * recipe_number


ingredients_summary = dict()
health_summary = dict()
selected_recipe = dict()

sidebar = st.sidebar

for cat_i, recipe_list in tab_number_dict.items():
    for recipe_i, recipe_number in recipe_list.items():
        if recipe_number:
            
            try:
                recipe_name = category_recipe_dict[cat_i][recipe_i]["recipe_name"]
                selected_recipe[recipe_name] = int(recipe_number)
            
                health_table = category_recipe_dict[cat_i][recipe_i]["每一份"]
                update_health_summary(health_table, recipe_number)

                ingredient_table = category_recipe_dict[cat_i][recipe_i]["材料"]
                update_ingredients_summary(ingredient_table, recipe_number)

            except:
                pass


def percentage_to_text(val):

    lower = 0.7
    upper = 1.3

    if val<= upper and val >= lower:
        return "(適中)"
    elif val < lower:
        return "(低於推薦)"
    elif val > upper:
        return "(過量)"

# Define a function to apply style to a column
def style_column(val):

    if "適中" in val:
        return "color: green"
    elif "低於推薦" in val:
        return "color: blue"
    elif "過量" in val:
        return "color: red"


with sidebar:

    if selected_recipe:
        with st.expander("食谱", expanded=True):
            st.table(pd.DataFrame(selected_recipe.items(), columns=['食谱', '份']))

    if ingredients_summary:
        with st.expander("材料", expanded=True):
            st.table(pd.DataFrame(ingredients_summary.items(), columns=['材料', '分量']))

    if health_summary:
        with st.expander("营养", expanded=True): 
            df_table = pd.DataFrame(health_summary.items(), columns=['营养', ''])
            
            df_table["guide"] = [2000, 300, 50, 90, 33, 6000]
            df_table["guide"] *= N_people
            df_table["guide"] *= 0.4 
            
            df_table["percentage"] = (df_table[""] / df_table["guide"])
            df_table["text"] = df_table["percentage"].apply(percentage_to_text)
            df_table[""] = df_table[""].astype(str) + df_table["text"]


            df_table = df_table[["营养",""]].copy()
            styled_df = df_table.style.applymap(style_column, subset=[""])
            st.table(styled_df)


    if ingredients_summary or health_summary:
        st.write("發送至我的Whatsapp")
        col1, col2 = st.columns([6,1])
        with col1:
            st.text_input(
            "Placeholder for the other text input widget",
            "+6969 669 6969",
            key="placeholder",
            label_visibility ="collapsed"
            )
        with col2:
            st.button("💌")

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 