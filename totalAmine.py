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

def calculate_TA(jumlah_titran, faktor_buret, faktor_HClO4, berat_sampel):
    try:
        return round((jumlah_titran * faktor_buret * faktor_HClO4 * 5.61) / berat_sampel, 4)
    except ZeroDivisionError:
        st.error("Cannot calculate TA: berat_sampel should not be zero")

def app():
    # logging.info('Total Amine Page Started')
    st.title('Total Amine')
    st.write('This is the Total Amine Calculator Page.')

    df = conn.query("SELECT * FROM ta_temp")
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
        if not selected_row.empty:
            input_values = {label: selected_row[label].values[0] for label in ['sec_item_num', 'nama_item', 'LOT']}

            displayed_df = df[(df['nama_item'] == input_values['nama_item']) & (df['LOT'] == input_values['LOT'])].sort_values(by='timestamp', ascending=True)
            st.dataframe(displayed_df[['nama_item', 'LOT', 'timestamp', 'suhu', 'TA', 'keterangan']],
                        column_config={
                            "nama_item": "Nama Item",
                            "timestamp": "Timestamp",
                            "suhu" : "Suhu",
                            "TA" : "Total Amine",
                            "keterangan": "Keterangan"
                        },
                        use_container_width=True, hide_index=True)

            if st.button("Submit to database"):
                try:
                    with conn.session as session:
                        displayed_df.iloc[:, 1:].to_sql('ta', con=engine, if_exists='append', index=False)
                        session.execute(text("DELETE FROM ta_temp WHERE nama_item=:n1 AND LOT=:n2"), {"n1": input_values['nama_item'], "n2": input_values['LOT']})
                        st.success("Data successfully moved from TA_temp to TA in the database.")
                        st.cache_data.clear()
                        st.experimental_rerun()
                except Exception as e:
                    st.error(f"An error occurred: {e}")

        else:
            st.warning('Tidak ada sampel aktif saat ini, mohon pilih opsi (sampel baru)')

    with st.container() as input_section:
        col1, col2 = st.columns(2)

        with col1:
            sec_item_num = st.text_input("Second item number", value=input_values['sec_item_num'], disabled=(opsi == 'sampel aktif'))
            nama_item = st.text_input("Nama item", value=input_values['nama_item'], disabled=(opsi == 'sampel aktif'))
            LOT = st.text_input("LOT", value=input_values['LOT'], disabled=(opsi == 'sampel aktif'))
            faktor_buret = st.number_input("Faktor buret", format='%f', value=1.008)
            faktor_HClO4 = st.number_input("Faktor HClO4", format='%f', value=1.008)

        with col2:
            suhu = st.text_input('Suhu')
            berat_sampel = st.number_input("Berat sampel", format='%f')
            jumlah_titran = st.number_input("Jumlah titran", format='%f')
            if berat_sampel > 0 and jumlah_titran > 0:
                TA = calculate_TA(jumlah_titran, faktor_buret, faktor_HClO4, berat_sampel)
                st.text(f"nilai Total Amine: {TA}")
            keterangan = st.text_input('keterangan')
            submitted = st.button('submit')

    if submitted:
        if TA and sec_item_num != '' and nama_item != '' and LOT != '':
            with conn.session as session:
                session.execute(text("""INSERT INTO ta_temp (sec_item_num, nama_item, LOT, suhu, FAKTOR_BURET, FAKTOR_HClO4, berat_sampel, jumlah_titran, TA, keterangan) 
                                        VALUES (:n1, :n2, :n3, :n4, :n5, :n6, :n7, :n8, :n9, :n10);"""), 
                                        {"n1":sec_item_num, "n2":nama_item.upper(), 
                                        "n3":LOT.upper(), "n4":suhu, "n5": faktor_buret,
                                        "n6": faktor_HClO4, "n7":berat_sampel, 
                                        "n8":jumlah_titran, "n9":TA, "n10":keterangan
                                        })
            st.success('Yeay, data has been successfully inserted!')
            time.sleep(2)
            st.cache_data.clear()
            st.experimental_rerun()
        else:
            st.warning('Mohon lengkapi form di atas')
        
    st.latex(r'''
    Total\:Amine =
    \frac{{jumlah\:titran \:(mL)} \:x\: {faktor\:buret} \:x\: {faktor\:HClO4} \:x\: {5.61}}{berat\:sampel}
    ''')

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app()