import streamlit as st
import sqlite3
import pandas as pd
import time
import numpy as np
import logging

# Database connection string
DB_CONNECTION_STRING = 'qc.db'

def connect_to_db():
    """
    Connects to the SQLite database and returns the connection object.
    """
    return sqlite3.connect(DB_CONNECTION_STRING)

def get_data_from_db(query):
    """
    Fetches data from the SQLite database based on the provided SQL query.
    """
    with connect_to_db() as conn:
        return pd.read_sql_query(query, conn)

def insert_into_db(query, data):
    """
    Inserts data into the SQLite database based on the provided SQL query and data.
    """
    try:
        with connect_to_db() as conn:
            c = conn.cursor()
            c.execute(query, data)
    except Exception as e:
        logging.error(f"An error occurred when trying to insert data into the database: {e}")
        st.error(f"An error occurred: {e}")

def update_db(query, data):
    """
    Updates data in the SQLite database based on the provided SQL query and data.
    """
    try:
        with connect_to_db() as conn:
            c = conn.cursor()
            c.execute(query, data)
    except Exception as e:
        logging.error(f"An error occurred when trying to update data in the database: {e}")
        st.error(f"An error occurred: {e}")

def app():
    logging.info('Solid Content Page Started')
    st.title('Solid Content')
    st.write('This is the Solid Content Calculator Page.')

    query = "SELECT * FROM solid_contents WHERE berat_sampel_kering IS NULL"
    df = get_data_from_db(query)
    
    # Creating new row for validating 
    new_row = pd.Series([None, None, None, None, None,
                        None, None, None, None, None], index=df.columns)
    new_row_df = pd.DataFrame([new_row])                    
    df = pd.concat([df, new_row_df], ignore_index=True)
    df.index = np.arange(1, len(df)+1)

    # displayed table
    displayed_df = df[['sec_item_num', 'nama_item', 'LOT', 'berat_wadah', 'berat_sampel_basah', 'timestamp_init']][:-1]
    displayed_df = displayed_df.rename(columns={
        'sec_item_num': 'Second Item Number',
        'nama_item': 'Nama Item',
        'LOT': 'LOT',
        'berat_wadah': 'Berat Wadah (g)',
        'berat_sampel_basah': 'Berat Sampel (g)',
        'timestamp_init': 'Waktu Mulai'
        })
    st.table(displayed_df)

    # Fitur input sampel dan update sampel
    col1, col2 = st.columns(2)

    with col1:
        with st.expander("Tambah sampel baru"):
            with st.form("add_sample", clear_on_submit=True):
                sec_item_num = st.text_input('Second Item Number')
                nama_item = st.text_input('Nama Item')
                lot = st.text_input('LOT')
                berat_wadah = st.number_input("Berat Wadah", format='%f')
                berat_sampel_basah = st.number_input("Berat Sampel Basah", format='%f')

                submitted = st.form_submit_button("Submit")
            if submitted:
                data = (sec_item_num, nama_item, lot, berat_wadah, berat_sampel_basah)
                query = '''INSERT INTO solid_contents (sec_item_num, nama_item, LOT, berat_wadah, berat_sampel_basah)
                            VALUES (?, ?, ?, ?, ?)'''
                insert_into_db(query, data)
                st.success('Data berhasil ditambahkan')
                time.sleep(2)
                st.experimental_rerun()

    with col2:
        with st.expander("Input sampel kering"):
            col_1, col_2 = st.columns(2)
            with col_1:
                sample = st.selectbox('Pilih nama item',
                                options = df['nama_item'].unique(),
                                format_func=lambda x: 'Select...' if x == None else x,
                                index= len(df['nama_item'].unique()) - 1,
                                key='sample_to_remove')
                
            with col_2:
                lot = st.selectbox('Pilih LOT',
                                    options=df[df['nama_item']==sample].LOT.to_list(),
                                    format_func=lambda x: '' if x == None else x,
                                    disabled = st.session_state.sample_to_remove == None,
                                    key='lot_to_remove')

            if sample != None and lot != None:
                df_selected = df[(df['nama_item'] == sample) & (df['LOT'] == lot)]
                berat_sampel_kering = st.number_input("Berat sampel kering", format='%f')
                if berat_sampel_kering > 0 :
                    solid_content = round((berat_sampel_kering - float(df_selected['berat_wadah'])) / float(df_selected['berat_sampel_basah']) * 100, 2)
                    st.text(f"nilai Solid Content: {solid_content}%")
            
            submitted = st.button("Submit")
            if submitted:
                if sample != None and solid_content > 0:
                    # solid_content = round((berat_sampel_kering - float(df_selected['berat_wadah'])) / float(df_selected['berat_sampel_basah']) * 100, 2)
                    remaining_data = (berat_sampel_kering, solid_content, sample, lot)
                    query = '''UPDATE solid_contents 
                                SET berat_sampel_kering = ?, 
                                    timestamp2 = (strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime')),
                                    sc = ? 
                                WHERE nama_item = ? AND LOT = ?'''
                    update_db(query, remaining_data)
                    st.success(f'berhasil memasukkan ke database')
                    time.sleep(10)
                    st.experimental_rerun()
                else:
                    st.error('silahkan isi form di atas terlebih dahulu')


    st.latex(r'''
    Solid\:contents (\%) =
    \frac{\left({hasil\:oven \:(g)} - {wadah\:kosong \:(g)}\right)}{berat\:sampel \:(g)} \: x \:100\%
    ''')

if __name__ == "__main__":
    # Setup logging configuration
    logging.basicConfig(level=logging.INFO)
    app()