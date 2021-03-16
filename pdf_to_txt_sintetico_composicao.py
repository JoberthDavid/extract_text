#*-* coding: utf-8 *-*
import pdftotext
from datetime import datetime
from progress.bar import Bar
from progress.bar import PixelBar

from funcoes import (
                        iniciar_dicionario_arquivo,
                        retornar_regex_arquivo,
                        configurar_dicionario_arquivo,
                        retornar_item,
                        retornar_path,
                        retornar_origem,
                        gerar_arquivo_dados_basicos,
                        gerar_arquivo_custos_unitarios_composicoes,
                        iniciar_dicionario,
                        retornar_regex,
                        retornar_regex_cabecalho,
                        configurar_dicionario,
                        escrever_arquivo_cadastro,
                        escrever_arquivo_custos
                    )

pdf_file = "SICRO/TO 07-2019 Relatório Sintético de Composições de Custos.pdf"


d_arquivo = iniciar_dicionario_arquivo()
regex_arquivo = retornar_regex_arquivo( pdf_file )

if ( regex_arquivo is not None ):
    configurar_dicionario_arquivo( d_arquivo, regex_arquivo )

item = retornar_item( d_arquivo )

path =  retornar_path( d_arquivo )

origem_dados = retornar_origem( d_arquivo )

arquivo_composicao = gerar_arquivo_dados_basicos( path )

custos_unitarios = gerar_arquivo_custos_unitarios_composicoes( path )

with open( pdf_file, "rb" ) as f:
    cadastro = pdftotext.PDF( f )
    num_pages = len( cadastro )


with PixelBar('Extraindo dados do PDF', max=num_pages, suffix='%(index)d/%(max)d - %(percent).1f%% - %(eta)ds') as bar:


    lista_dicionarios_onerado = list()

    for pagina in cadastro:
        linhas_pagina_atual_pdf_onerado = pagina.split('\n')


        linhas_pagina_atual_pdf_onerado.pop(-2)


        for k in range( len( linhas_pagina_atual_pdf_onerado ) ):

            d = iniciar_dicionario( item )

            regex = retornar_regex( item, linhas_pagina_atual_pdf_onerado[k] )

            cabecalho = retornar_regex_cabecalho( linhas_pagina_atual_pdf_onerado[k] )

            if ( cabecalho is None ):

                if ( regex is not None ) and ( len( regex.groups() ) > 4 ):
                    configurar_dicionario( item, d, regex )
                    lista_dicionarios_onerado.append( d )

                elif ( regex is not None ) and ( len( regex.groups() ) <= 4 ) and ( len( lista_dicionarios_onerado ) > 1 ):
                    descricao_anterior = lista_dicionarios_onerado[-1]['descricao']
                    descricao_atual = regex.group('re_descricao')
                    lista_dicionarios_onerado[-1]['descricao'] = ' '.join( [ descricao_anterior, descricao_atual ] )

        bar.next()


with PixelBar('Escrevendo TXT', max=len( lista_dicionarios_onerado ), suffix='%(index)d/%(max)d - %(percent).1f%% - %(eta)ds') as bar:

    for d_composicao in lista_dicionarios_onerado:  
        escrever_arquivo_cadastro( item, arquivo_composicao, origem_dados, d_composicao )
        escrever_arquivo_custos( item, custos_unitarios, origem_dados, d_composicao )

        bar.next()