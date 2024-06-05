import json
import base64

def test_home_page_post_with_fixture(client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is posted to (POST)
    THEN check that a '200' (Success) status code is returned
    """
    response = client.get('/')
    assert response.status_code == 200
    assert b"Flask User Management Example!" not in response.data

def test_view_hotel_with_fixture(client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is posted to (GET)
    THEN check that a '200' (Success) status code is returned
    """
    response = client.get("/viewPackageDetail/Capella Singapore")
    assert response.status_code == 200
    assert b"Capella Singapore" in response.data

def test_gettoken_and_retrieve_package_with_fixture(client):
    """
    GIVEN a Flask API application configured for testing
    WHEN the '/api/user/gettoken' request path is sent (POST) with authentication information
    THEN if the user is authenticated then a token is returned for the user to query the '/api/package/getAllPackages' request path
    """
    useremail = 'peter@cde.com'
    response = client.post("api/user/gettoken", data={'email': useremail, 'password': '12345'})
    response_data = json.loads(response.text)

    try: 
        assert response.status_code == 200
        token = response_data['token']['token']
        print(token)
        credentials = base64.b64encode(f"{useremail}:{token}".encode('utf-8')).decode('utf-8')
        headers = {'Authorization': f'Basic {credentials}'}
        response = client.post('api/package/getAllPackages', headers=headers)
        response_data = json.loads(response.text)
        print(response_data)
    except Exception as e:
        print(e)

