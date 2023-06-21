import streamlit as st
import pandas as pd
import time
import numpy as np
import logging
from PIL import Image

# Database connection string
conn = st.experimental_connection("qcdb", type="sql", autocommit=True)
engine = create_engine("mysql+mysqldb://inkaliqc:qcoke@192.168.0.70/qc")

# Viscosity factor
visc_factor_data = {
    "speed": [0.3, 0.6, 1.5, 3, 6, 12, 30, 60, 0.3, 0.6, 1.5, 3, 6, 12, 30, 60, 0.3, 0.6, 1.5, 3, 6, 12, 30, 60, 0.3, 0.6, 1.5, 3, 6, 12, 30, 60],
    "spindle": [1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4],
    "factor": [200, 100, 40, 20, 10, 5, 2, 1,
            1000, 500, 200, 100, 50, 25, 10, 5,
            4000, 2000, 800, 400, 200, 100, 40, 20,
            20000, 10000, 4000, 2000, 1000, 500, 200, 100]
}
v_factor_df = pd.DataFrame(visc_factor)

# Viscosity calculation
def calculate_viscosity(spindle, speed, measurement):
    df_row = v_factor_df[(v_factor_df['spindle'] == spindle) & (v_factor_df['speed'] == speed)]
    factor = int(df_row['factor'])
    viscosity = factor * measurement
    return viscosity

def app():
    logging.info('Viskositas Page Started')
    st.title('Viscosity')
    st.write('This is the Viscosity Calculator Page.')

    st.subheader("We will be available soon✌️")

    image = Image.open('maintenance.jpeg')

    st.image(image, use_column_width='always')
    

if __name__ == "__main__":
    # Setup logging configuration
    logging.basicConfig(level=logging.INFO)
    app()