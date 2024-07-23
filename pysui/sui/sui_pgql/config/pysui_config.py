#    Copyright Frank V. Castellucci
#    SPDX-License-Identifier: Apache-2.0

# -*- coding: utf-8 -*-

"""Pysui Configuration."""


import platform
from pathlib import Path
from typing import Optional

from pysui.abstracts.client_keypair import SignatureScheme
from pysui.sui.sui_pgql.config.confmodel import PysuiConfigModel
import pysui.sui.sui_pgql.config.confgroup as cfg_group


class PysuiConfiguration:
    """pysui configuration class."""

    SUI_JSON_RPC_GROUP: str = "sui_json_config"
    SUI_GQL_RPC_GROUP: str = "sui_gql_config"
    SUI_USER_GROUP: str = "user"

    def __init__(
        self,
        *,
        from_cfg_path: str = None,
        group_name: Optional[str] = "sui_gql_config",
        profile_name: Optional[str] = None,
        address: Optional[str] = None,
        alias: Optional[str] = None,
        persist: Optional[bool] = False,
    ):
        """PysuiConfiguration initialization.

        :param from_cfg_path: Where to read/write PysuiConfig.json, defaults to '~/.pysui'
        :type from_cfg_path: str, optional
        :param group_name: Sets the active ProfileGroup, defaults to "sui_gql_config"
        :type group_name: Optional[str], optional
        :param profile_name: Sets the active Profile, defaults to None
        :type profile_name: Optional[str], optional
        :param address: Sets the active address, defaults to None
        :type address: Optional[str], optional
        :param alias: Sets the active address via alias name (precedence is address argument), defaults to None
        :type alias: Optional[str], optional
        :param persist: Indicates wheter to persist any changes made above, defaults to False
        :type persist: Optional[bool], optional
        """
        # Get the base configuration folder and profile file
        self._config_root = Path(from_cfg_path or "~/.pysui").expanduser()
        # _ecfgdir = Path(self._config_root).expanduser()
        self._config_file = self._config_root / "PysuiConfig.json"
        # If the primmary path doesn't exist create
        if not self._config_root.exists():
            self._config_root.mkdir()
        # If above, then true else determine
        if not self._config_file.exists():
            # Populate the default profile configuration and write
            self._model: PysuiConfigModel = PysuiConfigModel()
            self._config_file.write_text(self._model.to_json(indent=2))
        else:
            self._model: PysuiConfigModel = PysuiConfigModel.from_json(
                self._config_file.read_text(encoding="utf8")
            )
        # Set up user group if not exist, don't overwrite
        self.model.add_group(
            group=cfg_group.ProfileGroup(self.SUI_USER_GROUP, "", "", [], [], [], []),
            make_active=False,
        )
        # Initialize from sui config if found
        if not self._model.has_group(group_name=self.SUI_JSON_RPC_GROUP):
            self.rebuild_from_sui_client(
                rebuild_gql=not self._model.has_group(group_name=self.SUI_GQL_RPC_GROUP)
            )
        # Make active as per arguments
        self.make_active(
            group_name=group_name,
            profile_name=profile_name,
            address=address,
            alias=alias,
            persist=persist,
        )

    def _write_model(self):
        """Writes out the configuration model."""
        self._config_file.write_text(self.to_json(indent=2))

    def to_json(self, *_cmds, **kwargs) -> str:
        """."""
        return self._model.to_json(**kwargs)

    def rebuild_from_sui_client(
        self,
        *,
        rebuild_gql: bool = False,
        persist: bool = True,
    ):
        """Delete existing JSON SUI_JSON_RPC_GROUP group and regenerate from sui binary configuration."

        :param rebuild_gql: Delete and rebuild the SUI_GQL_RPC_GROUP, defaults to False
        :type rebuild_gql: bool, optional
        :param persist: Persist updated PysuiConfiguration, defaults to True
        :type persist: bool, optional
        """
        # Determine if sui configuration installed
        _scfg = Path("~/.sui/sui_config").expanduser()
        if _scfg.exists():
            # If exists legacy group, remove it
            if self._model.has_group(group_name=self.SUI_JSON_RPC_GROUP):
                self._model.remove_group(group_name=self.SUI_JSON_RPC_GROUP)
            # Determine if sui binaries installed
            if platform.system() == "Windows":
                _bcfg = Path("~/.cargo/bin/sui.exe").expanduser()
            else:
                _bcfg = Path("~/.cargo/bin/sui").expanduser()
            _ = self._model.initialize_json_rpc(
                sui_config=_scfg,
                sui_binary=_bcfg,
                json_rpc_group_name=self.SUI_JSON_RPC_GROUP,
            )
            if rebuild_gql:
                if self._model.has_group(group_name=self.SUI_GQL_RPC_GROUP):
                    self._model.remove_group(group_name=self.SUI_GQL_RPC_GROUP)
                _ = self._model.initialize_gql_rpc(
                    sui_binary=_bcfg,
                    gql_rpc_group_name=self.SUI_GQL_RPC_GROUP,
                    json_rpc_group_name=self.SUI_JSON_RPC_GROUP,
                )

            if persist:
                self._write_model()

    @property
    def model(self) -> PysuiConfigModel:
        """."""
        return self._model

    @property
    def active_group(self) -> cfg_group.ProfileGroup:
        """Return the active group."""
        return self._model.active_group

    @property
    def active_address(self) -> str:
        """Returns the active groups active address."""
        return self.active_group.using_address

    @property
    def active_address_alias(self) -> str:
        """Returns the active groups active address."""
        return self.active_group.active_alias

    @property
    def active_env(self) -> str:
        """Returns the active groups active profile name."""
        return self.active_group.using_profile

    @property
    def url(self) -> str:
        """Returns the active groups active profile url."""
        return self.active_group.active_profile.url

    @property
    def faucet_url(self) -> str:
        """Returns the active groups active profile faucet url."""
        return self.active_group.active_profile.faucet_urls

    @property
    def faucet_status_url(self) -> str:
        """Returns the active groups active profile faucet status url."""
        return self.active_group.active_profile.faucet_status_url

    @property
    def config_path(self) -> str:
        """Return configuration breadcrumb path."""
        _group = self.active_group
        return f"{_group.group_name}.{_group.active_profile.profile_name}"

    def address_for_alias(self, *, alias_name: str) -> str:
        """Return the address for the alias name in current group."""
        return self.active_group.address_for_alias(alias=alias_name)

    def alias_for_address(self, *, address: str) -> str:
        """Return the alias for the address in current group."""
        return self.active_group.alias_for_address(address=address)

    def make_active(
        self,
        *,
        group_name: Optional[str] = None,
        profile_name: Optional[str] = None,
        address: Optional[str] = None,
        alias: Optional[str] = None,
        persist: Optional[bool] = True,
    ):
        """Activate specific aspects of configuration."""
        # Track changes for persist
        _changes: bool = False

        # If group specified and it's not the active
        if group_name and self._model.group_active != group_name:
            # If  it exists and is not already the active group then set it
            if _group := self._model.has_group(group_name=group_name):
                self._model.active_group = group_name
                _changes = True
            else:
                raise ValueError(f"{group_name} does not exist")
        else:
            _group = self.active_group

        # Change profile, checks if it exists
        if profile_name and _group.using_profile != profile_name:
            _group.active_profile = profile_name
            _changes = True

        # Change activte address, checks if exists
        if address and _group.active_address != address:
            _group.active_address = address
            _changes = True
        # Else try alias
        elif alias and _group.active_alias != alias:
            _group.active_alias = alias
            _changes = True

        if _changes and persist:
            self._write_model()

    def keypair_for_address(self, *, address: str, in_group: Optional[str] = None):
        """Returnn the SuiKeyPair for an address."""
        _group = (
            self._model.get_group(group_name=in_group)
            if in_group
            else self.active_group
        )
        return _group.keypair_for_address(address=address)

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
    ) -> tuple[str, str]:
        """Creates a new keypair returning generated passphrase and associated address."""
        # Resolve group
        _group = (
            self._model.get_group(group_name=in_group)
            if in_group
            else self.active_group
        )

        if of_keytype in [
            SignatureScheme.ED25519,
            SignatureScheme.SECP256K1,
            SignatureScheme.SECP256R1,
        ]:
            mnem, new_addy, prf_key, prf_alias = (
                cfg_group.ProfileGroup.new_keypair_parts(
                    of_keytype=of_keytype,
                    word_counts=word_counts,
                    derivation_path=derivation_path,
                    alias=alias,
                    alias_list=_group.alias_list,
                )
            )
            new_addy = _group.add_keypair_and_parts(
                new_address=new_addy,
                new_alias=prf_alias,
                new_key=prf_key,
                make_active=make_active,
            )
            if make_active and _group.group_name != self.active_group.group_name:
                self._model.active_group = _group.group_name
            if persist:
                self._write_model()
            return mnem, new_addy
        raise NotImplementedError(
            f"{of_keytype}: Not recognized as valid keypair scheme."
        )

    def add_keys(
        self,
        *,
        key_block: list[dict[str, str]],
        in_group: Optional[str] = None,
        persist: Optional[bool] = True,
    ) -> list[str]:
        """Add one or more keys to a group. Each dict has k/v:

            {
                "key_string": str # Either a base64 or bech32 private key
                "alias": str     # Optional alias, one will be generated otherwise
            }

        :param key_block: List of key construct dictionaries
        :type key_block: list[dict]
        :param in_group: Group to add new profile, defaults to active_group or excepts if not exists
        :type in_group: Optional[str]
        :param persist: Persist updates to PysuiConfig.json, defaults to True
        :type persist: Optional[bool], optional
        :return: List of addresses derived from keys
        :rtype: list[str]
        """
        _group = (
            self._model.get_group(group_name=in_group)
            if in_group
            else self.active_group
        )

        addies: list[str] = _group.add_keys(keys=key_block)

        if persist:
            self._write_model()

        return addies

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
    ):
        """Adds a new profile to exiting or named group, equivelant of `sui client new-env`.

        :param profile_name: The name of the new profile, exception if exists
        :type porfile_name: str
        :param url: The url reference for the profile
        :type url: str
        :param faucet_url: The faucet url reference for the profile, defaults to None
        :type faucet_url: Optional[str], optional
        :param faucet_status_url: The faucet status url reference for the profile, defaults to None
        :type faucet_status_url: Optional[str], optional
        :param make_active: Sets this as the groups active_profile, defaults to False
        :type make_active: Optional[bool], optional
        :param in_group: Group to add new profile, defaults to active_group or excepts if not exists
        :type in_group: Optional[str], optional
        :param persist: Persist updates to PysuiConfig.json, defaults to True
        :type persist: Optional[bool], optional
        """
        _group = (
            self._model.get_group(group_name=in_group)
            if in_group
            else self.active_group
        )
        _group.add_profile(
            new_prf=cfg_group.Profile(profile_name, url, faucet_url, faucet_status_url),
            make_active=make_active,
        )
        if persist:
            self._write_model()

    def update_profile(
        self,
        *,
        profile_name: str,
        url: Optional[str] = None,
        faucet_url: Optional[str] = None,
        faucet_status_url: Optional[str] = None,
        in_group: Optional[str] = None,
        persist: Optional[bool] = True,
    ):
        """Updates and exiting profile.

        :param profile_name: The name of the existing profile, exception if not exists
        :type porfile_name: str
        :param url: The url reference for the profile, defaults to None
        :type url: Optional[str], optional
        :param faucet_url: The faucet url reference for the profile, defaults to None
        :type faucet_url: Optional[str], optional
        :param faucet_status_url: The faucet status url reference for the profile, defaults to None
        :type faucet_status_url: Optional[str], optional
        :param make_active: Sets this as the groups active_profile, defaults to False
        :type make_active: Optional[bool], optional
        :param in_group: Group to add new profile, defaults to active_group or excepts if not exists
        :type in_group: Optional[str], optional
        :param persist: Persist updates to PysuiConfig.json, defaults to True
        :type persist: Optional[bool], optional
        """
        _group = (
            self._model.get_group(group_name=in_group)
            if in_group
            else self.active_group
        )
        _prf = _group.get_profile(profile_name)
        _prf.url = url or _prf.url
        _prf.faucet_url = faucet_url or _prf.faucet_url
        _prf.faucet_status_url = faucet_status_url or _prf.faucet_status_url
        if persist:
            self._write_model()

    def rename_alias(
        self,
        *,
        existing_alias: str,
        new_alias: str,
        in_group: Optional[str] = None,
        persist: Optional[bool] = True,
    ) -> str:
        """Rename an alias in a group, default to active_group."""
        _group = (
            self._model.get_group(group_name=in_group)
            if in_group
            else self.active_group
        )

        _res = _group.replace_alias_name(from_alias=existing_alias, to_alias=new_alias)
        if _res and persist:
            self._write_model()
