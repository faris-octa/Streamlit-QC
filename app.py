import streamlit as st
import sc
import av
import viskositas
import totalAmine
import logging

# Dictionary mapping page names to modules
PAGES = {
    "Solid Content": sc,
    "Acid Value": av,
    "Viscosity": viskositas,
    "Total Amine": totalAmine
}

def main():
    """
    Main function to run the Streamlit app.
    """
    # Set the configuration for the Streamlit page
    st.set_page_config(page_title="Faris' Webpage", page_icon=":tada:", layout="wide",)
    
    st.sidebar.title('Main Menu')

    # Allow the user to select a page
    selection = st.sidebar.radio("Go to", list(PAGES.keys()))

    # Try to display the selected page
    try:
        page = PAGES[selection]
        page.app()
    except Exception as e:
        logging.error(f"An error occurred when trying to display the page: {e}")
        st.error(f"An error occurred: {e}")

    hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: visible;}
            footer:after{
                content:'by Faris Octa';
                display:block;
                position:relative;
            }
            header {visibility: hidden;}
            </style>
            """
    st.markdown(hide_st_style, unsafe_allow_html=True)

if __name__ == "__main__":
    # Setup logging configuration
    logging.basicConfig(level=logging.INFO)
    main()