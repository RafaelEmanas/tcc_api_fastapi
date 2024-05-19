from bs4 import BeautifulSoup

from selenium import webdriver
import selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

driver_option = webdriver.ChromeOptions()
driver_option.add_argument("--headless")
driver_service = Service(ChromeDriverManager().install())

class RequestUrl(BaseModel):
    url: str

def get_number(string:str):
    number = ''
    for i in range(len(string)):
        if string[i].isnumeric() or string[i]=='.' or string[i]==',':
            number+=string[i]
    return number

@app.get("/")
def index():
    return selenium.__version__

@app.post("/extract")
def extractProducts(requestUrl : RequestUrl):

    url = requestUrl.url

    driver = webdriver.Chrome(service=driver_service, options=driver_option)

    driver.get(url)
    products_table_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'tabResult')))
    total_div_element = driver.find_element(By.ID, 'totalNota')
    html_content_products = products_table_element.get_attribute('outerHTML')
    html_content_total = total_div_element.get_attribute('outerHTML')
    driver.quit()
    
    soup1 = BeautifulSoup(html_content_products, 'html.parser')
    soup2 = BeautifulSoup(html_content_total, 'html.parser')

    produtos_comprados_dict = {'produtos_comprados': [], 'produtos_precototal': ''}

    quantidade_itens_comprados = len(soup1.find_all("tr"))

    for i in range(quantidade_itens_comprados):
        item_element = soup1.find('tr', id=f'Item + {i+1}')

        item_nome = item_element.td.span.text
        item_quantidade = item_element.td.find_all('span')[2].text
        item_unidade = item_element.td.find_all('span')[3].text
        item_precounidade = item_element.td.find_all('span')[4].text

        product_dict = {
            'produto_id': i,
            'produto_nome': item_nome,
            'produto_unidade': item_unidade[5:],
            'produto_quantidade': float(item_quantidade[6:].replace(",", ".")),
            'produto_precounidade': float(get_number(item_precounidade)[2:].replace(",", ".")),
            'produto_selecionado': False,
            'produto_disponivel': True
        }
        produtos_comprados_dict['produtos_comprados'].append(product_dict)

    total_pagar = soup2.find_all('div')[2].span.text
    produtos_comprados_dict['produtos_precototal'] = float(total_pagar.replace(',','.'))

    return produtos_comprados_dict