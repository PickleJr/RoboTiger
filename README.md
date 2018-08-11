# RoboTiger
A Manager/Admin bot that helps run the TigerLan Discord server.

## To set up the bot for yourself
### Requirements
* Python 3.6
* Pipenv

### Set up
1. Clone this repository
2. run `pipenv install --python 3.6`
3. Create a `db` folder in the root of the project, and then create an empty `index.json`.
4. Create a copy of `config.example.ini`, name that copy `config.ini`, and paste the copy into the root of the project.
5. Update the contents of `config.ini` to the relevant information of your bot.

### Run the bot
This assumes that you have a command prompt opened at the root of your project.
1. Run `pipenv run python index.py`
Alternatively you can enter the pipenv shell and run it from there:
1. `pipenv shell`
2. `python index.py`

## To contribute
1. Fork the repository onto your own account.
2. Follow the setup instructions, but use your own fork instead of this repo.
3. Create a new branch in your fork.
4. Work on whatever changes you wanted to do.
5. Pull from this repo to ensure that your fork is up-to-date.
6. Submit a pull request and we'll go from there. :)

See [this link](https://help.github.com/articles/fork-a-repo/) or get in touch with me if you have any questions about contributing.
Don't be afraid to open an issue!