for i in dev_settings:
    widget = DevFlagCard(
        title = None,
        subtitle = i['name'],
        code = i['key'],
        description = i['desc'],
        items = self.resolve_requires(dev_settings, i),
        needs_restart = i.get('need_restart', False),
    )

    toggle_switch = widget.toggle_switch()
    toggle_switch.setChecked(dev_flags.get(i['key'], False))
    if i.get('need_restart', False):
        toggle_switch.stateChanged.connect(lambda chk,idx=i['key']:(self.save_dev_config(chk, idx),self.restart_ask(),))
    else:
        toggle_switch.stateChanged.connect(lambda chk,idx=i['key']:(self.save_dev_config(chk, idx)))

    layout.addWidget(widget)

[
    {
        "name": "aaa",
        "key": "aa",
        "desc": "描述",
        "need_restart": True,
        "requires": ["bb", "cc"],
    },
    {
        "name": "bbb",
        "key": "bb",
        "desc": "描述",
        "requires": ["dd"],
    },
    {
        "name": "ccc",
        "key": "cc",
        "desc": "描述",
        "requires": ["dd"],
    },
    {
        "name": "ddd",
        "key": "dd",
        "desc": "描述"
    },
]