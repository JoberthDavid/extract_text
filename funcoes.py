import re
from io import TextIOWrapper
from typing import Match, Union

from constantes import (
                        COMPOSICAO_PRINCIPAL,
                        EQUIPAMENTO,
                        EQUIPAMENTO_CUSTO_HORARIO,
                        MAO_DE_OBRA,
                        MAO_DE_OBRA_CUSTO_HORARIO,
                        EXECUCAO_HORARIO,
                        EXECUCAO_UNITARIO,
                        MATERIAL,
                        MATERIAL_CUSTO_UNITARIO,
                        ATIVIDADE_AUXILIAR,
                        ATIVIDADE_AUXILIAR_CUSTO_UNITARIO,
                        TEMPO_FIXO,
                        TEMPO_FIXO_CUSTO_UNITARIO,
                        TRANSPORTE,
                        TRANSPORTE_CUSTO_UNITARIO,
                        DIRETO_TOTAL_UNITARIO,
                        CODIGO_HORARIO,
                        CODIGO_HORARIO_EXECUCAO,
                        CODIGO_UNITARIO,
                        CODIGO_UNITARIO_DIRETO_TOTAL
                    )

mao_de_obra = '_sintetico_mao_de_obra_'
material = '_sintetico_material_'
equipamento = '_sintetico_equipamento_'
composicao = '_sintetico_composicao_'


def formatar_numero( numero: str ) -> str:
    return numero.strip(' ').replace('-','0.0000').replace('.','').replace(',','.')


def formatar_percentual( percentual: str ) -> str:
    return percentual.strip(' ').replace(',','.').replace('%','')


def formatar_descricao( descricao: str ) -> str:
    return descricao.strip(' ').replace('.','').replace(',','.').replace('          ',' ').replace('         ',' ').replace('        ',' ').replace('       ',' ').replace('      ',' ').replace('     ',' ').replace('    ',' ').replace('   ',' ').replace('  ',' ')


def retornar_pattern_mao_de_obra() -> str:
    return r'(?P<re_codigo>[P]\d{4}) (\s{1,4}) (?P<re_descricao>(.+) (\s+)) (?P<re_unidade>h|mês) (\s+) (?P<re_salario>\d*.\d+,\d{4}|\s*-) (\s+) (?P<re_encargos_sociais>\d*.\d+,\d{4}%) (\s+) (?P<re_custo>\d*.\d+,\d{4}|\s*-) (\s+) (?P<re_periculosidade>\d*.\d+,\d{4}%)'


def retornar_pattern_alfa_material() -> str:
    return r'(?P<re_codigo>[M]\d{4}) (?P<re_descricao>.+) (?P<re_unidade>\w{1,5}) (?P<re_custo>\d*.*\d*.\d+,\d{4}|\s*-)'


def retornar_pattern_beta_material() -> str:
    return r'(?P<re_descricao>\w*)'


def retornar_pattern_alfa_equipamento() -> str:
    return r'(?P<re_codigo>[E|A]\d{4}) (?P<re_descricao>.+) (?P<re_aquisicao>\d*.*\d*.\d+,\d{4}|\s*-) (?P<re_depreciacao>\d*.*\d*.\d+,\d{4}|\s*-) (?P<re_oportunidade_capital>\d*.*\d*.\d+,\d{4}|\s*-) (?P<re_seguros_impostos>\d*.*\d*.\d+,\d{4}|\s*-) (?P<re_manutencao>\d*.*\d*.\d+,\d{4}|\s*-) (?P<re_operacao>\d*.*\d*.\d+,\d{4}|\s*-) (?P<re_mao_de_obra>\d*.*\d*.\d+,\d{4}|\s*-) (?P<re_custo_produtivo>\d*.*\d*.\d+,\d{4}|\s*-) (?P<re_custo_improdutivo>\d*.*\d*.\d+,\d{4}|\s*-)'


def retornar_pattern_beta_equipamento() -> str:
    return r'(?P<re_codigo>[E|A]\d{4}) (?P<re_descricao>.+) (?P<re_custo_produtivo>\d*.*\d*.\d+,\d{4}|\s*-) (?P<re_custo_improdutivo>\d*.*\d*.\d+,\d{4}|\s*-)'


def retornar_pattern_alfa_composicao() -> str:
    return r'(?P<re_codigo>^\d{7}) (?P<re_descricao>(.+) (\S+) (.+)) (?P<re_unidade>\S+) (?P<re_custo>.+\,\d{2}|\s*-)'


def retornar_pattern_beta_composicao() -> str:
    return r'(?P<re_descricao>(\s*) (.+) (\S*))'


def iniciar_dicionario_mao_de_obra( item: str ) -> dict:
    return {
            'codigo' : '',
            'descricao': '',
            'unidade': '',
            'encargos_sociais_onerado': '',
            'periculosidade': '',
            'salario': '',
            'custo_onerado': '',
            'encargos_sociais_desonerado': '',
            'custo_desonerado': '',
            'categoria': str(MAO_DE_OBRA),
        }


def iniciar_dicionario_material( item: str ) -> dict:
    return {
            'codigo': '',
            'descricao': '',
            'unidade': '',
            'custo': '',
            'categoria': str(MATERIAL),            
        }


def iniciar_dicionario_equipamento( item: str ) -> dict:
    return {
            'codigo': '',
            'descricao': '',
            'unidade': '',
            'aquisicao': '',
            'depreciacao': '',
            'oportunidade_capital': '',
            'seguros_impostos': '',
            'manutencao': '',
            'operacao': '',
            'mao_de_obra_onerado': '',
            'custo_produtivo_onerado': '',
            'custo_improdutivo_onerado': '',
            'mao_de_obra_desonerado': '',
            'custo_produtivo_desonerado': '',
            'custo_improdutivo_desonerado': '',
            'categoria': str(EQUIPAMENTO),
        }


def iniciar_dicionario_composicao( item: str ) -> dict:
    return {
            'codigo': '',
            'descricao': '',
            'unidade': '',
            'custo_onerado': '',
            'custo_desonerado': '',
            'categoria': str(COMPOSICAO_PRINCIPAL),
        }


def iniciar_dicionario( item: str ) -> dict:
    d = dict()
    if item == mao_de_obra:
        d = iniciar_dicionario_mao_de_obra( item )
    elif item == material:
        d = iniciar_dicionario_material( item )
    elif item == equipamento:
        d = iniciar_dicionario_equipamento( item )
    elif item == composicao:
        d = iniciar_dicionario_composicao( item )
    return d


def retornar_dados_cadastro_mao_de_obra(origem_dados: str, d: dict) -> str:
    return ','.join([origem_dados,
                d['codigo'],
                formatar_descricao( d['descricao'] ),
                d['unidade'],
                '\n']
            )


def retornar_dados_cadastro_material(origem_dados: str, d: dict) -> str:
    return ','.join([origem_dados,
                d['codigo'],
                formatar_descricao( d['descricao'] ),
                d['unidade'],
                '\n']
            )


def retornar_dados_cadastro_equipamento(origem_dados: str, d: dict) -> str:
    return ','.join([origem_dados,
                d['codigo'],
                formatar_descricao( d['descricao'] ),
                d['unidade'],
                '\n']
            )


def retornar_dados_cadastro_composicao(origem_dados: str, d: dict) -> str:
    return ','.join([origem_dados, 
                d['codigo'], 
                formatar_descricao( d['descricao'] ),
                d['unidade'],
                '\n']
            )


def escrever_arquivo_cadastro(item: str, descricao: TextIOWrapper, origem_dados: str, d: dict) -> None:
    if item == mao_de_obra:
        descricao.write( 
            retornar_dados_cadastro_mao_de_obra( origem_dados, d )
        )
    elif item == material:
        descricao.write(
            retornar_dados_cadastro_material( origem_dados, d )
        )
    elif item == equipamento:
        descricao.write(
            retornar_dados_cadastro_equipamento( origem_dados, d )
        )
    elif item == composicao:
        descricao.write(
            retornar_dados_cadastro_composicao( origem_dados, d )
        )


def retornar_dados_custos_mao_de_obra(origem_dados: str, d: dict) -> str:
    return ','.join([origem_dados,
                d['codigo'],
                formatar_numero( d['custo_onerado'] ),
                '',
                formatar_numero( d['custo_desonerado'] ),
                '',
                '',
                d['categoria'],
                '\n']
            )


def retornar_dados_custos_material(origem_dados: str, d: dict) -> str:
    return ','.join([origem_dados,
                d['codigo'],
                '',
                '',
                '',
                '',
                formatar_numero( d['custo'] ),
                d['categoria'],
                '\n']
            )


def retornar_dados_custos_equipamento(origem_dados: str, d: dict) -> str:
    return ','.join([origem_dados,
                d['codigo'],
                formatar_numero( d['custo_produtivo_onerado'] ),
                formatar_numero( d['custo_improdutivo_onerado'] ),
                formatar_numero( d['custo_produtivo_desonerado'] ),
                formatar_numero( d['custo_improdutivo_desonerado'] ),
                '',
                d['categoria'],
                '\n']
            )


def retornar_dados_custos_composicao(origem_dados: str, d: dict) -> str:
    return ','.join([origem_dados,
                d['codigo'],
                formatar_numero( d['custo_onerado'] ),
                formatar_numero( d['custo_desonerado'] ),
                '\n']
            )


def escrever_arquivo_custos(item: str, custos_unitarios: TextIOWrapper, origem_dados: str, d: dict) -> None:
    if item == mao_de_obra:
        custos_unitarios.write(
            retornar_dados_custos_mao_de_obra( origem_dados, d )
        )
    elif item == material:
        custos_unitarios.write(
            retornar_dados_custos_material( origem_dados, d )
        )
    elif item == equipamento:
        custos_unitarios.write(
            retornar_dados_custos_equipamento( origem_dados, d )
        )
    elif item == composicao:
        custos_unitarios.write(
            retornar_dados_custos_composicao( origem_dados, d )
        )


def retornar_detalhamento_custos_mao_de_obra(origem_dados: str, d: dict) -> str:
    return ','.join([origem_dados,
                d['codigo'],
                formatar_numero( d['salario'] ),
                formatar_percentual( d['periculosidade'] ),
                formatar_percentual( d['encargos_sociais_onerado'] ),
                formatar_percentual( d['encargos_sociais_desonerado'] ),
                '\n']
            )


def retornar_detalhamento_custos_equipamento(origem_dados: str, d: dict) -> str:
    return ','.join([origem_dados,
                d['codigo'],
                formatar_numero( d['aquisicao'] ),
                formatar_numero( d['depreciacao'] ),
                formatar_numero( d['oportunidade_capital'] ),
                formatar_numero( d['seguros_impostos'] ),
                formatar_numero( d['manutencao'] ),
                formatar_numero( d['operacao'] ),
                formatar_numero( d['mao_de_obra_onerado'] ),
                formatar_numero( d['mao_de_obra_desonerado'] ),
                '\n']
            )


def escrever_arquivo_detalhamento_custos(item: str, detalhamento_custos: TextIOWrapper, origem_dados: str, d: dict) -> None:
    if item == mao_de_obra:
        detalhamento_custos.write(
            retornar_detalhamento_custos_mao_de_obra( origem_dados, d )
        )
    elif item == equipamento:
        detalhamento_custos.write(
            retornar_detalhamento_custos_equipamento( origem_dados, d )
        )


def retornar_regex_cabecalho(linha: str ):
    regex_1 = r'(CGCIT)'
    regex_2 = r'(.*) - (\w{1,20}/\d{4})'
    regex_3 = r'(\s*) (Custo Unitário|Preço Unitário)'
    regex_4 = r'(Código)'
    regex_5 = r'(\s*) \(R\$\)'
    lista_regex = [regex_1, regex_2, regex_3, regex_4, regex_5]
    retorno = None
    for rx in lista_regex:
        if ( re.match(rx, linha) is not None ):
            retorno = re.match(rx, linha)
    return retorno


def retornar_regex( item: str, linha: str ):
    if True:#item == mao_de_obra:
        print( item )
        return re.match( retornar_pattern_mao_de_obra(), linha)

    elif item == material:
        regex_alfa = re.match( retornar_pattern_alfa_material(), linha)
        regex_beta = re.match( retornar_pattern_beta_material(), linha)

        if regex_alfa is not None:
            return regex_alfa
        elif regex_beta is not None:
            return regex_beta

    elif item == equipamento:
        regex_alfa = re.match( retornar_pattern_alfa_equipamento(), linha)
        regex_beta = re.match( retornar_pattern_beta_equipamento(), linha)

        if regex_alfa is not None:
            return regex_alfa
        elif regex_beta is not None:
            return regex_beta

    elif item == composicao:
        regex_alfa = re.match( retornar_pattern_alfa_composicao(), linha)
        regex_beta = re.match( retornar_pattern_beta_composicao(), linha)

        if regex_alfa is not None:
            return regex_alfa
        elif regex_beta is not None:
            return regex_beta


def configurar_dicionario_mao_de_obra(d: dict, regex_alfa: Match , regex_beta = None) -> None:
    d['codigo'] = regex_alfa.group('re_codigo')
    d['descricao'] = regex_alfa.group('re_descricao')
    d['unidade'] =  regex_alfa.group('re_unidade')
    d['encargos_sociais_onerado'] =  regex_alfa.group('re_encargos_sociais')
    d['periculosidade'] = regex_alfa.group('re_periculosidade')
    d['salario'] = regex_alfa.group('re_salario')
    d['custo_onerado'] = regex_alfa.group('re_custo')
    d['encargos_sociais_desonerado'] = regex_beta.group('re_encargos_sociais')
    d['custo_desonerado'] = regex_beta.group('re_custo')


def configurar_dicionario_material(d: dict, regex_alfa: Match) -> None:
    d['codigo'] = regex_alfa.group('re_codigo')
    d['descricao'] = regex_alfa.group('re_descricao')
    d['unidade'] = regex_alfa.group('re_unidade')
    d['custo'] = regex_alfa.group('re_custo')


def configurar_dicionario_equipamento(d: dict, regex_alfa: Match , regex_beta = None) -> None:
    d['codigo'] = regex_alfa.group('re_codigo')
    d['descricao'] = regex_alfa.group('re_descricao')
    d['unidade'] = 'h'
    if len(regex_alfa.groups()) == 11:
        d['aquisicao'] = regex_alfa.group('re_aquisicao')
        d['depreciacao'] = regex_alfa.group('re_depreciacao')
        d['oportunidade_capital'] = regex_alfa.group('re_oportunidade_capital')
        d['seguros_impostos'] = regex_alfa.group('re_seguros_impostos')
        d['manutencao'] = regex_alfa.group('re_manutencao')
        d['operacao'] = regex_alfa.group('re_operacao')
        d['mao_de_obra_onerado'] = regex_alfa.group('re_mao_de_obra')
        d['mao_de_obra_desonerado'] = regex_beta.group('re_mao_de_obra')
        d['custo_produtivo_onerado'] = regex_alfa.group('re_custo_produtivo')
        d['custo_improdutivo_onerado'] = regex_alfa.group('re_custo_improdutivo')
        d['custo_produtivo_desonerado'] = regex_beta.group('re_custo_produtivo')
        d['custo_improdutivo_desonerado'] = regex_beta.group('re_custo_improdutivo')
    else:
        d['custo_produtivo_onerado'] = regex_alfa.group('re_custo_produtivo')
        d['custo_improdutivo_onerado'] = regex_alfa.group('re_custo_improdutivo')
        d['custo_produtivo_desonerado'] = regex_beta.group('re_custo_produtivo')
        d['custo_improdutivo_desonerado'] = regex_beta.group('re_custo_improdutivo')


def configurar_dicionario_composicao(d: dict, regex_alfa: Match , regex_beta = None) -> None:
    d['codigo'] = regex_alfa.group('re_codigo')
    d['descricao'] = regex_alfa.group('re_descricao')
    d['unidade'] = regex_alfa.group('re_unidade')
    d['custo_onerado'] = regex_alfa.group('re_custo')
    d['custo_desonerado'] = formatar_numero('0')#regex_beta.group('re_custo')


def configurar_dicionario( item: str, d: dict, regex_alfa: Match , regex_beta = None) -> dict:
    if item == mao_de_obra:
        configurar_dicionario_mao_de_obra(d, regex_alfa, regex_beta)

    elif item == material:
        configurar_dicionario_material(d, regex_alfa)

    elif item == equipamento:
        configurar_dicionario_equipamento(d, regex_alfa, regex_beta)

    elif item == composicao:
        configurar_dicionario_composicao(d, regex_alfa, regex_beta)

    return d


def preparar_grupo_regex_arquivo( grupo: str ) -> str:
    grupo_regex = grupo.replace('Analítico','_analitico').replace('Sintético','_sintetico').replace('Composições de Custos','_composicao_').replace('Mão de Obra','_mao_de_obra_').replace('Equipamentos','_equipamento_').replace('Materiais','_material_')
    return grupo_regex


def retornar_pattern_arquivo() -> str:
    return r'(?P<re_sistema>(.+))/(?P<re_estado>\w{2}) (?P<re_mes_base>(\d{2}))-(?P<re_ano_base>(\d{4})) (Relatório) (?P<re_item_a>(Analítico|Sintético)) (de) (?P<re_item_b>Composições de Custos|Equipamentos|Mão de Obra|Mao de Obra|Materiais)( - com desoneração| - com desoneraç╞o)?\.pdf$'


def retornar_regex_arquivo( pdf_file: str ):
    return re.match( retornar_pattern_arquivo(), pdf_file)


def configurar_dicionario_arquivo(d: dict, regex_alfa: Match) -> None:
    d['sistema'] = regex_alfa.group('re_sistema')
    d['estado'] = regex_alfa.group('re_estado')
    d['mes_base'] = regex_alfa.group('re_mes_base')
    d['ano_base'] = regex_alfa.group('re_ano_base')
    d['item'] = preparar_grupo_regex_arquivo( ''.join( [ regex_alfa.group('re_item_a'), regex_alfa.group('re_item_b') ] ) )


def iniciar_dicionario_arquivo() -> dict:
    d = {
        'sistema': '',
        'estado': '',
        'mes_base': '',
        'ano_base': '',
        'item': '',
    }
    return d


def retornar_raiz( d_arquivo: dict ) -> str:
    return ''.join( [ 'TXT/', d_arquivo['sistema'] ] )


def retornar_path( d_arquivo: dict ) -> str:
    return '_'.join( [ retornar_raiz( d_arquivo ), d_arquivo['estado'], d_arquivo['mes_base'], d_arquivo['ano_base'] ] )


def retornar_data_base( d_arquivo: dict ) -> str:
    return '-'.join( [ d_arquivo['mes_base'], d_arquivo['ano_base'] ] )


def retornar_origem( d_arquivo: dict ) -> str:
    return ','.join( [  d_arquivo['sistema'], d_arquivo['estado'], retornar_data_base( d_arquivo ) ] )


def retornar_item( d_arquivo: dict ) -> str:
    return d_arquivo['item']


def gerar_arquivo_dados_basicos( path: str ) -> TextIOWrapper:
    return open( ''.join( [ path, '_dados_basicos.txt' ] ), 'a', encoding="utf-8" )


def gerar_arquivo_custos_unitarios_composicoes( path: str ) -> TextIOWrapper:
    return open( ''.join( [ path, '_composicoes_custos_unitarios.txt' ] ), 'w', encoding="utf-8" )


def gerar_arquivo_custos_unitarios_insumos( path: str ) -> TextIOWrapper:
    return open( ''.join( [ path, '_insumos_custos_unitarios.txt' ] ), 'a', encoding="utf-8" )


def gerar_arquivo_detalhamento_custos_mao_de_obra( path: str) -> TextIOWrapper:
    return open( ''.join( [ path, '_detalhamento_mao_de_obra_custo_unitario.txt' ] ), 'w', encoding="utf-8" )


def gerar_arquivo_detalhamento_custos_equipamento( path: str) -> TextIOWrapper:
    return open( ''.join( [ path, '_detalhamento_equipamento_custo_unitario.txt' ] ), 'w', encoding="utf-8" )
