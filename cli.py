import types

current_context_desc = "#"
context_chain = [{"scope": "root", "prompt": current_context_desc, "dataset": None, "selected_item": None}]
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
        "subcommands": {"organizations": {}, "configurations": {}, "debug": {"subcommands": {"context": {}}}},
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
        "subcommands": {"networks": {}, "configurations": {}, "debug": {"subcommands": {"context": {}}}},
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
        "function": "exec_show_parse",
        "subcommands": {"devices": {}, "configurations": {}, "debug": {"subcommands": {"context": {}}}},
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
        "subcommands": {"interfaces": {}, "configurations": {}, "debug": {"subcommands": {"context": {}}}},
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
        "subcommands": {"configurations": {}, "debug": {"subcommands": {"context": {}}}},
        "function": "exec_show_parse",
        "help": "show ['configuration']"
    },
    {
        "command": "shut",
        "function": "exec_handle_disable",
        "help": "shut"
    }
]


def make_context(context_command_list):
    ctx = "import cmd2\n"
    ctx += "import cli_commands\n"
    ctx += "\n"
    ctx += "class DynamicContext(cmd2.Cmd):\n"
    ctx += '    """Dynamic Context"""\n'
    ctx += '    def __init__(self, *args, **kwargs):\n'
    ctx += '        super().__init__(*args, **kwargs)\n'
    ctx += '        try:\n'
    ctx += '            del cmd2.Cmd.do_edit\n'
    ctx += '            del cmd2.Cmd.do_alias\n'
    ctx += '            del cmd2.Cmd.do_macro\n'
    ctx += '            del cmd2.Cmd.do_py\n'
    ctx += '            del cmd2.Cmd.do_run_pyscript\n'
    ctx += '            del cmd2.Cmd.do_run_script\n'
    ctx += '            del cmd2.Cmd.do_shell\n'
    ctx += '            del cmd2.Cmd.do_shortcuts\n'
    ctx += '            del cmd2.Cmd.do_set\n'
    ctx += '        except:\n'
    ctx += '            pass\n'
    ctx += "\n"
    for c in context_command_list:
        ccmd = c["command"]
        if ccmd.find("|") > 0:
            ccmd = ccmd.split("|")[0]
        ctx += make_context_def(ccmd, c)

    global context_chain
    abbr_cmd_list = []
    current_scope_info = context_chain[len(context_chain) - 1]
    current_scope_commands = context["global"] + context[current_scope_info["scope"]]
    for s in current_scope_commands:
        abbr_cmd_list.append({"command": s["command"], "function": s["function"]})

    ctx += '    def default(self, arg):\n'
    ctx += '        global context_chain\n'
    ctx += '        base_arg = arg.argv[0]\n'
    ctx += '        cmd_list = ' + str(abbr_cmd_list) + '\n'
    ctx += '        for c in cmd_list:\n'
    ctx += '             if base_arg in c["command"]:\n'
    ctx += '                  r = getattr(cli_commands, c["function"])(self, arg.argv[1:], ' + str(context_chain) + ')\n'
    ctx += '                  if r is True:\n'
    ctx += '                      return True\n'
    ctx += '                  elif r is not None:\n'
    ctx += '                      print(r)\n'
    ctx += '                      self.exit_code = 999\n'
    ctx += '                      return True\n'
    return ctx


def make_context_def(context_command, context_command_detail):
    ctxcmd = "    def do_" + context_command + "(self, arg):\n"
    ctxcmd += '        """' + context_command_detail["help"] + '"""\n'
    ctxcmd += '        r = cli_commands.' + context_command_detail["function"] + '(self, arg.argv[1:], ' + str(context_chain) + ')\n'
    ctxcmd += '        if r is True:\n'
    ctxcmd += '            return True\n'
    ctxcmd += '        elif r is not None:\n'
    ctxcmd += '            print(r)\n'
    ctxcmd += '            self.exit_code = 999\n'
    ctxcmd += '            return True\n'
    ctxcmd += "\n"
    ctxcmd += "\n"
    return ctxcmd


def import_code(code, name):
    module = types.ModuleType(name)     # create blank module
    exec(code, module.__dict__)         # populate the module with code
    return module


if __name__ == '__main__':
    curcontext = "root"
    firstrun = True
    while True:
        c = make_context(context["global"] + context[curcontext])
        m = import_code(c, 'mod')
        r = m.DynamicContext()
        r.context = curcontext
        if firstrun:
            r.intro = 'Welcome to the Meraki shell. Type help or ? to list commands.\n'
            firstrun = False
        r.context = curcontext
        r.execdata = context_chain[len(context_chain)-1]["dataset"]
        r.prompt = context_chain[len(context_chain)-1]["prompt"] + ' '
        x = r.cmdloop()
        if x == 998:    # context switch (down)
            context_chain[len(context_chain) - 1]["dataset"] = r.execdata
            curcontext = r.temp_context
            context_chain.append({"scope": curcontext, "prompt": r.temp_context_desc, "dataset": None, "selected_item": r.temp_id})
        elif x == 997:  # context switch (up/exit)
            context_chain[len(context_chain) - 1]["dataset"] = r.execdata
            curcontext = r.temp_context
            del context_chain[len(context_chain) - 1]
        elif x == 996:  # context switch (to root)
            context_chain[0]["dataset"] = r.execdata
            curcontext = r.temp_context
            while len(context_chain) > 1:
                del context_chain[len(context_chain) - 1]
        elif x == 999:  # end of command; send prompt again
            context_chain[len(context_chain) - 1]["dataset"] = r.execdata
        elif x == 995:  # direct context switch via 'context' command
            context_chain = r.temp_context_chain
            curcontext = r.temp_context
        else:
            break
