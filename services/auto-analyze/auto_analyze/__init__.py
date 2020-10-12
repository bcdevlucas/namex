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
import asyncio
import os

from quart import Quart, jsonify, request

from .analyzer import auto_analyze

from nltk.stem import PorterStemmer
porter = PorterStemmer()

STEM_W = 0.85
SUBS_W = 0.65
OTHER_W = 3.0

EXACT_MATCH = 1.0
HIGH_SIMILARITY = 0.85
MEDIUM_SIMILARITY = 0.71
MINIMUM_SIMILARITY = 0.66

HIGH_CONFLICT_RECORDS = 20

app = Quart(__name__)

# Set config
QUART_APP = os.getenv('QUART_APP')


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
    app.run()


"""
Test with this:
curl -X POST -H "Content-Type: application/json" --data '{"names": ["something","whatever","description","body"] }' localhost:7000
"""
