import streamlit as st
import pandas as pd

df = pd.read_excel('acuan.xlsx')
# print(dataframe)

st.dataframe(
    df,
    column_config={
        "Flammable": st.column_config.CheckboxColumn(
        "Flammable",
        help="Select your **favorite** widgets",
        default=False
        ),
        "Irritant": st.column_config.CheckboxColumn(
        "Irritant",
        help="Select your **favorite** widgets",
        default=False
        ),
        "MSDS": st.column_config.LinkColumn(
        "Trending apps",
        help="The top trending Streamlit apps",
        validate="^https://[a-z]+\.streamlit\.app$",
        )
        },
    hide_index = True
)