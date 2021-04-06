#*-* coding: utf-8 *-*
import pdftotext
from datetime import datetime
from progress.bar import Bar
from progress.bar import PixelBar

from classes import (
                        Arquivo,
                        Material,
                        RegexMaterial,
                        RegexArquivo,
                    )

##### Extraindo dados arquivo PDF

pdf_file = "SICRO/GO 10-2020 Relatório Sintético de Materiais.pdf"

with open( pdf_file, "rb" ) as f:
    cadastro = pdftotext.PDF( f )
    num_pages = len( cadastro )

with PixelBar('Extraindo dados do PDF', max=num_pages, suffix='%(index)d/%(max)d - %(percent).1f%% - %(eta)ds') as bar:

    lista_material = list()

    for pagina in cadastro:
        linhas_pagina_atual_pdf = pagina.split('\n') 
        linhas_pagina_atual_pdf.pop(-2)

        for linha in linhas_pagina_atual_pdf:

            obj_regex = RegexMaterial( linha )

            if ( obj_regex.cabecalho is None ):

                if ( obj_regex.principal is not None ) and ( len( obj_regex.principal.groups() ) == 4 ):

                    obj_material = Material( obj_regex.principal )
                    lista_material.append( obj_material )               

        bar.next()

##### Escrevendo arquivo TXT

obj_regex_arquivo = RegexArquivo( pdf_file )

if ( obj_regex_arquivo.regex is not None ):
    obj_arquivo = Arquivo( obj_regex_arquivo.regex )

with PixelBar('Escrevendo TXT', max=len( lista_material ), suffix='%(index)d/%(max)d - %(percent).1f%% - %(eta)ds') as bar:

    for material in lista_material:  
        material.escrever_arquivo_cadastro( obj_arquivo.arquivo_dado_basico, obj_arquivo.origem )
        material.escrever_arquivo_custo( obj_arquivo.arquivo_custo_unitario, obj_arquivo.origem )

        bar.next()