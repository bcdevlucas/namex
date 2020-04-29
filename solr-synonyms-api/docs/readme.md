
# Solr Synonyms API

This web service provides a ReST API to the synonyms used by Solr. The initial functionality is limited to querying a
term to determine what synonym lists it appears in.

#### Flask Secret Key

This application requires a Flask `SECRET_KEY` to do secure cookie hashing. Never commit keys to the repository, and
never use a key in more than one namespace. The application deployment will read the key from an OpenShift secret. In a
Python console:

```
>>> import os, binascii

>>> binascii.hexlify(os.urandom(24))
b'[big_long_key_in_hex]'
```

Copy the `big_long_key_in_hex` and create a secret in OpenShift (make sure you're in the right project):

```
C:\> oc create secret generic solr-synonyms-api --from-literal=flask-secret-key=[big_long_key_in_hex]
```

#### Deficiencies - Code

1. Authorization is missing, but it's currently a read-only web service
2. Configure proper logging
3. Set the host in app.py to 0.0.0.0 but link in PyCharm doesn't work (use localhost)
4. Add version numbers to requirements.txt
5. Fix the warning for the dotenv import in config.py
6. Fix desktop to run on port 8080, not 5000


#### Re-building the Swagger Client using Swagger Hub

These are the manual build steps for re-building the Swagger Client. We will eventually move to a solution that is more
automated, using the swagger-codegen project to generate our code instead of SwaggerHub.

##### Pre-requisites:

- You will need a SwaggerHub account. There is a free tier.
- You will need to fork and clone the Synonyms API Client project locally.
  
    https://github.com/bcgov/namex-synonyms-api-py-client

##### Steps:

1. Modify/create new endpoint in solr-synonyms-api.
2. Run solr-synonyms-api from your local machine (localhost). 

    1. Stop the API first if it's already started.
    2. Click the link in the console output to the Swagger Docs for the API. 
    
    ```http://localhost:your-port>```

3. Click on the link at the left-up corner under Synonyms API header pointing to the JSON spec for the API.
    
    http://localhost:5002/api/v1/swagger.json
    
4. Open up SwaggerHub in your browser and select your API project.
    
    https://app.swaggerhub.com
   
    - If you haven't already created a new Project, create one for the API.

5. Update the API project.
   
    - Copy the content of swagger.json from Step 3 and copy it into the API editor (the big black text area).
    - Make sure the following three lines are at the TOP of the file:
    
    ```
    swagger: '2.0'
    host: solr-synonyms-api.servicebc-ne-dev.svc:8080
    schemes: [http, https]
    ```
    
    - Remove any duplicate parameters.
    - Save the API project in SwaggerHub.
    
6. Export auto-generated code. Toward the top right of the project page, there is an Export menu. 
    1. Click Export, then choose Download API > Json Resolved. 
    2. Click Export, then choose Download Client SDK > Python.

7. Unzip the downloaded files ```swagger-client-generated, python-client-generated```.
8. Copy the following into the root of your Synonyms API Client project:
    
    1. From ```swagger-client-generated``` copy ```swagger.json ```
	2. From ```python-client-generated``` copy everything except:
	  
	  ```
	  .gitignore
	  .swagger-codegen
	  .travis.yml
	  .swagger-codegen-ignore
	  ```
	  
9. In your Synonyms API Client project search and replace:  

    ```solr-synonyms-api-servicebc-ne-dev.svc:8080``` with ```localhost:<your-port>```

10. Commit your the changes and push.

#### Using the Swagger Client in Your Application

1. Just include the package in your requirements:

    ```git+https://github.com/bcgov/namex-synonyms-api-py-client.git#egg=swagger_client```

2. Import the client like any other package:
    
    ```from swagger_client import SynonymsApi```
