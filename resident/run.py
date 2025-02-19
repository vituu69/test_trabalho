import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import pandas as pd

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'pt-BR,pt;q=0.9',
    'cache-control': 'max-age=0',
    'referer': 'https://www.residentevildatabase.com/personagens/',
    'sec-ch-ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
}


def get_content(url):
    """
    Faz uma requisição HTTP GET para a URL especificada e retorna a resposta.

    Parâmetros:
        url (str): A URL da página a ser acessada.

    Retorna:
        requests.Response: Objeto de resposta da requisição.
    """
    resp = requests.get(url, headers=headers)
    return resp


def get_basic_infos(soup):
    """
    Extrai informações básicas de um personagem a partir do objeto BeautifulSoup.

    Esta função busca a div com a classe 'td-page-content', seleciona o segundo
    parágrafo (<p>) e, em seguida, extrai os elementos <em> contidos nele. Para cada
    elemento <em>, o texto é dividido em chave e valor usando o caractere ':'.

    Parâmetros:
        soup (BeautifulSoup): Objeto BeautifulSoup contendo o conteúdo HTML da página.

    Retorna:
        dict: Dicionário com as informações básicas do personagem.
    """
    div_page = soup.find("div", class_="td-page-content")
    paragrafo = div_page.find_all("p")[1]
    ems = paragrafo.find_all("em")
    data = {}
    for i in ems:
        # Divide o texto em chave e valor; ignora possíveis partes extras
        chave, valor, *_ = i.text.split(":")
        chave = chave.strip(" ")
        data[chave] = valor.strip(" ")
    return data


def get_aparicoes(soup):
    """
    Extrai a lista de aparições de um personagem a partir do objeto BeautifulSoup.

    A função localiza a div com a classe 'td-page-content', procura um cabeçalho <h4>
    e, a partir deste, encontra a lista (<li>) que contém as aparições do personagem.

    Parâmetros:
        soup (BeautifulSoup): Objeto BeautifulSoup contendo o conteúdo HTML da página.

    Retorna:
        list: Lista de strings, onde cada string representa uma aparição do personagem.
    """
    lis = (soup.find("div", class_="td-page-content")
               .find("h4")
               .find_next()
               .find_all("li"))
    aparicoes = [i.text for i in lis]
    return aparicoes


def get_personagem_infos(url):
    """
    Obtém as informações de um personagem a partir de sua URL.

    Esta função realiza uma requisição à URL do personagem, processa o HTML com BeautifulSoup,
    extrai as informações básicas e a lista de aparições, e retorna todas essas informações em um dicionário.

    Parâmetros:
        url (str): A URL da página do personagem.

    Retorna:
        dict: Dicionário contendo as informações do personagem.
              Caso a requisição falhe, retorna um dicionário vazio.
    """
    resp = get_content(url)
    if resp.status_code != 200:
        print("Não foi possível obter os dados")
        return {}
    else:
        soup = BeautifulSoup(resp.text, 'html.parser')
        data = get_basic_infos(soup)
        data["Aparicoes"] = get_aparicoes(soup)
        return data


def get_links():
    """
    Extrai os links de todas as páginas de personagens do site.

    A função acessa a página principal de personagens, processa o HTML com BeautifulSoup,
    localiza a div com a classe 'td-page-content' e extrai os atributos 'href' de todas as âncoras (<a>).

    Retorna:
        list: Lista de URLs (str) dos personagens.
    """
    url = "https://www.residentevildatabase.com/personagens/"
    resp = requests.get(url, headers=headers)
    soup_personagens = BeautifulSoup(resp.text, 'html.parser')
    ancoras = (soup_personagens.find("div", class_="td-page-content")
                               .find_all("a"))
    links = [i["href"] for i in ancoras]
    return links


# Coleta os links dos personagens e extrai as informações de cada um
links = get_links()
data = []
for i in tqdm(links):
    d = get_personagem_infos(i)
    d["Link"] = i
    # Extrai o nome do personagem a partir da URL, formata e adiciona ao dicionário
    nome = i.strip("/").split("/")[-1].replace("-", " ").title()
    d["Nome"] = nome
    data.append(d)

# Cria um DataFrame e salva os dados em dois arquivos CSV
df = pd.DataFrame(data)
df.to_csv(r"resident/csv/dados_re.csv", sep=';', index=False)
df.to_csv(r"resident/csv/dados_com_erro_de_formatacao.csv", sep=';', index=False)
