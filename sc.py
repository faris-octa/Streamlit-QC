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
    st.title('Solid Content')
    st.write('This is the Solid Content Calculator Page.')

    # Ambil data dari database
    df = conn.query("SELECT * FROM solid_content WHERE berat_sampel_kering IS NULL")
    
    # Cek jika terdapat sampel yang sedang aktif
    if not df.empty:
        # Membuat baris kosong untuk validasi 
        new_row = pd.Series([None, None, None, None, None,
                            None, None, None, None, None], index=df.columns)
        new_row_df = pd.DataFrame([new_row])                    
        df = pd.concat([df, new_row_df], ignore_index=True)
        df.index = np.arange(1, len(df)+1)

        # Menampilkan tabel
        displayed_df = df[['nama_item', 'LOT', 'berat_wadah', 'berat_sampel_basah', 'timestamp_init']][:-1]
        displayed_df = displayed_df.rename(columns={
            'nama_item': 'Nama Item',
            'LOT': 'LOT',
            'berat_wadah': 'Berat Wadah (g)',
            'berat_sampel_basah': 'Berat Sampel (g)',
            'timestamp_init': 'Waktu Mulai'
            })
        st.dataframe(displayed_df, use_container_width=True, hide_index=True)

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

                # Menangani submit form
                submitted = st.form_submit_button("Submit", use_container_width=True)
            # Cek jika form sudah diisi dengan benar dan menambahkan ke database
            if submitted:
                if sec_item_num == '' or nama_item == '' or lot == '' or berat_wadah <= 0 or berat_sampel_basah <=0:
                    st.error('Mohon lengkapi form dengan benar')
                else:
                    with conn.session as session:
                        session.execute(text("""INSERT INTO solid_content (sec_item_num, nama_item, LOT, berat_wadah, berat_sampel_basah) 
                                            VALUES (:n1, :n2, :n3, :n4, :n5);"""), 
                                            {"n1": sec_item_num, "n2":nama_item.upper(), 
                                            "n3":lot.upper(), "n4":berat_wadah, "n5":berat_sampel_basah}) 
                        st.success('Data berhasil ditambahkan')
                    # Refresh halaman
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
                berat_sampel_kering = st.number_input("Berat hasil oven (g)", format='%f')
                if berat_sampel_kering > 0 :
                    solid_content = round((berat_sampel_kering - float(df_selected['berat_wadah'])) / float(df_selected['berat_sampel_basah']) * 100, 2)
                    st.text(f"nilai Solid Content: {solid_content}%")
            
            submitted = st.button("Submit", use_container_width=True)
            if submitted:
                if sample != None and solid_content > 0:
                    remaining_data = (berat_sampel_kering, solid_content, sample, lot)
                    with conn.session as session:
                        session.execute(text("""UPDATE solid_content
                                                SET berat_sampel_kering = :n1,
                                                    timestamp2 = DATE_FORMAT(NOW(), '%Y-%m-%d %H:%i:%s'),
                                                        sc = :n2
                                                WHERE nama_item = :n3 AND LOT = :n4"""),
                                        {"n1": berat_sampel_kering, "n2":solid_content, "n3":sample, "n4":lot})
                        st.success(f'berhasil input {sample} ke database')
                    st.cache_data.clear()
                    time.sleep(5)
                    st.experimental_rerun()
                else:
                    st.error('silahkan pilih sampel terlebih dahulu')


    st.latex(r'''
    Solid\:contents (\%) =
    \frac{{hasil\:oven \:(g)} - {wadah\:kosong \:(g)}}{berat\:sampel \:(g)} \: x \:100\%
    ''')

if __name__ == "__main__":
    # Setup logging configuration
    logging.basicConfig(level=logging.INFO)
    app()