import selenium
import pandas as pd
import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import pandas as pd
import hashlib



# Inicializando o navegador Chrome via Selenium
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')  # Executar o navegador sem interface gráfica
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

# Criando uma nova instância do WebDriver
driver = webdriver.Chrome(options=chrome_options)


REGULAR_POST_IMAGE_SIZE_IN_BYTES = 20000 # in bytes
HEADER_SIZE = 6 #

def sanitize_filename(url):
    # Use a hash of the URL to create a unique, valid filename
    return hashlib.md5(url.encode()).hexdigest() + ".jpg"

def file_size_in_bytes(file_path):
  return os.path.getsize(file_path)

# last_suffix_not_used é o último suffixo (utilizado no diretório de images) + 1 !
def download_images_from_url(url, download_path, wait_time_in_seconds):
    driver.get(url)
    time.sleep(wait_time_in_seconds)

    # Encontrar todos os elementos <img> na página
    img_elements = driver.find_elements(By.TAG_NAME, 'img')

    image_urls = []
    for img in img_elements:
        src = img.get_attribute('src')
        if src:
            image_urls.append(src)

    print(f'Encontradas {len(image_urls)} imagens.')

    # Criar o diretório de download se não existir
    os.makedirs(download_path, exist_ok=True)

    default_sleep_in_between = 1

    # Baixar as imagens
    for i, image_url in enumerate(image_urls):
        try:
            time.sleep(default_sleep_in_between)
            response = requests.get(image_url)
            image_path = os.path.join(download_path, sanitize_filename(image_url))
            #print(image_path)
            with open(image_path, 'wb') as f:
                f.write(response.content)
            if file_size_in_bytes(image_path) < REGULAR_POST_IMAGE_SIZE_IN_BYTES:
                os.remove(image_path)
            else:
                print(f'Imagem {image_url} baixada com sucesso.')
        except Exception as e:
            print(f'Erro ao baixar imagem {i}: {e}')

    return 0
'''
 1 - Esta é a forma de coletar as imagens
 2 - Basta iterar sobre as urls no dataset, estabelecer um tempo de espera para o selinium
 3 - Estabelecer um caminho para salvar as imagens, IMPORTANTE:
    SE o argumento last_suffix_used não for especificado,
    ENTÃO a função vai sobrescrever imagens já existentes.
'''
def run_example():
  url = 'https://twitter.com/leiatheinvestor/status/1788003043805483214'
  download_folder = 'images/'  # Caminho da pasta para salvar as imagens
  wait_time_in_seconds = 5
  download_images_from_url(url, download_folder, wait_time_in_seconds)
  print("Suas imagens estão no diretório images, basta fazer double click na imagem que o colab abre na lateral")

#def run_coleta():


def pre_process(dataset=None, url_column_name=None):
  if dataset is None:
    print("Argumento dataset inválido!")
    return None
  elif url_column_name is None:
    print("Argumento url_column_name inválido!")
    return None
  elif url_column_name not in dataset.columns:
    print("Argumento " + url_column_name + " não está presente no dataset")
    return None

  dataset = dataset.drop( list(set(dataset.columns.tolist()) - set(['Status URL'])), axis='columns')
  return dataset

#dataset é o dataframe recebido como .xlsx SEM O CABEÇALHO!
def extract_images_from_dataset(download_folder = None, wait_time_in_seconds = 5, dataset=None, url_column_name=None, last_suffix_not_used=0):
  res = pre_process(dataset, url_column_name)
  if res is None:
    return None
  else:
    dataset = res

  urls_list = dataset[url_column_name].tolist()

  L = [ download_images_from_url(url, download_folder, wait_time_in_seconds) for url in urls_list ]

  #print("Suas imagens estão no diretório images, basta fazer double click na imagem que o colab abre na lateral")

#run_example()
#url = 'https://twitter.com/leiatheinvestor/status/1788003043805483214'
#print( hashlib.md5( url.encode('utf-8')).hexdigest() + ".jpg" )

df = pd.read_excel('dataset_imagens_twitter.xlsx',skiprows=HEADER_SIZE)
df2 = df.head(10).copy()
extract_images_from_dataset(download_folder="images", dataset=df2,url_column_name='Status URL')