import glob
from selenium import webdriver
import time
import pandas as pd
from selenium.webdriver.common.by import By
import yfinance as yf

#diretorio onde será salva a lista de empresas da bolsa
diretorio_download = "C:\\Users\\Pichau\\OneDrive\\FACULDADE\\DEV DE SISTEMAS PYTHON\\PYTHON AVANCADO ESP\\MAPA\\DOWNLOADS\\STOCK_LIST"

#criei esta variavel pra não precisar ficar fazendo o download do arquivo cada vez que eu rodo. Qualquer coisa é só trocar a # do file name ali na main, e ele vai baixar o arquivo e pegar o nome novo
downloaded_file = "C:\\Users\\Pichau\\OneDrive\\FACULDADE\\DEV DE SISTEMAS PYTHON\\PYTHON AVANCADO ESP\\MAPA\\DOWNLOADS\\STOCK_LIST\\IBOVDia_24-04-23.csv"
def main():

    # Usar este filename abaixo se já tiver baixado o arquivo e quiser usar somente ele, sem baixar novos
    file_name = downloaded_file

    # Usar este filename abaixo quando for testar o código baixando um novo arquivo. Assim ele baixa o arquivo e pega o nome do último arquivo baixado para usar
    #file_name = download_file_and_get_the_name()

    # formata o arquivo baixado para deixar no formato que precisamos para ler
    stock_list = format_downloaded_file(file_name)

    # print de todas as linhas na tela
    # print_stock_list(stock_list)

    # coleta os dados do histórico das cotações
    # get_historical_value(stock_list)

    # Pega os percentuais de variação nas cotações
    hist_data = get_historical_value(stock_list)
    variation_through_time = get_variation_through_the_time(hist_data)

    # Pega as 10 que mais valorizaram ao longo do tempo
    filter_main_x_stocks(variation_through_time, 10)


def get_historical_value(stock_list):
    # converte a lista de ativos e formata para que seja possível usar o yahoo finance
    tickers_list = list(stock_list.codigo)
    tickers_list = map(lambda a: f"{a}.SA", tickers_list)
    tickers_sa = " ".join(list(tickers_list))
    #usando pandas para interpretar os dados
    yf.pdr_override()
    #pegando os dados via API
    historic_data = yf.download(tickers=tickers_sa, period='2y')
    # pegando só os dados das cotações
    historical_value = historic_data['Adj Close']
    # remover os NaN
    historical_value.dropna(how='all', inplace=True)

    return historical_value


def get_variation_through_the_time(historical_data):

    # Pega a variação diária
    variation_through_time = historical_data.pct_change()

    # calcula o percentual acumulado
    accum_result = (1 + variation_through_time).cumprod()
    accum_result.iloc[0] = 1

    accum_result = 1000 * accum_result
    accum_result['saldo'] = accum_result.sum(axis=1)
    accum_result['retorno'] = accum_result['saldo'].pct_change()

    return accum_result

def filter_main_x_stocks(accum_result, quant):

    df = accum_result
    first_row = df.iloc[0]
    last_row = df.iloc[-1]
    final_variation = (last_row - first_row) / first_row * 100
    final_variation.columns = ['Ativo','Variação %']
    print(final_variation.sort_values(ascending=False)[:quant])



def get_ativos():
    options = webdriver.ChromeOptions()
    prefs = {"download.default_directory": diretorio_download}
    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(executable_path='C:\\Users\\Pichau\\WebDriver', chrome_options=options)
    driver.get("https://sistemaswebb3-listados.b3.com.br/indexPage/day/IBOV?language=pt-br")
    btn_download = driver.find_element(By.PARTIAL_LINK_TEXT, "Download")
    btn_download.click()
    time.sleep(3)
    driver.close()

def format_downloaded_file(file_name):

    # Lê o arquivo que baixamos
    df_ativos = pd.read_csv(file_name, sep=';', skiprows=1, encoding='latin-1', index_col=False)
    # Exclui as duas últimas colunas
    df_ativos.drop(df_ativos.index[-2:], inplace=True)
    # Renomeia os cabeçalhos
    df_ativos.rename(columns={
        'Qtde. Teórica':'qte_teorica',
        'Ação':'acao',
        'Código':'codigo',
        'Part. (%)':'participacao',
        'Tipo':'tipo'
    }, inplace=True)

    # converte a coluna de quantidade e participação para número

    df_ativos['qte_teorica'] = df_ativos['qte_teorica'].str.replace('.', '').astype(float)
    df_ativos['participacao'] = df_ativos['participacao'].str.replace(',', '.').astype(float)

    return df_ativos



# method to get the downloaded file name
def download_file_and_get_the_name():
    # get file list before download
    list_of_files_before_download = glob.glob(diretorio_download +'/*.csv')

    # Get the loop start time ( current time)
    start = time.time()

    # this is the time in seconds , we set to zero initially
    elapsed = 0

    get_ativos()

    while elapsed < 10:

        list_of_files_after_download = glob.glob(diretorio_download +'/*.csv')
        # get time and check if 120 second is elapsed
        done = time.time()
        elapsed = done - start

        # get new file list
        list_of_files_after_download = glob.glob(diretorio_download +'/*.csv')
        newfile = \
            list(set(list_of_files_after_download).difference(list_of_files_before_download))
        # if new file is created then break the loop
        if len(newfile):
            break
    file_name= newfile[0]
    print('Arquivo baixado. Você pode acessar o arquivo baixado através do link: ' + file_name)
    return file_name

if __name__=='__main__':

    main()