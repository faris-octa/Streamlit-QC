import streamlit as st

st.set_page_config(
    page_title="Home",
    page_icon="👋",
    layout = "wide",
    menu_items={
        'Get Help': 'https://docs.streamlit.io/',
        'Report a bug': "mailto:m.faris.octa@gmail.com",
        'About': """
        This is an INKALI QC Calculator App
        \nAuthor : Faris Octa
        """
    })

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

        if lot_option_av != None:
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
    df = qc_conn.query("select * from totalamine", 
    show_spinner = True, 
    ttl=10
    )

    sampel_option_ta = st.selectbox(
        'Nama Item',
        df['ItemDescription'].unique().tolist(),
        index=None,
        placeholder="Pilih Item...",
        key = "sampel_option_ta"
        )

    if sampel_option_ta != None:
        lot_option_ta = st.selectbox(
            'Lot Number',
            df.loc[df['ItemDescription'] == sampel_option_ta, 'LotSerialNumber'].unique().tolist(),
            index=None,
            placeholder="Pilih Lot...",
            key = "lot_option_ta"
            )

        if lot_option_ta != None:
            st.dataframe(
                df.loc[(df['ItemDescription'] == sampel_option_ta) & (df['LotSerialNumber'] == lot_option_ta),
                ["TimeStamp", "Suhu", "FaktorBuret", "FaktorHClO4", "BeratSampel", "JumlahTitran", "TotalAmine", "Keterangan", "Operator"]
                ],
                column_config={
                    "FaktorBuret": "Faktor Buret",
                    "FaktorHClO4": "Faktor HClo4",
                    "BeratSampel": "Berat Sample (g)",
                    "Suhu": "Temperature",
                    "JumlahTitran": "Titran (mL)",
                    "TotalAmine": "Total Amine",
                    "Keterangan" : "Status",
                    "TimeStamp" : st.column_config.DatetimeColumn("Waktu", format="h:mm a")
                },
                hide_index = True,
                use_container_width = True
            )
        
            # st.dataframe(df) -> uncomment for debugging

elif qc_option == "Solid Content":
    df = qc_conn.query("select * from solidcontent", 
    show_spinner = True, 
    ttl=10
    )

    sampel_option_sc = st.selectbox(
        'SecondItemNumber',
        df['SecondItemNumber'].unique().tolist(),
        index=None,
        placeholder="Pilih Item...",
        key = "sampel_option_sc"
        )

    if sampel_option_sc != None:
        lot_option_sc = st.selectbox(
            'Lot Number',
            df.loc[df['SecondItemNumber'] == sampel_option_sc, 'LotSerialNumber'].unique().tolist(),
            index=None,
            placeholder="Pilih Lot...",
            key = "lot_option_sc"
            )

        if lot_option_sc != None:
            st.dataframe(
                df.loc[(df['SecondItemNumber'] == sampel_option_sc) & (df['LotSerialNumber'] == lot_option_sc),
                ["Metode", "SolidContent", "BeratWadah", "BeratSampelBasah", "BeratAkhir", "Status", "Operator1", "Operator2", "TimeStampInit", "TimeStampEnd"]
                ],
                column_config={
                    "BeratWadah": "Berat Cawan",
                    "BeratSampelBasah": "Berat Sampel",
                    "BeratAkhir": "Berat Oven",
                    "SolidContent": "(%) Solid Content",
                    "TimeStampInit": st.column_config.DatetimeColumn("Waktu Masuk", format="h:mm a"),
                    "TimeStampEnd": st.column_config.DatetimeColumn("Waktu Keluar", format="h:mm a"),
                },
                hide_index = True,
                use_container_width = True
            )
        
            # st.dataframe(df) #-> uncomment for debugging   
            
elif qc_option == "Volatile Matter":
    df = qc_conn.query("select * from volatilematter", 
    show_spinner = True, 
    ttl=10
    )

    sampel_option_vm = st.selectbox(
        'Nama Item',
        df['ItemDescription'].unique().tolist(),
        index=None,
        placeholder="Pilih Item...",
        key = "sampel_option_vm"
        )

    if sampel_option_vm != None:
        lot_option_vm = st.selectbox(
            'Lot Number',
            df.loc[df['ItemDescription'] == sampel_option_vm, 'LotSerialNumber'].unique().tolist(),
            index=None,
            placeholder="Pilih Lot...",
            key = "lot_option_vm"
            )

        if lot_option_vm != None:
            st.dataframe(
                df.loc[(df['ItemDescription'] == sampel_option_vm) & (df['LotSerialNumber'] == lot_option_vm),
                ["VolatileMatter", "BeratWadah", "BeratNa2SO4", "BeratSampelBasah", "BeratAkhir", "Status", "Operator1", "Operator2", "TimeStampInit", "TimeStampEnd"]
                ],
                column_config={
                    "BeratWadah": "Berat Cawan",
                    "BeratNa2SO4": "Na2SO4 (g)",
                    "BeratSampelBasah": "Berat Sampel",
                    "BeratAkhir": "Berat Oven",
                    "VolatileMatter": "(%) Volatile Matter",
                    "TimeStampInit": st.column_config.DatetimeColumn("Waktu Masuk", format="h:mm a"),
                    "TimeStampEnd": st.column_config.DatetimeColumn("Waktu Keluar", format="h:mm a"),
                },
                hide_index = True,
                use_container_width = True
            )
        
            # st.dataframe(df) #-> uncomment for debugging

