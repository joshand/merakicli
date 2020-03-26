context = {}
context["global"] = [
    {
        "command": "context",
        "function": "switch_context",
        "help": "change to the specified context"
    },
    {
        "command": "exit",
        "function": "exec_up_context",
        "help": "exit the current context"
    },
    {
        "command": "quit",
        "function": "exec_quit",
        "help": "exit the program"
    },
    {
        "command": "end",
        "function": "exec_root_context",
        "help": "exit to root context"
    },
    {
        "command": "no",
        "function": "exec_handle_no",
        "help": "negate a command"
    },
    {
        "command": "show",
        "subcommands": [{
            "command": "debug",
            "help": "show debug information",
            "subcommands": [{
                "command": "context",
                "help": "debug current context"
            }]
        }],
        "function": "exec_show_parse",
        "help": "show information for a given object"
    }

]
context["root"] = [
    {
        "command": "exit",
        "function": "exec_quit",
        "help": "exit the program"
    },
    {
        "command": "show",
        "subcommands": [{"command": "organizations", "help": "show list of organizations"}],
        "function": "exec_show_parse",
        "help": "show information for a given object"
    },
    {
        "command": "organization",
        "function": "exec_context_org",
        "help": "enter the context of a specific organziation"
    }
]
context["organization"] = [
    {
        "command": "show",
        "subcommands": [{"command": "networks", "help": "show list of networks"}, {"command": "configuration", "help": "show organization configuration"}],
        "function": "exec_show_parse",
        "help": "show ['networks', 'configuration']"
    },
    {
        "command": "network",
        "function": "exec_context_net",
        "help": "enter the context of a specific network"
    }
]
context["network"] = [
    {
        "command": "show",
        "subcommands": [{"command": "devices", "help": "show list of devices"}, {"command": "configuration", "help": "show network configuration"}],
        "function": "exec_show_parse",
        "help": "show ['devices', 'configuration']"
    },
    {
        "command": "device",
        "function": "exec_context_dev",
        "help": "enter the context of a specific device"
    }
]
context["device"] = [
    {
        "command": "show",
        "subcommands": [{"command": "interfaces", "help": "show list of interfaces"}, {"command": "configuration", "help": "show device configuration"}],
        "function": "exec_show_parse",
        "help": "show ['interfaces', 'configuration']"
    },
    {
        "command": "interface",
        "function": "exec_context_int",
        "help": "enter the context of a specific interface"
    }
]
context["interface"] = [
    {
        "command": "show",
        "subcommands": [{"command": "configuration", "help": "show interface configuration"}],
        "function": "exec_show_parse",
        "help": "show ['configuration']"
    },
    {
        "command": "shut",
        "function": "exec_handle_disable",
        "help": "shut"
    }
]