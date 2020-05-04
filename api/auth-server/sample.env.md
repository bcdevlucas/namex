#### Flask app settings
```
export FLASK_APP="wsgi.py"
export FLASK_RUN_PORT=5000
export SECRET="some md5 hash local dev"
export APP_SETTINGS="dev"
export DATABASE_URL="postgresql://postgres@localhost"
export DATABASE_HOST="localhost"
export DATABASE_NAME="namex-sample"
export DATABASE_USERNAME="postgres"
export DATABASE_PASSWORD=""
export DATABASE_PORT="5432"
export FLASK_ENV=development
```

#### Print settings to console
```
echo FLASK_APP=$FLASK_APP
echo SECRET=$SECRET$APP_SETTINGS
echo APP_SETTINGS=$APP_SETTINGS
echo DATABASE_URL=$DATABASE_URL
```

#### OpenID Connect settings for BC Gov SSO and the ServiceBC realm
```
export JWT_OIDC_WELL_KNOWN_CONFIG=""
export JWT_OIDC_AUDIENCE=""
export JWT_OIDC_CLIENT_SECRET=""
```
##### Specify the encryption algorithm to use for OpenID Connect
##### eg. JWT_OIDC_ALGORITHMS="RS256"
```
export JWT_OIDC_ALGORITHMS=""

echo JWT_OIDC_WELL_KNOWN_CONFIG=$JWT_OIDC_WELL_KNOWN_CONFIG
```
#### OpenID Connect settings for local development using the dockerized local authentication server (Keycloak)
##### Run 'docker-compose up' in the <namex-repo-root>/auth-server directory to launch a Keycloak authentication server instance
```
export LOCALAUTH_JWT_OIDC_WELL_KNOWN_CONFIG="https://<keycloak-server-url>/auth/realms/<namex-local>/.well-known/openid-configuration"
export LOCALAUTH_JWT_OIDC_AUDIENCE="NameX-Local-Dev"
export LOCALAUTH_JWT_OIDC_CLIENT_SECRET=""
```
#### Specify the encryption algorithm to use for OpenID Connect
##### eg. JWT_OIDC_ALGORITHMS="RS256"
```
export LOCALAUTH_JWT_OIDC_ALGORITHMS="RS256"

echo JWT_OIDC_WELL_KNOWN_CONFIG=$JWT_OIDC_WELL_KNOWN_CONFIG
```
#### Configure Synonyms API
```
export SOLR_BASE_URL="http://localhost:54325"
export SOLR_SYNONYMS_API_URL="http://localhost:5555/api/v1/synonyms"
```
############ TEST ENVIRONMENT SETTINGS #########################

##### Test Postgres database (local) used for DESTRUCTIVE pytests
##### Make sure you are pointing to your local namex test database, 
##### you'll want to use a different database from development!
```
export DATABASE_TEST_USERNAME="postgres"
export DATABASE_TEST_PASSWORD=""
export DATABASE_TEST_NAME="namex-local-blank"
export DATABASE_TEST_HOST="localhost"
export DATABASE_TEST_PORT="5432"
```