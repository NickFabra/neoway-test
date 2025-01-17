from unittest.mock import MagicMock, patch
from discogs_scraper import get_artists_links, scrape_artist_info, scrape_album_info


# Teste para get_artists_links
@patch("discogs_scraper.sync_playwright")
def test_get_artists_links(mock_playwright):
    mock_browser = MagicMock()
    mock_page = MagicMock()
    mock_playwright.return_value.__enter__.return_value.chromium.launch.return_value = mock_browser
    mock_browser.new_page.return_value = mock_page

    # Simula o comportamento
    mock_page.locator.return_value.text_content.side_effect = ["Artist 1", "Artist 2"]
    mock_page.locator.return_value.get_attribute.side_effect = ["/artist1", "/artist2"]
    mock_page.locator.return_value.count.return_value = 1

    # Executa o teste
    result = get_artists_links("rock")
    assert len(result) == 2
    assert result[0] == ("Artist 1", "https://www.discogs.com/artist1")
    assert result[1] == ("Artist 2", "https://www.discogs.com/artist2")


# Teste para scrape_artist_info
@patch("discogs_scraper.sync_playwright")
def test_scrape_artist_info(mock_playwright):
    mock_browser = MagicMock()
    mock_page = MagicMock()
    mock_playwright.return_value.__enter__.return_value.chromium.launch.return_value = mock_browser
    mock_browser.new_page.return_value = mock_page

    # Simula os valores retornados para nome e ID do artista
    mock_page.locator.return_value.text_content.side_effect = ["Artist Name", "12345"]

    # Simula o método count() para garantir que retorne um número
    mock_page.locator.return_value.count.return_value = 1

    # Simula os sites
    site_mock = MagicMock()
    site_mock.get_attribute.return_value = "https://www.artistwebsite.com"
    mock_page.locator.return_value.element_handles.return_value = [site_mock]

    # Executa o teste
    artist_info = scrape_artist_info("https://www.discogs.com/artist1", "rock")
    assert artist_info is not None, "A função retornou None"
    assert artist_info["name"] == "Artist Name"
    assert artist_info["id"] == "12345"
    assert artist_info["genre"] == "rock"
    assert len(artist_info["sites"]) == 1
    assert artist_info["sites"][0] == "https://www.artistwebsite.com"


# Teste para scrape_album_info
@patch("discogs_scraper.sync_playwright")
def test_scrape_album_info(mock_playwright):
    mock_browser = MagicMock()
    mock_page = MagicMock()
    mock_playwright.return_value.__enter__.return_value.chromium.launch.return_value = mock_browser
    mock_browser.new_page.return_value = mock_page

    # Simula o comportamento para a gravadora
    def mock_record_label(selector):
        if selector == "th:has-text('Label') + td":
            label_mock = MagicMock()
            label_mock.nth.return_value.text_content.return_value = "Awesome Records"
            label_mock.count.return_value = 1
            return label_mock
        raise ValueError(f"Unexpected selector {selector}")

    # Simula os estilos
    def mock_styles(selector):
        if selector == "th:has-text('Style') + td a":
            style_mock_1 = MagicMock()
            style_mock_1.text_content.return_value = "Rock"
            style_mock_2 = MagicMock()
            style_mock_2.text_content.return_value = "Alternative"
            return [style_mock_1, style_mock_2]
        raise ValueError(f"Unexpected selector {selector}")

    # Simula o seletor principal de faixas
    def mock_tracklist(selector):
        if selector == "#release-tracklist table tbody tr":
            tracklist_mock = MagicMock()
            tracklist_mock.count.return_value = 1
            return tracklist_mock
        raise ValueError(f"Unexpected selector {selector}")

    # Simula os seletores das faixas
    def mock_tracks(selector):
        track_mock_number = MagicMock()
        track_mock_name = MagicMock()
        track_mock_time = MagicMock()

        if "trackPos" in selector:
            track_mock_number.nth.return_value.text_content.return_value = "1"
            track_mock_number.count.return_value = 1
            return track_mock_number
        elif "trackTitle" in selector:
            track_mock_name.nth.return_value.text_content.return_value = "Track 1"
            track_mock_name.count.return_value = 1
            return track_mock_name
        elif "duration" in selector:
            track_mock_time.nth.return_value.text_content.return_value = "3:45"
            track_mock_time.count.return_value = 1
            return track_mock_time
        raise ValueError(f"Unexpected selector {selector}")

    # Configura o side_effect para mockar diferentes seletores
    def mock_locator(selector):
        if "Label" in selector:
            return mock_record_label(selector)
        elif "Style" in selector:
            return MagicMock(all=lambda: mock_styles(selector))
        elif selector == "#release-tracklist table tbody tr":
            return mock_tracklist(selector)
        elif "trackPos" in selector or "trackTitle" in selector or "duration" in selector:
            return mock_tracks(selector)
        raise ValueError(f"Unexpected selector {selector}")

    mock_page.locator.side_effect = mock_locator

    # Executa o teste
    album_info = scrape_album_info("https://www.discogs.com/album1")
    assert album_info["record_label"] == "Awesome Records"
    assert len(album_info["styles"]) == 2
    assert "Rock" in album_info["styles"]
    assert "Alternative" in album_info["styles"]
    assert len(album_info["tracks"]) == 1
    assert album_info["tracks"][0]["name"] == "Track 1"
    assert album_info["tracks"][0]["time"] == "3:45"
