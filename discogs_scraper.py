from playwright.sync_api import sync_playwright
import json

BASE_URL = "https://www.discogs.com"

# Função para obter os 10 primeiros artistas automaticamente
def get_artists(genre):
    search_url = f"https://www.discogs.com/pt_BR/search/?sort=want%2Cdesc&q={genre}&type=artist&layout=sm"
    artists = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(search_url, timeout=120000, wait_until="domcontentloaded")

        try:
            page.wait_for_selector("#search_results", timeout=60000)
            for i in range(1, 11):  # Pegando os 10 primeiros artistas
                artist_selector = f"#search_results > li:nth-child({i}) > div.card_body > h4 > a"
                artist_element = page.locator(artist_selector)

                if artist_element.count() > 0:
                    artist_name = artist_element.text_content().strip()
                    artist_link = BASE_URL + artist_element.get_attribute("href")
                    artists.append((artist_name, artist_link))
        except Exception as e:
            print(f"Erro ao coletar o link dos artistas: {e}")
        finally:
            browser.close()

    return artists

# Função para coletar informações do artista e seus 10 primeiros álbuns
def scrape_artist_info(url, genre):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(url, timeout=120000, wait_until="domcontentloaded")

        artist_info = None

        try:
            # Captura o nome do artista
            page.wait_for_selector("h1.MuiTypography-root", timeout=60000)
            artist_name = page.locator("h1.MuiTypography-root").text_content().strip()
            
            # Captura os membros da banda
            members_selector = "th:has-text('Membros') + td a.link_1ctor"
            members_elements = page.locator(members_selector)
            members = [member.text_content().strip() for member in members_elements.element_handles()]
            
            # Captura os sites associados
            sites_selector = "th:has-text('Sites') + td a"
            sites_elements = page.locator(sites_selector)
            sites = [site.get_attribute("href") for site in sites_elements.element_handles()]

            albums_tab_selector = "p.facet_1Bq8g"
            page.click(albums_tab_selector)
            page.wait_for_selector(".discographyGrid_31ecR", timeout=60000)

            album_name_selector = ".discographyGrid_31ecR tbody tr td.title_oY1q1 a.link_1ctor"
            album_year_selector = ".discographyGrid_31ecR tbody tr td.year_2QrBV"

            albums = []
            for i in range(min(10, page.locator(album_name_selector).count())):  # Pegando os 10 primeiros álbuns
                album_name = page.locator(album_name_selector).nth(i).text_content().strip()
                album_link = BASE_URL + page.locator(album_name_selector).nth(i).get_attribute("href")
                album_year = page.locator(album_year_selector).nth(i).text_content().strip()
                albums.append({"name": album_name, "link": album_link, "year": album_year})

            artist_info = {"genre": genre, "name": artist_name, "members": members, "sites": sites, "albums": albums}

        except Exception as e:
            print(f"Erro ao coletar informações do artista: {e}")


        finally:
            browser.close()
            return artist_info

# Função para acessar uma versão específica do álbum
def navigate_to_album_version(master_url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(master_url, timeout=120000, wait_until="domcontentloaded")

        try:
            version_selector = "#versions table tbody tr td.title_3z5nf.cell_WT9P- a"
            if page.locator(version_selector).count() > 0:
                return BASE_URL + page.locator(version_selector).nth(0).get_attribute("href")
        except Exception as e:
            print(f"Erro ao acessar a versão do álbum: {e}")
        finally:
            browser.close()

    return None

# Função para coletar informações do álbum e faixas
def scrape_album_info(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(url, timeout=120000, wait_until="domcontentloaded")

        album_info = None

        try:
            page.wait_for_selector("#release-tracklist table", timeout=60000)

            record_label_selector = "th:has-text('Label') + td"
            record_label = page.locator(record_label_selector).nth(0).text_content().strip() if page.locator(record_label_selector).count() > 0 else "Gravadora não encontrada"

            styles_selector = "th:has-text('Style') + td a"
            styles = [style.text_content().strip() for style in page.locator(styles_selector).all()]

            tracks = []
            tracklist_selector = "#release-tracklist table tbody tr"

            for i in range(page.locator(tracklist_selector).count()):
                track_number_selector = f"{tracklist_selector}:nth-child({i+1}) td.trackPos_2RCje span"
                track_name_selector = f"{tracklist_selector}:nth-child({i+1}) td.trackTitle_CTKp4 > span"
                track_time_selector = f"{tracklist_selector}:nth-child({i+1}) td.duration_2t4qr span"

                track_number = page.locator(track_number_selector).nth(0).text_content().strip() if page.locator(track_number_selector).count() > 0 else "N/A"
                track_name = page.locator(track_name_selector).nth(0).text_content().strip() if page.locator(track_name_selector).count() > 0 else "N/A"

                # Ajuste para capturar corretamente o tempo da música
                if page.locator(track_time_selector).count() > 0:
                    track_time = page.locator(track_time_selector).nth(0).text_content().strip()
                else:
                    track_time = "Desconhecido"

                tracks.append({
                    "number": track_number,
                    "name": track_name,
                    "time": track_time
                })

        except Exception as e:
            print(f"Erro ao coletar informações do álbum: {e}")

        finally:
            browser.close()
            album_info = {"record_label": record_label, "styles": styles, "tracks": tracks}
            return album_info


if __name__ == "__main__":
    # Fluxo principal para salvar JSONL corretamente
    genre = "rock"
    artists = get_artists(genre)
    artists_data = []

    with open("discogsArtistsAlbums.jsonl", "w") as file:  # Arquivo JSONL
        for artist_name, artist_url in artists:
            print(f"Coletando informações do artista: {artist_name}")
            artist_data = scrape_artist_info(artist_url, genre)

            if artist_data != None:
                for album in artist_data["albums"]:
                    print(f"Coletando informações do álbum: {album['name']}")
                    album_version_link = navigate_to_album_version(album["link"])

                    if album_version_link:
                        album_info = scrape_album_info(album_version_link)
                        album.update(album_info)
                    else:
                        print(f"Não foi possível coletar informações da versão específica do álbum {album['name']}")

                artists_data.append(artist_data)

                # Salvando cada artista como uma linha JSONL
                json.dump(artist_data, file, ensure_ascii=False)
                file.write("\n")
