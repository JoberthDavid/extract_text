#*-* coding: utf-8 *-*
from datetime import datetime

import pdftotext
from progress.bar import Bar, PixelBar

from classes import (
                        RegexArquivo,
                        Arquivo,
                        RegexMaoDeObra,
                        MaoDeObra,
                    )

##### Extraindo dados arquivo PDF

pdf_file = "SICRO/GO 10-2020 Relatório Sintético de Mao de Obra.pdf"

with open( pdf_file, "rb" ) as f:
    cadastro = pdftotext.PDF( f )
    num_pages = len( cadastro )

with PixelBar('Extraindo dados do PDF', max=num_pages, suffix='%(index)d/%(max)d - %(percent).1f%% - %(eta)ds') as bar:

    lista_mao_de_obra = list()

    for pagina in cadastro:
        linhas_pagina_atual_pdf_file = pagina.split('\n')
        linhas_pagina_atual_pdf_file.pop(-2)


        for linha in linhas_pagina_atual_pdf_file:
            
            obj_regex = RegexMaoDeObra( linha )

            if ( obj_regex.cabecalho is None ) and ( obj_regex.principal is not None ):

                obj_mao_de_obra = MaoDeObra( obj_regex.principal )
                lista_mao_de_obra.append( obj_mao_de_obra )  

        bar.next()

##### Escrevendo arquivo TXT

obj_regex_arquivo = RegexArquivo( pdf_file )

if ( obj_regex_arquivo.regex is not None ):
    obj_arquivo = Arquivo( obj_regex_arquivo.regex )

with PixelBar('Escrevendo TXT', max=len( lista_mao_de_obra ), suffix='%(index)d/%(max)d - %(percent).1f%% - %(eta)ds') as bar:

    for mao_de_obra in lista_mao_de_obra:  
        mao_de_obra.escrever_arquivo_cadastro( obj_arquivo.arquivo_dado_basico, obj_arquivo.origem )
        mao_de_obra.escrever_arquivo_custo( obj_arquivo.arquivo_custo_unitario, obj_arquivo.origem )
        mao_de_obra.escrever_arquivo_detalhamento_custos( obj_arquivo.arquivo_detalhamento_custo_mao_de_obra, obj_arquivo.origem )

        bar.next()