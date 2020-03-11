from flask_restplus import Api

authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    }
}

api = Api(
    title='BC Registries Namex: Word Classification API',
    version='1.0',
    description='The Word Classification API Service for the Names Examination System',
    prefix='/api/v1',
    security=['apikey'],
    authorizations=authorizations)