# Correção da exclusão de produto

## Causa

A rotina anterior excluía registros de `movimentacao` antes de remover as linhas correspondentes de `item_entrada` e `item_saida`. Como essas tabelas possuem chaves estrangeiras para `movimentacao.id`, o MySQL bloqueava a exclusão (erro 1451).

## Ajuste

- A exclusão do produto agora ocorre dentro de uma única transação.
- As movimentações do produto são bloqueadas e identificadas primeiro.
- Os itens de entrada e saída associados são removidos antes das movimentações.
- As movimentações são excluídas antes do produto.
- Se alguma etapa falhar, toda a transação é desfeita (`rollback`).
- Os cabeçalhos dos pedidos são preservados, e a mensagem da tela informa quantos itens vinculados foram removidos.
- Falhas inesperadas são registradas com traceback no terminal.

**Importante:** excluir um produto remove as linhas de itens dos pedidos que dependem das suas movimentações. Os registros gerais dos pedidos continuam no sistema, mas não mostrarão os itens removidos.
