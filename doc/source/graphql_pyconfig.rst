GraphQL PysuiConfiguration
""""""""""""""""""""""""""

PysuiConfiguration is the replacement for the legacy SuiConfig and this new class should be
used when creating a new GraphQL clients. This new configuration scheme is also leveraged
by the GraphQL SuiTransaction.


General
=======
Up until now, pysui relied on the presence of ``~/.sui`` and it's constituent configuration elements including
``client.yaml``, ``sui.keystore``, and ``sui.aliases`` which were all encapsulated by SuiConfig. While SuiConfig
supported some maniplations (i.e. adding new keys, alias management, etc.) it fell short of a more robust management
strategy. In addition, the code itself did not gracefully age with the advent of Sui GraphQL RPC. Until Mysten
eliminates JSON RPC, SuiConfig may continue to be used with the JSON RPC clients.

PysuiConfiguration persists its own configuratoin (default to ``~/.pysui``) and offers more flexibility when it
comes to configuration management. Amongst other things:

#. It does not presume it's configuration is persisted to a fixed location (configurable)
#. It supports programmatic switching between it's primary components (see Anatomy below)
#. It has a smaller code base that, when legacy JSON RPC support is removed, has a smaller memory footprint
#. And more...

Anatomy of PysuiConfiguration
=============================
The primary data model for PysuiConfiguration is a series of related ``dataclasses`` objects:

* The root data model is ``PysuiConfigModel`` which is a member of PysuiConfiguration.
    It manages one or more...

    * ``ProfileGroup``, or group for short, encapsulates unique environment configurations.
        Example configuration may include "sui_json_config" (reserved), "sui_gql_config" (reserved)
        or "user" (reserved). New groups may be created by the developer. Its construct includes,
        all of which are configurable:

        * One or more ``Profile``, or profile, a named object containing individual urls for communicatinhg to Sui with.
        * Associated keys, aliases and addresses
        * Identifies an active profile
        * Identifies an active address

PysuiConfiguration
==================

PysuiConfiguration is the primary object to interact with when managing or using the underlying groups and
profiles. However; it is import to understand the initial setup before using it as part of the GraphQL Clients
and the arguments you can pass to the constructor rely on that understanding.

First time instantiation
------------------------
The first time PysuiConfiguration is used it will look for the ``PysuiConfig.json`` file in the
default configuration folder ``~/.pysui`` unless that folder path is overriden with
the argument ``from_cfg_path``. If the configuration file is found it is loaded, otherwise it initializes
a new configuration file with initial groups and their contents.

If Sui binaries installed
~~~~~~~~~~~~~~~~~~~~~~~~~
Three groups will be created and initially populated:

    **sui_json_config** - This group and it's profiles will be populated from the contents of ``~/.sui/sui_config`` from the
    files ``client.yaml``, ``sui.keystore`` and ``sui.aliases``.

    **sui_gql_config** - This group and will create four profiles, each one with a ``url`` pointing to Mysten's free
    GraphQL nodes. It will also copy the keys, aliases and addresses from the ``sui_json_config`` group.

    **user** - Even though you may create your own groups this group is initially created as a convenience and begins
    empty.

The location of the ``sui`` binary will be captured, if present, enabling Move project compiling.

If Sui binaries not installed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**sui_gql_config** and **user** will be created however; **sui_gql_config** will be populated with a new
active address and keypair (ed25519), an alias of 'Primary', and will make 'testnet' profile active.

The location of the ``sui`` binary will be captured, if present, enabling Move project compiling.

Changing PysuiConfig Active
===========================
Defaults of what is considered 'active' is whatever was last persisted but can be
changed at runtime.

At PysuiConfig Construction
----------------------------

* from_cfg_path (str) - Controls where PysuiConfiguration reads/writes ``PysuiConfig.json``
* group_name (str) - Sets the ``active_group`` for the session, for example:

.. code-block:: python
    :linenos:

    # Set group to builtin Sui's GraphQL RPC group
    cfg = PysuiConfiguration(group_name=PysuiConfiguration.SUI_GQL_RPC_GROUP )

    # Set group to builtin 'user' group
    cfg = PysuiConfiguration(group_name=PysuiConfiguration.SUI_USER_GROUP)

    # Set group to other user defined group
    cfg = PysuiConfiguration(group_name="Primary Group")

* profile_name (str) - Sets which profile is active of the current ``active_group``. It is the equivalent of ``sui client switch --env``:

.. code-block:: python
    :linenos:

    # Set group to builtin Sui's GraphQL RPC group
    cfg = PysuiConfiguration(group_name=PysuiConfiguration.SUI_GQL_RPC_GROUP, profile_name="mainnet" )

* address or alias (str) - Sets which Sui address is active using either and explicit address or an alias. It is the equivalent of ``sui client switch --address``:

.. code-block:: python
    :linenos:

    # Set group to builtin Sui's GraphQL RPC group
    cfg = PysuiConfiguration(alias="Primary")

* persist (bool) - Controls whether to persist any changes made above to ``PysuiConfig.json``. If not set to True the changes are in memory only.

After Construction
------------------
Changing what is active after PysuiConfiguration has been constructed is done through the ``PysuiConfig.make_active(...)`` method.
It takes the same arguments as the constructor with the exception of the ``from_cfg_path``.

**NOTE** If changing the active group and or profile after you've constructed a client will require creating a new
client. Changing the active address will not require recreating a client.

.. code-block:: python
    :linenos:

    # Set group to builtin Sui's GraphQL RPC group
    cfg = PysuiConfiguration(group_name=PysuiConfiguration.SUI_GQL_RPC_GROUP, profile_name="mainnet" )
    client = SyncGqlClient(pysui_config=cfg)

    # Changing active profile
    client.config.make_active(profile_name="testnet")
    client = SyncGqlClient(pysui_config=cfg)

Rebuilding from ``client.yaml``
===============================
Depending on use of the Sui command line ``sui client ...`` it may be desierable to reconstruct the PysuiConfiguration
``sui_json_config`` group again or for the first time.

**WARNING** This is a destructive call that will delete the existing ``sui_json_config`` group if it exists as well as
the ``sui_gql_config`` if you so choose.

The following shows the method defaults

.. code-block:: python

    cfg.rebuild_from_sui_client(rebuild_gql: bool = False,persist: bool = True)


Bottom Up Changes
=================

Profile
-------
A Profile is the equivalent of what sui CLI calls 'env' (a.k.a. environment). It encapsulate
a unique name and relevant url information such as the primary endpoint, faucet and faucet status urls.

**WARNING** All methods support an optional ``persist`` flag argument. Keep in mind that this will persist *any*
changes that may have occured previouos where the ``persist`` flag was set to False. If you want changes to be
ephemeral only set this to False.

The following methods are available on the PysuiConfiguration instance.

Creating a new Profile
~~~~~~~~~~~~~~~~~~~~~~
Create a new profile in an explicit group or, default, the active group. Will raise an exception if the
explicit group *does not* exist, or the profile (with profile_name) *does* exist.

.. code-block:: python

    def new_profile(
        self,
        *,
        profile_name: str,
        url: str,
        faucet_url: Optional[str] = None,
        faucet_status_url: Optional[str] = None,
        make_active: Optional[bool] = False,
        in_group: Optional[str] = None,
        persist: Optional[bool] = True,
    )

Update Existing
~~~~~~~~~~~~~~~
Update an existing profile in an explicit group or, default, the active group. Will raise an exception if the
explicit group or the profile (with profile_name) *does not* exist.


.. code-block:: python

    def update_profile(
        self,
        *,
        profile_name: str,
        url: str,
        faucet_url: Optional[str] = None,
        faucet_status_url: Optional[str] = None,
        in_group: Optional[str] = None,
        persist: Optional[bool] = True,
    )

ProfileGroup
------------
In addition to Profiles the ProfileGroup manages the addresses, aliases for addresses and private keys.

**WARNING** All methods support an optional ``persist`` flag argument. Keep in mind that this will persist *any*
changes that may have occured previouos where the ``persist`` flag was set to False. If you want changes to be
ephemeral only, set this to False.

The following methods are available on the PysuiConfiguration instance.

Creating a new Keypair
~~~~~~~~~~~~~~~~~~~~~~
Create a new keypair of type and add to an explict group or, default, the active group. Will raise an exception
if the explicit group does *not* exist or the optional alias *does* exist.

Returns the mnemonic string and address string upon success.

.. code-block:: python

    def new_keypair(
        self,
        *,
        of_keytype: SignatureScheme,
        in_group: Optional[str] = None,
        word_counts: Optional[int] = 12,
        derivation_path: Optional[str] = None,
        make_active: Optional[bool] = False,
        alias: Optional[str] = None,
        persist: Optional[bool] = True,
    )

Adding Keys to Greoup
~~~~~~~~~~~~~~~~~~~~~
If you do not want to generate new keys you can import existing keys into a group.

.. code-block:: python

    def add_keys(
        self,
        *,
        key_block: list[dict[str, str]],
        in_group: Optional[str] = None,
        persist: Optional[bool] = True,
    ) -> list[str]

The ``key_block`` is a list of dictionaries containing the base64 or bech32 keystring and an optional
alias, for example:

.. code-block:: python

    def populate_keys(cfg:PysuiConfiguration):
        """Add some keys to existing group."""
        block=[
            {"key_string":"ANlIGCd0ZdkpLGEsRTDzRF4q96ZQAJfuaU+G0/L93+I2","alias":"Foo"},
            {"key_string":"AJj3zoXJMl2Eax5vw29na0w4DxO6PrMl3Zrrf1X/b9z4","alias":"Bar"},
            {"key_string":"AATnunevLZEyy9MFNQAWRESwhMmJucte+Gh5WjSOXC58","alias":None},
        ]
        addresses = cfg.add_keys(key_block=block, persist=False)

If no alias is provided, one will be generated. Keystrings and aliases are checked for collisions.
If successful, addresses for the added keys are returned.

Creating a new Group
~~~~~~~~~~~~~~~~~~~~
Create a new group will raise an exception if the group_name group *does* exist.

.. code-block:: python

    def new_group(
        self,
        *,
        group_name: str,
        profile_block: list[dict[str, str]],
        key_block: list[dict[str, str]],
        active_address_index: int,
        make_group_active: Optional[bool] = False,
        persist: Optional[bool] = True,
    ) -> list[str]

The following is an example of creating a fictional group:

.. code-block:: python

    def add_new_group(cfg: PysuiConfiguration):
        """."""
        key_blocks = [
            {"key_string": "ANlIGCd0ZdkpLGEsRTDzRF4q96ZQAJfuaU+G0/L93+I2", "alias": "Foo"},
            {"key_string": "AJj3zoXJMl2Eax5vw29na0w4DxO6PrMl3Zrrf1X/b9z4", "alias": "Bar"},
            {"key_string": "AATnunevLZEyy9MFNQAWRESwhMmJucte+Gh5WjSOXC58", "alias": None},
        ]
        profile_blocks = [
            {
                "profile_name": "dev_only",
                "url": "https://dev.fictional.com",
                "faucet_url": None,
                "faucet_status_url": None,
                "make_active": False,
            },
            {
                "profile_name": "test_only",
                "url": "https://test.fictional.com",
                "faucet_url": None,
                "faucet_status_url": None,
                "make_active": True,
            },
        ]
        addies = cfg.new_group(
            group_name="emphemeral_group",
            key_block=key_blocks,
            profile_block=profile_blocks,
            active_address_index=0,
            make_group_active=True,
            persist=False,
        )
        for addy in addies:
            print(f"Address: {addy}")
