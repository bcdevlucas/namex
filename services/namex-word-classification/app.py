import logging

import word_classification


# Leave this as DEBUG for now.
logging.basicConfig(level=logging.DEBUG)

# Listen on all interfaces, and the catalog Python container expects the application to be on 8080.
application = word_classification.create_app()
if __name__ == '__main__':
    application.run(host='0.0.0.0', port=8091, debug=True)
