#*-* coding: utf-8 *-*
from constantes import ATIVIDADE_AUXILIAR, EQUIPAMENTO, MAO_DE_OBRA, MATERIAL, TEMPO_FIXO, TRANSPORTE
import pdftotext
import re
from datetime import datetime
from progress.bar import Bar
from progress.bar import PixelBar

pdf_file = "SICRO/GO 10-2020 Relatório Analítico de ComposiçΣes de Custos.pdf"

path = 'TXT/' + '_'.join([pdf_file[0:5], pdf_file[6:8], pdf_file[9:11], pdf_file[12:16], 'analitico_composicao_'])

origem_dados = ','.join([pdf_file[0:5], pdf_file[6:8], pdf_file[9:16]])

composicao = open(''.join([path,'dado_basico.txt']), 'w', encoding="utf-8")
apropriacao = open(''.join([path,'apropriacao.txt']), 'w', encoding="utf-8")
# insumo = open(''.join([path,'insumo.txt']), 'a')
# atividade_auxiliar = open(''.join([path, 'atividade_auxiliar.txt']), 'w')
#tempo_fixo = open(''.join([path,'tempo_fixo.txt']), 'w')
#momento_transporte = open(''.join([path,'momento_transporte.txt']), 'w')
# transporte = open(''.join([path,'transporte.txt']), 'a')

with open(pdf_file, "rb") as f:
    pdf = pdftotext.PDF(f)
    num_pages = len(pdf)

with PixelBar('Escrevendo TXT', max=num_pages, suffix='%(index)d/%(max)d - %(percent).1f%% - %(eta)ds') as bar:
    for page in pdf:
        rows = page.\
            replace('                         ', ' ').\
            replace('                        ', ' ').\
            replace('                       ', ' ').\
            replace('                      ', ' ').\
            replace('                     ', ' ').\
            replace('                    ', ' ').\
            replace('                   ', ' ').\
            replace('                  ', ' ').\
            replace('                 ', ' ').\
            replace('                ', ' ').\
            replace('               ', ' ').\
            replace('              ', ' ').\
            replace('             ', ' ').\
            replace('            ', ' ').\
            replace('           ', ' ').\
            replace('          ', ' ').\
            replace('         ', ' ').\
            replace('        ', ' ').\
            replace('       ', ' ').\
            replace('      ', ' ').\
            replace('     ', ' ').\
            replace('    ', ' ').\
            replace('   ', ' ').\
            replace('  ', ' ').\
            split('\n')
        # rows = page.strip().split('\n')
        
        d = dict(
            uf = '',
            data_base = '',
            composicao = '',
            descricao = '',
            fic = '',
            producao = '',
            unidade = '',
            lista_insumo = list(),
            lista_equipamento = list(),
            lista_mao_de_obra = list(),
            lista_material = list(),
            lista_atitivade_auxiliar = list(),
            lista_tempo_fixo = list(),
            lista_transporte = list())

        for i in range(len(rows)-3):
            regex_fic = (re.match(r'(.+) (.+) (FIC) (\d\,\d\d\d\d\d)',rows[i])) #fic
            regex_producao = (re.match(r'(.+) (.+) (Produção da equipe) (\d{1,3}(\.\d{3})*,\d{5}) (.+)',rows[i])) #produção da equipe e unidade
            regex_codigo = (re.match(r'(\d{7}) (.+) (Valores em reais \(R\$\))',rows[i+1])) #código e descrição
            regex_equipamento = (re.match(r'( [EA]\d{4}) (.+) (\d+\,\d{5}) (\d+\,\d{2})',rows[i])) #equipamentos
            regex_mao_obra = (re.match(r'( [P]\d{4}) (.+) (\d+\,\d{5})',rows[i])) #mão de obra
            regex_tempo_fixo = (re.match(r'( \d{7}| [M]\d{4}) (.+) (59\d{5}){1} (\d+\,\d{5}) (t){1}',rows[i])) #tempo fixo
            regex_transporte_rodoviario = (re.match(r'( \d{7}| [M]\d{4}) (.+) (\d+\,\d{5}) (tkm){1} (59\d{5}) (59\d{5}) (59\d{5})',rows[i])) #transporte
            regex_transporte_ferroviario = (re.match(r'( \d{7}| [M]\d{4}) (.+) (\d+\,\d{5}) (tkm){1} (59\d{5})',rows[i])) #transporte ferrovia
            regex_atividade_auxiliar = (re.match(r'( \d{7}) (.+) (\d+\,\d{5}) (\w{1,3})',rows[i])) #atividade auxiliar
            regex_material = (re.match(r'( [M]\d{4}) (.+) (\d+\,\d{5}) (\w{1,3})',rows[i])) #material

            #fic
            if regex_fic is not None:
                d['fic'] = regex_fic.group(4)#.replace(',', '.')
                d['uf'] = regex_fic.group(2)

            #produção da equipe e unidade
            elif regex_producao is not None:
                d['producao'] = regex_producao.group(4)#.replace('.', '').replace(',', '.')
                d['unidade'] = regex_producao.group(5)
                d['data_base'] = regex_producao.group(2)

                #classifica a composição como unitária ou horária
                if d['producao'] == '1,00000':
                    tipo = 'unitária'
                else:
                    tipo = 'horária'

                #código e descrição
                d['composicao'] = regex_codigo.group(1)

                if d['fic'] == '':
                    fic = '0,00000'
                else:
                    fic = d['fic']

                #grava no arquivo
                composicao.write(
                    ';'.join([origem_dados,
                    d['composicao'],
                    fic,
                    d['producao'],
                    tipo,
                    '\n']))

                i = i + 4 #pulando as linhas i=3 até i=6

            #equipamentos
        
            elif regex_equipamento is not None:
                d['lista_insumo'].append( regex_equipamento.group(1,3,4) )
                
                #acrescentando dados a um arquivo composicao txt #o índice -1 pega o último elemento da lista e os índices 0,1,2 são as posições na tupla
                apropriacao.write(
                    ';'.join([origem_dados,
                    d['composicao'],
                    d['lista_insumo'][-1][0].strip(),
                    d['lista_insumo'][-1][1],#.replace(',', '.')
                    d['lista_insumo'][-1][2],#.replace('.', '').replace(',', '.')
                    '',
                    str(EQUIPAMENTO),
                    '\n']))

            #mão de obra
            elif regex_mao_obra is not None:
                d['lista_insumo'].append( regex_mao_obra.group(1,3) )

                #acrescentando dados a um arquivo composicao txt
                apropriacao.write(
                    ';'.join([origem_dados,
                    d['composicao'],
                    d['lista_insumo'][-1][0].strip(),
                    d['lista_insumo'][-1][1],#.replace('.', '').replace(',', '.')
                    '',
                    '',
                    str(MAO_DE_OBRA),
                    '\n']))

            #tempo fixo
            elif regex_tempo_fixo is not None:
                d['lista_tempo_fixo'].append( regex_tempo_fixo.group(3,4,1) )

            #transporte
            elif regex_transporte_rodoviario is not None:

                if len( d['lista_tempo_fixo'] ) == 0:
                    tf = ''
                else:
                    for item in d['lista_tempo_fixo']:
                        tf = item[0]

                d['lista_transporte'].append( regex_transporte_rodoviario.group(5,3,1) )
                d['lista_transporte'].append( regex_transporte_rodoviario.group(6,3,1) )
                d['lista_transporte'].append( regex_transporte_rodoviario.group(7,3,1) )
                
                apropriacao.write(
                    ';'.join([origem_dados,
                    d['composicao'],
                    tf,
                    d['lista_transporte'][-3][1],#.replace('.', '').replace(',', '.')
                    '',
                    d['lista_transporte'][-3][2].strip(),
                    str(TEMPO_FIXO),
                    '\n']))

                apropriacao.write(
                    ';'.join([origem_dados,
                    d['composicao'],
                    d['lista_transporte'][-3][0],
                    d['lista_transporte'][-3][1],#.replace('.', '').replace(',', '.')
                    '',
                    d['lista_transporte'][-3][2].strip(),
                    str(TRANSPORTE),
                    '\n']))

                apropriacao.write(
                    ';'.join([origem_dados,
                    d['composicao'],
                    d['lista_transporte'][-2][0],
                    d['lista_transporte'][-3][1],#.replace('.', '').replace(',', '.')
                    '',
                    d['lista_transporte'][-3][2].strip(),
                    str(TRANSPORTE),
                    '\n']))

                apropriacao.write(
                    ';'.join([origem_dados,
                    d['composicao'],
                    d['lista_transporte'][-1][0],
                    d['lista_transporte'][-3][1],#.replace('.', '').replace(',', '.')
                    '',
                    d['lista_transporte'][-3][2].strip(),
                    str(TRANSPORTE),
                    '\n']))

            #transporte ferrovia                        
            elif regex_transporte_ferroviario is not None:

                if len( d['lista_tempo_fixo'] ) != 0:
                    tf = d['lista_tempo_fixo'][-1][0]
                else:
                    tf = ''

                d['lista_transporte'].append( regex_transporte_ferroviario.group(5,3,1) )

                apropriacao.write(
                    ';'.join([origem_dados,
                    d['composicao'],
                    tf,
                    d['lista_transporte'][-1][1],#.replace(',', '.')
                    '',
                    d['lista_transporte'][-1][2].strip(),
                    str(TEMPO_FIXO),
                    '\n']))

                apropriacao.write(
                    ';'.join([origem_dados,
                    d['composicao'],
                    d['lista_transporte'][-1][0],
                    d['lista_transporte'][-1][1],#.replace(',', '.')
                    '',
                    d['lista_transporte'][-1][2].strip(),
                    str(TRANSPORTE),
                    '\n']))

            #atividade auxiliar
            elif regex_atividade_auxiliar is not None:
                d['lista_atitivade_auxiliar'].append( regex_atividade_auxiliar.group(1,3) )

                apropriacao.write(
                    ';'.join([origem_dados,
                    d['composicao'],
                    d['lista_atitivade_auxiliar'][-1][0].strip(),
                    d['lista_atitivade_auxiliar'][-1][1],#.replace('.', '').replace(',', '.')
                    '',
                    '',
                    str(ATIVIDADE_AUXILIAR),
                    '\n']))

            #material
            elif regex_material is not None:
                d['lista_insumo'].append( regex_material.group(1,3) )

                apropriacao.write(
                    ';'.join([origem_dados,
                    d['composicao'],
                    d['lista_insumo'][-1][0].strip(),
                    d['lista_insumo'][-1][1],#.replace('.', '').replace(',', '.')
                    '',
                    '',
                    str(MATERIAL),
                    '\n']))

        bar.next()