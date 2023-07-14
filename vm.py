import streamlit as st
import pandas as pd
from sqlalchemy.sql import text
import time
import numpy as np
import logging

# Database connection string
conn = st.experimental_connection("qcdb", type="sql", autocommit=True)

def app():
    logging.info('Volatile Matter Page Started')
    st.title('Volatile Matter')
    st.write('This is the Volatile Matter Calculator Page.')

    df = conn.query("SELECT * FROM volatile_matter WHERE berat_sampel_kering IS NULL")
    
    if not df.empty:
        # Creating new row for validating 
        new_row = pd.Series([None, None, None, None, None,
                            None, None, None, None, None,
                            None], index=df.columns)
        new_row_df = pd.DataFrame([new_row])                    
        df = pd.concat([df, new_row_df], ignore_index=True)
        df.index = np.arange(1, len(df)+1)

        # displayed table
        displayed_df = df[['sec_item_num', 'nama_item', 'LOT', 'berat_cawan', 'berat_Na2SO4','berat_sampel_basah', 'timestamp_init']][:-1]
        displayed_df = displayed_df.rename(columns={
            'sec_item_num': 'Second Item Number',
            'nama_item': 'Nama Item',
            'LOT': 'LOT',
            'berat_cawan': 'Berat Cawan (g)',
            'berat_Na2SO4': 'Berat Na2SO4 (g)',
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
                berat_cawan = st.number_input('Berat Cawan (g)', format='%f')
                berat_Na2SO4 = st.number_input('Berat Na2SO4 (20 - 30 gr)', format='%f')
                berat_sampel_basah = st.number_input('Berat Sampel (1.5 - 2.0 gr)', format='%f')
                
                submitted = st.form_submit_button("Submit")
            if submitted:
                if sec_item_num == '' or nama_item == '' or lot == '' or berat_cawan <= 0 or berat_sampel_basah <= 0:
                    st.error('Mohon lengkapi form dengan benar')
                else:
                    with conn.session as session:
                        session.execute(text("""INSERT INTO volatile_matter (sec_item_num, nama_item, LOT, berat_cawan, berat_Na2SO4, berat_sampel_basah) 
                                            VALUES (:n1, :n2, :n3, :n4, :n5, :n6);"""), 
                                            {"n1": sec_item_num, "n2":nama_item, 
                                            "n3":lot, "n4":berat_cawan,
                                            "n5": berat_Na2SO4, "n6":berat_sampel_basah}) 
                        st.success('Data berhasil ditambahkan')
                    time.sleep(2)
                    st.cache_data.clear()
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
                berat_sampel_kering = st.number_input("Berat hasil oven (2.5 jam)", format='%f')
                if berat_sampel_kering > 0 :
                    berat_total = float(df_selected['berat_Na2SO4']) + float(df_selected['berat_cawan']) + float(df_selected['berat_sampel_basah'])
                    volatile_matter = round((berat_total - berat_sampel_kering) / float(df_selected['berat_sampel_basah']) * 100, 2)
                    st.text(f"nilai Volatile Matter: {volatile_matter}%")
            
            submitted = st.button("Submit")
            if submitted:
                if sample != None and volatile_matter > 0:
                    remaining_data = (berat_sampel_kering, volatile_matter, sample, lot)
                    with conn.session as session:
                        session.execute(text("""UPDATE volatile_matter
                                                SET berat_sampel_kering = :n1,
                                                    timestamp2 = DATE_FORMAT(NOW(), '%Y-%m-%d %H:%i:%s'),
                                                        volatile_matter = :n2
                                                WHERE nama_item = :n3 AND LOT = :n4"""),
                                        {"n1": berat_sampel_kering, "n2":volatile_matter, "n3":sample, "n4":lot})
                        st.success(f'berhasil input {sample} ke database')
                    st.cache_data.clear()
                    time.sleep(5)
                    st.experimental_rerun()
                else:
                    st.error('silahkan pilih sampel terlebih dahulu')


    # st.latex(r'''
    # Solid\:contents (\%) =
    # \frac{{hasil\:oven \:(g)} - {wadah\:kosong \:(g)}}{berat\:sampel \:(g)} \: x \:100\%
    # ''')

if __name__ == "__main__":
    # Setup logging configuration
    logging.basicConfig(level=logging.INFO)
    app()