from snet.contracts import get_contract_def


def get_contract_address(cmd, contract_name, error_message=None):
    """
    We try to get config address from the different sources.
    The order of priorioty is following:
    - command line argument (at)
    - command line argument (<contract_name>_at)
    - current session configuration (current_<contract_name>_at)
    - networks/*json
    """

    # try to get from command line argument at or contractname_at
    a = "at"
    if hasattr(cmd.args, a) and getattr(cmd.args, a):
        return cmd.w3.to_checksum_address(getattr(cmd.args, a))

    # try to get from command line argument contractname_at
    a = "%s_at" % contract_name.lower()
    if hasattr(cmd.args, a) and getattr(cmd.args, a):
        return cmd.w3.to_checksum_address(getattr(cmd.args, a))

    # try to get from current session configuration
    rez = cmd.config.get_session_field("current_%s_at" % (contract_name.lower()), exception_if_not_found=False)
    if rez:
        return cmd.w3.to_checksum_address(rez)

    error_message = error_message or "Fail to read %s address from \"networks\", you should " \
                                     "specify address by yourself via --%s_at parameter" % (
                        contract_name, contract_name.lower())
    # try to take address from networks
    return read_default_contract_address(w3=cmd.w3, contract_name=contract_name)


def read_default_contract_address(w3, contract_name):
    chain_id = w3.net.version  # this will raise exception if endpoint is invalid
    contract_def = get_contract_def(contract_name)
    networks = contract_def["networks"]
    contract_address = networks.get(chain_id, {}).get("address", None)
    if not contract_address:
        raise Exception()
    contract_address = w3.to_checksum_address(contract_address)
    return contract_address


def get_field_from_args_or_session(config, args, field_name):
    """
    We try to get field_name from diffent sources:
    The order of priorioty is following:
   read_default_contract_address - command line argument (--<field_name>)
    - current session configuration (default_<filed_name>)
    """
    rez = getattr(args, field_name, None)
    # type(rez) can be int in case of wallet-index, so we cannot make simply if(rez)
    if rez is not None:
        return rez
    rez = config.get_session_field("default_%s" % field_name, exception_if_not_found=False)
    if rez:
        return rez
    raise Exception("Fail to get default_%s from config, should specify %s via --%s parameter" % (
        field_name, field_name, field_name.replace("_", "-")))
