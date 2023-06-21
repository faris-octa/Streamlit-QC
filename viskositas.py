import streamlit as st
import pandas as pd
from sqlalchemy.sql import text
from sqlalchemy import create_engine
import numpy as np
import time
import logging

# Database connection string
conn = st.experimental_connection("qcdb", type="sql", autocommit=True)
engine = create_engine("mysql+mysqldb://inkaliqc:qcoke@192.168.0.70/qc")

# Viscosity factor
visc_factor_data = {
    "speed": [0.3, 0.6, 1.5, 3, 6, 12, 30, 60, 0.3, 0.6, 1.5, 3, 6, 12, 30, 60, 0.3, 0.6, 1.5, 3, 6, 12, 30, 60, 0.3, 0.6, 1.5, 3, 6, 12, 30, 60],
    "spindle": [1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4],
    "factor": [200, 100, 40, 20, 10, 5, 2, 1,
            1000, 500, 200, 100, 50, 25, 10, 5,
            4000, 2000, 800, 400, 200, 100, 40, 20,
            20000, 10000, 4000, 2000, 1000, 500, 200, 100]
}
v_factor_df = pd.DataFrame(visc_factor_data)

# Viscosity calculation
def calculate_viscosity(spindle, speed, measurement):
    df_row = v_factor_df[(v_factor_df['spindle'] == spindle) & (v_factor_df['speed'] == speed)]
    factor = int(df_row['factor'])
    viscosity = factor * measurement
    return viscosity

def app():
    # logging.info('Viskositas Page Started')
    st.title('Viscosity')
    st.write('This is the Viscosity Calculator Page.')

    try:
        df = conn.query("SELECT * FROM viscosity_temp")
        active_df = df[['sec_item_num', 'nama_item', 'LOT']].drop_duplicates()
    except:
        None

    #########
    opsi = st.radio('Pilih sampel', options=[f'sampel aktif ({len(active_df)})', 'sampel baru'], horizontal=True, label_visibility='hidden')
    if opsi == 'sampel baru':
        input_values = {'sec_item_num': '', 'nama_item': '', 'LOT': ''}
    else:  # if opsi == 'sampel aktif'
        def combine_columns(row):
            return str(row['nama_item']) + ' (' + str(row['LOT']) + ')'

        combined_list = active_df.apply(combine_columns, axis=1).tolist()
        selected_sample = st.selectbox('Pilih Sampel', options=combined_list, index= len(active_df)-1)
        selected_row = df.loc[(df['nama_item'] + ' (' + df['LOT'] + ')') == selected_sample]
        input_values = {label: selected_row[label].values[0] for label in ['sec_item_num', 'nama_item', 'LOT']}

        displayed_df = df[(df['nama_item'] == input_values['nama_item']) & (df['LOT'] == input_values['LOT'])].sort_values(by='timestamp', ascending=True)
        st.table(displayed_df)

    #########
        if st.button("Submit to database"):
            try:
                with conn.session as session:
                    displayed_df.iloc[:, 1:].to_sql('viscosity', con=engine, if_exists='append', index=False)
                    session.execute(text("DELETE FROM viscosity_temp WHERE nama_item=:n1 AND LOT=:n2"), {"n1": input_values['nama_item'], "n2": input_values['LOT']})
                    st.success("Data successfully moved from viscosity temp to av in the database.")
                    st.cache_data.clear()
                    st.experimental_rerun()
            except Exception as e:
                st.error(f"An error occurred: {e}")











    with st.container() as input_section:
        col1, col2 = st.columns(2)

        with col1:
            sec_item_num = st.text_input("Second item number")
            nama_item = st.text_input("Nama item")
            LOT = st.text_input("LOT")

        with col2:
            spindle = st.selectbox('tipe spindle', options=(1, 2, 3, 4))
            speed = st.selectbox('speed', options=(0.3, 0.6, 1.5, 3, 6, 12, 30, 60))
            measurement = st.text_input("measurement")
            if measurement:
                viscosity = calculate_viscosity(spindle, speed, int(measurement))
                st.text(f"nilai viskositas: {viscosity} mPas")
            keterangan = st.text_input('keterangan')
        
            submitted = st.button('submit')

        if submitted:
            print(sec_item_num, nama_item, LOT, spindle, speed, viscosity, keterangan)
            with conn.session as session:
                session.execute(text("""INSERT INTO viscosity_test (sec_item_num, nama_item, LOT, spindle, speed, viscosity, keterangan) 
                                    VALUES (:n1, :n2, :n3, :n4, :n5, :n6, :n7);"""), 
                                    {"n1":sec_item_num, "n2":nama_item, 
                                    "n3":LOT, "n4":spindle, "n5": speed,
                                    "n6": viscosity, "n7":keterangan
                                    })
            st.success('Yeay, data has been successfully inserted!')
            st.experimental_rerun()
    

if __name__ == "__main__":
    # Setup logging configuration
    logging.basicConfig(level=logging.INFO)
    app()