
# Devolutiva formativa — Atividade 01 da SA

**Estudante:** Pedro  
**Turma:** Rio Negrinho — Tarde  
**Unidade Curricular:** Programação de Aplicativos  
**Projeto:** Fábrica de Chocolate — ERP  
**Código analisado:** `codigo/app.py`  
**Referência:** Situação de Aprendizagem nº 1 — *Da Ideia ao Código*

## O que você já conseguiu desenvolver

Pedro, você apresentou um sistema de gerenciamento de fábrica de chocolates, com controle de ingredientes, produção, vendas, receitas de produtos e relatórios. A proposta demonstra iniciativa para representar diferentes atividades de uma empresa em um mesmo programa.

Pontos positivos identificados:

- Utilizou **programação orientada a objetos** com as classes `Ingrediente`, `Chocolate`, `Cliente` e `FabricaERP`.
- Organizou o sistema em métodos para consultar estoques, comprar ingredientes, produzir, vender e gerar relatórios.
- Criou **receitas de fabricação** associando produtos às quantidades de ingredientes necessárias.
- Implementou verificações de estoque antes da produção e das vendas.
- Utilizou `try/except ValueError` nas funções de entrada numérica.
- Desenvolveu regras para desconto por quantidade e benefício de fidelidade.
- Implementou **salvamento e carregamento de informações em JSON**.
- Criou um relatório com receitas, despesas registradas, histórico de produção e produto mais vendido.

## O que precisa ser corrigido

### 1. Proteger os dados durante o salvamento

O sistema salva os dados quando a opção de sair é selecionada. Se o programa for encerrado inesperadamente antes disso, alterações realizadas durante a sessão podem ser perdidas.

**Como melhorar:** considerar o salvamento após operações importantes, como compras, produção e vendas. Também é recomendável tratar erros de leitura e gravação.

### 2. Validar todas as quantidades de receitas

No cadastro de chocolates, quantidades negativas de ingredientes não geram uma mensagem específica: elas simplesmente deixam de ser adicionadas à receita.

**Como melhorar:** rejeitar explicitamente valores negativos, permitir zero quando o ingrediente não for utilizado e exigir pelo menos um ingrediente com quantidade positiva.

### 3. Melhorar a precisão do relatório financeiro

O relatório apresenta a diferença entre vendas e compras de ingredientes como "Lucro Líquido". Entretanto, o programa não considera outras despesas, como energia, mão de obra e custos operacionais.

**Como melhorar:** apresentar o valor como **resultado simplificado** ou **saldo entre vendas e compras registradas**, até que o sistema contemple os demais custos.

## Oportunidades de melhoria

### 4. Simplificar a representação dos dados em JSON

Métodos como `to_dict()` armazenam alguns valores únicos dentro de listas, por exemplo, `"Estoque": [self.estoque]`.

**Como melhorar:** salvar valores individuais diretamente, quando não houver necessidade de uma coleção. Isso simplificará a serialização, a leitura e a manutenção do arquivo.

### 5. Tratar arquivos de dados inválidos

O método `carregar_dados()` espera que o arquivo JSON contenha determinadas chaves e uma estrutura válida.

**Como melhorar:** considerar situações em que o arquivo esteja ausente, incompleto ou corrompido, informando o problema sem encerrar inesperadamente a aplicação.

### 6. Proteger informações utilizadas nos testes

O programa utiliza CPF ou telefone como identificador para clientes do programa de fidelidade.

**Como melhorar:** usar dados fictícios nas demonstrações, evitar publicar cadastros reais e, futuramente, definir identificadores internos que não dependam de documentos pessoais.

### 7. Organizar e documentar os módulos

A classe `FabricaERP` reúne várias operações de estoque, produção, vendas e relatórios.

**Como melhorar:** à medida que o projeto crescer, considerar a separação dessas áreas em módulos. Incluir docstrings que descrevam as regras importantes e atualizar o README com orientações específicas para executar o sistema.

## Testes recomendados

1. Repor ingredientes com quantidades válidas e inválidas.
2. Produzir chocolates com estoque suficiente.
3. Tentar produzir sem ingredientes suficientes.
4. Vender produtos disponíveis e conferir a redução do estoque.
5. Tentar vender uma quantidade maior que a disponível.
6. Verificar o desconto por quantidade e as regras de fidelidade.
7. Salvar e reiniciar o sistema, conferindo os dados.
8. Testar o carregamento de um arquivo JSON incompleto ou inválido.

## Prioridades para a próxima versão

1. **Melhorar o salvamento e o tratamento dos arquivos de dados.**
2. **Validar integralmente as quantidades das receitas.**
3. **Corrigir a nomenclatura do relatório financeiro.**
4. **Simplificar a estrutura dos dados serializados.**
5. **Documentar as regras e os resultados dos testes.**

## Mensagem final

Pedro, seu projeto demonstra compreensão de **classes, objetos, métodos, estruturas de dados, regras de negócio e persistência de informações**. Você conseguiu relacionar diferentes processos de uma fábrica, especialmente estoque, produção e vendas.

Seu próximo desafio é fortalecer a confiabilidade das informações e verificar o comportamento do programa em situações inesperadas. **Continue desenvolvendo com atenção às validações e à organização dos dados.** Sua aplicação já possui uma base consistente para novas funcionalidades.
