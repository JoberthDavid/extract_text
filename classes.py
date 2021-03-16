class Composicao:

    def __init__(self):
        self.uf = ''
        self.data_base = ''
        self.composicao = ''
        self.descricao = ''
        self.fic = ''
        self.producao = ''
        self.unidade = ''
        self.lista_insumo = list()
        self.lista_atitivade_auxiliar = list()
        self.lista_tempo_fixo = list()
        self.lista_transporte = list()


class MaoDeObra:

    def __init__(self):
        self.codigo = ''
        self.salario = 0.0000
        self.encargos_sociais = 0.0000
        self.custo = 0.0000
        self.periculosidade = 0.0000
    
    def format_percentage(self, valor):
        return ( valor / 100 )

    def set_cost(self):
        es = self.format_percentage( self.encargos_sociais )
        pe = self.format_percentage( self.periculosidade )
        self.custo = ( pe * self.salario ) + self.salario * ( 1 + es )