def test_root_page_has_swaggerui(client):
    rv = client.get('/')
    assert b'Synonyms API' in rv.data
