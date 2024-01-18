import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.sql import text
import time

def calculate_sc(berat_kering, berat_wadah, berat_sampel):
    """
    Calculate the % solid content (%SC) based on provided parameters.
    
    Args:
    berat_kering: The amount of sample after oven.
    berat_wadah: The wadah weight.
    berat_sampel: The sample weight.

    Returns:
    SC: The calculated Solid Contents (%).
    """
    try:
        return round((berat_kering - berat_wadah) / berat_sampel * 100, 2)
    except ZeroDivisionError:
        st.error("Cannot calculate AV: berat_sampel should not be zero")

# CONNECTION SETTINGS
wo_conn = st.connection("prodDB", type="sql", autocommit=True)
qc_conn = st.connection("qcdb", type="sql", autocommit=True)

# query dari tabel workorder item yang saat ini aktif dan yang berupa produk
wo_df = wo_conn.query(
    "SELECT * FROM workorder where IsActive = 1 AND SecondItemNumber NOT LIKE '%-%'",
    show_spinner = True, 
    ttl=10
    )

sc_df = qc_conn.query(
    "SELECT * FROM solidcontent WHERE BeratAkhir IS NULL",
    show_spinner = True,
    ttl = 10
    )
sc_df['Sample'] = sc_df.apply(lambda row: f"{row['ItemDescription']} ({row['LotSerialNumber']})", axis=1)


## UI SECTION
st.title('Solid Content')
st.write('Solid Content Calculator Page.')
st.divider()

# st.dataframe(sc_df, hide_index=True)
if not sc_df.empty:
    st.dataframe(
        sc_df.iloc[:, 2:9],
        column_config={
            'ItemDescription': 'Item',
            'LotSerialNumber': 'LOT',
            'Operator1': 'Operator 1',
            'BeratWadah': 'Berat Piringan (g)',
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
            # st.write(f"Item Name: :red[{item['ItemDescription']}]")
            item_name = st.text_input("Item Name", value = item["ItemDescription"])
            st.write(f"Second Item Number: :red[{item['SecondItemNumber']}]")
            st.write(f"LOT: :red[{item['LotSerialNumber']}]")


            metode = st.selectbox(
                'Metode Pengukuran',
                ["3 jam", "1 jam", "KETT"],
                index=None,
                placeholder="Select Measurement Method...",
                key = "metode"
                )

            # berat_wadah = st.number_input("Berat Wadah (g)", format='%f')
            # berat_sampel_basah = st.number_input("Berat Sampel (g)", format='%f')

            # operator_1 = st.text_input('Nama Operator', key="operator1")
            
            if metode == "3 jam" or metode == "1 jam":
                berat_wadah = st.number_input("Berat Wadah (g)", format='%f')
                berat_sampel_basah = st.number_input("Berat Sampel (g)", format='%f')
                operator_1 = st.text_input('Nama Operator', key="operator1")

                if berat_wadah>0 and berat_sampel_basah>0 and operator_1 != "":
                    if st.button('submit'):
                        if not ((sc_df['SecondItemNumber'] == item['SecondItemNumber']) & (sc_df['LotSerialNumber'] == item['LotSerialNumber'])).any():
                            with qc_conn.session as session:
                                session.execute(text("""INSERT INTO solidcontent (SecondItemNumber, ItemDescription, LotSerialNumber, Metode, Operator1, BeratWadah, BeratSampelBasah) 
                                                VALUES (:n1, :n2, :n3, :n4, :n5, :n6, :n7);"""),
                                                {"n1":item['SecondItemNumber'], "n2":item_name, "n3":item['LotSerialNumber'], 
                                                "n4":metode, "n5": operator_1.upper(), "n6": berat_wadah, 
                                                "n7":berat_sampel_basah
                                                })
                            st.success('Input Data Success')
                            time.sleep(2)
                            st.cache_data.clear()
                            st.rerun()
                        else:
                            st.warning("Sampel sudah aktif")

            elif metode == "KETT":
                operator_1 = st.text_input('Nama Operator', key="operator1KETT")
                if st.button('submit'):
                    if not ((sc_df['SecondItemNumber'] == item['SecondItemNumber']) & (sc_df['LotSerialNumber'] == item['LotSerialNumber'])).any():
                        with qc_conn.session as session:
                            session.execute(text("""INSERT INTO solidcontent (SecondItemNumber, ItemDescription, LotSerialNumber, Metode, Operator1) 
                                                    VALUES (:n1, :n2, :n3, :n4, :n5);"""),
                                                    {"n1":item['SecondItemNumber'], "n2":item_name, "n3":item['LotSerialNumber'], 
                                                    "n4":metode, "n5": operator_1.upper()
                                                    })
                        st.success('Input Data Success')
                        time.sleep(2)
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.warning("Sampel sudah aktif")



            # # if operator_1 != "" and metode == None or berat_wadah <= 0 or berat_sampel_basah <= 0:
            # if metode != None and berat_wadah>0 and berat_sampel_basah>0 and operator_1 != "":
            #     if st.button('submit'):
            #         if not ((sc_df['SecondItemNumber'] == item['SecondItemNumber']) & (sc_df['LotSerialNumber'] == item['LotSerialNumber'])).any():
            #             with qc_conn.session as session:
            #                 session.execute(text("""INSERT INTO solidcontent (SecondItemNumber, ItemDescription, LotSerialNumber, Metode, Operator1, BeratWadah, BeratSampelBasah) 
            #                                     VALUES (:n1, :n2, :n3, :n4, :n5, :n6, :n7);"""),
            #                                     {"n1":item['SecondItemNumber'], "n2":item_name, "n3":item['LotSerialNumber'], 
            #                                     "n4":metode, "n5": operator_1, "n6": berat_wadah, 
            #                                     "n7":berat_sampel_basah
            #                                     })
            #             st.success('Input Data Success')
            #             time.sleep(2)
            #             st.cache_data.clear()
            #             st.rerun()
            #         else:
            #             st.warning("Sampel sudah aktif")




with col2 as sampel_aktif:
    with st.container(border=True):
        st.write(f"Sampel Aktif :red[({len(sc_df)})]")

        option_sample_active = st.selectbox(
            'SAMPLE',
            sc_df['Sample'].tolist(),
            index=None,
            placeholder="Select Active Sample..." if len(sc_df) > 0 else "Tidak Ada Sampel Aktif",
            key = "option_sample_active"
            )

        if option_sample_active is not None:
            sample_active_data = sc_df.loc[sc_df['Sample'] == option_sample_active].iloc[0]
            st.write(f"Metode pengukuran: :red[{sample_active_data['Metode']}]")

            
            if sample_active_data["Metode"] == "KETT":
                solid_content = st.number_input("Hasil KETT (%)", format='%f')
                keterangan = st.text_input('Keterangan (opsional)', key="keterangan")
                operator_2 = st.text_input('Nama Operator', key="operator2")

                if operator_2 != "":
                    if st.button('Selesai'):
                        with qc_conn.session as session:
                            session.execute(text(
                                """UPDATE solidcontent
                                    SET Operator2 = :n1, TimeStampEnd = DATE_FORMAT(NOW(), '%Y-%m-%d %H:%i:%s'), SolidContent = :n2, Status = :n3
                                    WHERE SecondItemNumber = :n4 AND LotSerialNumber = :n5 AND Metode = :n6"""),
                            {"n1":operator_2.upper(), "n2":solid_content, "n3": keterangan, 
                            "n4":sample_active_data["SecondItemNumber"], "n5": sample_active_data["LotSerialNumber"], "n6": sample_active_data["Metode"]})
                        st.success(f"Data sampel {option_sample_active} telah berhasil masuk database.")
                        time.sleep(2)
                        st.cache_data.clear()
                        st.rerun()
            
            else:
                berat_sampel_kering = st.number_input("Berat Hasil Oven (g)", format='%f')

                if berat_sampel_kering > 0:
                    solid_content = calculate_sc(berat_sampel_kering, sample_active_data["BeratWadah"], sample_active_data["BeratSampelBasah"])
                    st.write(f"Nilai Solid Content: {solid_content}%")

                    keterangan = st.text_input('Keterangan (opsional)', key="keterangan")
                    operator_2 = st.text_input('Nama Operator', key="operator2")

                    if operator_2 != "":
                        if st.button('Selesai'):
                            with qc_conn.session as session:
                                session.execute(text(
                                    """UPDATE solidcontent
                                        SET Operator2 = :n1, BeratAkhir = :n2, TimeStampEnd = DATE_FORMAT(NOW(), '%Y-%m-%d %H:%i:%s'), SolidContent = :n3, Status = :n4
                                        WHERE SecondItemNumber = :n5 AND LotSerialNumber = :n6"""),
                                {"n1":operator_2, "n2":berat_sampel_kering, "n3": solid_content, 
                                "n4":keterangan, "n5": sample_active_data["SecondItemNumber"], "n6": sample_active_data["LotSerialNumber"]})
                            st.success(f"Data sampel {option_sample_active} telah berhasil masuk database.")
                            time.sleep(2)
                            st.cache_data.clear()
                            st.rerun()

                
