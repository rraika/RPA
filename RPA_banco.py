from dotenv import load_dotenv
from os import getenv
import psycopg2
load_dotenv()
#Conectar aos dois bancos de dados
try:
    #Conexão com o banco de origem (1° ano) banco A
    conn_primeiro_banco = psycopg2.connect(
        port=getenv("DB_PRIMEIRO_ANO_PORT"),
        host=getenv("DB_PRIMEIRO_ANO_HOST"),
        database=getenv("DB_PRIMEIRO_ANO_DATABASE"),
        user=getenv("DB_PRIMEIRO_ANO_USER"),
        password=getenv("DB_PRIMEIRO_ANO_PASSWORD")
    )
    print("Conexão com o banco de origem bem-sucedida!")

    #Conexão com o banco de destino (2° ano) banco B
    conn_segundo_banco = psycopg2.connect(
        port=getenv("DB_SEGUNDO_ANO_PORT"),
        host=getenv("DB_SEGUNDO_ANO_HOST"),
        database=getenv("DB_SEGUNDO_ANO_DATABASE"),
        user=getenv("DB_SEGUNDO_ANO_USER"),
        password=getenv("DB_SEGUNDO_ANO_PASSWORD")
    )
    print("Conexão com o banco de destino bem-sucedida!")

    #Cursores para os dois bancos
    banco_a_cursor = conn_primeiro_banco.cursor()
    banco_b_cursor = conn_segundo_banco.cursor()

    #Definindo colunas manualmente (sem 'transferir')
    colunas_adm = ['nome', 'email', 'senha']  #Colunas da tabela adm
    colunas_evento_analise = ['nome', 'descricao', 'dt_evento', 'organizador', 'status']  #Colunas da tabela evento_analise
    colunas_filtros = ['categoria']  #Colunas da tabela filtros

    #Dicionário de tabelas e suas colunas
    tabelas = {
        'adm': colunas_adm,
        'evento_analise': colunas_evento_analise,
        'filtros': colunas_filtros
    }

    #Loop para transferir do Banco A para o Banco B
    for tabela, colunas in tabelas.items():
        columns = ', '.join(colunas)
        placeholders = ', '.join(['%s'] * len(colunas))

        #Selecionar as linhas onde transferir é True no Banco A
        banco_a_cursor.execute(f"SELECT {columns} FROM {tabela} WHERE transferir = True")
        rows_a = banco_a_cursor.fetchall()

        if rows_a:
            #Inserir no Banco B
            for row in rows_a:
                banco_b_cursor.execute(f"INSERT INTO {tabela} ({columns}) VALUES ({placeholders})", row)
            conn_segundo_banco.commit()

            #Atualizar o campo transferir para False no Banco A
            banco_a_cursor.execute(f"UPDATE {tabela} SET transferir = False WHERE transferir = True")
            conn_primeiro_banco.commit()

    #Loop para transferir do Banco B para o Banco A
    for tabela, colunas in tabelas.items():
        columns = ', '.join(colunas)
        placeholders = ', '.join(['%s'] * len(colunas))

        #Selecionar as linhas onde transferir é True no Banco B
        banco_b_cursor.execute(f"SELECT {columns} FROM {tabela} WHERE transferir = True")
        rows_b = banco_b_cursor.fetchall()

        if rows_b:
            #Inserir no Banco A
            for row in rows_b:
                banco_a_cursor.execute(f"INSERT INTO {tabela} ({columns}) VALUES ({placeholders})", row)
            conn_primeiro_banco.commit()

            #Atualizar o campo transferir para False no Banco B
            banco_b_cursor.execute(f"UPDATE {tabela} SET transferir = False WHERE transferir = True")
            conn_segundo_banco.commit()

    #Fechar cursores e conexões
    banco_a_cursor.close()
    banco_b_cursor.close()
    conn_primeiro_banco.close()
    conn_segundo_banco.close()

    print("Transferência bem-sucedida!")

except Exception as e:
    print(f"Erro: {e}")
