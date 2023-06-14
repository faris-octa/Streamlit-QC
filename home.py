import streamlit as st
import pandas as pd
from sqlalchemy.sql import text
import time
import numpy as np
import logging

# Database connection string
conn = st.experimental_connection("qcdb", type="sql", autocommit=True)

def app():
    logging.info('Solid Content Page Started')
    st.title('Home')

    opsi = ['Solid Content', 'Acid Value', 'Total Amine']
    sample = st.selectbox('Pilih jenis pengukuran',
                                options = opsi,
                                key='sample_to_remove')
    
    if sample == 'Solid Content':
        df = conn.query("SELECT * FROM solid_contents_test")
    elif sample == 'Acid Value':
        df = conn.query("SELECT * FROM av_test")
    elif sample == 'Total Amine':
        df = conn.query("SELECT * FROM ta")

    st.table(df)
    
    # # Creating new row for validating 
    # new_row = pd.Series([None, None, None, None, None,
    #                     None, None, None, None, None], index=df.columns)
    # new_row_df = pd.DataFrame([new_row])                    
    # df = pd.concat([df, new_row_df], ignore_index=True)
    # df.index = np.arange(1, len(df)+1)

    # # displayed table
    # displayed_df = df[['sec_item_num', 'nama_item', 'LOT', 'berat_wadah', 'berat_sampel_basah', 'timestamp_init']][:-1]
    # displayed_df = displayed_df.rename(columns={
    #     'sec_item_num': 'Second Item Number',
    #     'nama_item': 'Nama Item',
    #     'LOT': 'LOT',
    #     'berat_wadah': 'Berat Wadah (g)',
    #     'berat_sampel_basah': 'Berat Sampel (g)',
    #     'timestamp_init': 'Waktu Mulai'
    #     })
    # st.table(displayed_df)

if __name__ == "__main__":
    # Setup logging configuration
    logging.basicConfig(level=logging.INFO)
    app()