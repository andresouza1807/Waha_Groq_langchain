#!/usr/bin/env python3
"""
Script para adicionar novos lembretes facilmente
"""
import json
import sys
from datetime import datetime, timedelta


def carregar_lembretes(arquivo='lembretes.json'):
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def salvar_lembretes(lembretes, arquivo='lembretes.json'):
    with open(arquivo, 'w', encoding='utf-8') as f:
        json.dump(lembretes, f, indent=2, ensure_ascii=False)


def adicionar_lembrete_interativo():
    print('='*60)
    print('Adicionar Novo Lembrete')
    print('='*60)

    # Coleta informações
    numero = input('Número WhatsApp (com DDI, ex: 5511999999999): ').strip()
    mensagem = input('Mensagem do lembrete: ').strip()

    print('\nData do lembrete:')
    print('  1 - Hoje')
    print('  2 - Amanhã')
    print('  3 - Data específica (AAAA-MM-DD)')
    opcao_data = input('Escolha: ').strip()

    if opcao_data == '1':
        data = datetime.now().strftime('%Y-%m-%d')
    elif opcao_data == '2':
        data = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    else:
        data = input('Data (AAAA-MM-DD): ').strip()

    hora = input('Hora (HH:MM): ').strip()

    print('\nRecorrência:')
    print('  1 - Único (não repete)')
    print('  2 - Diário')
    print('  3 - Semanal')
    print('  4 - Mensal')
    opcao_rec = input('Escolha: ').strip()

    recorrencia_map = {
        '1': False,
        '2': 'diario',
        '3': 'semanal',
        '4': 'mensal'
    }

    recorrente = recorrencia_map.get(opcao_rec, False)

    # Carrega lembretes existentes
    lembretes = carregar_lembretes()

    # Gera novo ID
    novo_id = max([l['id'] for l in lembretes], default=0) + 1

    # Cria novo lembrete
    novo_lembrete = {
        'id': novo_id,
        'ativo': True,
        'numero': numero,
        'mensagem': mensagem,
        'data': data,
        'hora': hora,
        'recorrente': recorrente
    }

    lembretes.append(novo_lembrete)
    salvar_lembretes(lembretes)

    print('\n' + '='*60)
    print('✓ Lembrete adicionado com sucesso!')
    print('='*60)
    print(f'ID: {novo_id}')
    print(f'Para: {numero}')
    print(f'Data/Hora: {data} às {hora}')
    print(f'Mensagem: {mensagem}')
    print(f'Recorrente: {recorrente if recorrente else "Não"}')
    print('='*60)


def listar_lembretes():
    lembretes = carregar_lembretes()

    if not lembretes:
        print('Nenhum lembrete cadastrado')
        return

    print('\n' + '='*60)
    print('Lembretes Cadastrados')
    print('='*60)

    for l in lembretes:
        status = '✓' if l.get('ativo') else '✗'
        rec = f" (🔄 {l.get('recorrente')})" if l.get('recorrente') else ''
        print(f"\n[{status}] ID {l['id']}: {l['data']} às {l['hora']}{rec}")
        print(f"    Para: {l['numero']}")
        print(f"    Msg: {l['mensagem']}")

    print('\n' + '='*60)


def remover_lembrete():
    listar_lembretes()

    lembrete_id = int(input('\nID do lembrete para remover: '))

    lembretes = carregar_lembretes()
    lembretes = [l for l in lembretes if l['id'] != lembrete_id]

    salvar_lembretes(lembretes)
    print(f'\n✓ Lembrete {lembrete_id} removido')


def main():
    if len(sys.argv) > 1:
        comando = sys.argv[1]
        if comando == 'listar':
            listar_lembretes()
        elif comando == 'remover':
            remover_lembrete()
        else:
            print('Comandos: listar, remover')
    else:
        adicionar_lembrete_interativo()


if __name__ == '__main__':
    main()
