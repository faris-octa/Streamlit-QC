import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.sql import text
import time

def calculate_viscosity(factor, measurement):
    viscosity = factor * measurement
    return viscosity

# CONNECTION SETTINGS
wo_conn = st.connection("prodDB", type="sql", autocommit=True)
qc_conn = st.connection("qcdb", type="sql", autocommit=True)

# query dari tabel workorder item yang saat ini aktif dan yang berupa produk
wo_df = wo_conn.query(
    "SELECT * FROM workorder where IsActive = 1 AND SecondItemNumber NOT LIKE '%-%'",
    show_spinner = True, 
    ttl=10
    )           

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
        st.write(f"Item Name: :red[{item['ItemDescription']}]")
        st.write(f"Second Item Number: :red[{item['SecondItemNumber']}]")
        st.write(f"LOT: :red[{item['LotSerialNumber']}]")

        with st.container(border=True) as input_section:
            operator = st.text_input('Nama Operator', key="operator2")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("Atas")
                faktor_buret = st.number_input("Faktor buret", format='%f', value=1.008)
                faktor_HClO4 = st.number_input("Faktor HClO4", format='%f', value=1.008)
                suhu = st.text_input('Suhu')
