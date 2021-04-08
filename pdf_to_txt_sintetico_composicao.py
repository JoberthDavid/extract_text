#*-* coding: utf-8 *-*
import pdftotext
from datetime import datetime
from progress.bar import Bar
from progress.bar import PixelBar

from classes import (
                        RegexComposicao,
                        Composicao,
                        RegexArquivo,
                        Arquivo,
                    )

##### Extraindo dados arquivo PDF

pdf_file_onerado = "SICRO/GO 10-2020 Relatório Sintético de ComposiçΣes de Custos.pdf"

with open( pdf_file_onerado, "rb" ) as f:
    cadastro_onerado = pdftotext.PDF( f )
    num_pages_onerado = len( cadastro_onerado )

with PixelBar('Extraindo dados do PDF', max=num_pages_onerado, suffix='%(index)d/%(max)d - %(percent).1f%% - %(eta)ds') as bar:

    lista_composicao = list()

    for pagina in cadastro_onerado:
        linhas_pagina_atual_pdf = pagina.split('\n') 
        linhas_pagina_atual_pdf.pop(-2)

        for linha in linhas_pagina_atual_pdf:

            obj_regex = RegexComposicao( linha )

            if ( obj_regex.cabecalho is None ) and ( obj_regex.principal is not None ) and ( len( obj_regex.principal.groups() ) > 4 ):
                obj_composicao = Composicao( obj_regex.principal )
                lista_composicao.append( obj_composicao )   
            elif ( obj_regex.cabecalho is None ) and ( obj_regex.principal is not None ) and ( len( obj_regex.principal.groups() ) <= 4 ) and ( len( lista_composicao ) > 1 ):
                descricao_anterior = lista_composicao[-1].descricao
                descricao_atual = obj_regex.principal.group('re_descricao').strip()
                lista_composicao[-1].descricao = ' '.join( [ descricao_anterior, descricao_atual ] )

        bar.next()

##### Escrevendo arquivo TXT

obj_regex_arquivo = RegexArquivo( pdf_file_onerado )

if ( obj_regex_arquivo.regex is not None ):
    obj_arquivo = Arquivo( obj_regex_arquivo.regex )

with PixelBar('Escrevendo TXT', max=len( lista_composicao ), suffix='%(index)d/%(max)d - %(percent).1f%% - %(eta)ds') as bar:

    for composicao in lista_composicao:  
        composicao.escrever_arquivo_cadastro( obj_arquivo.arquivo_dado_basico, obj_arquivo.origem )
        composicao.escrever_arquivo_custo( obj_arquivo.arquivo_custo_unitario, obj_arquivo.origem )

        bar.next()