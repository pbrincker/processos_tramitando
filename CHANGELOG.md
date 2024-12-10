# Changelog

## [1.0.1] - 2024-12-10

### Correções
- Corrigido o funcionamento das datas no sistema de tramitação:
  - A data informada pelo usuário agora é corretamente considerada no registro do histórico
  - O cálculo de prazos (úteis e corridos) agora considera a data selecionada como início
  - O registro de histórico mantém consistência entre data_registro e created_at
  - Melhorada a validação dos campos de prazo na tramitação

### Melhorias Técnicas
- Refatoração da função tramitar_processo para melhor tratamento de datas
- Ajustes na validação de campos do formulário de tramitação
- Melhoria na consistência dos registros de histórico de processos
