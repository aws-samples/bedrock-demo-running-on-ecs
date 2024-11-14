########################################################################
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
########################################################################

import streamlit as st
import requests
import os


API_ENDPOINT = os.environ.get('API_ENDPOINT')
API_URL = f'{API_ENDPOINT}/api/prompt'


st.set_page_config(
    page_title='Gen AI - Text'
)

st.title('무엇이든 물어보세요.')

instruction = st.text_area('질문을 입력하세요.', '', height=200)

with st.form('text_form', clear_on_submit=True):
    submitted = st.form_submit_button('Submit')
    if submitted:
        with st.spinner('Loading...'):
            if instruction == '':
                st.error('질문을 입력하세요.')
            else:
                data = {'instruction': instruction}
                response = requests.post(API_URL, json=data)

                result = response.json()

                print(result)

                st.info(result['text'])
