"""
Cantina FATEC — Sistema de Gestão
Atlética FATEC Rio Claro

Ponto de entrada do sistema com menu interativo.
"""

import sys
import os

# Garante que o diretório raiz do projeto está no path
sys.path.insert(0, os.path.dirname(__file__))

from sistema.estoque import Estoque
from sistema.gerenciador_pagamentos import GerenciadorPagamentos
from sistema.gerenciador_vendas import GerenciadorVendas
from relatorios import Relatorios
from utils import gerador_dados, persistencia
from modelos.produto import LoteProduto
from datetime import date


# ------------------------------------------------------------------ #
#  Utilitários de UI                                                   #
# ------------------------------------------------------------------ #

def cls():
    os.system("cls" if os.name == "nt" else "clear")


def pausar():
    input("\n  [ pressione Enter para continuar ]")


def linha(c="=", n=62):
    print(c * n)


def cabecalho(titulo: str):
    linha()
    print(f"  🍽️   {titulo}")
    linha()


# ------------------------------------------------------------------ #
#  Inicialização                                                       #
# ------------------------------------------------------------------ #

def criar_sistema():
    estoque    = Estoque()
    pagamentos = GerenciadorPagamentos()
    vendas     = GerenciadorVendas(estoque, pagamentos)
    return estoque, pagamentos, vendas


def carregar_ou_criar():
    dados = persistencia.carregar()
    if dados:
        estoque    = dados["estoque"]
        pagamentos = dados["pagamentos"]
        vendas     = dados["vendas"]
        # Reconectar referências (necessário após desserialização)
        vendas._estoque    = estoque
        vendas._pagamentos = pagamentos
        print("  📂 Sistema restaurado do arquivo salvo.")
    else:
        estoque, pagamentos, vendas = criar_sistema()
        print("  📋 Novo sistema iniciado (sem dados anteriores).")
    return estoque, pagamentos, vendas


# ------------------------------------------------------------------ #
#  Menus                                                               #
# ------------------------------------------------------------------ #

MENU_PRINCIPAL = """
  1.  Inicializar com dados aleatórios (Faker)
  2.  ─── ESTOQUE ──────────────────────────────
  3.  Visualizar Estoque
  4.  Adicionar Lote ao Estoque
  5.  Editar Quantidade de Lote
  6.  ─── VENDAS ───────────────────────────────
  7.  Realizar Venda Manual
  8.  Simular Vendas Automáticas
  9.  ─── RELATÓRIOS ───────────────────────────
  10. Relatório de Estoque
  11. Relatório de Vendas
  12. Relatório de Consumo
  13. Relatório de Pagamentos PIX
  14. ─── DADOS ──────────────────────────────
  15. Salvar Dados
  16. Carregar Dados
  0.  Sair
"""


def menu_principal(estoque, pagamentos, vendas, relatorios):
    while True:
        cabecalho("CANTINA FATEC — Sistema de Gestão")
        print(f"  Estoque: {estoque} | {vendas} | {pagamentos}")
        print(MENU_PRINCIPAL)
        opcao = input("  Escolha uma opção: ").strip()

        # ---- Inicialização ----
        if opcao == "1":
            cabecalho("Inicializar com Faker")
            confirmar = input(
                "  ⚠️  Isso APAGARÁ os dados atuais. Confirmar? (s/n): "
            ).lower()
            if confirmar == "s":
                estoque, pagamentos, vendas = criar_sistema()
                relatorios.__init__(estoque, pagamentos, vendas)
                print("\n  Gerando estoque...")
                gerador_dados.gerar_lotes(estoque, n_lotes=40)
                print("  Simulando vendas...")
                gerador_dados.simular_vendas(vendas, estoque, n_vendas=60)
                print("\n  ✅ Sistema populado com sucesso!")
            pausar()

        # ---- Estoque ----
        elif opcao == "3":
            relatorios.relatorio_estoque()
            pausar()

        elif opcao == "4":
            cabecalho("Adicionar Lote ao Estoque")
            try:
                nome     = input("  Nome do produto    : ").strip()
                pc       = float(input("  Preço de compra  R$: "))
                pv       = float(input("  Preço de venda   R$: "))
                dc_str   = input("  Data de compra (AAAA-MM-DD) [hoje]: ").strip()
                dv_str   = input("  Data de vencimento (AAAA-MM-DD)   : ").strip()
                qtd      = int(input("  Quantidade                        : "))

                dc = date.fromisoformat(dc_str) if dc_str else date.today()
                dv = date.fromisoformat(dv_str)

                lote = LoteProduto(
                    nome_produto=nome,
                    preco_compra=pc,
                    preco_venda=pv,
                    data_compra=dc,
                    data_vencimento=dv,
                    quantidade=qtd,
                )
                estoque.adicionar_lote(lote)
                print(f"\n  ✅ {lote}")
            except (ValueError, KeyError) as e:
                print(f"\n  ❌ Erro: {e}")
            pausar()

        elif opcao == "5":
            cabecalho("Editar Quantidade de Lote")
            relatorios.relatorio_estoque()
            try:
                nome   = input("  Nome do produto : ").strip()
                id_lot = input("  ID do lote      : ").strip().upper()
                qtd    = int(input("  Nova quantidade : "))
                estoque.editar_quantidade(nome, id_lot, qtd)
                print("  ✅ Quantidade atualizada com sucesso.")
            except (ValueError, KeyError) as e:
                print(f"\n  ❌ Erro: {e}")
            pausar()

        # ---- Vendas ----
        elif opcao == "7":
            cabecalho("Realizar Venda Manual")
            try:
                nome      = input("  Nome do consumidor          : ").strip()
                categoria = input("  Categoria (aluno/professor/servidor): ").strip()
                curso     = input("  Curso (IA/ESG/N/A)          : ").strip()
                pix       = input("  Chave PIX (CPF/e-mail/tel)  : ").strip()

                carrinho = []
                print("\n  Adicione produtos (deixe o nome em branco para finalizar):")
                while True:
                    prod = input("    Produto   : ").strip()
                    if not prod:
                        break
                    qtd = int(input("    Quantidade: "))
                    carrinho.append((prod, qtd))

                if not carrinho:
                    print("  ⚠️  Carrinho vazio — venda cancelada.")
                else:
                    venda, pagamento = vendas.realizar_venda(
                        nome, categoria, curso, carrinho, pix
                    )
                    print(f"\n  ✅ Venda registrada:\n     {venda}")
                    print(f"  💳 Pagamento PIX:\n     {pagamento}")
            except ValueError as e:
                print(f"\n  ❌ Erro: {e}")
            pausar()

        elif opcao == "8":
            cabecalho("Simular Vendas Automáticas")
            try:
                n_str = input("  Número de vendas a simular [60]: ").strip()
                n = int(n_str) if n_str else 60
                gerador_dados.simular_vendas(vendas, estoque, n_vendas=n)
            except ValueError as e:
                print(f"\n  ❌ Erro: {e}")
            pausar()

        # ---- Relatórios ----
        elif opcao == "10":
            relatorios.relatorio_estoque()
            pausar()

        elif opcao == "11":
            relatorios.relatorio_vendas()
            pausar()

        elif opcao == "12":
            relatorios.relatorio_consumo()
            pausar()

        elif opcao == "13":
            relatorios.relatorio_pagamentos()
            pausar()

        # ---- Persistência ----
        elif opcao == "15":
            persistencia.salvar(estoque, pagamentos, vendas)
            pausar()

        elif opcao == "16":
            dados = persistencia.carregar()
            if dados:
                estoque    = dados["estoque"]
                pagamentos = dados["pagamentos"]
                vendas     = dados["vendas"]
                vendas._estoque    = estoque
                vendas._pagamentos = pagamentos
                relatorios.__init__(estoque, pagamentos, vendas)
                print("  ✅ Dados carregados com sucesso!")
            else:
                print("  ❌ Arquivo de dados não encontrado.")
            pausar()

        # ---- Sair ----
        elif opcao == "0":
            resp = input("\n  Deseja salvar antes de sair? (s/n): ").lower()
            if resp == "s":
                persistencia.salvar(estoque, pagamentos, vendas)
            print("\n  👋 Até logo!\n")
            break

        else:
            print("  ❌ Opção inválida.")
            pausar()


# ------------------------------------------------------------------ #
#  Entry point                                                         #
# ------------------------------------------------------------------ #

def main():
    print("\n" + "=" * 62)
    print("  🚀  Iniciando Cantina FATEC...")
    print("=" * 62)

    estoque, pagamentos, vendas = carregar_ou_criar()
    relatorios = Relatorios(estoque, pagamentos, vendas)

    menu_principal(estoque, pagamentos, vendas, relatorios)


if __name__ == "__main__":
    main()
