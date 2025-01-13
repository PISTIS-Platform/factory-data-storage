# PISTIS Factory Data Storage

The Factory Data Storage is a service developed for PISTIS. It provides storage and access to a Postgres database to perform CRUD operations on datasets. It is populated with raw datasets when a Job Confugurator executes the Data Registration workflow and later during the data enrichment process, these datasets are transformed into SQL tables with table schema conforming to properties from the PISTIS Data Model.

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
docker build -t datastorage .

```

2. Run docker compose

```
docker-compose up

```

## Maintainer

***

[Sangeetha Reji](mailto:sangeetha.reji@fokus.fraunhofer.de)

## License

***

[Apache 2.0](http://www.apache.org/licenses/LICENSE-2.0)