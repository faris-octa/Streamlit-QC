import streamlit as st

st.set_page_config(
    page_title="Home",
    page_icon="👋",
)

qc_conn = st.connection("qcdb", type="sql", autocommit=True)


st.write("# Welcome to QC App! 👋")
st.divider()

st.sidebar.success("Pilih opsi di atas untuk input data.")

measurement = ["Acid Value", "Solid Content", "Total Amine", "Volatile Matter"]

qc_option = st.selectbox(
        'Pengukuran',
        measurement,
        index=None,
        placeholder="Pilih jenis pengukuran...",
        key = "qc_option"
    )


if qc_option == "Acid Value":
    df = qc_conn.query("select * from acidvalue", 
    show_spinner = True, 
    ttl=10
    )

    sampel_option_av = st.selectbox(
        'Nama Item',
        df['ItemDescription'].unique().tolist(),
        index=None,
        placeholder="Pilih Item...",
        key = "sampel_option_av"
    )

    if sampel_option_av != None:
        lot_option_av = st.selectbox(
            'Lot Number',
            df.loc[df['ItemDescription'] == sampel_option_av, 'LotSerialNumber'].unique().tolist(),
            index=None,
            placeholder="Pilih Lot...",
            key = "lot_option_av"
        )

        if lot_option_av is not None:
            st.dataframe(
                df.loc[(df['ItemDescription'] == sampel_option_av) & (df['LotSerialNumber'] == lot_option_av),
                ["TimeStamp", "Suhu", "FaktorBuret", "FaktorNaOH", "BeratSampel", "JumlahTitran", "AcidValue", "Keterangan", "Operator"]
                ],
                column_config={
                    "FaktorBuret": "Faktor Buret",
                    "FaktorNaOH": "Faktor NaOH",
                    "BeratSampel": "Berat Sample (g)",
                    "Suhu": "Temperature",
                    "JumlahTitran": "Titran (mL)",
                    "AcidValue": "Acid Value",
                    "Keterangan" : "Status",
                    "TimeStamp" : st.column_config.DatetimeColumn("Waktu", format="h:mm a")
                },
                hide_index = True,
                use_container_width = True
            )
        
        # st.dataframe(df)

elif qc_option == "Total Amine":
    None