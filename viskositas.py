import streamlit as st
import pandas as pd
import time
import numpy as np
import logging
from PIL import Image

visc_factor = {
    "speed": [0.3, 0.6, 1.5, 3, 6, 12, 30, 60, 0.3, 0.6, 1.5, 3, 6, 12, 30, 60, 0.3, 0.6, 1.5, 3, 6, 12, 30, 60, 0.3, 0.6, 1.5, 3, 6, 12, 30, 60],
    "spindle": [1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4],
    "factor": [200, 100, 40, 20, 10, 5, 2, 1]
}

visc_factor_df = pd.DataFrame(visc_factor)

# filter data
result = visc_factor_df[(visc_factor_df['speed'] == 1) & (visc_factor_df['spindle'] == 1)]
print(result['factor'])

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