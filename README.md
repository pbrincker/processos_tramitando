# Sistema de Gestão de Licitações

Sistema especializado de digitalização e otimização de processos licitatórios para administração pública, implementando automatização e controle de fluxos governamentais.

## Funcionalidades

- Autenticação baseada em perfil de usuário
- Dashboard analítico com métricas
- Gerenciamento CRUD completo de processos licitatórios
- Sistema de tramitação integrado
- Notificações internas
- Métricas e relatórios
- Controle de acesso seguro
- Múltiplas modalidades de licitação

## Stack Tecnológica

- **Backend:** Flask (Python)
- **Banco de dados:** PostgreSQL
- **Frontend:** HTML/CSS Responsivo com Bootstrap
- **Bibliotecas:** Chart.js para visualizações
- **Segurança:** Autenticação baseada em perfil

## Configuração do Ambiente

1. Clone o repositório
2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure as variáveis de ambiente no arquivo `.env`:
```
DATABASE_URL=postgresql://user:password@localhost:5432/database
```

4. Execute as migrações do banco de dados:
```bash
flask db upgrade
```

5. Inicie o servidor:
```bash
python app.py
```

## Contribuição

Por favor, leia o arquivo CONTRIBUTING.md para detalhes sobre nosso código de conduta e o processo para enviar pull requests.

## Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo LICENSE.md para detalhes.
