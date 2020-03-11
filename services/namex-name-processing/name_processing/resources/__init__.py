from flask_restplus import Api

authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    }
}

api = Api(
    title='BC Registries Namex: Name Processing API',
    version='1.0',
    description='The Name Processing API Service for the Names Examination System',
    prefix='/api/v1',
    security=['apikey'],
    authorizations=authorizations)