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

##### Abrindo arquivo PDF onerado

pdf_file_onerado = "SICRO/GO 10-2020 Relatório Sintético de Mao de Obra.pdf"

with open( pdf_file_onerado, "rb" ) as f_onerado:
    cadastro_onerado = pdftotext.PDF( f_onerado )
    num_pages_onerado = len( cadastro_onerado )

##### Extraindo dados do PDF onerado

with PixelBar('Extraindo dados do PDF onerado', max=num_pages_onerado, suffix='%(index)d/%(max)d - %(percent).1f%% - %(eta)ds') as bar:

###### Populando lista com instância de MaoDeObra

    lista_mao_de_obra = list()

    for pagina in cadastro_onerado:
        linhas_pagina_atual_pdf_file_onerado = pagina.split('\n')
        linhas_pagina_atual_pdf_file_onerado.pop(-2)

        for linha in linhas_pagina_atual_pdf_file_onerado:
            
            obj_regex_onerado = RegexMaoDeObra( linha )

            if ( obj_regex_onerado.cabecalho is None ) and ( obj_regex_onerado.principal is not None ):

                obj_mao_de_obra = MaoDeObra( obj_regex_onerado.principal )
                lista_mao_de_obra.append( obj_mao_de_obra )  

        bar.next()


##### Abrindo arquivo PDF desonerado

pdf_file_desonerado = "SICRO/GO 10-2020 Relatório Sintético de Mao de Obra - com desoneracao.pdf"

with open( pdf_file_desonerado, "rb" ) as f_desonerado:
    cadastro_desonerado = pdftotext.PDF( f_desonerado )
    num_pages_desonerado = len( cadastro_desonerado )

##### Extraindo dados do PDF desonerado

with PixelBar('Extraindo dados do PDF desonerado', max=num_pages_desonerado, suffix='%(index)d/%(max)d - %(percent).1f%% - %(eta)ds') as bar:

###### fazendo o mesmo para o arquivo desonerado

    lista_mao_de_obra_auxiliar = list()

    for pagina in cadastro_desonerado:
        linhas_pagina_atual_pdf_file_desonerado = pagina.split('\n')
        linhas_pagina_atual_pdf_file_desonerado.pop(-2)

        for linha in linhas_pagina_atual_pdf_file_desonerado:
            
            obj_regex_desonerado = RegexMaoDeObra( linha )

            if ( obj_regex_desonerado.cabecalho is None ) and ( obj_regex_desonerado.principal is not None ):

                obj_mao_de_obra = MaoDeObra( obj_regex_desonerado.principal )
                lista_mao_de_obra_auxiliar.append( obj_mao_de_obra )  

        bar.next()


with PixelBar('Compilando dados dos PDF onerado e desonerado', max=len( lista_mao_de_obra ), suffix='%(index)d/%(max)d - %(percent).1f%% - %(eta)ds') as bar:

###### compilando os dados na lista_mao_de_obra

    for item_onerado in lista_mao_de_obra:
        for item_desonerado in lista_mao_de_obra_auxiliar:
            if item_onerado.codigo == item_desonerado.codigo:
                item_onerado.custo_desonerado = item_desonerado.custo_onerado
                item_onerado.encargos_sociais_desonerado = item_desonerado.encargos_sociais_onerado
        bar.next()


##### Escrevendo arquivo TXT

obj_regex_arquivo = RegexArquivo( pdf_file_onerado )

if ( obj_regex_arquivo.regex is not None ):
    obj_arquivo = Arquivo( obj_regex_arquivo.regex )

with PixelBar('Escrevendo TXT', max=len( lista_mao_de_obra ), suffix='%(index)d/%(max)d - %(percent).1f%% - %(eta)ds') as bar:

    for mao_de_obra in lista_mao_de_obra:  
        mao_de_obra.escrever_arquivo_cadastro( obj_arquivo.arquivo_dado_basico, obj_arquivo.origem )
        mao_de_obra.escrever_arquivo_custo( obj_arquivo.arquivo_custo_unitario, obj_arquivo.origem )
        mao_de_obra.escrever_arquivo_detalhamento_custos( obj_arquivo.arquivo_detalhamento_custo_mao_de_obra, obj_arquivo.origem )

        bar.next()