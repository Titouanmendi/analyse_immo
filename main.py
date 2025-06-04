# analyse_immo/main.py
import streamlit.web.cli as stcli
import sys

if __name__ == "__main__":
    sys.argv = ["streamlit", "run", "app/search.py"]
    stcli.main()