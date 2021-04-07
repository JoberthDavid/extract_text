import re
from io import TextIOWrapper
from typing import Match, Union

from constantes import (
                        MATERIAL,
                        MAO_DE_OBRA,
                    )


class DescricaoNormalizada:

    def __init__( self, descricao: str ) -> None:
        self.descricao = self.obter_descricao_normalizada( descricao )

    def obter_descricao_normalizada( self, descricao ) -> str:
        return descricao.strip().replace('.','')


class NumeroNormalizado:

    def __init__( self, numero: str ) -> None:
        self.numero = self.obter_numero_normalizado( numero )

    def obter_numero_normalizado( self, numero ) -> str:
        return numero.strip().replace('-','0.0000').replace('.','').replace(',','.') 


class PercentualNormalizado:

    def __init__( self, percentual: str ) -> None:
        self.percentual = self.obter_numero_normalizado( percentual )

    def obter_numero_normalizado( self, percentual ) -> str:
        return percentual.strip().replace(',','.').replace('%','')


class Arquivo:

    def __init__( self, regex: Match) -> None:
        self.sistema = regex.group('re_sistema')
        self.estado = regex.group('re_estado')
        self.mes_base = regex.group('re_mes_base')
        self.ano_base = regex.group('re_ano_base')
        self.item = self.preparar_grupo_regex_arquivo( regex.group('re_item_a'), regex.group('re_item_b') )
        self.data_base = self.retornar_data_base()
        self.origem = self.retornar_origem()
        self.arquivo_dado_basico = self.gerar_arquivo_dado_basico()
        self.arquivo_custo_unitario = self.gerar_arquivo_custo_unitario_insumo()
        self.arquivo_detalhamento_custo_mao_de_obra = self.gerar_arquivo_detalhamento_custo_mao_de_obra()

    def preparar_grupo_regex_arquivo( self, item_a, item_b ) -> str:
        grupo = ''.join( [ item_a, item_b ] )
        grupo_regex = grupo.\
            replace('Analítico','_analitico').\
            replace('Sintético','_sintetico').\
            replace('Composições de Custos','_composicao_').\
            replace('ComposiçΣes de Custos','_composicao_').\
            replace('Mão de Obra','_mao_de_obra_').\
            replace('Mao de Obra','_mao_de_obra_').\
            replace('Equipamentos','_equipamento_').\
            replace('Materiais','_material_')
        return grupo_regex

    def retornar_data_base( self ):
        return '-'.join( [ self.mes_base, self.ano_base ] )

    def retornar_origem( self ) -> str:
        return ';'.join( [ self.sistema, self.estado, self.retornar_data_base() ] )

    def retornar_raiz( self ) -> str:
        return ''.join( [ 'TXT/', self.sistema ] )

    def retornar_path( self ) -> str:
        return '_'.join( [ self.retornar_raiz(), self.estado, self.mes_base, self.ano_base ] )

    def gerar_arquivo_dado_basico( self ) -> TextIOWrapper:
        return open( ''.join( [ self.retornar_path(), '_dados_basicos.txt' ] ), 'a', encoding="utf-8" )

    def gerar_arquivo_custo_unitario_insumo( self ) -> TextIOWrapper:
        return open( ''.join( [ self.retornar_path(), '_insumos_custos_unitarios.txt' ] ), 'a', encoding="utf-8" )

    def gerar_arquivo_detalhamento_custo_mao_de_obra( self ) -> TextIOWrapper:
        return open( ''.join( [ self.retornar_path(), '_detalhamento_mao_de_obra_custo_unitario.txt' ] ), 'w', encoding="utf-8" )


class RegexArquivo:

    def __init__( self, pdf_file: str ):
        self.regex = self.retornar_regex_arquivo( pdf_file )

    def retornar_pattern_arquivo( self ) -> str:
        return r'(?P<re_sistema>(.+))/(?P<re_estado>\w{2}) (?P<re_mes_base>(\d{2}))-(?P<re_ano_base>(\d{4})) (Relatório) (?P<re_item_a>(Analítico|Sintético)) (de) (?P<re_item_b>Composições de Custos|ComposiçΣes de Custos|Equipamentos|Mão de Obra|Mao de Obra|Materiais)( - com desoneração| - com desoneraç╞o| - com desoneracao)?\.pdf$'

    def retornar_regex_arquivo( self, pdf_file: str ) -> Match:
        return re.match( self.retornar_pattern_arquivo(), pdf_file )


class Regex:

    def __init__( self, avaliado: str ) -> None:
        regex_1 = r'(CGCIT)'
        regex_2 = r'(.*) - (\w{1,20}/\d{4})'
        regex_3 = r'(\s*) (Custo Unitário|Preço Unitário)'
        regex_4 = r'(Código)'
        regex_5 = r'(\s*) \(R\$\)'
        lista_regex = [regex_1, regex_2, regex_3, regex_4, regex_5]
        self.cabecalho = self.obter_regex_cabecalho( avaliado, lista_regex )

    def obter_regex_cabecalho( self, avaliado: str, lista: list ):
        retorno = None
        for rx in lista:
            if ( re.match( rx, avaliado) is not None ):
                retorno = re.match( rx, avaliado)
        return retorno


class RegexMaterial(Regex):

    def __init__(self, avaliado: str ) -> None:
        super().__init__( avaliado )
        self.principal = self.obter_regex( avaliado )

    def retornar_pattern_alfa_material( self ) -> str:
        return r'(?P<re_codigo>[M]\d{4}) (?P<re_descricao>.+) (?P<re_unidade>\w{1,5}) (?P<re_custo>\d*.*\d*.\d+,\d{4}|\s*-)'

    def retornar_pattern_beta_material( self ) -> str:
        return r'(\s+(?P<re_descricao1>.+)(\n)(\s+)(.+)(\n))'

    def obter_regex( self, avaliado ) -> Match:
        regex_alfa = re.match( self.retornar_pattern_alfa_material(), avaliado )
        regex_beta = re.match( self.retornar_pattern_beta_material(), avaliado, re.MULTILINE )
        if regex_alfa is not None:
            return regex_alfa
        elif regex_beta is not None:
            return regex_beta


class Material:

    def __init__( self, regex: Match ) -> None:
        self.regex = regex
        self.codigo = self.obter_codigo()
        obj_descricao = DescricaoNormalizada( self.obter_descricao() )
        self.descricao = obj_descricao.descricao
        self.unidade = self.obter_unidade()
        obj_custo = NumeroNormalizado( self.obter_custo() )
        self.custo = obj_custo.numero
        self.categoria = str(MATERIAL)

    def obter_codigo( self ):
        return self.regex.group('re_codigo')

    def obter_descricao( self ) -> str:
        if self.obter_codigo() == 'M3795':
            retorno = 'Instalações do Estaleiro Padrão para beneficiamento de estruturas navais, \
                        inclusive mobiliário, equipamentos de informática e de segurança '
        else:
            retorno = self.regex.group('re_descricao')
        return retorno

    def obter_unidade( self ):
        return self.regex.group('re_unidade')

    def obter_custo( self ):
        return self.regex.group('re_custo')

    def retornar_dados_cadastro_material( self, origem_dados: str ) -> str:
        dados = ';'.join( [origem_dados, self.codigo, self.descricao, self.unidade] )
        dados = '{}{}'.format( dados, '\n' )
        return dados

    def escrever_arquivo_cadastro( self, arquivo: TextIOWrapper, origem_dados: str ) -> None:
        arquivo.write( self.retornar_dados_cadastro_material( origem_dados ) )

    def retornar_dados_custos_material( self, origem_dados: str ) -> str:
        dados = ';'.join( [origem_dados, self.codigo, '','','','', self.custo, self.categoria] )
        dados = '{}{}'.format( dados, '\n' )
        return dados

    def escrever_arquivo_custo( self, custos_unitarios: TextIOWrapper, origem_dados: str ) -> None:
        custos_unitarios.write( self.retornar_dados_custos_material( origem_dados ) )


class RegexMaoDeObra(Regex):

    def __init__(self, avaliado: str ) -> None:
        super().__init__( avaliado )
        self.principal = self.obter_regex( avaliado )

    def retornar_pattern_alfa_mao_de_obra( self ) -> str:
        return r'(?P<re_codigo>[P]\d{4}|\w*) (?P<re_descricao>.+) (?P<re_unidade>h|mês) (?P<re_salario>\d*.\d+,\d{4}|\s*-) (?P<re_encargos_sociais>\d*.\d+,\d{4}%|\s*-) (?P<re_custo>\d*.\d+,\d{4}|\s*-) (?P<re_periculosidade>\d*.\d+,\d{4}%|\s*-)'

    def retornar_pattern_beta_mao_de_obra( self ) -> str:
        return r'(\s*)? (?P<re_codigo>[P]\d{4}) (?P<re_descricao>.+) (?P<re_unidade>h|mês) (\s*) (?P<re_salario>\d*.\d+,\d{4}) (\s*) (?P<re_encargos_sociais>\d*.\d+,\d{4}%) (\s*) (?P<re_custo>\d*.\d+,\d{4}) (\s*) (?P<re_periculosidade>\d*.\d+,\d{4}%)'

    def obter_regex( self, avaliado ) -> Match:
        regex_alfa = re.match( self.retornar_pattern_alfa_mao_de_obra(), avaliado )
        regex_beta = re.match( self.retornar_pattern_beta_mao_de_obra(), avaliado )
        if regex_alfa is not None:
            return regex_alfa
        elif regex_beta is not None:
            return regex_beta


class MaoDeObra:

    def __init__( self, regex: Match ) -> None:
        self.regex = regex
        self.codigo = self.obter_codigo()
        self.descricao = self.obter_descricao()
        self.unidade = self.obter_unidade()
        self.periculosidade = self.obter_periculosidade()
        self.salario = self.obter_salario()
        self.custo_onerado = self.obter_custo_onerado()
        self.custo_desonerado = ''
        self.encargos_sociais_onerado = self.obter_encargos_sociais_onerado()
        self.encargos_sociais_desonerado = ''
        self.categoria = str(MAO_DE_OBRA)

    def obter_codigo( self ):
        return self.regex.group('re_codigo')

    def obter_descricao( self ) -> str:
        obj_descricao = DescricaoNormalizada( self.regex.group('re_descricao') )
        return obj_descricao.descricao

    def obter_unidade( self ) -> str:
        return self.regex.group('re_unidade')

    def obter_periculosidade( self ) -> str:
        obj_periculosidade = PercentualNormalizado( self.regex.group('re_periculosidade') )
        return obj_periculosidade.percentual

    def obter_salario( self ) -> str:
        obj_salario = NumeroNormalizado( self.regex.group('re_salario') )
        return obj_salario.numero

    def obter_custo_onerado( self ) -> str:
        obj_custo_onerado = NumeroNormalizado( self.regex.group('re_custo') )
        return obj_custo_onerado.numero

    def obter_encargos_sociais_onerado( self ) -> str:
        obj_encargos_sociais_onerado = PercentualNormalizado( self.regex.group('re_encargos_sociais') )
        return obj_encargos_sociais_onerado.percentual

    def retornar_dados_cadastro_mao_de_obra( self, origem_dados: str ) -> str:
        dados = ';'.join( [origem_dados, self.codigo, self.descricao, self.unidade] )
        dados = '{}{}'.format( dados, '\n' )
        return dados

    def escrever_arquivo_cadastro( self, arquivo: TextIOWrapper, origem_dados: str ) -> None:
        arquivo.write( self.retornar_dados_cadastro_mao_de_obra( origem_dados ) )

    def retornar_dados_custos_mao_de_obra( self, origem_dados: str ) -> str:
        dados = ';'.join( [origem_dados, self.codigo, self.custo_onerado,'',self.custo_desonerado,'','', self.categoria] )
        dados = '{}{}'.format( dados, '\n' )
        return dados

    def escrever_arquivo_custo( self, custos_unitarios: TextIOWrapper, origem_dados: str ) -> None:
        custos_unitarios.write( self.retornar_dados_custos_mao_de_obra( origem_dados ) )

    def retornar_detalhamento_custos_mao_de_obra( self, origem_dados: str ) -> str:
        detalhes = ';'.join([origem_dados, self.codigo, self.salario, self.periculosidade, self.encargos_sociais_onerado, self.encargos_sociais_desonerado] )
        detalhes = '{}{}'.format( detalhes, '\n' )
        return detalhes

    def escrever_arquivo_detalhamento_custos( self, detalhamento_custos: TextIOWrapper, origem_dados: str ) -> None:
        detalhamento_custos.write( self.retornar_detalhamento_custos_mao_de_obra( origem_dados ) )