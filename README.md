# PISTIS Factory Data Storage API

The Factory Data Storage API is a service developed for PISTIS.

## Table of Contents

***

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Deployment](#deployment)
4. [Maintainer](#maintainer) 
5. [License](#license)


## Prerequisites

***

*  [Docker](https://www.docker.com/) >= 20

Not mandatory, but useful tools:

 * Docker Desktop
 * Pgadmin
 * Postman

 ## Installation

***

1. Build docker image

```
docker build -t assetstore .

```

2. Run docker compose

```
docker-compose up

```

## Deployment

***

Deployment should be done using [Docker](https://www.docker.com/) containers. 
Changes to the `master` and `develop` branch are deployed automatically.
View the `.gitlab-ci.yml` file for details.

## Maintainer

***

[Sangeetha Reji](mailto:sangeetha.reji@fokus.fraunhofer.de)

## License

***

[Apache 2.0](http://www.apache.org/licenses/LICENSE-2.0)