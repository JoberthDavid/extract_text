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
                        gerar_arquivo_custos_unitarios_insumos,
                        iniciar_dicionario,
                        retornar_regex,
                        retornar_regex_cabecalho,
                        configurar_dicionario,
                        escrever_arquivo_cadastro,
                        escrever_arquivo_custos
                    )

pdf_file = "SICRO/GO 10-2020 Relatório Sintético de Materiais.pdf"

d_arquivo = iniciar_dicionario_arquivo()
regex_arquivo = retornar_regex_arquivo( pdf_file )

if ( regex_arquivo is not None ):
    configurar_dicionario_arquivo( d_arquivo, regex_arquivo )

item = retornar_item( d_arquivo )

path =  retornar_path( d_arquivo )

origem_dados = retornar_origem( d_arquivo )

arquivo_material = gerar_arquivo_dados_basicos( path )

custos_unitarios = gerar_arquivo_custos_unitarios_insumos( path )

with open( pdf_file, "rb" ) as f:
    cadastro = pdftotext.PDF( f )
    num_pages = len( cadastro )

with PixelBar('Extraindo dados do PDF', max=num_pages, suffix='%(index)d/%(max)d - %(percent).1f%% - %(eta)ds') as bar:

    lista_dicionarios = list()

    for pagina in cadastro:
        linhas_pagina_atual_pdf = pagina.split('\n') 


        linhas_pagina_atual_pdf.pop(-2)


        for k in range( len( linhas_pagina_atual_pdf ) ):

            d = iniciar_dicionario( item )

            regex = retornar_regex( item, linhas_pagina_atual_pdf[k] )

            cabecalho = retornar_regex_cabecalho( linhas_pagina_atual_pdf[k] )

            if ( cabecalho is None ):

                if ( regex is not None ) and ( len( regex.groups() ) == 4 ):
                    configurar_dicionario( item, d, regex )
                    lista_dicionarios.append( d )

                # é um único caso de material com descrição em duas linhas_pagina_atual_pdf, foi mais fácil criar uma exceção
                if d['codigo'] == 'M3795':
                    d['descricao'] = \
                        'Instalações do Estaleiro Padrão para beneficiamento de estruturas navais, \
                        inclusive mobiliário, equipamentos de informática e de segurança '

        bar.next()


with PixelBar('Escrevendo TXT', max=len( lista_dicionarios ), suffix='%(index)d/%(max)d - %(percent).1f%% - %(eta)ds') as bar:

    for d_material in lista_dicionarios:  
        escrever_arquivo_cadastro( item, arquivo_material, origem_dados, d_material )
        escrever_arquivo_custos( item, custos_unitarios, origem_dados, d_material )

        bar.next()