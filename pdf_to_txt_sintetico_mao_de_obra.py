#*-* coding: utf-8 *-*
from datetime import datetime

import pdftotext
from progress.bar import Bar, PixelBar

from funcoes import (
                        iniciar_dicionario_arquivo,
                        retornar_regex_arquivo,
                        configurar_dicionario_arquivo,
                        retornar_item,
                        retornar_path,
                        retornar_origem,
                        gerar_arquivo_dados_basicos,
                        gerar_arquivo_custos_unitarios_insumos,
                        gerar_arquivo_detalhamento_custos_mao_de_obra,
                        iniciar_dicionario,
                        retornar_regex,
                        retornar_regex_cabecalho,
                        configurar_dicionario,
                        escrever_arquivo_cadastro,
                        escrever_arquivo_custos,
                        escrever_arquivo_detalhamento_custos
                    )
from classes import (
                        RegexArquivo,
                        Arquivo,
                        RegexMaoDeObra,
                        MaoDeObra,
                    )

pdf_file = "SICRO/GO 10-2020 Relatório Sintético de Mao de Obra.pdf"

with open( pdf_file, "rb" ) as f:
    cadastro = pdftotext.PDF( f )
    num_pages = len( cadastro )

#####################

obj_regex_arquivo = RegexArquivo( pdf_file )

if ( obj_regex_arquivo.regex is not None ):
    obj_arquivo = Arquivo( obj_regex_arquivo.regex )

with PixelBar('Extraindo dados do PDF', max=num_pages, suffix='%(index)d/%(max)d - %(percent).1f%% - %(eta)ds') as bar:

    lista_mao_de_obra = list()

    lista_dicionarios = list()

    for pagina in cadastro:
        linhas_pagina_atual_pdf_file = pagina.split('\n')
        linhas_pagina_atual_pdf_file.pop(-2)


        for linha in linhas_pagina_atual_pdf_file:

            d = iniciar_dicionario( obj_arquivo.item )
            
            obj_regex = RegexMaoDeObra( linha )

            if ( obj_regex.cabecalho is None ) and ( obj_regex.principal is not None ):

                configurar_dicionario( obj_arquivo.item, d, obj_regex.principal )

                if d['codigo'] not in lista_dicionarios:
                    lista_dicionarios.append( d['codigo'] )
                    lista_mao_de_obra.append( d )

        bar.next()


with PixelBar('Escrevendo TXT', max=len( lista_mao_de_obra ), suffix='%(index)d/%(max)d - %(percent).1f%% - %(eta)ds') as bar:

    for mao_de_obra in lista_mao_de_obra:  
        escrever_arquivo_cadastro( obj_arquivo.item, obj_arquivo.arquivo_dado_basico, obj_arquivo.origem, mao_de_obra )
        escrever_arquivo_custos( obj_arquivo.item, obj_arquivo.arquivo_custo_unitario, obj_arquivo.origem, mao_de_obra )
        escrever_arquivo_detalhamento_custos( obj_arquivo.item, obj_arquivo.arquivo_detalhamento_custo_mao_de_obra, obj_arquivo.origem, mao_de_obra )

        bar.next()