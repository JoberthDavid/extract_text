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
                        gerar_arquivo_detalhamento_custos_equipamento,
                        iniciar_dicionario,
                        retornar_regex,
                        retornar_regex_cabecalho,
                        configurar_dicionario,
                        escrever_arquivo_cadastro,
                        escrever_arquivo_custos,
                        escrever_arquivo_detalhamento_custos
                    )

pdf_file = "SICRO/GO 10-2020 Relatório Sintético de Equipamentos.pdf"

pdf_file_desonerado = "SICRO/GO 10-2020 Relatório Sintético de Equipamentos - com desoneraç╞o.pdf"


d_arquivo = iniciar_dicionario_arquivo()
regex_arquivo = retornar_regex_arquivo( pdf_file )

if ( regex_arquivo is not None ):
    configurar_dicionario_arquivo( d_arquivo, regex_arquivo )

item = retornar_item( d_arquivo )

path =  retornar_path( d_arquivo )

origem_dados = retornar_origem( d_arquivo )

arquivo_equipamento = gerar_arquivo_dados_basicos( path )

custos_unitarios = gerar_arquivo_custos_unitarios_insumos( path )

detalhamento_custos = gerar_arquivo_detalhamento_custos_equipamento( path )

with open( pdf_file, "rb" ) as f:
    cadastro = pdftotext.PDF( f )
    num_pages = len( cadastro )

with open( pdf_file_desonerado, "rb" ) as f_desonerado:
    cadastro_desonerado = pdftotext.PDF( f_desonerado )
    num_pages_desonerado = len( cadastro_desonerado )

with PixelBar('Extraindo dados do PDF', max=num_pages, suffix='%(index)d/%(max)d - %(percent).1f%% - %(eta)ds') as bar:

    lista_dicionarios_onerado = list()

    lista_dicionarios_desonerado = list()

    lista_dicionarios = list()

    for j in range( len( cadastro ) ):


        linhas_desonerado = cadastro_desonerado[j].split('\n')
        linhas_desonerado.pop(-2)


        linhas_pagina_atual_pdf_onerado = cadastro[j].split('\n')
        linhas_pagina_atual_pdf_onerado.pop(-2)


        for k in range( len( linhas_pagina_atual_pdf_onerado ) ):

            d = iniciar_dicionario( item )

            regex_onerado = retornar_regex( item, linhas_pagina_atual_pdf_onerado[k] )
            regex_desonerado = retornar_regex( item, linhas_desonerado[k] )

            cabecalho_onerado = retornar_regex_cabecalho( linhas_pagina_atual_pdf_onerado[k] )
            cabecalho_desonerado = retornar_regex_cabecalho( linhas_desonerado[k] )

            if ( cabecalho_onerado is None ) and ( cabecalho_desonerado is None ):

                if regex_onerado is not None:
                    configurar_dicionario( item, d, regex_onerado, regex_desonerado )
                    
                    if d['codigo'] not in lista_dicionarios:
                        lista_dicionarios.append( d['codigo'] )
                        lista_dicionarios_onerado.append( d )

        bar.next()


with PixelBar('Escrevendo TXT', max=len( lista_dicionarios_onerado ), suffix='%(index)d/%(max)d - %(percent).1f%% - %(eta)ds') as bar:
    
    for d_equipamento in lista_dicionarios_onerado:
        escrever_arquivo_cadastro( item, arquivo_equipamento, origem_dados, d_equipamento )
        escrever_arquivo_custos( item, custos_unitarios, origem_dados, d_equipamento )
        escrever_arquivo_detalhamento_custos( item, detalhamento_custos, origem_dados, d_equipamento )

        bar.next()