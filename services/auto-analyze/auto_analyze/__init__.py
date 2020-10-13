# Copyright © 2020 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""The service that analyizes an array of names."""
# This is important as this will add modules purporting to be Flask modules for later use by the extension.
# Without this, Flask-SQLAlchemy may not work!
import quart.flask_patch
# Thanks!

import asyncio
import os


from quart import Quart, jsonify, request
import config

from namex import models
from namex.models import db, ma
from .analyzer import auto_analyze

# Set config
QUART_APP = os.getenv('QUART_APP')


def create_app(run_mode=os.getenv('FLASK_ENV', 'production')):
    print('CREATING APPLICATION')
    quart_app = Quart(__name__)
    quart_app.config.from_object(config.CONFIGURATION[run_mode])

    db.init_app(quart_app)
    ma.init_app(quart_app)

    @quart_app.after_request
    def add_version(response):
        os.getenv('OPENSHIFT_BUILD_COMMIT', '')
        # response.headers["API"] = 'NameX/{ver}'.format(ver=run_version)
        return response

    register_shellcontext(quart_app)

    return quart_app


def register_shellcontext(quart_app):
    """Register shell context objects."""
    def shell_context():
        """Shell context objects."""
        return {
            'app': quart_app,
            # 'jwt': jwt,
            'db': db,
            'models': models
        }

    quart_app.shell_context_processor(shell_context)


app = create_app()


@app.route('/', methods=['POST'])
async def private_service():
    """Return the outcome of this private service call."""
    json_data = await request.get_json()
    vector1_dist = json_data.get("vector1_dist")
    vector1_desc = json_data.get("vector1_desc")
    list_name = json_data.get("list_name")
    dict_substitution = json_data.get("dict_substitution")
    dict_synonyms = json_data.get("dict_synonyms")

    result = await asyncio.gather(
        *[auto_analyze(name, list_name, vector1_dist, vector1_desc, dict_substitution, dict_synonyms) for name in json_data.get('names')]
    )
    return jsonify(result=result)


if __name__ == "__main__":
    app.run(port=7000, host='localhost')

"""
Test with this:
curl -X POST -H "Content-Type: application/json" --data '{"names": ["something","whatever","description","body"] }' localhost:7000
"""
