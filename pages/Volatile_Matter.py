import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.sql import text
import time

def calculate_VM(berat_kering, berat_total, berat_sampel):
    """
    Calculate the % Volatile Matter (%SC) based on provided parameters.
    
    Args:
    berat_kering: The amount of sample after oven.
    berat_total: The amount of Na2SO4, "cawan" and wet sample weight.
    berat_sampel: The sample weight.

    Returns:
    VM: The calculated Volatile Matters.
    """
    try:
        return round((berat_total - berat_kering) / berat_sampel * 100, 2)
    except ZeroDivisionError:
        st.error("Cannot calculate Volatile Matter: Berat Sampel should not be zero")

# CONNECTION SETTINGS
wo_conn = st.connection("prodDB", type="sql", autocommit=True)
qc_conn = st.connection("qcdb", type="sql", autocommit=True)

# query dari tabel workorder item yang saat ini aktif dan yang berupa produk
wo_df = wo_conn.query(
    "SELECT * FROM workorder where IsActive = 1 AND SecondItemNumber NOT LIKE '%-%'",
    show_spinner = True, 
    ttl=10
    )

vm_df = qc_conn.query(
    "SELECT * FROM volatilematter WHERE BeratAkhir IS NULL",
    show_spinner = True,
    ttl = 10
    )
vm_df['Sample'] = vm_df.apply(lambda row: f"{row['ItemDescription']} ({row['LotSerialNumber']})", axis=1)


## UI SECTION
st.title('Volatile Matter')
st.write('Volatile Matter Calculator Page.')
st.divider()

# st.dataframe(vm_df, hide_index=True)
if not vm_df.empty:
    st.dataframe(
        vm_df.iloc[:, 2:9],
        column_config={
            'ItemDescription': 'Item',
            'LotSerialNumber': 'LOT',
            'Operator1': 'Operator 1',
            'BeratWadah': 'Berat Cawan (g)',
            'BeratNa2SO4': 'Berat Na2SO4 (g)',
            'BeratSampelBasah': 'Berat Sampel (g)',
            'TimeStampInit': st.column_config.DatetimeColumn("Waktu", format="ddd, h:mm a"),
            'SolidContent': None
            },
        use_container_width=False,
        hide_index=True)

col1, col2 = st.columns(2)

with col1 as sampel_baru:
    with st.container(border=True):
        st.write("Sampel Baru")

        option = st.selectbox(
            'WO NUMBER',
            wo_df['OrderNumber'].tolist(),
            index=None,
            placeholder="Select Work Order Number...",
            key = "option"
            )

        if option is not None:
            item = wo_df.loc[wo_df['OrderNumber'] == option].iloc[0]
            st.write(f"Item Name: :red[{item['ItemDescription']}]")
            st.write(f"Second Item Number: :red[{item['SecondItemNumber']}]")
            st.write(f"LOT: :red[{item['LotSerialNumber']}]")


            berat_wadah = st.number_input("Berat Cawan (g)", format='%f')
            berat_Na2SO4 = st.number_input('Berat Na2SO4 (20 - 30 gr)', format='%f')
            berat_sampel_basah = st.number_input("Berat Sampel (1.5 - 2.0 gr)", format='%f')

            operator_1 = st.text_input('Nama Operator', key="operator1")
            
            # if operator_1 != "" and metode == None or berat_wadah <= 0 or berat_sampel_basah <= 0:
            if berat_wadah>0 and berat_sampel_basah>0 and berat_Na2SO4>0 and operator_1 != "":
                if st.button('submit'):
                    if not ((vm_df['SecondItemNumber'] == item['SecondItemNumber']) & (vm_df['LotSerialNumber'] == item['LotSerialNumber'])).any():
                        with qc_conn.session as session:
                            session.execute(text("""INSERT INTO volatilematter (SecondItemNumber, ItemDescription, LotSerialNumber, Operator1, BeratWadah, BeratNa2SO4, BeratSampelBasah) 
                                                VALUES (:n1, :n2, :n3, :n4, :n5, :n6, :n7);"""),
                                                {"n1":item['SecondItemNumber'], "n2":item['ItemDescription'], "n3":item['LotSerialNumber'], 
                                                "n4":operator_1, "n5": berat_wadah, "n6": berat_Na2SO4, 
                                                "n7":berat_sampel_basah
                                                })
                        st.success('Input Data Success')
                        time.sleep(2)
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.warning("Sampel sudah aktif")




with col2 as sampel_aktif:
    with st.container(border=True):
        st.write(f"Sampel Aktif :red[({len(vm_df)})]")

        option_sample_active = st.selectbox(
            'SAMPLE',
            vm_df['Sample'].tolist(),
            index=None,
            placeholder="Select Active Sample..." if len(vm_df) > 0 else "Tidak Ada Sampel Aktif",
            key = "option_sample_active"
            )

        if option_sample_active is not None:
            sample_active_data = vm_df.loc[vm_df['Sample'] == option_sample_active].iloc[0]

            berat_sampel_kering = st.number_input("Berat Hasil 2.5 Jam Oven (g)", format='%f')

            if berat_sampel_kering > 0:
                berat_total = sample_active_data["BeratWadah"] + sample_active_data["BeratNa2SO4"] + sample_active_data["BeratSampelBasah"]
                volatile_matter = calculate_VM(berat_sampel_kering, berat_total, sample_active_data["BeratSampelBasah"])
                st.write(f"Nilai Volatile Matter: {volatile_matter}%")

                keterangan = st.text_input('Keterangan (opsional)', key="keterangan")
                operator_2 = st.text_input('Nama Operator', key="operator2")

                if operator_2 != "":
                    if st.button('Selesai'):
                        with qc_conn.session as session:
                            session.execute(text(
                                """UPDATE volatilematter
                                    SET Operator2 = :n1, BeratAkhir = :n2, TimeStampEnd = DATE_FORMAT(NOW(), '%Y-%m-%d %H:%i:%s'), VolatileMatter = :n3, Status = :n4
                                    WHERE SecondItemNumber = :n5 AND LotSerialNumber = :n6"""),
                            {"n1":operator_2, "n2":berat_sampel_kering, "n3": volatile_matter, 
                            "n4":keterangan, "n5": sample_active_data["SecondItemNumber"], "n6": sample_active_data["LotSerialNumber"]})
                        st.success(f"Data sampel {option_sample_active} telah berhasil masuk database.")
                        time.sleep(2)
                        st.cache_data.clear()
                        st.rerun()
                   


