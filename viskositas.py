import streamlit as st
import pandas as pd
import time
import numpy as np
import logging
from PIL import Image

def app():
    logging.info('Viskositas Page Started')
    st.title('Viscosity')
    st.write('This is the Viscosity Calculator Page.')

    st.subheader("We will be available soon✌️")

    image = Image.open('maintenance.jpeg')

    st.image(image)
    

if __name__ == "__main__":
    # Setup logging configuration
    logging.basicConfig(level=logging.INFO)
    app()