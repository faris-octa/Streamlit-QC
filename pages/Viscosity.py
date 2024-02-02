import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.sql import text
import time
import pandas as pd

# dataframe viscometer BL
BL_factor = {
    "speed": [0.3, 0.6, 1.5, 3, 6, 12, 30, 60, 0.3, 0.6, 1.5, 3, 6, 12, 30, 60, 0.3, 0.6, 1.5, 3, 6, 12, 30, 60, 0.3, 0.6, 1.5, 3, 6, 12, 30, 60],
    "spindle": [1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4],
    "factor": [200, 100, 40, 20, 10, 5, 2, 1,
            1000, 500, 200, 100, 50, 25, 10, 5,
            4000, 2000, 800, 400, 200, 100, 40, 20,
            20000, 10000, 4000, 2000, 1000, 500, 200, 100]
}
BL_factor_df = pd.DataFrame(BL_factor)

def calculate_viscosity(spindle, speed, measurement):
    factor = BL_factor_df[(BL_factor_df['spindle'] == spindle) & (BL_factor_df['speed'] == speed)]["factor"].iloc[0]
    viscosity = factor * measurement
    return viscosity

# Filter Products
products = ["NEOSTECKER HF-9113", "NEOSTECKER HF-9189", "NEOSTECKER HF-9119", "NEOSTECKER HF-920"]

# CONNECTION SETTINGS
wo_conn = st.connection("prodDB", type="sql", autocommit=True)
qc_conn = st.connection("qcdb", type="sql", autocommit=True)


# query dari tabel workorder item yang saat ini aktif dan yang berupa produk
wo_df = wo_conn.query(
    "SELECT * FROM workorder where IsActive = 1 AND SecondItemNumber NOT LIKE '%-%'",
    show_spinner = True, 
    ttl=10
    )  

wo_df = wo_df[wo_df['ItemDescription'].isin(products)]         

viscosity_temp_df = qc_conn.query(
    "select * from viscositytemp", 
    show_spinner = True, 
    ttl=10
    )

viscosity_temp_df['Sampel'] = viscosity_temp_df.apply(lambda row: f"{row['ItemDescription']} ({row['LotSerialNumber']})", axis=1)

# st.dataframe(ta_temp_df) # <-- UNCOMMENT FOR DEBUGGING

## UI SECTION
st.title('Viscosity')
st.write('Viscosity Calculator Page.')

tab1, tab2 = st.tabs([f"Sampel Aktif ({len(viscosity_temp_df['Sampel'].unique())})", "Sampel Baru"])

with tab1:
    st.write("Under maintenance")
    st.dataframe(viscosity_temp_df)

with tab2:
    option = st.selectbox(
        'WO NUMBER',
        wo_df['OrderNumber'].tolist(),
        index=None,
        placeholder="Select Work Order Number...",
        key = "option1"
    )

    if option != None:
        item = wo_df.loc[wo_df['OrderNumber'] == option].iloc[0]

        col_1, col_2, col_3 = st.columns(3)
        with col_1:
            st.write(f"Item Name: :red[{item['ItemDescription']}]")
        
        with col_2:
            st.write(f"Second Item Number: :red[{item['SecondItemNumber']}]")
        
        with col_3:
            st.write(f"LOT: :red[{item['LotSerialNumber']}]")

        with st.container(border=True) as input_section:
            operator2 = st.text_input('Nama Operator', value=None, key="operator2")
            visco_type = st.selectbox(
                'Viscometer Type',
                ["BL", "BH"],
                index=None,
                placeholder="Select Viscometer type...",
                key = "viscotype option"
            )
            
            col_atas, col_bawah = st.columns(2)
            
            with col_atas:
                st.write("Atas")

                pH_atas = st.number_input("pH atas", format='%f', label_visibility="visible", placeholder= "", value=None)
                spindle_atas = st.selectbox('tipe spindle', [1,2,3,4], index = None, placeholder= "", label_visibility="visible", key="spindle_atas")  
                speed_atas = st.selectbox('kecepatan', BL_factor_df["speed"].unique().tolist(), index=None, placeholder= "", label_visibility="visible", key="speed_atas")
                measurement_atas = st.number_input("pembacaan", format='%f', label_visibility="visible", placeholder= "(1-100)", value=None, key="measurement_atas")
                if spindle_atas != None and speed_atas != None and measurement_atas != None:
                    viscosity_atas = calculate_viscosity(spindle_atas, speed_atas, measurement_atas)
                    st.write(f"Nilai viskositas Atas: {viscosity_atas}")
                else:
                    viscosity_atas = None

            with col_bawah:
                st.write("Bawah")

                pH_bawah = st.number_input("pH bawah", format='%f', label_visibility="visible", placeholder= "", value=None)
                spindle_bawah = st.selectbox('tipe spindle', [1,2,3,4], index = None, placeholder= "", label_visibility="visible", key="spindle_bawah")  
                speed_bawah = st.selectbox('kecepatan', BL_factor_df["speed"].unique().tolist(), index=None, placeholder= "", label_visibility="visible", key="speed_bawah")
                measurement_bawah = st.number_input("pembacaan", format='%f', label_visibility="visible", placeholder= "(1-100)", value=None, key="measurement_bawah")
                if spindle_bawah != None and speed_bawah != None and measurement_bawah != None:
                    viscosity_bawah = calculate_viscosity(spindle_bawah, speed_bawah, measurement_bawah)
                    st.write(f"Nilai viskositas bawah: {viscosity_bawah}")
                else:
                    viscosity_bawah = None

            keterangan2 = st.text_input('Keterangan', value=None, key="keterangan")
            if st.button('submit', use_container_width=True):
                if operator2 == None:
                    st.warning("Input Nama Operator")
                elif ((viscosity_temp_df['SecondItemNumber'] == item['SecondItemNumber']) & (viscosity_temp_df['LotSerialNumber'] == item['LotSerialNumber'])).any():
                    st.warning("Sampel sudah aktif")
                else:
                    # st.write(item) -> for debug
                    with qc_conn.session as session:
                        session.execute(text("""INSERT INTO viscositytemp (SecondItemNumber, ItemDescription, LotSerialNumber, Operator, ViscoType, pHAtas, SpindleAtas, SpeedAtas, DialAtas, ViscosityAtas, pHBawah, SpindleBawah, SpeedBawah, DialBawah, ViscosityBawah, Keterangan) 
                                                VALUES (:n1, :n2, :n3, :n4, :n5, :n6, :n7, :n8, 
                                                        :n9, :n10, :n11, :n12, :n13, :n14, :n15, :n16);"""),
                                        {"n1":item['SecondItemNumber'], "n2":item['ItemDescription'], "n3":item['LotSerialNumber'], 
                                        "n4":operator2.capitalize(), "n5": visco_type,
                                        "n6": pH_atas, "n7":spindle_atas, "n8":speed_atas, "n9":measurement_atas, "n10":viscosity_atas, 
                                        "n11": pH_bawah, "n12":spindle_bawah, "n13":speed_bawah, "n14":measurement_bawah, "n15":viscosity_bawah,
                                        "n16":keterangan2
                                        })  
                    st.success('Input Data Success')
                    time.sleep(2)
                    st.cache_data.clear()
                    del st.session_state["option1"]
                    st.rerun()

                

                
