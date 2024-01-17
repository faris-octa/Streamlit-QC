import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.sql import text
import time

def calculate_TA(jumlah_titran, faktor_buret, faktor_HClO4, berat_sampel):
    """
    Calculate the Total Amine based on provided parameters.
    
    Args:
    jumlah_titran: The amount of titrant used in the titration.
    faktor_buret: The buret factor.
    faktor_HClO4: The HClO4 factor.
    berat_sampel: The sample weight.

    Returns:
    Total Amine: The calculated Amine value.
    """
    try:
        return round((jumlah_titran * faktor_buret * faktor_HClO4 * 5.61) / berat_sampel, 4)
    except ZeroDivisionError:
        st.error("Cannot calculate Total Amine: berat sampel should not be zero")
    

# CONNECTION SETTINGS
wo_conn = st.connection("prodDB", type="sql", autocommit=True)
qc_conn = st.connection("qcdb", type="sql", autocommit=True)

# query dari tabel workorder item yang saat ini aktif dan yang berupa produk
wo_df = wo_conn.query(
    "SELECT * FROM workorder where IsActive = 1 AND SecondItemNumber NOT LIKE '%-%'",
    show_spinner = True, 
    ttl=10
    )           

ta_temp_df = qc_conn.query(
    "select * from totalaminetemp", 
    show_spinner = True, 
    ttl=10
    )

ta_temp_df['Sampel'] = ta_temp_df.apply(lambda row: f"{row['ItemDescription']} ({row['LotSerialNumber']})", axis=1)
    
# st.dataframe(ta_temp_df) # <-- UNCOMMENT FOR DEBUGGING


## UI SECTION
st.title('Total Amine')
st.write('Total Amine Calculator Page.')

tab1, tab2 = st.tabs([f"Sampel Aktif ({len(ta_temp_df['Sampel'].unique())})", "Sampel Baru"])

with tab1:

    sampel_option = st.selectbox(
        'Sampel',
        ta_temp_df['Sampel'].unique().tolist(),
        index=None,
        placeholder="Select Active Sample..." if len(ta_temp_df) > 0 else "Tidak Ada Sampel Aktif",
        key = "sampel_option2"
    )

    if sampel_option is not None:
        with st.container(border=True):
            displayed_df = ta_temp_df[(ta_temp_df['Sampel'] == sampel_option)].sort_values(by='TimeStamp', ascending=True)
            
            SecondItemNumber1 = displayed_df.iloc[0,1]
            ItemDescription1 = displayed_df.iloc[0,2]
            LotSerialNumber1 = displayed_df.iloc[0,3]
            
            st.dataframe(
                displayed_df[["ItemDescription", "LotSerialNumber", "Suhu", "TotalAmine", "TimeStamp", "Keterangan"]],
                column_config={
                    "ItemDescription": "Nama Item",
                    "LotSerialNumber": "LOT",
                    "TotalAmine": "Total Amine",
                    "TimeStamp": st.column_config.DatetimeColumn("Waktu", format="ddd, h:mm a")
                },
                hide_index = True,
                use_container_width = True
            )

            if st.button('Selesai'):
                st.write(displayed_df.iloc[:, 1:-1])
                try:
                    engine = create_engine("mysql+mysqldb://inkaliqc:qcoke@192.168.0.70/qc")
                    displayed_df.iloc[:, 1:-1].to_sql('totalamine', con=engine, if_exists='append', index=False)
                    with qc_conn.session as session:
                        session.execute(text("""DELETE FROM totalaminetemp 
                                            WHERE SecondItemNumber = :n1 AND LotSerialNumber = :n2"""),
                                            {"n1": SecondItemNumber1, "n2": LotSerialNumber1})
                        st.success(f"Data sampel {sampel_option} telah berhasil masuk database.")
                        time.sleep(2)
                        st.cache_data.clear()
                        st.rerun()
                except Exception as e:
                    st.error(f"An error occurred: {e}")



        with st.container(border=True) as input_section:

            st.write(f"Item Name: :red[{SecondItemNumber1}]")
            st.write(f"Second Item Number: :red[{ItemDescription1}]")
            st.write(f"LOT: :red[{LotSerialNumber1}]")


            operator1 = st.text_input('Nama Operator', key="operator_tab1")
        
            col1, col2 = st.columns(2)
            
            with col1:
                faktor_buret1 = st.number_input("Faktor buret", format='%f', value=1.008, key="buret_tab1")
                faktor_HClO41 = st.number_input("Faktor HClO4", format='%f', value=1.008, key="faktorHClO4_tab1")
                suhu1 = st.text_input('Suhu', key="suhu_tab1")

            
            with col2:
                berat_sampel1 = st.number_input("Berat sampel (gram)", format='%f', key="beratSampel_tab1")
                jumlah_titran1 = st.number_input("Jumlah titran (mL)", format='%f', key="jumlahTitran_tab1")
                TA1 = 0
                if berat_sampel1 > 0 and jumlah_titran1 > 0 and operator1 != "":
                    TA1 = calculate_TA(jumlah_titran1, faktor_buret1, faktor_HClO41, berat_sampel1)
                    st.text(f"nilai Acid Value: {TA1}")
                    keterangan1 = st.text_input('keterangan', key="keterangan_tab1")
            
                    if st.button('submit', key="submit_tab1"):
                        if TA1 > 0:
                            with qc_conn.session as session:
                                session.execute(text("""INSERT INTO totalaminetemp (SecondItemNumber, ItemDescription, LotSerialNumber, Suhu, FaktorBuret, FaktorHClO4, BeratSampel, JumlahTitran, TotalAmine, Keterangan, Operator) 
                                                    VALUES (:n1, :n2, :n3, :n4, :n5, :n6, :n7, :n8, :n9, :n10, :n11);"""),
                                                {"n1":SecondItemNumber1, "n2":ItemDescription1, "n3":LotSerialNumber1, 
                                                "n4":suhu1, "n5": faktor_buret1, "n6": faktor_HClO41, 
                                                "n7":berat_sampel1, "n8":jumlah_titran1, "n9":TA1, 
                                                "n10":keterangan1, "n11":operator1.capitalize()
                                                })    
                            
                            st.success('Input Data Success')
                            time.sleep(2)
                            st.cache_data.clear()
                            del st.session_state["sampel_option2"]
                            st.rerun()

with tab2:

    option = st.selectbox(
        'WO NUMBER',
        wo_df['OrderNumber'].tolist(),
        index=None,
        placeholder="Select Work Order Number...",
        key = "option1"
    )

    if option is not None:
        item = wo_df.loc[wo_df['OrderNumber'] == option].iloc[0]
        st.write(f"Item Name: :red[{item['ItemDescription']}]")
        st.write(f"Second Item Number: :red[{item['SecondItemNumber']}]")
        st.write(f"LOT: :red[{item['LotSerialNumber']}]")

        with st.container(border=True) as input_section:
            operator = st.text_input('Nama Operator', key="operator2")
            
            col1, col2 = st.columns(2)
            
            with col1:
                faktor_buret = st.number_input("Faktor buret", format='%f', value=1.008)
                faktor_HClO4 = st.number_input("Faktor HClO4", format='%f', value=1.008)
                suhu = st.text_input('Suhu')

            
            with col2:
                berat_sampel = st.number_input("Berat sampel (gram)", format='%f')
                jumlah_titran = st.number_input("Jumlah titran (mL)", format='%f')
                TA = 0
                if berat_sampel > 0 and jumlah_titran > 0:
                    TA = calculate_TA(jumlah_titran, faktor_buret, faktor_HClO4, berat_sampel)
                    st.text(f"nilai Total Amine: {TA}")
                    keterangan = st.text_input('keterangan', key = "keterangan2")
            
                    if st.button('submit'):
                        if TA > 0 and not ((ta_temp_df['SecondItemNumber'] == item['SecondItemNumber']) & (ta_temp_df['LotSerialNumber'] == item['LotSerialNumber'])).any():
                            with qc_conn.session as session:
                                session.execute(text("""INSERT INTO totalaminetemp (SecondItemNumber, ItemDescription, LotSerialNumber, Suhu, FaktorBuret, FaktorHClO4, BeratSampel, JumlahTitran, TotalAmine, Keterangan, Operator) 
                                                    VALUES (:n1, :n2, :n3, :n4, :n5, :n6, :n7, :n8, :n9, :n10, :n11);"""),
                                                {"n1":item['SecondItemNumber'], "n2":item['ItemDescription'], "n3":item['LotSerialNumber'], 
                                                "n4":suhu, "n5": faktor_buret, "n6": faktor_HClO4, 
                                                "n7":berat_sampel, "n8":jumlah_titran, "n9":TA, 
                                                "n10":keterangan, "n11":operator.capitalize()
                                                })  
                            st.success('Input Data Success')
                            time.sleep(2)
                            st.cache_data.clear()
                            del st.session_state["option1"]
                            st.rerun()

                        else:
                            st.warning("Sampel sudah aktif")