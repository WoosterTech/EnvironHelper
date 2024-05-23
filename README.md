# EnvironHelper

## Description

Command line tool to create a .env file from a settings.py file.

## Installation

### From Source

1. Clone the repository.
    - `git clone https://github.com/WoosterTech/EnvironHelper.git`
2. Install the dependencies.
    - This project uses [Poetry](https://python-poetry.org/)
    - For development: `poetry install --with dev`
        - optionally include `test` as well
    - Otherwise: `poetry install`
3. See [Usage](#usage)

## Usage

Syntax is:

```bash
environhelper -s settings.py -o .env
```

If no options are specified it will use the default as shown above.

## Contributing

Contributions are welcome! Please follow the guidelines outlined in [Contributing](CONTRIBUTING.md).

## License

This project is licensed under the [MIT License](LICENSE).

## Contact

- Karl Wooster
- <karl@woostertech.com>
- <https://woostertech.com>
