
# Talao.co API Demo Members Base v0.1

This is a demo for talao.co's API

Use Case: A group which has a base of members (companies), wishes to propose to its members to be "certified" on the Blockchain by third party companies for which they have provided services. The certificates are added to the profile of the members on the portal of the group. On this portal you can search for companies according to certified competence criteria.

## Documentation
https://talao.readthedocs.io/en/latest/api/
## Installation

Clone this repository : 

```bash
git clone https://github.com/AlexLeclerc102/talao_api_use_case_2.git
```

## Requirements

[Flask](https://flask.palletsprojects.com/en/1.1.x/) : `$ pip install Flask`

## Usage

You will need to have a client_id and a client_secret and store them in a json file named client_credentials.json.

If you don't have them contact contact@talao.io

Launch using:

```bash
$ export FLASK_APP=demo
$ export FLASK_DEBUG=1
$ flask run
```

By default this app will launch on 127.0.0.1:5000

## License

See the [LICENSE](https://github.com/AlexLeclerc102/talao_api_use_case_2/blob/master/LICENSE) file for license rights and limitations (MIT).

