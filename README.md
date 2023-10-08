# NYU DevOps Fall 2023 : Shopcarts

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)

This is the repo for the Shopcarts API


## Contents

The project contains the following:

```text
.gitignore          - this will ignore vagrant and other metadata files
.flaskenv           - Environment variables to configure Flask
.gitattributes      - File to gix Windows CRLF issues
.devcontainers/     - Folder with support for VSCode Remote Containers
dot-env-example     - copy to .env to use environment variables
requirements.txt    - list if Python libraries required by your code
config.py           - configuration parameters

service/                   - service python package
├── __init__.py            - package initializer
├── models.py              - module with business models
├── routes.py              - module with service routes
└── common                 - common code package
    ├── error_handlers.py  - HTTP error handling code
    ├── log_handlers.py    - logging setup code
    └── status.py          - HTTP status constants

tests/              - test cases package
├── __init__.py     - package initializer
├── test_models.py  - test suite for business models
└── test_routes.py  - test suite for service routes
```

## Running the tests

Run the tests using `green`. The goal is to have 95% coverage with 100% passing tests.

```bash
$ green
```

## Running the service

The project uses honcho which gets it's commands from the Procfile. To start the service simply use:

```bash
$ honcho start
```

You should be able to reach the service at: http://localhost:8000. The port that is used is controlled by an environment variable defined in the .flaskenv file which Flask uses to load it's configuration from the environment by default.

## Information about this repo

### Models

##### `Shopcart`

| `Name`      | `Comment`             | `Data type` |
| ----------- | --------------------- | --------------- |
| id | Unique ID for the shopcart. | uuid         |
| items | List of items in the shopcart | `CartItem`         |

##### `CartItem`

| `Name`      | `Comment`             | `Data type` |
| ----------- | --------------------- | --------------- |
| id | Unique ID for the item. | uuid         |
| shopcart_id | ID of the shopcart it belongs to | uuid       |
| product_name | Name of the product | string       |
| quantity | Quantity of the product in the cart | Number       |
| price | Price of the product when it was added | Float       |

### Routes

```bash
$ flask routes

Endpoint          Methods  Rule
----------------  -------  -----------------------------------------------------
index             GET      /

list_shopcarts     GET      /???
create_shopcarts   POST     /???
get_shopcarts      GET      /???/<???>
update_shopcarts   PUT      /???/<???>
delete_shopcarts   DELETE   /???/<???>

list_cart_items    GET      /???/<int:???>/???
create_cart_items  POST     /???/<???>/???
get_cart_items     GET      /???/<???>/???/<???>
update_cart_items  PUT      /???/<???>/???/<???>
delete_cart_items  DELETE   /???/<???>/???/<???>
```

## License

Copyright (c) John Rofrano. All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the NYU masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by *John Rofrano*, Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.