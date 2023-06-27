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

def calculate_av(jumlah_titran, faktor_buret, faktor_NaOH, berat_sampel):
    try:
        return round((jumlah_titran * faktor_buret * faktor_NaOH * 5.61) / berat_sampel, 4)
    except ZeroDivisionError:
        st.error("Cannot calculate AV: berat_sampel should not be zero")

def app():
    # logging.info('Acid Value Page Started')
    st.title('Acid Value')
    st.write('This is the Acid Value Calculator Page.')

    df = conn.query("SELECT * FROM av_temp")
    active_df = df[['sec_item_num', 'nama_item', 'LOT']].drop_duplicates()

    opsi = st.radio('Pilih sampel', options=['sampel baru', f'sampel aktif ({len(active_df)})'], horizontal=True, label_visibility='hidden')

    if opsi == 'sampel baru':
        input_values = {'sec_item_num': '', 'nama_item': '', 'LOT': ''}

    else:  # if opsi == 'sampel aktif'
        def combine_columns(row):
            return str(row['nama_item']) + ' (' + str(row['LOT']) + ')'

        combined_list = active_df.apply(combine_columns, axis=1).tolist()
        selected_sample = st.selectbox('Pilih Sampel', options=combined_list, index= len(active_df)-1)
        selected_row = df.loc[(df['nama_item'] + ' (' + df['LOT'] + ')') == selected_sample]
        if not selected_row.empty:
            input_values = {label: selected_row[label].values[0] for label in ['sec_item_num', 'nama_item', 'LOT']}

            displayed_df = df[(df['nama_item'] == input_values['nama_item']) & (df['LOT'] == input_values['LOT'])].sort_values(by='timestamp', ascending=True)
            st.table(displayed_df[['sec_item_num', 'nama_item', 'LOT', 'timestamp', 'suhu', 'AV', 'keterangan']])
            if st.button("Submit to database"):
                try:
                    with conn.session as session:
                        displayed_df.iloc[:, 1:].to_sql('av', con=engine, if_exists='append', index=False)
                        session.execute(text("DELETE FROM av_temp WHERE nama_item=:n1 AND LOT=:n2"), {"n1": input_values['nama_item'], "n2": input_values['LOT']})
                        st.success("Data successfully moved from av_temp to av in the database.")
                        st.cache_data.clear()
                        st.experimental_rerun()
                except Exception as e:
                    st.error(f"An error occurred: {e}")
        else:
            st.warning('Tidak ada sampel aktif saat ini, mohon pilih opsi (sampel baru)')


    #####################################################
    with st.container() as input_section:
        col1, col2 = st.columns(2)

        with col1:
            sec_item_num = st.text_input("Second item number", value=input_values['sec_item_num'], disabled=(opsi == 'sampel aktif'))
            nama_item = st.text_input("Nama item", value=input_values['nama_item'], disabled=(opsi == 'sampel aktif'))
            LOT = st.text_input("LOT", value=input_values['LOT'], disabled=(opsi == 'sampel aktif'))
            faktor_buret = st.number_input("Faktor buret", format='%f')
            faktor_NaOH = st.number_input("Faktor NaOH", format='%f')

        with col2:
            suhu = st.text_input('Suhu')
            berat_sampel = st.number_input("Berat sampel", format='%f')
            jumlah_titran = st.number_input("Jumlah titran", format='%f')
            if berat_sampel > 0 and jumlah_titran > 0:
                AV = calculate_av(jumlah_titran, faktor_buret, faktor_NaOH, berat_sampel)
                st.text(f"nilai Acid Value: {AV}")
            keterangan = st.text_input('keterangan')
            submitted = st.button('submit')

    if submitted:
        if AV and sec_item_num != '' and nama_item != '' and LOT != '':
            with conn.session as session:
                session.execute(text("""INSERT INTO av_temp (sec_item_num, nama_item, LOT, suhu, FAKTOR_BURET, FAKTOR_NaOH, berat_sampel, jumlah_titran, AV, keterangan) 
                                        VALUES (:n1, :n2, :n3, :n4, :n5, :n6, :n7, :n8, :n9, :n10);"""), 
                                        {"n1":sec_item_num, "n2":nama_item, 
                                        "n3":LOT, "n4":suhu, "n5": faktor_buret,
                                        "n6": faktor_NaOH, "n7":berat_sampel, 
                                        "n8":jumlah_titran, "n9":AV, "n10":keterangan
                                        })
            st.success('Yeay, data has been successfully inserted!')
            time.sleep(2)
            st.cache_data.clear()
            st.experimental_rerun()
        else:
            st.warning('Mohon lengkapi form di atas')
        

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app()