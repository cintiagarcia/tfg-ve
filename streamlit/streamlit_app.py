# streamlit_app.py

import streamlit as st
import s3fs
import pandas as pd
from st_files_connection import FilesConnection
import numpy as np
import time


# # Create an S3 file system object
# fs = s3fs.S3FileSystem()

# # List all objects in the bucket
# bucket_name = "clean-data-ve-eu-central-1"
# file_paths = fs.glob(f"{bucket_name}/*")

# # Iterate over the file paths and read each object
# for file_path in file_paths:
#     with fs.open(file_path, "rb") as file:
#         # Read the object content, a csv file
#         df = pd.read_csv(file)

#         # Print results
#         for row in df.itertuples():
#             st.write(f"{row.provincia} tiene en total: {row.total} en el año: {row.año}")


st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

st.write("# Welcome to Streamlit! 👋")

st.sidebar.success("Select a page above.")


# Add a placeholder
latest_iteration = st.empty()
bar = st.progress(0)

for i in range(100):
  # Update the progress bar with each iteration.
  latest_iteration.text(f'Iteration {i+1}')
  bar.progress(i + 1)
  time.sleep(0.1)

'...and now we\'re done!'
