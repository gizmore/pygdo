# IBDES v0.1

IBDES is an acronym for International Bot Data Exchange Standard

It is a simple rule to exchange data between different communication network architectures.

Currently it is basically to authenticate a sending user and a target channel for a cross network message.

There is no real auth algorithm, because IBDES should only be transferred over unforgeable connections/channels.

The protocol is intentionally small. The current implementation does not
negotiate a version, define escaping, or provide encryption.


## Message envelope

The logical envelope is:

```text
target_channel{optional_server_name} sender_name{server_name}  payload
```

Grammar:
```
message := target SP sender SP payload
target  := channel ["{" server "}"]
sender  := name "{" server "}"
```

if the optional server name is omitted, it is the same server as the sender's.


### Channel message

The channel starts with `#` and identifies the channel where the message has been sent to.

```text
#general gizmore{mogwai} hello everyone
```

You prefix a `#` when rendering a channel name that does not already
have it.

On IRC it is possible to have channel names that start with `##`.

There are special `###` rooms that denote a physical location: `###House_Room`.


### Private message

The reserved channel name `#-` identifies a user-directed response to whom received the message.


```text
#- mira{mogwai} gizmore: here are your command results.
```


----


----





# TCP Connector example (move to gdo/net somewhere?)


## Session lifecycle

After accepting a connection, PyGDO creates an anonymous user named
`TCP_<user-id>` and a session channel for that user. The peer address is stored
as the user's display name.

The `tcpauth` command can authenticate the session using positional `login`
and `password` parameters. On successful authentication, the session's user,
session object, and channel are replaced with the authenticated user's
context. Only one TCP session may represent a given authenticated user at a
time.

When the connection closes, PyGDO removes that session and announces the user
leaving the server.


## Commands and responses

Client input is passed to PyGDO's normal message parser. A command must use the
server or channel trigger, for example:

```text
$help
```

The response is returned in an IBDES envelope. Non-command input is accepted by
the transport but is not executed by `Message.execute()` unless it begins with
the active trigger.

## Security considerations

IBDES v0.1 does not define TLS, encryption, or a key exchange. The TCP listener
must therefore be restricted to a trusted network or protected by an external
secure transport. Authentication credentials sent with `tcpauth` require the
same care as any other plaintext application protocol.

## Implementation reference

The reference implementation is:

- [`gdo/net/connector/TCP.py`](../gdo/net/connector/TCP.py)
- [`gdo/net/method/tcpauth.py`](../gdo/net/method/tcpauth.py)
- [`gdo/base/Message.py`](../gdo/base/Message.py)
