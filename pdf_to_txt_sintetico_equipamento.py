#*-* coding: utf-8 *-*
import pdftotext
from datetime import datetime
from progress.bar import Bar
from progress.bar import PixelBar

from classes import (
                        RegexEquipamento,
                        Equipamento,
                        RegexArquivo,
                        Arquivo,
                    )

##### Abrindo arquivo PDF onerado

pdf_file_onerado = "SICRO/GO 10-2020 Relatório Sintético de Equipamentos.pdf"

with open( pdf_file_onerado, "rb" ) as f_onerado:
    cadastro_onerado = pdftotext.PDF( f_onerado )
    num_pages_onerado = len( cadastro_onerado )

##### Extraindo dados do PDF onerado

with PixelBar('Extraindo dados do PDF onerado', max=num_pages_onerado, suffix='%(index)d/%(max)d - %(percent).1f%% - %(eta)ds') as bar:


###### Populando lista com instância de Equipamento

    lista_equipamento = list()

    for pagina in cadastro_onerado:
        linhas_pagina_atual_pdf_file_onerado = pagina.split('\n')
        linhas_pagina_atual_pdf_file_onerado.pop(-2)

        for linha in linhas_pagina_atual_pdf_file_onerado:
            
            obj_regex_onerado = RegexEquipamento( linha )

            if ( obj_regex_onerado.cabecalho is None ) and ( obj_regex_onerado.principal is not None ):

                obj_equipamento = Equipamento( obj_regex_onerado.principal )
                lista_equipamento.append( obj_equipamento )

        bar.next()


##### Abrindo arquivo PDF desonerado

pdf_file_desonerado = "SICRO/GO 10-2020 Relatório Sintético de Equipamentos - com desoneraç╞o.pdf"

with open( pdf_file_desonerado, "rb" ) as f_desonerado:
    cadastro_desonerado = pdftotext.PDF( f_desonerado )
    num_pages_desonerado = len( cadastro_desonerado )

##### Extraindo dados do PDF desonerado

with PixelBar('Extraindo dados do PDF desonerado', max=num_pages_desonerado, suffix='%(index)d/%(max)d - %(percent).1f%% - %(eta)ds') as bar:

###### fazendo o mesmo para o arquivo desonerado

    lista_equipamento_auxiliar = list()

    for pagina in cadastro_desonerado:
        linhas_pagina_atual_pdf_file_desonerado = pagina.split('\n')
        linhas_pagina_atual_pdf_file_desonerado.pop(-2)

        for linha in linhas_pagina_atual_pdf_file_desonerado:
            
            obj_regex_desonerado = RegexEquipamento( linha )

            if ( obj_regex_desonerado.cabecalho is None ) and ( obj_regex_desonerado.principal is not None ):

                obj_equipamento = Equipamento( obj_regex_desonerado.principal )
                lista_equipamento_auxiliar.append( obj_equipamento )  

        bar.next()


with PixelBar('Compilando dados dos PDF onerado e desonerado', max=len( lista_equipamento ), suffix='%(index)d/%(max)d - %(percent).1f%% - %(eta)ds') as bar:

###### compilando os dados na lista_equipamento

    for item_onerado in lista_equipamento:
        for item_desonerado in lista_equipamento_auxiliar:
            if item_onerado.codigo == item_desonerado.codigo:
                item_onerado.custo_produtivo_desonerado = item_desonerado.custo_produtivo_onerado
                item_onerado.custo_improdutivo_desonerado = item_desonerado.custo_improdutivo_onerado
                item_onerado.mao_de_obra_desonerado = item_desonerado.mao_de_obra_onerado
                
        bar.next()
        
##### Escrevendo arquivo TXT

obj_regex_arquivo = RegexArquivo( pdf_file_onerado )

if ( obj_regex_arquivo.regex is not None ):
    obj_arquivo = Arquivo( obj_regex_arquivo.regex )

with PixelBar('Escrevendo TXT', max=len( lista_equipamento ), suffix='%(index)d/%(max)d - %(percent).1f%% - %(eta)ds') as bar:

    for equipamento in lista_equipamento:  
        equipamento.escrever_arquivo_cadastro( obj_arquivo.arquivo_sintetico_dado_basico, obj_arquivo.origem )
        equipamento.escrever_arquivo_custo( obj_arquivo.arquivo_sintetico_custo_unitario, obj_arquivo.origem )
        equipamento.escrever_arquivo_detalhamento_custos( obj_arquivo.arquivo_analitico_custo_equipamento, obj_arquivo.origem )

        bar.next()