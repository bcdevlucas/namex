def test_root_page_has_swaggerui(client):
    rv = client.get('/')
    assert b'Word Classification API' in rv.data
