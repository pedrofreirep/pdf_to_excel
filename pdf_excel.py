import streamlit as st # data app development
import pandas as pd
import subprocess # process in the os
from subprocess import STDOUT, check_call #os process manipuation
import os #os process manipuation
import base64 # byte object into a pdf file 
import camelot as cam # extracting tables from PDFs 
from io import BytesIO

# to run this only once and it's cached
@st.cache_data
def gh():
    """install ghostscript on the linux machine"""
    proc = subprocess.Popen('apt-get install -y ghostscript', shell=True, stdin=None, stdout=open(os.devnull,"wb"), stderr=STDOUT, executable="/bin/bash")
    proc.wait()

gh()




st.title("📋 Transformando bases em PDF para Excel")
# st.subheader("with `Camelot` Python library")

# st.markdown('Este é um transformador seguro de bases salvas em um arquivo PDF para Excel, onde os arquivos aqui carregados não são salvos, copiados ou armezados pela Blue AI em nenhum momento. Esta aplicação é gratuita, você pode usar quando e o quanto quiser. O código desta aplicação em breve estará aberto e será público.')
st.caption('Feito com 🧠 por Blue AI.')
st.info('Este é um transformador seguro de bases salvas em um arquivo PDF para Excel, onde **os arquivos aqui carregados não são salvos, copiados ou armezados pela Blue AI** em nenhum momento. Esta aplicação é gratuita, **você pode usar quando e o quanto quiser**. O código desta aplicação em breve estará aberto e será público.')

# file uploader on streamlit 
st.markdown('\n\n')
st.write('#### 1) Comece escolhendo o seu arquivo PDF para ser transformado')
input_pdf = st.file_uploader(label = "Carregue o seu PDF aqui:", type = 'pdf')

st.markdown('\n\n')
st.markdown("#### 2) Agora selecione a página do seu arquivo que será transformada")

page_number = st.text_input("Digite o número da página, ex: 3:", value = 1)

# run this only when a PDF is uploaded

if input_pdf is not None:
    # byte object into a PDF file 
    with open("input.pdf", "wb") as f:
        base64_pdf = base64.b64encode(input_pdf.read()).decode('utf-8')
        f.write(base64.b64decode(base64_pdf))
    f.close()

    # read the pdf and parse it using stream
    table = cam.read_pdf("input.pdf", pages = page_number, flavor = 'stream')

    # st.markdown("### Number of Tables")

    # display the output after parsing 
    # st.write(table)

    # display the table

    if len(table) > 0:

        # extract the index value of the table
        
        # option = st.selectbox(label = "Select the Table to be displayed", options = range(len(table)))
        option = 0

        st.markdown('\n\n')
        st.markdown('#### 3) Avalie o resultado e baixe o seu arquivo, agora em Excel')

        # display the dataframe
        
        st.dataframe(table[option].df)

        def to_excel(df):
            output = BytesIO()
            writer = pd.ExcelWriter(output, engine='xlsxwriter')
            table[option].df.to_excel(writer, index=False, sheet_name='Sheet1')
            workbook = writer.book
            worksheet = writer.sheets['Sheet1']
            format1 = workbook.add_format({'num_format': '0.00'}) 
            worksheet.set_column('A:A', None, format1)  
            writer.save()
            processed_data = output.getvalue()
            return processed_data
        df_xlsx = to_excel(table[option].df)
        st.download_button(label='📥 Baixar Planilha',
                                        data=df_xlsx ,
                                        file_name= 'teste.xlsx')