import streamlit as st
import sqlite3
import pandas as pd
import time
import numpy as np
import logging

def app():
    logging.info('Total Amine Page Started')
    st.title('Total Amine')
    st.write('This is the Total Amine Calculator Page.')

    st.subheader("We will be available soon")

if __name__ == "__main__":
    # Setup logging configuration
    logging.basicConfig(level=logging.INFO)
    app()