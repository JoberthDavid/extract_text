#*-* coding: utf-8 *-*
import pdftotext
import re
from io import TextIOWrapper
from typing import Match, Union
from datetime import datetime
from progress.bar import Bar
from progress.bar import PixelBar

from constantes import ATIVIDADE_AUXILIAR, EQUIPAMENTO, MAO_DE_OBRA, MATERIAL, TEMPO_FIXO, TRANSPORTE


class RegexApropriacao:

    def __init__( self, pagina ) -> None:
        self.linhas = self.obter_linhas( pagina )
        self.regex_fic = ''
        self.regex_producao = ''
        self.regex_codigo = ''
        self.regex_equipamento = ''
        self.regex_mao_de_obra = ''
        self.regex_tempo_fixo = ''
        self.regex_transporte_rodoviario = ''
        self.regex_transporte_ferroviario = ''
        self.regex_atividade_auxiliar = ''
        self.regex_material = ''

    def obter_linhas( self, pagina ) -> list:
        rows = pagina.\
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
        return rows
        # rows = page.strip().split('\n')

    def obter_pattern_fic( self ) -> str:
        return r'(.+) (?P<re_uf>.+) (FIC) (?P<re_fic>\d\,\d\d\d\d\d)'

    def obter_pattern_producao( self ) -> str:
        return r'(.+) (?P<re_data_base>.+) (Produção da equipe) (?P<re_producao>\d{1,3}(\.\d{3})*,\d{5}) (?P<re_unidade>.+)'
    
    def obter_pattern_codigo( self ) -> str:
        return r'(?P<re_codigo>\d{7}) (.+) (Valores em reais \(R\$\))'

    def obter_pattern_equipamento( self ) -> str:
        return r'(?P<re_equipamento> [EA]\d{4}) (.+) (?P<re_quantidade>\d+\,\d{5}) (?P<re_utilizacao>\d+\,\d{2})'

    def obter_pattern_mao_de_obra( self ) -> str:
        return r'(?P<re_mao_de_obra> [P]\d{4}) (.+) (?P<re_quantidade>\d+\,\d{5})'

    def obter_pattern_tempo_fixo( self ) -> str:
        return r'(?P<re_item_transportado> \d{7}| [M]\d{4}) (.+) (?P<re_tempo_fixo>59\d{5}){1} (?P<re_quantidade>\d+\,\d{5}) (t){1}'
    
    def obter_pattern_transporte_rodoviario( self ) -> str:
        return r'(?P<re_item_transportado> \d{7}| [M]\d{4}) (.+) (?P<re_quantidade>\d+\,\d{5}) (tkm){1} (?P<re_leito_natural>59\d{5}) (?P<re_revestimento_primario>59\d{5}) (?P<re_pavimentado>59\d{5})'

    def obter_pattern_transporte_ferroviario( self ) -> str:
        return r'(?P<re_item_transportado> \d{7}| [M]\d{4}) (.+) (?P<re_quantidade>\d+\,\d{5}) (tkm){1} (?P<re_ferroviario>59\d{5})'

    def obter_pattern_atividade_auxiliar( self ) -> str:
        return r'(?P<re_atividade_auxiliar> \d{7}) (.+) (?P<re_quantidade>\d+\,\d{5}) (\w{1,3})'

    def obter_pattern_material( self ) -> str:
        return r'(?P<re_material> [M]\d{4}) (.+) (?P<re_quantidade>\d+\,\d{5}) (\w{1,3})'

    def obter_regex_fic( self, range ) -> Match:
        avaliado = self.linhas[ range ]
        return re.match( self.obter_pattern_fic(), avaliado )

    def obter_regex_producao( self, range ) -> Match:
        avaliado = self.linhas[ range ]
        return re.match( self.obter_pattern_producao(), avaliado )

    def obter_regex_codigo( self, range ) -> Match:
        avaliado = self.linhas[ range + 1]
        return re.match( self.obter_pattern_codigo(), avaliado )

    def obter_regex_equipamento( self, range ) -> Match:
        avaliado = self.linhas[ range ]
        return re.match( self.obter_pattern_equipamento(), avaliado )

    def obter_regex_mao_de_obra( self, range ) -> Match:
        avaliado = self.linhas[ range ]
        return re.match( self.obter_pattern_mao_de_obra(), avaliado )

    def obter_regex_tempo_fixo( self, range ) -> Match:
        avaliado = self.linhas[ range ]
        return re.match( self.obter_pattern_tempo_fixo(), avaliado )

    def obter_regex_transporte_rodoviario( self, range ) -> Match:
        avaliado = self.linhas[ range ]
        return re.match( self.obter_pattern_transporte_rodoviario(), avaliado )

    def obter_regex_transporte_ferroviario( self, range ) -> Match:
        avaliado = self.linhas[ range ]
        return re.match( self.obter_pattern_transporte_ferroviario(), avaliado )

    def obter_regex_atividade_auxiliar( self, range ) -> Match:
        avaliado = self.linhas[ range ]
        return re.match( self.obter_pattern_atividade_auxiliar(), avaliado )

    def obter_regex_material( self, range ) -> Match:
        avaliado = self.linhas[ range ]
        return re.match( self.obter_pattern_material(), avaliado )


class Apropriacao:

    def __init__( self ) -> None:
        self.tipo = 'horária'
        self.uf = ''
        self.data_base = ''
        self.composicao = ''
        self.descricao = ''
        self.fic = '0.00000'
        self.producao = ''
        self.unidade = ''
        self.lista_insumo = list()
        self.lista_equipamento = list()
        self.lista_mao_de_obra = list()
        self.lista_material = list()
        self.lista_atitivade_auxiliar = list()
        self.lista_tempo_fixo = list()
        self.lista_transporte = list()

    def obter_apropriacao_equipamento( self, origem_dados: str ) -> str:
        equipamento = self.lista_insumo[-1][0].strip()
        quantidade = self.lista_insumo[-1][1].replace(',', '.')
        utilizacao = self.lista_insumo[-1][2].replace('.', '').replace(',', '.')
        dados = ';'.join( [origem_dados, self.composicao, equipamento, quantidade, utilizacao, '', str(EQUIPAMENTO)] )
        dados = '{}{}'.format( dados, '\n' )
        return dados

    def escrever_arquivo_apropriacao_equipamento( self, apropriacao: TextIOWrapper, origem_dados: str ) -> None:
        apropriacao.write( self.obter_apropriacao_equipamento( origem_dados ) )

    def obter_apropriacao_mao_de_obra( self, origem_dados: str ) -> str:
        mao_de_obra = self.lista_insumo[-1][0].strip()
        quantidade = self.lista_insumo[-1][1].replace('.', '').replace(',', '.')
        dados = ';'.join( [origem_dados, self.composicao, mao_de_obra, quantidade, '', '', str(MAO_DE_OBRA)] )
        dados = '{}{}'.format( dados, '\n' )
        return dados

    def escrever_arquivo_apropriacao_mao_de_obra( self, apropriacao: TextIOWrapper, origem_dados: str ) -> None:
        apropriacao.write( self.obter_apropriacao_mao_de_obra( origem_dados ) )

    def obter_apropriacao_tempo_fixo( self, origem_dados: str ) -> str:
        tempo_fixo = self.lista_tempo_fixo[-1][0].strip()
        quantidade = self.lista_tempo_fixo[-1][1].replace('.', '').replace(',', '.')
        item_transportado = self.lista_tempo_fixo[-1][2].strip()
        dados = ';'.join( [origem_dados, self.composicao, tempo_fixo, quantidade, '', item_transportado, str(TEMPO_FIXO)] )
        dados = '{}{}'.format( dados, '\n' )
        return dados

    def escrever_arquivo_apropriacao_tempo_fixo( self, apropriacao: TextIOWrapper, origem_dados: str ) -> None:
        apropriacao.write( self.obter_apropriacao_tempo_fixo( origem_dados ) )

    def obter_apropriacao_material( self, origem_dados: str ) -> str:
        material = self.lista_insumo[-1][0].strip()
        quantidade = self.lista_insumo[-1][1].replace('.', '').replace(',', '.')
        dados = ';'.join( [origem_dados, self.composicao, material, quantidade, '', '', str(MATERIAL)] )
        dados = '{}{}'.format( dados, '\n' )
        return dados

    def escrever_arquivo_apropriacao_material( self, apropriacao: TextIOWrapper, origem_dados: str ) -> None:
        apropriacao.write( self.obter_apropriacao_material( origem_dados ) )

    def obter_apropriacao_atividade_auxiliar( self, origem_dados: str ) -> str:
        atividade_auxiliar = self.lista_atitivade_auxiliar[-1][0].strip()
        quantidade = self.lista_atitivade_auxiliar[-1][1].replace('.', '').replace(',', '.')
        dados = ';'.join( [origem_dados, self.composicao, atividade_auxiliar, quantidade, '', '', str(ATIVIDADE_AUXILIAR)] )
        dados = '{}{}'.format( dados, '\n' )
        return dados

    def escrever_arquivo_apropriacao_atividade_auxiliar( self, apropriacao: TextIOWrapper, origem_dados: str ) -> None:
        apropriacao.write( self.obter_apropriacao_atividade_auxiliar( origem_dados ) )


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

                #classifica a composição como unitária ou horária
                if obj_composicao.producao == '1.00000':
                    obj_composicao.tipo = 'unitária'

                #código e descrição
                obj_composicao.composicao = regex_codigo.group('re_codigo')

                #grava no arquivo
                composicao.write(
                    ';'.join([origem_dados,
                    obj_composicao.composicao,
                    obj_composicao.fic,
                    obj_composicao.producao,
                    obj_composicao.tipo,
                    '\n']))

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
                
                apropriacao.write(
                    ';'.join([origem_dados,
                    obj_composicao.composicao,
                    obj_composicao.lista_transporte[-3][0],
                    obj_composicao.lista_transporte[-3][1],#.replace('.', '').replace(',', '.')
                    '',
                    obj_composicao.lista_transporte[-3][2].strip(),
                    str(TRANSPORTE),
                    '\n']))

                apropriacao.write(
                    ';'.join([origem_dados,
                    obj_composicao.composicao,
                    obj_composicao.lista_transporte[-2][0],
                    obj_composicao.lista_transporte[-2][1],#.replace('.', '').replace(',', '.')
                    '',
                    obj_composicao.lista_transporte[-2][2].strip(),
                    str(TRANSPORTE),
                    '\n']))

                apropriacao.write(
                    ';'.join([origem_dados,
                    obj_composicao.composicao,
                    obj_composicao.lista_transporte[-1][0],
                    obj_composicao.lista_transporte[-1][1],#.replace('.', '').replace(',', '.')
                    '',
                    obj_composicao.lista_transporte[-1][2].strip(),
                    str(TRANSPORTE),
                    '\n']))

            #transporte ferrovia                        
            elif regex_transporte_ferroviario is not None:

                obj_composicao.lista_transporte.append( regex_transporte_ferroviario.group('re_ferroviario','re_quantidade','re_item_transportado') )


                apropriacao.write(
                    ';'.join([origem_dados,
                    obj_composicao.composicao,
                    obj_composicao.lista_transporte[-1][0],
                    obj_composicao.lista_transporte[-1][1],#.replace(',', '.')
                    '',
                    obj_composicao.lista_transporte[-1][2].strip(),
                    str(TRANSPORTE),
                    '\n']))

            #atividade auxiliar
            elif regex_atividade_auxiliar is not None:
                obj_composicao.lista_atitivade_auxiliar.append( regex_atividade_auxiliar.group('re_atividade_auxiliar','re_quantidade') )

                obj_composicao.escrever_arquivo_apropriacao_atividade_auxiliar( apropriacao, origem_dados )

            #material
            elif regex_material is not None:
                obj_composicao.lista_insumo.append( regex_material.group('re_material','re_quantidade') )

                obj_composicao.escrever_arquivo_apropriacao_material( apropriacao, origem_dados )

        bar.next()
