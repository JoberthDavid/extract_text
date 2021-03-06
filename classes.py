import re
from io import TextIOWrapper
from typing import Match, Union

from constantes import (
                        MATERIAL,
                        MAO_DE_OBRA,
                        EQUIPAMENTO,
                        COMPOSICAO_PRINCIPAL,
                        ATIVIDADE_AUXILIAR,
                        TEMPO_FIXO,
                        TRANSPORTE,
                    )


class DescricaoNormalizada:

    def __init__( self, descricao: str ) -> None:
        self.descricao = self.obter_descricao_normalizada( descricao )

    def obter_descricao_normalizada( self, descricao ) -> str:
        return descricao.strip().replace('.','').replace(';','-')


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
        self.data_base = self.obter_data_base()
        self.origem = self.obter_origem()
        self.arquivo_sintetico_dado_basico = self.gerar_arquivo_sintetico_dado_basico()
        self.arquivo_sintetico_custo_unitario = self.gerar_arquivo_sintetico_custo_unitario()
        self.arquivo_sintetico_custo_unitario_composicao = self.gerar_arquivo_sintetico_custo_unitario_composicao()
        self.arquivo_analitico_custo_mao_de_obra = self.gerar_arquivo_analitico_custo_mao_de_obra()
        self.arquivo_analitico_custo_equipamento = self.gerar_arquivo_analitico_custo_equipamento()

    def preparar_grupo_regex_arquivo( self, item_a, item_b ) -> str:
        grupo = ''.join( [ item_a, item_b ] )
        grupo_regex = grupo.\
            replace('Anal??tico','_analitico').\
            replace('Sint??tico','_sintetico').\
            replace('Composi????es de Custos','_composicao_').\
            replace('Composi????es de Custos','_composicao_').\
            replace('M??o de Obra','_mao_de_obra_').\
            replace('Mao de Obra','_mao_de_obra_').\
            replace('Equipamentos','_equipamento_').\
            replace('Materiais','_material_')
        return grupo_regex

    def obter_data_base( self ):
        return '-'.join( [ self.mes_base, self.ano_base ] )

    def obter_origem( self ) -> str:
        return ';'.join( [ self.sistema, self.estado, self.obter_data_base() ] )

    def obter_raiz( self ) -> str:
        return ''.join( [ 'TXT/', self.sistema ] )

    def obter_path( self ) -> str:
        return '_'.join( [ self.obter_raiz(), self.estado, self.mes_base, self.ano_base ] )

    def gerar_arquivo_sintetico_dado_basico( self ) -> TextIOWrapper:
        return open( ''.join( [ self.obter_path(), '_sintetico_dado_basico.txt' ] ), 'a', encoding="utf-8" )

    def gerar_arquivo_sintetico_custo_unitario( self ) -> TextIOWrapper:
        return open( ''.join( [ self.obter_path(), '_sintetico_custo_unitario.txt' ] ), 'a', encoding="utf-8" )

    def gerar_arquivo_sintetico_custo_unitario_composicao( self ) -> TextIOWrapper:
        return open( ''.join( [ self.obter_path(), '_sintetico_custo_unitario_composicao.txt' ] ), 'a', encoding="utf-8" )

    def gerar_arquivo_analitico_custo_mao_de_obra( self ) -> TextIOWrapper:
        return open( ''.join( [ self.obter_path(), '_analitico_custo_unitario_mao_de_obra.txt' ] ), 'a', encoding="utf-8" )

    def gerar_arquivo_analitico_custo_equipamento( self ) -> TextIOWrapper:
        return open( ''.join( [ self.obter_path(), '_analitico_custo_unitario_equipamento.txt' ] ), 'a', encoding="utf-8" )



class RegexArquivo:

    def __init__( self, pdf_file: str ):
        self.regex = self.obter_regex_arquivo( pdf_file )

    def obter_pattern_arquivo( self ) -> str:
        return r'(?P<re_sistema>(.+))/(?P<re_estado>\w{2}) (?P<re_mes_base>(\d{2}))-(?P<re_ano_base>(\d{4})) (Relat??rio) (?P<re_item_a>(Anal??tico|Sint??tico)) (de) (?P<re_item_b>Composi????es de Custos|Composi????es de Custos|Equipamentos|M??o de Obra|Mao de Obra|Materiais)( - com desonera????o| - com desonera?????o| - com desoneracao)?\.pdf$'

    def obter_regex_arquivo( self, pdf_file: str ) -> Match:
        return re.match( self.obter_pattern_arquivo(), pdf_file )


class Regex:

    def __init__( self, avaliado: str ) -> None:
        regex_1 = r'(CGCIT)'
        regex_2 = r'(.*) - (\w{1,20}/\d{4})'
        regex_3 = r'(\s*) (Custo Unit??rio|Pre??o Unit??rio)'
        regex_4 = r'(C??digo)'
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

    def obter_pattern_alfa_material( self ) -> str:
        return r'(?P<re_codigo>[M]\d{4}) (?P<re_descricao>.+) (?P<re_unidade>\w{1,5}) (?P<re_custo>\d*.*\d*.\d+,\d{4}|\s*-)'

    def obter_pattern_beta_material( self ) -> str:
        return r'(\s+(?P<re_descricao1>.+)(\n)(\s+)(.+)(\n))'

    def obter_regex( self, avaliado ) -> Match:
        regex_alfa = re.match( self.obter_pattern_alfa_material(), avaliado )
        regex_beta = re.match( self.obter_pattern_beta_material(), avaliado, re.MULTILINE )
        if regex_alfa is not None:
            return regex_alfa
        elif regex_beta is not None:
            return regex_beta


class RegexMaoDeObra(Regex):

    def __init__(self, avaliado: str ) -> None:
        super().__init__( avaliado )
        self.principal = self.obter_regex( avaliado )

    def obter_pattern_alfa_mao_de_obra( self ) -> str:
        return r'(?P<re_codigo>[P]\d{4}|\w*) (?P<re_descricao>.+) (?P<re_unidade>h|m??s) (?P<re_salario>\d*.\d+,\d{4}|\s*-) (?P<re_encargos_sociais>\d*.\d+,\d{4}%|\s*-) (?P<re_custo>\d*.\d+,\d{4}|\s*-) (?P<re_periculosidade>\d*.\d+,\d{4}%|\s*-)'

    def obter_pattern_beta_mao_de_obra( self ) -> str:
        return r'(\s*)? (?P<re_codigo>[P]\d{4}) (?P<re_descricao>.+) (?P<re_unidade>h|m??s) (\s*) (?P<re_salario>\d*.\d+,\d{4}) (\s*) (?P<re_encargos_sociais>\d*.\d+,\d{4}%) (\s*) (?P<re_custo>\d*.\d+,\d{4}) (\s*) (?P<re_periculosidade>\d*.\d+,\d{4}%)'

    def obter_regex( self, avaliado ) -> Match:
        regex_alfa = re.match( self.obter_pattern_alfa_mao_de_obra(), avaliado )
        regex_beta = re.match( self.obter_pattern_beta_mao_de_obra(), avaliado )
        if regex_alfa is not None:
            return regex_alfa
        elif regex_beta is not None:
            return regex_beta


class RegexEquipamento(Regex):

    def __init__(self, avaliado: str ) -> None:
        super().__init__( avaliado )
        self.principal = self.obter_regex( avaliado )

    def obter_pattern_alfa_equipamento( self ) -> str:
        return r'(?P<re_codigo>[E|A]\d{4}) (?P<re_descricao>.+) (?P<re_aquisicao>\d*.*\d*.\d+,\d{2,4}|\s*-) (?P<re_depreciacao>\d*.*\d*.\d+,\d{2,4}|\s*-) (?P<re_oportunidade_capital>\d*.*\d*.\d+,\d{2,4}|\s*-) (?P<re_seguros_impostos>\d*.*\d*.\d+,\d{2,4}|\s*-) (?P<re_manutencao>\d*.*\d*.\d+,\d{2,4}|\s*-) (?P<re_operacao>\d*.*\d*.\d+,\d{2,4}|\s*-) (?P<re_mao_de_obra>\d*.*\d*.\d+,\d{2,4}|\s*-) (?P<re_custo_produtivo>\d*.*\d*.\d+,\d{2,4}|\s*-) (?P<re_custo_improdutivo>\d*.*\d*.\d+,\d{2,4}|\s*-)'

    def obter_pattern_beta_equipamento( self ) -> str:
        return r'(?P<re_codigo>[E|A]\d{4}) (?P<re_descricao>.+) (?P<re_custo_produtivo>\d*.*\d*.\d+,\d{2,4}|\s*-) (?P<re_custo_improdutivo>\d*.*\d*.\d+,\d{2,4}|\s*-)'

    def obter_regex( self, avaliado ) -> Match:
        regex_alfa = re.match( self.obter_pattern_alfa_equipamento(), avaliado )
        regex_beta = re.match( self.obter_pattern_beta_equipamento(), avaliado )
        if regex_alfa is not None:
            return regex_alfa
        elif regex_beta is not None:
            return regex_beta


class RegexComposicao(Regex):

    def __init__(self, avaliado: str ) -> None:
        super().__init__( avaliado )
        self.principal = self.obter_regex( avaliado )

    def obter_pattern_alfa_composicao( self ) -> str:
        return r'(?P<re_codigo>^\d{7}) (?P<re_descricao>(.+) (\S+) (.+)) (?P<re_unidade>\S+) (?P<re_custo>.+\,\d{2}|\s*-)'

    def obter_pattern_beta_composicao( self ) -> str:
        return r'(?P<re_descricao>(\s*) (.+) (\S*))'

    def obter_regex( self, avaliado ) -> Match:
        regex_alfa = re.match( self.obter_pattern_alfa_composicao(), avaliado )
        regex_beta = re.match( self.obter_pattern_beta_composicao(), avaliado )
        if regex_alfa is not None:
            return regex_alfa
        elif regex_beta is not None:
            return regex_beta


class Sintetico:

    def __init__( self, regex: Match ) -> None:
        self.regex = regex
        self.codigo = self.obter_codigo()
        self.unidade = ''
        self.descricao = self.obter_descricao()

    def obter_codigo( self ) -> str:
        grupo = 're_codigo'
        if grupo in self.regex.groupdict():
            obj_codigo = DescricaoNormalizada( self.regex.group( grupo ) )
            return obj_codigo.descricao
        else:
            return ''

    def obter_descricao( self ) -> str:
        obj_descricao = DescricaoNormalizada( self.regex.group('re_descricao') )

        return obj_descricao.descricao

    def obter_dados_cadastro( self, origem_dados: str ) -> str:
        dados = ';'.join( [origem_dados, self.codigo, self.descricao, self.unidade] )
        dados = '{}{}'.format( dados, '\n' )
        return dados

    def escrever_arquivo_cadastro( self, arquivo: TextIOWrapper, origem_dados: str ) -> None:
        arquivo.write( self.obter_dados_cadastro( origem_dados ) )


class Material(Sintetico):

    def __init__( self, regex: Match ) -> None:
        super().__init__( regex )
        obj_custo = NumeroNormalizado( self.obter_custo() )
        self.unidade = self.obter_unidade()
        self.custo = obj_custo.numero
        self.categoria = str(MATERIAL)

    def obter_unidade( self ) -> str:
        return self.regex.group('re_unidade')

    def obter_custo( self ):
        return self.regex.group('re_custo')

    def obter_dados_custos_material( self, origem_dados: str ) -> str:
        dados = ';'.join( [origem_dados, self.codigo, '','','','', self.custo, self.categoria] )
        dados = '{}{}'.format( dados, '\n' )
        return dados

    def escrever_arquivo_custo( self, custos_unitarios: TextIOWrapper, origem_dados: str ) -> None:
        custos_unitarios.write( self.obter_dados_custos_material( origem_dados ) )


class MaoDeObra(Sintetico):

    def __init__( self, regex: Match ) -> None:
        super().__init__( regex )
        self.unidade = self.obter_unidade()
        self.periculosidade = self.obter_periculosidade()
        self.salario = self.obter_salario()
        self.custo_onerado = self.obter_custo_onerado()
        self.custo_desonerado = ''
        self.encargos_sociais_onerado = self.obter_encargos_sociais_onerado()
        self.encargos_sociais_desonerado = ''
        self.categoria = str(MAO_DE_OBRA)

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

    def obter_dados_custos_mao_de_obra( self, origem_dados: str ) -> str:
        dados = ';'.join( [origem_dados, self.codigo, self.custo_onerado,'',self.custo_desonerado,'','', self.categoria] )
        dados = '{}{}'.format( dados, '\n' )
        return dados

    def escrever_arquivo_custo( self, custos_unitarios: TextIOWrapper, origem_dados: str ) -> None:
        custos_unitarios.write( self.obter_dados_custos_mao_de_obra( origem_dados ) )

    def obter_detalhamento_custos_mao_de_obra( self, origem_dados: str ) -> str:
        detalhes = ';'.join([origem_dados, self.codigo, self.salario, self.periculosidade, self.encargos_sociais_onerado, self.encargos_sociais_desonerado] )
        detalhes = '{}{}'.format( detalhes, '\n' )
        return detalhes

    def escrever_arquivo_detalhamento_custos( self, detalhamento_custos: TextIOWrapper, origem_dados: str ) -> None:
        detalhamento_custos.write( self.obter_detalhamento_custos_mao_de_obra( origem_dados ) )


class Equipamento(Sintetico):

    def __init__( self, regex: Match ) -> None:
        super().__init__( regex )
        self.regex = regex
        self.unidade = 'h'
        self.aquisicao = self.obter_aquisicao()
        self.depreciacao = self.obter_depreciacao()
        self.oportunidade_capital = self.obter_oportunidade_capital()
        self.seguros_impostos = self.obter_seguros_impostos()
        self.manutencao = self.obter_manutencao()
        self.operacao = self.obter_operacao()
        self.mao_de_obra_onerado = self.obter_mao_de_obra_onerado()
        self.mao_de_obra_desonerado = ''
        self.custo_produtivo_onerado = self.obter_custo_produtivo_onerado()
        self.custo_improdutivo_onerado = self.obter_custo_improdutivo_onerado()
        self.custo_produtivo_desonerado = ''
        self.custo_improdutivo_desonerado = ''
        self.categoria = str(EQUIPAMENTO)

    def obter_aquisicao( self ) -> str:
        grupo = 're_aquisicao'
        if grupo in self.regex.groupdict():
            obj_aquisicao = PercentualNormalizado( self.regex.group( grupo ) )
            return obj_aquisicao.percentual
        else:
            return ''

    def obter_depreciacao( self ) -> str:
        grupo = 're_depreciacao'
        if grupo in self.regex.groupdict():
            obj_depreciacao = NumeroNormalizado( self.regex.group( grupo ) )
            return obj_depreciacao.numero
        else:
            return ''

    def obter_oportunidade_capital( self ) -> str:
        grupo = 're_oportunidade_capital'
        if grupo in self.regex.groupdict():
            obj_oportunidade_capital = NumeroNormalizado( self.regex.group( grupo ) )
            return obj_oportunidade_capital.numero
        else:
            return ''

    def obter_seguros_impostos( self ) -> str:
        grupo = 're_seguros_impostos'
        if grupo in self.regex.groupdict():
            obj_seguros_impostos = NumeroNormalizado( self.regex.group( grupo ) )
            return obj_seguros_impostos.numero
        else:
            return ''

    def obter_manutencao( self ) -> str:
        grupo = 're_manutencao'
        if grupo in self.regex.groupdict():
            obj_manutencao = NumeroNormalizado( self.regex.group( grupo ) )
            return obj_manutencao.numero
        else:
            return ''

    def obter_operacao( self ) -> str:
        grupo = 're_operacao'
        if grupo in self.regex.groupdict():
            obj_operacao = NumeroNormalizado( self.regex.group( grupo ) )
            return obj_operacao.numero
        else:
            return ''

    def obter_mao_de_obra_onerado( self ) -> str:
        grupo = 're_mao_de_obra'
        if grupo in self.regex.groupdict():
            obj_mao_de_obra_onerado = NumeroNormalizado( self.regex.group( grupo ) )
            return obj_mao_de_obra_onerado.numero
        else:
            return ''

    def obter_custo_produtivo_onerado( self ) -> str:
        grupo = 're_custo_produtivo'
        if grupo in self.regex.groupdict():
            obj_custo_produtivo_onerado = NumeroNormalizado( self.regex.group( grupo ) )
            return obj_custo_produtivo_onerado.numero
        else:
            return ''

    def obter_custo_improdutivo_onerado( self ) -> str:
        grupo = 're_custo_improdutivo'
        if grupo in self.regex.groupdict():
            obj_custo_improdutivo_onerado = NumeroNormalizado( self.regex.group( grupo ) )
            return obj_custo_improdutivo_onerado.numero
        else:
            return ''

    def obter_dados_custos_equipamento( self, origem_dados: str ) -> str:
        dados = ';'.join( [origem_dados, self.codigo, self.custo_produtivo_onerado,self.custo_improdutivo_onerado,self.custo_produtivo_desonerado,self.custo_improdutivo_desonerado,'',self.categoria] )
        dados = '{}{}'.format( dados, '\n' )
        return dados

    def escrever_arquivo_custo( self, custos_unitarios: TextIOWrapper, origem_dados: str ) -> None:
        custos_unitarios.write( self.obter_dados_custos_equipamento( origem_dados ) )

    def obter_detalhamento_custos_equipamento( self, origem_dados: str ) -> str:
        detalhes = ';'.join([origem_dados, self.codigo, self.aquisicao, self.depreciacao, self.oportunidade_capital, self.seguros_impostos, self.manutencao, self.operacao, self.mao_de_obra_onerado, self.mao_de_obra_desonerado] )
        detalhes = '{}{}'.format( detalhes, '\n' )
        return detalhes

    def escrever_arquivo_detalhamento_custos( self, detalhamento_custos: TextIOWrapper, origem_dados: str ) -> None:
        detalhamento_custos.write( self.obter_detalhamento_custos_equipamento( origem_dados ) )


class Composicao(Sintetico):

    def __init__( self, regex: Match ) -> None:
        super().__init__( regex )
        self.unidade = self.obter_unidade()
        self.custo = self.obter_custo()
        self.categoria = str(COMPOSICAO_PRINCIPAL)

    def obter_unidade( self ) -> str:
        grupo = 're_unidade'
        if grupo in self.regex.groupdict():
            obj_unidade = DescricaoNormalizada( self.regex.group( grupo ) )
            return obj_unidade.descricao
        else:
            return ''

    def obter_custo( self ) -> str:
        grupo = 're_custo'
        if grupo in self.regex.groupdict():
            obj_custo = NumeroNormalizado( self.regex.group( grupo ) )
            return obj_custo.numero
        else:
            return ''

    def obter_dados_custos_composicao( self, origem_dados: str ) -> str:
        dados = ';'.join( [origem_dados, self.codigo, self.custo, '', self.categoria] )
        dados = '{}{}'.format( dados, '\n' )
        return dados

    def escrever_arquivo_custo( self, custos_unitarios: TextIOWrapper, origem_dados: str ) -> None:
        custos_unitarios.write( self.obter_dados_custos_composicao( origem_dados ) )


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
        aux1 = pagina
        aux2 = ''
        while aux1 != aux2:
            aux2 = aux1
            aux1 = aux1.replace('  ', ' ')
        linhas = aux1.split('\n')
        return linhas

    def obter_pattern_fic( self ) -> str:
        return r'(.+) (?P<re_uf>.+) (FIC) (?P<re_fic>\d\,\d\d\d\d\d)'

    def obter_pattern_producao( self ) -> str:
        return r'(.+) (?P<re_data_base>.+) (Produ????o da equipe) (?P<re_producao>\d{1,3}(\.\d{3})*,\d{5}) (?P<re_unidade>.+)'
    
    def obter_pattern_codigo( self ) -> str:
        return r'(?P<re_codigo>\d{7}) (.+) (Valores em reais \(R\$\))'

    def obter_pattern_equipamento( self ) -> str:
        return r'(\s*) (?P<re_equipamento>[EA]\d{4}) (.+) (?P<re_quantidade>\d+\,\d{5}) (?P<re_utilizacao>\d+\,\d{2})'

    def obter_pattern_mao_de_obra( self ) -> str:
        return r'(\s*) (?P<re_mao_de_obra>[P]\d{4}) (.+) (?P<re_quantidade>\d+\,\d{5})'

    def obter_pattern_tempo_fixo( self ) -> str:
        return r'(\s*) (?P<re_item_transportado>\d{7}|[M]\d{4}) (.+) (?P<re_tempo_fixo>59\d{5}){1} (?P<re_quantidade>\d+\,\d{5}) (t){1}'
    
    def obter_pattern_transporte_rodoviario( self ) -> str:
        return r'(\s*) (?P<re_item_transportado>\d{7}|[M]\d{4}) (.+) (?P<re_quantidade>\d+\,\d{5}) (tkm){1} (?P<re_leito_natural>59\d{5}) (?P<re_revestimento_primario>59\d{5}) (?P<re_pavimentado>59\d{5})'

    def obter_pattern_transporte_ferroviario( self ) -> str:
        return r'(\s*) (?P<re_item_transportado>\d{7}|[M]\d{4}) (.+) (?P<re_quantidade>\d+\,\d{5}) (tkm){1} (?P<re_ferroviario>59\d{5})'

    def obter_pattern_atividade_auxiliar( self ) -> str:
        return r'(\s*) (?P<re_atividade_auxiliar>\d{7}) (.+) (?P<re_quantidade>\d+\,\d{5}) (\w{1,3})'

    def obter_pattern_material( self ) -> str:
        return r'(\s*) (?P<re_material>[M]\d{4}) (.+) (?P<re_quantidade>\d+\,\d{5}) (\w{1,3})'

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
        self.tipo = 'hor??ria'
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

    def obter_apropriacao_dado_basico( self, origem_dados: str ) -> str:
        if self.producao == '1.00000':
            self.tipo = 'unit??ria'
        dados = ';'.join( [origem_dados, self.composicao, self.fic, self.producao, self.tipo] )
        dados = '{}{}'.format( dados, '\n' )
        return dados

    def escrever_arquivo_apropriacao_dado_basico( self, dado_basico: TextIOWrapper, origem_dados: str ) -> None:
        dado_basico.write( self.obter_apropriacao_dado_basico( origem_dados ) )

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

    def obter_apropriacao_transporte_ferroviario( self, origem_dados: str ) -> str:
        transporte_ferroviario = self.lista_transporte[-1][0].strip()
        quantidade = self.lista_transporte[-1][1].replace('.', '').replace(',', '.')
        item_transportado = self.lista_transporte[-1][2].strip()
        dados = ';'.join( [origem_dados, self.composicao, transporte_ferroviario, quantidade, '', item_transportado, str(TRANSPORTE)] )
        dados = '{}{}'.format( dados, '\n' )
        return dados

    def escrever_arquivo_apropriacao_transporte_ferroviario( self, apropriacao: TextIOWrapper, origem_dados: str ) -> None:
        apropriacao.write( self.obter_apropriacao_transporte_ferroviario( origem_dados ) )

    def obter_apropriacao_transporte_pavimentado( self, origem_dados: str ) -> str:
        transporte_pavimentado = self.lista_transporte[-1][0].strip()
        quantidade = self.lista_transporte[-1][1].replace('.', '').replace(',', '.')
        item_transportado = self.lista_transporte[-1][2].strip()
        dados = ';'.join( [origem_dados, self.composicao, transporte_pavimentado, quantidade, '', item_transportado, str(TRANSPORTE)] )
        dados = '{}{}'.format( dados, '\n' )
        return dados

    def escrever_arquivo_apropriacao_transporte_pavimentado( self, apropriacao: TextIOWrapper, origem_dados: str ) -> None:
        apropriacao.write( self.obter_apropriacao_transporte_pavimentado( origem_dados ) )

    def obter_apropriacao_transporte_revestimento_primario( self, origem_dados: str ) -> str:
        transporte_revestimento_primario = self.lista_transporte[-2][0].strip()
        quantidade = self.lista_transporte[-2][1].replace('.', '').replace(',', '.')
        item_transportado = self.lista_transporte[-2][2].strip()
        dados = ';'.join( [origem_dados, self.composicao, transporte_revestimento_primario, quantidade, '', item_transportado, str(TRANSPORTE)] )
        dados = '{}{}'.format( dados, '\n' )
        return dados

    def escrever_arquivo_apropriacao_transporte_revestimento_primario( self, apropriacao: TextIOWrapper, origem_dados: str ) -> None:
        apropriacao.write( self.obter_apropriacao_transporte_revestimento_primario( origem_dados ) )

    def obter_apropriacao_transporte_leito_natural( self, origem_dados: str ) -> str:
        transporte_leito_natural = self.lista_transporte[-3][0].strip()
        quantidade = self.lista_transporte[-3][1].replace('.', '').replace(',', '.')
        item_transportado = self.lista_transporte[-3][2].strip()
        dados = ';'.join( [origem_dados, self.composicao, transporte_leito_natural, quantidade, '', item_transportado, str(TRANSPORTE)] )
        dados = '{}{}'.format( dados, '\n' )
        return dados

    def escrever_arquivo_apropriacao_transporte_leito_natural( self, apropriacao: TextIOWrapper, origem_dados: str ) -> None:
        apropriacao.write( self.obter_apropriacao_transporte_leito_natural( origem_dados ) )