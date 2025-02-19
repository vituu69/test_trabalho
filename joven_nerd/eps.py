import requests
import json
import datetime
import pandas as pd
import time 

class Coletor:
    """
    Classe responsável por coletar dados de uma API e salvá-los em formatos JSON ou CSV.

    Atributos:
        url (str): URL da API a ser consultada.
        instancia (str): Nome da instância ou categoria dos dados, utilizado na organização dos arquivos salvos.
    """

    def __init__(self, url, instancia):
        """
        Inicializa a instância da classe Coletor.

        Parâmetros:
            url (str): URL da API que será consultada.
            instancia (str): Nome da instância/categoria para organizar os arquivos de saída.
        """
        self.url = url
        self.instancia = instancia

    def formatacao(self):
        """
        Retorna uma string com a data e hora atual formatada, para ser utilizada em nomes de arquivos.

        Retorna:
            str: Data e hora atual no formato "YYYYMMDD_HHMMSS.ffffff".
        """
        now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S.%f")
        return now

    def get_content(self, **kwargs):
        """
        Realiza uma requisição GET para a URL configurada, passando parâmetros opcionais.

        Parâmetros:
            **kwargs: Parâmetros de consulta que serão enviados na requisição.

        Retorna:
            requests.Response: Objeto de resposta da requisição.
        """
        resp = requests.get(self.url, params=kwargs)
        return resp

    def save_csv(self, data):
        """
        Salva os dados fornecidos em um arquivo CSV.

        Parâmetros:
            data (list ou dict): Dados a serem salvos, compatíveis com a criação de um DataFrame do pandas.

        Observação:
            O arquivo CSV será salvo no diretório: 'data/{instancia}/csv/' com um nome baseado na data e hora atual.
        """
        df = pd.DataFrame(data)
        df.to_csv(f'data/csv/{self.formatacao()}.csv', index=False)

    def save_json(self, data, format='json'):
        """
        Salva os dados fornecidos em um arquivo JSON.

        Parâmetros:
            data (list ou dict): Dados a serem salvos.
            format (str): Formato de salvamento. Se for 'json', os dados serão salvos em JSON.

        Observação:
            O arquivo JSON será salvo no diretório: 'data/{instancia}/json/' com um nome baseado na data e hora atual.
        """
        if format == 'json':
            with open(f'joven_nerd/data/{self.instancia}/json/{self.formatacao()}.json', 'w') as open_file:
                json.dump(data, open_file)

    def save_data(self, data, format='json'):
        """
        Salva os dados no formato especificado, utilizando o método apropriado.

        Parâmetros:
            data (list ou dict): Dados a serem salvos.
            format (str): Formato de salvamento ('json' ou 'csv').
        """
        if format == 'json':
            self.save_json(data)
        elif format == 'csv':
            self.save_csv(data)

    def get_and_save(self, save_format='json', **kwargs):
        """
        Realiza uma requisição GET com os parâmetros fornecidos, salva os dados no formato especificado e retorna os dados.

        Parâmetros:
            save_format (str): Formato de salvamento ('json' ou 'csv').
            **kwargs: Parâmetros de consulta que serão enviados na requisição GET.

        Retorna:
            list ou dict: Dados obtidos da requisição se o status for 200; caso contrário, retorna None.
        """
        resp = self.get_content(**kwargs)
        if resp.status_code == 200:
            data = resp.json()
            self.save_data(data, save_format)
        else:
            data = None
            print(f'request sem sucesso {resp.status_code}')
        return data

    def auto_exec(self, seva_format='json', date_stop='2000-01-01'):
        """
        Executa automaticamente a coleta e salvamento de dados paginados até que uma condição de parada seja atingida.

        Parâmetros:
            seva_format (str): Formato de salvamento ('json' ou 'csv').
            date_stop (str): Data limite (no formato 'YYYY-MM-DD') para interromper a coleta, com base no campo 'published_at'.

        Funcionamento:
            - Itera sobre as páginas da API, solicitando dados com parâmetros de paginação.
            - Para cada página, salva os dados no formato especificado.
            - A coleta é interrompida se:
                a) A requisição falhar;
                b) A data de publicação do último item for anterior a 'date_stop';
                c) A quantidade de dados retornada for menor que 1000 (indicando última página).
            - Há pausas entre as requisições para evitar sobrecarga na API.
        """
        page = 1
        while True:
            print(f"Processando página: {page}")
            data = self.get_and_save(save_format=seva_format,
                                     page=page,
                                     per_page=100)  
            if data is None:
                print('Erro na coleta de dados. Aguardando 3 minutos para nova tentativa.')
                time.sleep(60*5)
            else:
                ultima_data = pd.to_datetime(data[-1]['published_at']).date()
                if ultima_data < pd.to_datetime(date_stop).date():
                    break
                elif len(data) < 10:
                    break
                page += 1
                time.sleep(5)

# Exemplo de uso da classe Coletor:
coleta = Coletor('https://api.jovemnerd.com.br/wp-json/jovemnerd/v1/nerdcasts/', 'episodios')
coleta.auto_exec()