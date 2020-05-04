#### OpenID Connect settings for a production realm
export JWT_OIDC_WELL_KNOWN_CONFIG=""
export JWT_OIDC_AUDIENCE=""
export JWT_OIDC_CLIENT_SECRET=""
##### Specify the encryption algorithm to use for OpenID Connect
##### eg. JWT_OIDC_ALGORITHMS="RS256"
export JWT_OIDC_ALGORITHMS=""

echo JWT_OIDC_WELL_KNOWN_CONFIG=$JWT_OIDC_WELL_KNOWN_CONFIG

#### OpenID Connect settings for local development using the dockerized local authentication server (Keycloak)
##### Run 'docker-compose up' in the <namex-repo-root>/auth-server directory to launch a Keycloak authentication server instance
export LOCALAUTH_JWT_OIDC_WELL_KNOWN_CONFIG="https://<keycloak-server-url>/auth/realms/<namex-local>/.well-known/openid-configuration"
export LOCALAUTH_JWT_OIDC_AUDIENCE="NameX-Local-Dev"
export LOCALAUTH_JWT_OIDC_CLIENT_SECRET=""
##### Specify the encryption algorithm to use for OpenID Connect
##### eg. JWT_OIDC_ALGORITHMS="RS256"
export LOCALAUTH_JWT_OIDC_ALGORITHMS="RS256"

echo JWT_OIDC_WELL_KNOWN_CONFIG=$JWT_OIDC_WELL_KNOWN_CONFIG