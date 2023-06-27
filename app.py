import streamlit as st
import home
import sc
import av
import viskositas
import totalAmine
import logging

# Dictionary mapping page names to modules
PAGES = {
    "---TRACKER---": home,
    "Acid Value": av,
    "Solid Content": sc,
    "Total Amine": totalAmine,
    "Viscosity": viskositas
}

def main():
    """
    Main function to run the Streamlit app.
    """
    st.set_page_config(
        page_title="INKALI QC Webpage", 
        page_icon=":tada:", 
        layout="wide")
    
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
        #MainMenu {visibility: visible;}
        footer {visibility: visible;}
        footer:after{
            content:'By Faris Octa';
            display:block;
            position:relative;
        }
        header {visibility: visible;}
        </style>
        """
    st.markdown(hide_st_style, unsafe_allow_html=True)

if __name__ == "__main__":
    # Setup logging configuration
    logging.basicConfig(level=logging.INFO)
    main()