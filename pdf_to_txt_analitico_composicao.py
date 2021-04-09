#*-* coding: utf-8 *-*
import pdftotext
from datetime import datetime
from progress.bar import Bar
from progress.bar import PixelBar

from classes import (
                        RegexApropriacao,
                        Apropriacao,
                    )

pdf_file = "SICRO/GO 10-2020 Relatório Analítico de ComposiçΣes de Custos.pdf"

path = 'TXT/' + '_'.join([pdf_file[0:5], pdf_file[6:8], pdf_file[9:11], pdf_file[12:16], 'analitico_composicao_'])

origem_dados = ','.join([pdf_file[0:5], pdf_file[6:8], pdf_file[9:16]])

composicao = open(''.join([path,'dado_basico.txt']), 'w', encoding="utf-8")
apropriacao = open(''.join([path,'apropriacao.txt']), 'w', encoding="utf-8")

with open(pdf_file, "rb") as f:
    pdf = pdftotext.PDF(f)
    num_pages = len(pdf)

with PixelBar('Escrevendo TXT', max=num_pages, suffix='%(index)d/%(max)d - %(percent).1f%% - %(eta)ds') as bar:
    for pagina in pdf:
          
        obj_composicao = Apropriacao()

        obj_regex = RegexApropriacao( pagina )

        for i in range(len(obj_regex.linhas)-3):
            regex_fic = obj_regex.obter_regex_fic( i )
            regex_producao = obj_regex.obter_regex_producao( i )
            regex_codigo = obj_regex.obter_regex_codigo( i )
            regex_equipamento = obj_regex.obter_regex_equipamento( i )
            regex_mao_obra = obj_regex.obter_regex_mao_de_obra( i )
            regex_tempo_fixo = obj_regex.obter_regex_tempo_fixo( i )
            regex_transporte_rodoviario = obj_regex.obter_regex_transporte_rodoviario( i )
            regex_transporte_ferroviario = obj_regex.obter_regex_transporte_ferroviario( i )
            regex_atividade_auxiliar = obj_regex.obter_regex_atividade_auxiliar( i )
            regex_material = obj_regex.obter_regex_material( i )

            #fic
            if regex_fic is not None:
                obj_composicao.fic = regex_fic.group('re_fic').replace(',', '.')
                obj_composicao.uf = regex_fic.group('re_uf')

            #produção da equipe e unidade
            elif regex_producao is not None:
                obj_composicao.producao = regex_producao.group('re_producao').replace('.', '').replace(',', '.')
                obj_composicao.unidade = regex_producao.group('re_unidade')
                obj_composicao.data_base = regex_producao.group('re_data_base')
                obj_composicao.composicao = regex_codigo.group('re_codigo')
                obj_composicao.escrever_arquivo_apropriacao_dado_basico( composicao, origem_dados )

                i = i + 4 #pulando as linhas i=3 até i=6

            #equipamentos
            elif regex_equipamento is not None:
                obj_composicao.lista_insumo.append( regex_equipamento.group('re_equipamento','re_quantidade','re_utilizacao') )
                obj_composicao.escrever_arquivo_apropriacao_equipamento( apropriacao, origem_dados )

            #mão de obra
            elif regex_mao_obra is not None:
                obj_composicao.lista_insumo.append( regex_mao_obra.group('re_mao_de_obra','re_quantidade') )
                obj_composicao.escrever_arquivo_apropriacao_mao_de_obra( apropriacao, origem_dados )

            #tempo fixo
            elif regex_tempo_fixo is not None:
                obj_composicao.lista_tempo_fixo.append( regex_tempo_fixo.group('re_tempo_fixo','re_quantidade','re_item_transportado') )
                obj_composicao.escrever_arquivo_apropriacao_tempo_fixo( apropriacao, origem_dados )

            #transporte
            elif regex_transporte_rodoviario is not None:

                obj_composicao.lista_transporte.append( regex_transporte_rodoviario.group('re_leito_natural','re_quantidade','re_item_transportado') )
                obj_composicao.lista_transporte.append( regex_transporte_rodoviario.group('re_revestimento_primario','re_quantidade','re_item_transportado') )
                obj_composicao.lista_transporte.append( regex_transporte_rodoviario.group('re_pavimentado','re_quantidade','re_item_transportado') )
                obj_composicao.escrever_arquivo_apropriacao_transporte_leito_natural( apropriacao, origem_dados )
                obj_composicao.escrever_arquivo_apropriacao_transporte_revestimento_primario( apropriacao, origem_dados )
                obj_composicao.escrever_arquivo_apropriacao_transporte_pavimentado( apropriacao, origem_dados )

            #transporte ferrovia                        
            elif regex_transporte_ferroviario is not None:
                obj_composicao.lista_transporte.append( regex_transporte_ferroviario.group('re_ferroviario','re_quantidade','re_item_transportado') )
                obj_composicao.escrever_arquivo_apropriacao_transporte_ferroviario( apropriacao, origem_dados )

            #atividade auxiliar
            elif regex_atividade_auxiliar is not None:
                obj_composicao.lista_atitivade_auxiliar.append( regex_atividade_auxiliar.group('re_atividade_auxiliar','re_quantidade') )
                obj_composicao.escrever_arquivo_apropriacao_atividade_auxiliar( apropriacao, origem_dados )

            #material
            elif regex_material is not None:
                obj_composicao.lista_insumo.append( regex_material.group('re_material','re_quantidade') )
                obj_composicao.escrever_arquivo_apropriacao_material( apropriacao, origem_dados )

        bar.next()