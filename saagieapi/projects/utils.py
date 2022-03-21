def check_exposed_ports(exposed_ports, list_exposed_port_field):
    """
    Check
    Parameters
    ----------
    exposed_ports : list
        List of exposed ports, each item of the list should be a dict
        and each dict should have 'port' as key
    list_exposed_port_field : list
        List of valid field of each exposed port
    Returns
    -------
    bool
        True if all exposed port is in the validate format
        Otherwise False
    """
    if type(exposed_ports) != list:
        return False
    else:
        if len(exposed_ports):
            check_type = all([type(ep) == dict for ep in exposed_ports])
            if check_type:
                check_port = all(["port" in ep.keys() for ep in exposed_ports])
                if check_port:
                    check_every_key = all([all(elem in list_exposed_port_field for elem in ep.keys()) for ep in exposed_ports])
                    if check_every_key:
                        return True
                    else:
                        return False
                else:
                    return False
            else:
                return False
        else:
            return True
