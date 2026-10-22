# Correção — exclusão de pedido de entrada

## Causas encontradas

1. A rota de exclusão chamava `PedidoEntrada.safe_delete(id, usuario_id=...)`, mas o método original aceitava somente `id`. Isso produzia um `TypeError` que era escondido pela mensagem genérica.
2. O método original tentava apagar somente o pedido pai, embora a tabela `item_entrada` tenha uma chave estrangeira para `pedido_entrada`.
3. O arquivo `banco.sql` usa `id_usuario`, enquanto parte do código usava `usuario_id`, o que pode gerar erro de coluna inexistente dependendo do esquema instalado.

## Alterações

- O modelo reconhece `usuario_id` e `id_usuario` e usa a coluna realmente existente para listar, localizar, salvar, atualizar e excluir pedidos.
- A exclusão usa uma transação: bloqueia o pedido, valida vínculos, trata itens, atualiza o estoque apenas para movimentos marcados como `ENTRADA`, remove movimentos de entrada que ficaram sem referência e por fim exclui o pedido.
- Movimentos `CADASTRO` e movimentos de entrada usados por outros itens/pedidos são preservados.
- Se reverter o estoque deixaria uma quantidade negativa, a operação é cancelada e a mensagem explica o motivo.
- Qualquer falha inesperada é registrada com traceback completo pelo logger do Flask no terminal; a interface mantém uma mensagem compreensível.

## Validação

- 24 arquivos Python analisados sem erros de sintaxe.
- 19 templates Jinja verificados sem erros de compilação.
- A conexão com o MySQL real não foi disponível neste ambiente, então a operação precisa ser testada no banco usado pelo SmartMeds.
