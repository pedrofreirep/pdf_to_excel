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
st.caption('Feito com 🧠 por [Blue AI](https://blueai.com.br/)')
st.info('Este é um transformador seguro de bases salvas em um arquivo PDF para Excel, onde **os arquivos aqui carregados não são salvos, copiados ou armezados pela Blue AI** em nenhum momento. Esta aplicação é gratuita, **você pode usar quando e o quanto quiser**. O código desta aplicação em breve estará aberto e será público.')

# file uploader on streamlit 
st.markdown('\n\n')
st.write('##### 1) Comece escolhendo o seu arquivo PDF para ser transformado')
input_pdf = st.file_uploader(label = "Carregue o seu PDF aqui:", type = 'pdf')

st.markdown('\n\n')
st.markdown("##### 2) Agora selecione a página do seu arquivo que será transformada")

page_number = st.text_input("Digite o número da página onde está a sua base, ex: 3:", value = 1)

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

        new_df = table[option].df
        # new_df

        st.markdown('\n\n')
        st.markdown('##### 3) Avalie o resultado e baixe o seu arquivo, agora em Excel')

        # display the dataframe
        with st.expander("Se precisar, clique aqui para configurações avançadas:"):
            premium_features = st.multiselect('Selecione aqui quais configurações avançadas você precisa:', options=['Configurar início da base', 'Apagar linhas desnecessárias'], default=None)
            if premium_features == ['Configurar início da base']:
                header_line = st.number_input('Selecione em qual linha está os nomes das colunas da sua base:', step=1)
                try:
                    new_df.columns = new_df.iloc[header_line]
                    new_df = new_df[(header_line + 1):]
                except ValueError:
                    st.error('Linha inválida para se tornar uma coluna, seleciona outra linha', icon="🚨")

            elif premium_features == ['Apagar linhas desnecessárias']:
                n_linhas = st.number_input('Quantos **tipos** de linhas você gostaria de apagar? \n\nex: 100 linhas com o mesmo conteúdo representa o mesmo tipo de linha.', step=1)
                for i in range(n_linhas):

                    df_column = st.selectbox('Selecione a coluna que inicia o conteúdo da linha que será apagada:', new_df.columns, key=f"drop_line`{[i]}`")
                    df_line = st.text_input('Escreva o conteúdo da primeira célula da linha que deseja apagar:', key=f"line_content`{[i]}`")

                    new_df[df_column] = new_df[df_column].astype(str)

                    def column_color(val):
                        color = '#FFDBE4'
                        return f'background-color: {color}'
                    
                    # def line_color(val):
                    #     color = '#FFDBE4'
                    #     return f'background-color: {color}'
                    
                    new_df = new_df.drop(new_df[new_df[df_column] == df_line].index)
            elif len(premium_features)>1:
                header_line = st.number_input('Selecione em qual linha está os nomes das colunas da sua base:', step=1)
                try:
                    new_df.columns = new_df.iloc[header_line]
                    # st.write(new_df.columns)
                    new_df = new_df[(header_line + 1):]
                    new_df
                except ValueError:
                    st.error('Linha inválida para se tornar uma coluna, seleciona outra linha', icon="🚨")

                n_linhas = st.number_input('Quantos **tipos** de linhas você gostaria de apagar? \n\nex: 100 linhas com o mesmo conteúdo representa o mesmo tipo de linha.', step=1)
                for i in range(n_linhas):

                    df_column = st.selectbox('Selecione a coluna que inicia o conteúdo da linha que será apagada:', new_df.columns, key=f"drop_line`{[i]}`")
                    df_line = st.text_input('Escreva o conteúdo da primeira célula da linha que deseja apagar:', key=f"line_content`{[i]}`")

                    new_df[df_column] = new_df[df_column].astype(str)

                    def column_color(val):
                        color = '#FFDBE4'
                        return f'background-color: {color}'
                    
                    new_df = new_df.drop(new_df[new_df[df_column] == df_line].index)
            else:
                pass

                

        try:
            new_df
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
        except ValueError:
            st.error('Verifique se os campos acima foram preenchidos corretamente', icon="🚨")
