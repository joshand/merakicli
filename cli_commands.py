from meraki_sdk.meraki_sdk_client import MerakiSdkClient
from meraki_sdk.exceptions.api_exception import APIException
from operator import itemgetter
import copy
from _config import *
import json

client = MerakiSdkClient(apikey)


def show_enabled(e_stat):
    if e_stat is True:
        return "Yes"
    else:
        return "No"


def xstr(s):
    return '' if s is None else str(s)


def format_data(srcdata):
    odata = ""
    widths = [max(map(len, col)) for col in zip(*srcdata)]
    for row in srcdata:
        odata += "  ".join((val.ljust(width) for val, width in zip(row, widths))) + "\n"

    return odata


def resolve_arg(arg, datalist):
    dodebug = False
    if dodebug: print(datalist)
    retval = None

    for x in datalist:
        # print(x)
        for y in x:
            if y.lower() == arg.lower():
                retval = x
                break

        if retval:
            break

    # if not retval:
    #     for x in datalist:
    #         # print(x)
    #         for y in x:
    #             # attempt to match "int3" type interfaces
    #             temp = re.findall(r'\d+', str(y))
    #             reslist = list(map(int, temp))
    #             if dodebug: print("match1=", arg, reslist, y)
    #             if isinstance(reslist, list) and len(reslist) >= 1:
    #                 if dodebug: print("match1.1=", reslist)
    #                 # res = str("".join(reslist))
    #                 res = "".join("{0}".format(n) for n in reslist)
    #                 if dodebug: print("match1.2=")
    #                 argtext = arg.lower().replace(res, "")
    #                 if dodebug: print("match1.3=")
    #                 # see if the text part starts the argument
    #                 if dodebug: print("match2=", arg, argtext, y)
    #                 if arg.lower().find(argtext) == 0:
    #                     argrest = arg.lower().replace(str(argtext.lower()), "")
    #                     if dodebug: print("match3=", arg, argrest, res, y)
    #                     if str(argrest).strip() == res.strip():
    #                         if dodebug: print("match4=", arg, argrest, res, y)
    #                         retval = x
    #                         break
    #
    #         if retval:
    #             break

    if retval is None:
        if isinstance(arg, int) and arg < len(datalist):
            retval = datalist[arg]

    return retval


def exec_quit(self, line, context):
    return True


def get_org_raw():
    try:
        srcdata = client.organizations.get_organizations()
    except APIException as e:
        print(f'Error {e.response_code} with error message {e.context.response.raw_body}')
        return ""

    newlist = sorted(srcdata, key=itemgetter('name'))

    outdata = [["#", "Organization ID", "Organization Name"]]
    ocount = 0
    for org in newlist:
        ocount += 1
        outdata.append([str(ocount), str(org["id"]), org["name"]])

    return outdata


def get_net_raw(orgid):
    try:
        srcdata = client.networks.get_organization_networks({"organization_id": orgid})
    except APIException as e:
        print(f'Error {e.response_code} with error message {e.context.response.raw_body}')
        return ""

    outdata = [["#", "Network ID", "Network Type", "Network Name"]]
    if srcdata == {}:
        pass
    else:
        newlist = sorted(srcdata, key=itemgetter('name'))

        ocount = 0
        for org in newlist:
            ocount += 1
            outdata.append([str(ocount), str(org["id"]), "/".join(org["productTypes"]), org["name"]])

    return outdata


def get_dev_raw(netid):
    try:
        srcdata = client.devices.get_network_devices(netid)
    except APIException as e:
        print(f'Error {e.response_code} with error message {e.context.response.raw_body}')
        return ""

    outdata = [["#", "Serial #", "Model", "MAC Address", "WAN 1", "WAN 2", "LAN", "Name"]]
    if not srcdata:
        devlist = outdata
    else:
        newlist = sorted(srcdata, key=itemgetter('model'))

        ocount = 0
        for dev in newlist:
            ocount += 1
            outdata.append([str(ocount), dev["serial"], dev["model"], dev["mac"], xstr(dev.get("wan1Ip")),
                            xstr(dev.get("wan2Ip")), xstr(dev.get("lanIp")), xstr(dev.get("name"))])

    return outdata


def decode_model(dev_model):
    if dev_model.find("MS") >= 0:
        return "switch"
    elif dev_model.find("MR") >= 0:
        return "wireless"
    elif dev_model.find("MX") >= 0:
        return "appliance"

    return "unknown"


def get_int_raw(dev_data, orgid, netid, devid):
    outdata = None
    devtype = decode_model(dev_data[2])

    if devtype == "wireless":
        outdata = [["#", "Interface", "IP-Assignment", "Name", "Enabled?", "Auth", "Band"]]
        try:
            int_data = client.ssids.get_network_ssids(netid)
        except APIException as e:
            print(f'Error {e.response_code} with error message {e.context.response.raw_body}')
            return ""
        for d in int_data:
            outdata.append([str(d["number"]), "SSID" + str(d["number"]), d["ipAssignmentMode"], d["name"], show_enabled(d["enabled"]), d["authMode"], d["bandSelection"]])
    elif devtype == "switch":
        outdata = [["#", "Interface", "Name", "Enabled?", "Type", "VLAN", "Voice VLAN"]]
        try:
            int_data = client.switch_ports.get_device_switch_ports(devid)
        except APIException as e:
            print(f'Error {e.response_code} with error message {e.context.response.raw_body}')
            return ""
        for d in int_data:
            pname = d["name"]
            if pname is None:
                pname = ""
            pvoicevlan = d["voiceVlan"]
            if pvoicevlan is None:
                pvoicevlan = ""

            outdata.append([str(d["number"]), "Ethernet" + str(d["number"]), pname, show_enabled(d.get("enabled", "")), d.get("type", ""), str(d.get("vlan", "")), str(pvoicevlan)])
        #print(outdata)
    elif devtype == "appliance":
        outdata = [["#", "Interface", "Enabled?", "Type", "Native", "Allowed", "DropUntag"]]
        int_data = client.management_interface_settings.get_network_device_management_interface_settings({"network_id": netid, "serial": devid})
        for d in int_data:
            if d.lower().find("wan") >= 0:
                isenabled = True
                vlanid = int_data[d]["vlan"]
                if vlanid is None:
                    vlanid = 1
                outdata.append([str(d.lower().replace("wan", "")), d.upper(), str(isenabled), "access", str(vlanid), "N/A", "False"])
        int_data = client.mx_vlan_ports.get_network_appliance_ports(netid)
        if int_data[0] == 'VLANs are not enabled for this network':
            pass
        else:
            for d in int_data:
                outdata.append([str(d["number"]), "LAN" + str(d["number"]), str(d["enabled"]), d["type"], str(d.get("vlan", "N/A")), str(d.get("allowedVlans", "N/A")), str(d.get("dropUntaggedTraffic", "N/A"))])

    intlist = outdata
    return intlist


def clear_none(instr):
    if instr is None:
        return ""
    else:
        return str(instr)


def parse_json_struct(scope, json, interface=None):
    ro_fields = {
        "organization": ["id", "url"],
        "network": ["id", "organizationId"],
        "device": ["networkId", "model", "mac"]
    }

    c = copy.deepcopy(json)
    outstr = ""
    if interface is not None:
        outstr += scope + " " + str(interface) + "\n"
        if "number" in c:
            c.pop("number", None)
    else:
        if "name" in c:
            outstr += scope + " " + str(c["name"]) + "\n"
            c.pop("name", None)
            if "id" in c:
                outstr += " ! id " + str(c["id"]) + "\n"
                c.pop("id", None)

    if "productTypes" in c:
        c.pop("type", None)
        pt = c["productTypes"]
        c.pop("productTypes", None)
        c["type"] = " ".join(pt)

    for k in c:
        if scope in ro_fields and k in ro_fields[scope]:
            outstr += " ! " + str(k) + " " + clear_none(c[k]) + "\n"
        else:
            outstr += " " + str(k) + " " + clear_none(c[k]) + "\n"

    return outstr


def get_config_data(scope, elemid, context_chain):
    if scope == "root":
        return "Unable to show configuration of the root level. You must access an organization first."
    elif scope == "organization":
        try:
            data = client.organizations.get_organization(elemid)
        except APIException as e:
            print(f'Error {e.response_code} with error message {e.context.response.raw_body}')
            return ""

        return parse_json_struct(scope, data)
    elif scope == "network":
        try:
            data = client.networks.get_network(elemid)
        except APIException as e:
            print(f'Error {e.response_code} with error message {e.context.response.raw_body}')
            return ""

        return parse_json_struct(scope, data)
    elif scope == "device":
        try:
            data = client.devices.get_network_device({"network_id": context_chain[len(context_chain)-2]["selected_item"], "serial": elemid})
        except APIException as e:
            print(f'Error {e.response_code} with error message {e.context.response.raw_body}')
            return ""

        return parse_json_struct(scope, data)
    elif scope == "interface":
        netid = context_chain[len(context_chain) - 3]["selected_item"]
        devid = context_chain[len(context_chain) - 2]["selected_item"]
        intname = context_chain[len(context_chain) - 1]["selected_item"]
        if "Ethernet" in intname:
            intnum = intname.replace("Ethernet", "")
            try:
                data = client.switch_ports.get_device_switch_port({"serial": devid, "number": intnum})
            except APIException as e:
                print(f'Error {e.response_code} with error message {e.context.response.raw_body}')
                return ""
            return parse_json_struct(scope, data, interface=intname)
        elif "SSID" in intname:
            intnum = intname.replace("SSID", "")
            try:
                data = client.ssids.get_network_ssid({"network_id": netid, "number": intnum})
            except APIException as e:
                print(f'Error {e.response_code} with error message {e.context.response.raw_body}')
                return ""
            return parse_json_struct(scope, data, interface=intname)
        elif "LAN" in intname or "WAN" in intname:
            data = None
            if "LAN" in intname:
                intnum = str(intname.replace("LAN", ""))
                itype = "LAN"
            else:
                intnum = str(intname.replace("WAN", ""))
                itype = "WAN"

            try:
                if itype == "WAN":
                    tempdata = client.management_interface_settings.get_network_device_management_interface_settings({"network_id": netid, "serial": devid})
                    for d in tempdata:
                        if intname.lower() in d.lower():
                            data = tempdata[d]
                            break
                else:
                    data = client.mx_vlan_ports.get_network_appliance_port({"network_id": netid, "appliance_port_id": intnum})
            except APIException as e:
                print(f'Error {e.response_code} with error message {e.context.response.raw_body}')
                return ""
            return parse_json_struct(scope, data, interface=intname)
    else:
        return "Unable to show configuration for scope " + scope


def exec_show_parse(self, list_line, context_chain):
    line = " ".join(list_line)
    curscope = context_chain[len(context_chain)-1]["scope"]
    if curscope == "root" and (line in "organizations" or line in "orgs"):
        outdata = get_org_raw()
        self.execdata = outdata
        return format_data(outdata)
    elif curscope == "organization" and (line in "networks" or line in "nets"):
        outdata = get_net_raw(context_chain[len(context_chain)-1]["selected_item"])
        self.execdata = outdata
        return format_data(outdata)
    elif curscope == "network" and (line in "devices" or line in "devs"):
        outdata = get_dev_raw(context_chain[len(context_chain)-1]["selected_item"])
        self.execdata = outdata
        return format_data(outdata)
    elif curscope == "device" and (line in "interfaces" or line in "ints"):
        prevdev = context_chain[len(context_chain) - 1]["selected_item"]
        r = resolve_arg(prevdev, context_chain[len(context_chain) - 2]["dataset"])
        outdata = get_int_raw(r, context_chain[len(context_chain) - 3]["selected_item"], context_chain[len(context_chain) - 2]["selected_item"], context_chain[len(context_chain) - 1]["selected_item"])
        self.execdata = outdata
        return format_data(outdata)
    elif line in "configuration":
        return get_config_data(curscope, context_chain[len(context_chain)-1]["selected_item"], context_chain)
    elif line in "debug context":
        return str(json.dumps(context_chain))
    else:
        return "Unknown argument: " + line


def exec_context_org(self, list_line, context_chain):
    line = " ".join(list_line)

    if self.execdata is None:
        e = get_org_raw()
        self.execdata = e
        r = resolve_arg(line, e)
    else:
        r = resolve_arg(line, self.execdata)

    if not r:
        orgname = str(line).strip()
        print("Unable to locate an Organization with the identifier '" + orgname + "'. Creating one...")
        try:
            data = client.organizations.create_organization(orgname)
        except APIException as e:
            print(f'Error {e.response_code} with error message {e.context.response.raw_body}')
            return ""

        e = get_org_raw()
        self.execdata = e
        r = resolve_arg(orgname, e)

    self.temp_context_desc = "Org-" + r[2] + "#"
    self.temp_context = "organization"
    self.temp_id = r[1]
    self.exit_code = 998
    return True


def exec_context_net(self, list_line, context_chain):
    line = " ".join(list_line)
    if self.execdata is None:
        e = get_net_raw(context_chain[len(context_chain)-1]["selected_item"])
        self.execdata = e
        r = resolve_arg(line, e)
    else:
        r = resolve_arg(line, self.execdata)

    if not r:
        netname = str(line).strip()
        print("Unable to locate a Network with the identifier '" + str(line) + "'. Creating one...")
        try:
            data = client.networks.create_organization_network({"organization_id": context_chain[len(context_chain)-1]["selected_item"], "create_organization_network": {"name": netname, "type": default_net_type, "tags": "", "time_zone": default_time_zone}})
        except APIException as e:
            print(f'Error {e.response_code} with error message {e.context.response.raw_body}')
            return ""

        e = get_net_raw(context_chain[len(context_chain)-1]["selected_item"])
        self.execdata = e
        r = resolve_arg(netname, e)

    self.temp_context_desc = context_chain[len(context_chain)-1]["prompt"][:-1] + "/Net-" + r[3] + "#"
    self.temp_context = "network"
    self.temp_id = r[1]
    self.exit_code = 998
    return True


def exec_context_dev(self, list_line, context_chain):
    line = " ".join(list_line)
    if self.execdata is None:
        e = get_dev_raw(context_chain[len(context_chain)-1]["selected_item"])
        self.execdata = e
        r = resolve_arg(line, e)
    else:
        r = resolve_arg(line, self.execdata)

    if not r:
        return "Unable to locate a Device with the identifier '" + str(line) + "'. To claim a new Device, use the command 'network claim <device-serial-number>'."

    self.temp_context_desc = context_chain[len(context_chain)-1]["prompt"][:-1] + "/Dev-" + r[1] + "#"
    self.temp_context = "device"
    self.temp_id = r[1]
    self.exit_code = 998
    return True


def exec_context_int(self, list_line, context_chain):
    line = " ".join(list_line)
    if self.execdata is None:
        prevdev = context_chain[len(context_chain) - 1]["selected_item"]
        r = resolve_arg(prevdev, context_chain[len(context_chain) - 2]["dataset"])
        e = get_int_raw(r, context_chain[len(context_chain) - 3]["selected_item"],
                              context_chain[len(context_chain) - 2]["selected_item"],
                              context_chain[len(context_chain) - 1]["selected_item"])

        self.execdata = e
        r = resolve_arg(line, e)
    else:
        r = resolve_arg(line, self.execdata)

    if not r:
        return "Unable to locate an Interface with the identifier '" + str(line) + "'."

    self.temp_context_desc = context_chain[len(context_chain)-1]["prompt"][:-1] + "/Int-" + r[1] + "#"
    self.temp_context = "interface"
    self.temp_id = r[1]
    self.exit_code = 998
    return True


def exec_up_context(self, list_line, context_chain):
    prevctx = context_chain[len(context_chain)-2]
    self.temp_context_desc = prevctx["prompt"]
    self.temp_context = prevctx["scope"]
    self.temp_id = prevctx["selected_item"]
    self.exit_code = 997
    return True


def exec_root_context(self, list_line, context_chain):
    prevctx = context_chain[0]
    self.temp_context_desc = prevctx["prompt"]
    self.temp_context = prevctx["scope"]
    self.temp_id = prevctx["selected_item"]
    self.exit_code = 996
    return True


def exec_handle_disable(self, list_line, context_chain):
    handle_port_toggle(self, list_line, context_chain, False)
    self.exit_code = 999
    return True


def exec_handle_no(self, list_line, context_chain):
    line = " ".join(list_line)
    curscope = context_chain[len(context_chain)-1]["scope"]
    if curscope == "interface" and line in "shutdown":
        handle_port_toggle(self, list_line, context_chain, True)
    elif curscope == "root" and list_line[0] in "organization":
        print("Unable to delete Organization: No API Coverage.")
    elif curscope == "organization" and list_line[0] in "network":
        arg = " ".join(list_line[1:])
        if self.execdata is None:
            e = get_net_raw(context_chain[len(context_chain) - 1]["selected_item"])
            self.execdata = e
            r = resolve_arg(arg, e)
        else:
            r = resolve_arg(arg, self.execdata)
        try:
            data = client.networks.delete_network(r[1])
        except APIException as e:
            print(f'Error {e.response_code} with error message {e.context.response.raw_body}')
            return ""

    self.exit_code = 999
    return True


def handle_port_toggle(self, list_line, context_chain, port_enabled):
    prevnet = context_chain[len(context_chain) - 3]["selected_item"]
    prevdev = context_chain[len(context_chain) - 2]["selected_item"]
    prevint = context_chain[len(context_chain) - 1]["selected_item"]
    if "Ethernet" in prevint:
        intnum = str(prevint.replace("Ethernet", ""))
        try:
            data = client.switch_ports.update_device_switch_port({"serial": prevdev, "number": intnum, "update_device_switch_port": {"enabled": port_enabled}})
        except APIException as e:
            print(f'Error {e.response_code} with error message {e.context.response.raw_body}')
            return ""
    elif "SSID" in prevint:
        intnum = str(prevint.replace("SSID", ""))
        try:
            data = client.ssids.update_network_ssid({"network_id": prevnet, "number": intnum, "update_network_ssid": {"enabled": port_enabled}})
        except APIException as e:
            print(f'Error {e.response_code} with error message {e.context.response.raw_body}')
            return ""
    elif "LAN" in prevint or "WAN" in prevint:
        if "LAN" in prevint:
            intnum = str(prevint.replace("LAN", ""))
            itype = "LAN"
        else:
            intnum = str(prevint.replace("WAN", ""))
            itype = "WAN"

        try:
            if itype == "WAN":
                upd_port = "wan" + intnum
                if port_enabled:
                    wan_state = "enabled"
                else:
                    wan_state = "disabled"
                data = client.management_interface_settings.update_network_device_management_interface_settings({"network_id": prevnet, "serial": prevdev, "update_network_device_management_interface_settings": {upd_port: {"wanEnabled": wan_state}}})
                print("wan toggle", j)
            else:
                data = client.mx_vlan_ports.update_network_appliance_port({"network_id": prevnet, "appliance_port_id": intnum, "update_network_appliance_port": {"enabled": port_enabled}})
        except APIException as e:
            print(f'Error {e.response_code} with error message {e.context.response.raw_body}')
            return ""

        return ""
    else:
        print(prevdev, prevint)


def switch_context(self, list_line, context_chain):
    out_chain = []
    orgid = None
    netid = None
    devid = None
    seldevdata = None
    intnum = None
    curcontext = "root"
    line = " ".join(list_line)
    ctxlist = line.split("/")
    for ctx in ctxlist:
        ctxname = "-".join(ctx.split("-")[1:])
        typectx = ctx.replace(ctxname, "").replace("-", "")
        if typectx.lower() == "org":
            orgdata = get_org_raw()
            r = resolve_arg(ctxname, orgdata)
            if r: orgid = str(r[1])
            out_chain.append({"scope": curcontext, "prompt": "#", "dataset": orgdata, "selected_item": None, "selected_data": r})
            curcontext = "organization"
        elif typectx.lower() == "net" and orgid is not None:
            netdata = get_net_raw(orgid)
            r = resolve_arg(ctxname, netdata)
            if r: netid = str(r[1])
            out_chain.append({"scope": curcontext, "prompt": "Org-" + out_chain[len(out_chain)-1]["selected_data"][2] + "#", "dataset": netdata, "selected_item": out_chain[len(out_chain)-1]["selected_data"][1], "selected_data": r})
            curcontext = "network"
        elif typectx.lower() == "dev" and netid is not None:
            devdata = get_dev_raw(netid)
            r = resolve_arg(ctxname, devdata)
            if r: devid = str(r[1])
            out_chain.append({"scope": curcontext, "prompt": out_chain[len(out_chain)-1]["prompt"][:-1] + "/Net-" + out_chain[len(out_chain)-1]["selected_data"][3] + "#", "dataset": devdata, "selected_item": out_chain[len(out_chain)-1]["selected_data"][1], "selected_data": r})
            curcontext = "device"
        elif typectx.lower() == "int" and devid is not None:
            intdata = get_int_raw(out_chain[len(out_chain)-1]["selected_data"], orgid, netid, devid)
            r = resolve_arg(ctxname, intdata)
            if r: intnum = str(r[1])
            out_chain.append({"scope": curcontext, "prompt": out_chain[len(out_chain)-1]["prompt"][:-1] + "/Dev-" + out_chain[len(out_chain)-1]["selected_data"][1] + "#", "dataset": intdata, "selected_item": out_chain[len(out_chain)-1]["selected_data"][1], "selected_data": r})
            curcontext = "interface"
            out_chain.append({"scope": curcontext, "prompt": out_chain[len(out_chain)-1]["prompt"][:-1] + "/Int-" + out_chain[len(out_chain)-1]["selected_data"][1] + "#", "dataset": None, "selected_item": intnum, "selected_data": None})

    self.temp_context_desc = line + "#"
    self.temp_context = curcontext
    self.temp_context_chain = out_chain
    self.exit_code = 995
    return True
