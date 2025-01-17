# Discogs Scraper com Playwright

## Descrição

Este projeto realiza a extração automática de informações de artistas e álbuns do site [Discogs](https://www.discogs.com/pt_BR) utilizando a biblioteca Playwright. O objetivo é coletar dados estruturados sobre os 10 primeiros artistas de um gênero musical especificado (foi utilizado rock como exemplo), incluindo seus álbuns e faixas.

## Funcionalidades

- Obtém automaticamente os 10 primeiros artistas de um determinado gênero musical no Discogs.
- Coleta informações detalhadas sobre cada artista, como nome, membros da banda e sites associados.
- Obtém detalhes sobre os 10 primeiros álbuns de cada artista, incluindo ano de lançamento e link para mais informações.
- Acessa versões específicas de álbuns e extrai dados como gravadora, estilos musicais e lista de faixas.
- Salva os dados coletados no formato JSONL.

## Dependências

Para executar este projeto, foi utulizado:

- **Python** (3.11.10)
- **Playwright** para Python (1.49.1)
- **Pytest** (8.3.4)
- **Unittest** (??????????????????????????) para mock nos testes
p
### Instalação do Playwright

Antes de rodar o script, instale as dependências necessárias:

```sh
pip install playwright
playwright install
```

## Como Executar

1. Certifique-se de que todas as dependências estão instaladas.
2. Execute o arquivo discogs_scraper.py:

```sh
python discogs_scraper.py
```

O script buscará informações sobre artistas do gênero "rock" (ou outro gênero que você queira modificar no código).

## Estrutura do Projeto

- `get_artists_links(genre)`: Obtém os links dos 10 primeiros artistas de um determinado gênero em ordem do artistas mais desejáveis conforme critérios da plataforma Discogs.
- `scrape_artist_info(url, genre)`: Coleta informações do artista e seus álbuns.
- `navigate_to_album_version(master_url)`: Acessa uma versão específica do álbum.
- `scrape_album_info(url)`: Extrai informações do álbum, como gravadora, estilos e faixas.
- Os dados extraídos são salvos no arquivo `discogsArtistsAlbums.jsonl`.

## Formato de Saída

Os dados coletados são armazenados no formato JSONL, com cada linha representando um artista e seus respectivos álbuns.

Exemplo de uma linha JSONL:

```json
{
  "id": "12345",
  "genre": "rock",
  "name": "Nome do artista",
  "members": ["Membro 1", "Membro 2"],
  "sites": ["https://wwww.siteartista.com"],
  "albums": [
    {
      "name": "Nome do álbum",
      "link": "https://www.album.com",
      "year": "2025",
      "record_label": "Nome da gravadora",
      "styles": ["Estilo 1", "Estilo 2"],
      "tracks": [
        {"number": "1", "name": "Titulo da faixa 1", "time": "3:45"},
        {"number": "2", "name": "Titulo da faixa 2", "time": "4:15"}
      ]
    }
  ]
}
```

## Testes

Este projeto inclui testes unitários utilizando **pytest** para garantir o funcionamento correto das funções principais. Os testes utilizam **unittest.mock** para simular o comportamento do Playwright.

### Como Executar os Testes

Antes de rodar os testes, certifique-se de que todas as dependências estão instaladas.

Para executá-los, utilize o seguinte comando:

```sh
pytest test_discogs_scraper.py
```

### Estrutura dos Testes

Os testes cobrem as principais funções do projeto:

- `test_get_artists_links`: Testa se a função get_artists_links retorna corretamente os links dos 10 primeiros artistas de um gênero.
- `test_scrape_artist_info`: Testa se a função scrape_artist_info extrai corretamente as informações de um artista.
- `test_scrape_album_info`: Testa se a função scrape_album_info coleta corretamente as informações de um álbum.
