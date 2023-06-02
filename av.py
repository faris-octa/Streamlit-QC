import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
import logging

def calculate_av(jumlah_titran, faktor_buret, faktor_NaOH, berat_sampel):
    try:
        return round((jumlah_titran * faktor_buret * faktor_NaOH * 5.61) / berat_sampel, 4)
    except ZeroDivisionError:
        st.error("Cannot calculate AV: berat_sampel should not be zero")

def load_data():
    query = "SELECT * FROM av_temp"
    return query_db(query)

def insert_db(query, data):
    logging.info("Inserting data into database")
    try:
        with sqlite3.connect('qc.db') as conn:
            conn.execute(query, data)
    except Exception as e:
        logging.error("Error occurred during database operation", exc_info=True)
        raise e
    logging.info("Data successfully inserted")

def query_db(query):
    logging.info("Querying database")
    try:
        with sqlite3.connect('qc.db') as conn:
            df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        logging.error("Error occurred during database operation", exc_info=True)
        raise e
    logging.info("Database query successful")

def app():
    logging.info('Acid Value Page Started')
    st.title('Acid Value')
    st.write('This is the Acid Value Calculator Page.')

    df = load_data()
    active_df = df[['sec_item_num', 'nama_item', 'LOT']].drop_duplicates()

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

        if st.button("Submit to database"):
            try:
                with sqlite3.connect('qc.db') as conn:
                    displayed_df.iloc[:, 1:].to_sql('av', conn, if_exists='append', index=False)
                    conn.execute(f"DELETE FROM av_temp WHERE nama_item='{input_values['nama_item']}' AND LOT='{input_values['LOT']}'")
                    conn.commit()
                    st.success("Data successfully moved from av_temp to av in the database.")
                    st.experimental_rerun()
            except Exception as e:
                st.error(f"An error occurred: {e}")

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
        plus_data = (sec_item_num, nama_item, LOT, suhu, faktor_buret, faktor_NaOH, berat_sampel, jumlah_titran, AV, keterangan)
        if AV:
            query = '''INSERT INTO av_temp (sec_item_num, nama_item, LOT, suhu, FAKTOR_BURET, FAKTOR_NaOH, berat_sampel, jumlah_titran, AV, keterangan) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
            insert_db(query, plus_data)
            st.success('Yeay, data has been successfully inserted!')
            st.experimental_rerun()
        else:
            st.warning('Mohon lengkapi form di atas')

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app()
