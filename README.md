# PyServerClient

Simple client-server command line interpreter powered by __Python 3__.

## Usage

First, run server. Open a terminal window and write:

```
python server.py config.cfg
```

Then open another terminal window and write:

```
python client.py config.cfg
```

In _config.cfg_ file you must specify host and port of server. Here is an example:

```
[general]

host = 127.0.0.1
port = 9090

```

## Commands

Only four commands are implemented out of the box:

- **hello** : Shows a welcome message.
- **reply** : Repeats input like a parrot.
- **test** : Show "TESTING".
- **exit** : Disconnect from server.
- **quit** : Shut down the server and exit.


## Create new commands

For create new commands you only need create a class that inherits from the **Command** class. The name of the new class must be of the form "CamelCase" followed by the word "Command". For example:

```
class OneTwoTreeCommand(Command):
...

```
Creates command:

```
one_two_tree [ args ...]
```
Arguments are passed to command as string and stored in **self.m** attribute.
