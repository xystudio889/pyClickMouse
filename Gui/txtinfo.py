from sharelibs import default_settings, settings

__all__ = ['SettingText', 'StyleClass', 'InputChange', 'SettingValue']

class SettingText:
    select_lang = 'select_lang'
    show_tray_icon ='show_tray_icon'
    soft_delay = 'soft_delay'
    click_delay = 'click_delay'
    click_times = 'click_times'
    delay_unit = 'delay_unit'
    times_unit = 'times_unit'
    delay_error_use_default = 'failed_use_default'
    times_error_use_default = 'times_failed_use_default'
    update_enabled = 'update_enabled'
    update_notify = 'update_notify'
    quiet_update = 'quiet_update'
    update_ok_notify = 'update_ok_notify'
    update_frequency = 'update_frequency'
    select_style = 'select_style'
    use_windows_color = 'use_windows_color'
    theme = 'theme'
    hotkey = 'hotkey'
    default_doc_link = 'default_doc_link'
    lang_doc = 'lang_doc'
    update_log_path = 'update_log_path'
    hotkey_enabled = 'hotkey_enabled'
    show_warning = 'show_warning'
    show_package_warning ='show_package_warning'
    feedback = 'feedback'
    modify_using_default_input = 'modify_using_default_input'
    modify_using_default_combo = 'modify_using_default_combo'
   
class SettingValue:
    def get(self, value):
        default_value = default_settings.get(value, None)

        return settings.get(value, default_value)
    
    def __getitem__(self, key):
        return self.get(key)
    
    def __setitem__(self, key, value):
        raise ValueError('SettingValue is readonly')
    
    def __delitem__(self, key):
        raise ValueError('SettingValue is readonly')

    @property
    def select_lang(self):
        return self[SettingText.select_lang]
    
    @property
    def show_tray_icon(self):
        return self[SettingText.show_tray_icon]
    
    @property
    def soft_delay(self):
        return self[SettingText.soft_delay]
    
    @property
    def click_delay(self):
        return self[SettingText.click_delay]
    
    @property
    def click_times(self):
        return self[SettingText.click_times]
    
    @property
    def delay_unit(self):
        return self[SettingText.delay_unit]
    
    @property
    def times_unit(self):
        return self[SettingText.times_unit]
    
    @property
    def delay_error_use_default(self):
        return self[SettingText.delay_error_use_default]
    
    @property
    def times_error_use_default(self):
        return self[SettingText.times_error_use_default]
    
    @property
    def update_enabled(self):
        return self[SettingText.update_enabled]
    
    @property
    def update_notify(self):
        return self[SettingText.update_notify]
    
    @property
    def quiet_update(self):
        return self[SettingText.quiet_update]
    
    @property
    def update_ok_notify(self):
        return self[SettingText.update_ok_notify]
    
    @property
    def update_frequency(self):
        return self[SettingText.update_frequency]
    
    @property
    def select_style(self):
        return self[SettingText.select_style]
    
    @property
    def use_windows_color(self):
        return self[SettingText.use_windows_color]
    
    @property
    def theme(self):
        return self[SettingText.theme]
    
    def _get_hotkey(self, val_name):
        setting_value = settings.get(SettingText.hotkey, {}).get(val_name, {})
        default_value = default_settings.get(SettingText.hotkey, {}).get(val_name, {})

        return default_value | setting_value # 右侧覆盖左侧
    
    @property
    def hotkey_list(self):
        return self._get_hotkey('hotkeys')
    
    @property
    def hotkey_enabled_list(self):
        return self._get_hotkey('enabled')
    
    @property
    def default_doc_link(self):
        return self[SettingText.default_doc_link]
    
    @property
    def lang_doc(self):
        return self[SettingText.lang_doc]
    
    @property
    def update_log_path(self):
        return self[SettingText.update_log_path]
    
    @property
    def hotkey_enabled(self):
        return self[SettingText.hotkey].get(SettingText.hotkey_enabled, True)
    
    @property
    def show_warning(self):
        return self[SettingText.show_warning]
    
    @property
    def show_package_warning(self):
        return self[SettingText.show_package_warning]
    
    @property
    def feedback(self):
        return self[SettingText.feedback]
    
    @property
    def hide_flags(self):
        return self[SettingText.hide_flags]
    
    @property
    def modify_using_default_input(self):
        return self[SettingText.modify_using_default_input]
    
    @property
    def modify_using_default_combo(self):
        return self[SettingText.modify_using_default_combo]
    
class StyleClass:
    big_14 = 'big_text_14'
    big_16 = 'big_text_16'
    big_20 = 'big_text_20'
    big_24 = 'big_text_24'

    frame = 'frame'
    selected = 'selected'
    dest = 'dest'
    b = 'bold'
    d_11 = 'dest_small'

    none = ''
    
class InputChange:
    main_window = 'main'
    setting_window = 'setting'
