def build_config(config):
    config.setdefaults(
        'day', {
            'background': 'bratzillas_cloetta_spelletta_1.png',
            'clock_visible': 1,
            'audio_enabled' : 1
        })
    config.setdefaults(
        'night' , {
            'background': 'bratzillas_cloetta_spelletta_2.png',
            'start_time': '20:30',
            'stop_time': '8:30',
            'clock_visible': 1,
            'moon_visible': 1,
            'audio_enabled' : 1
        })

def build_settings(settings, config, backgrounds):

    # setting types: title, bool, numeric, options, string, path
    jsondata = '''
[
    { "type": "title",
      "title": "Day" },

    { "type": "options",
      "title": "Background",
      "desc": "Background image for daytime",
      "section": "day",
      "key": "background",
      "options": <!--backgrounds--> },

    { "type": "bool",
      "title": "Audio enabled",
      "desc": "Audio enabled day mode",
      "section": "day",
      "key": "audio_enabled" },

    { "type": "bool",
      "title": "Clock visible",
      "desc": "Clock visible in day mode",
      "section": "day",
      "key": "clock_visible" },

    { "type": "title",
      "title": "Night" },

    { "type": "string",
      "title": "Start time",
      "desc": "Night mode start time",
      "section": "night",
      "key": "start_time" },

    { "type": "string",
      "title": "End time",
      "desc": "Night mode stop time",
      "section": "night",
      "key": "stop_time" },

    { "type": "options",
      "title": "Background",
      "desc": "Background image for nighttime",
      "section": "night",
      "key": "background",
      "options": <!--backgrounds--> },

    { "type": "bool",
      "title": "Audio enabled",
      "desc": "Audio enabled in night mode",
      "section": "night",
      "key": "audio_enabled" },

    { "type": "bool",
      "title": "Clock visible",
      "desc": "Clock visible in night mode",
      "section": "night",
      "key": "clock_visible" },

    { "type": "bool",
      "title": "Moon visible",
      "desc": "Moon overlay visible in night mode",
      "section": "night",
      "key": "moon_visible" }
]

'''
    backgrounds_string = "["
    for background in sorted(backgrounds):
        backgrounds_string += "\"%s\","%background
    backgrounds_string = backgrounds_string.rsplit(',', 1)[0]
    backgrounds_string += "]"
    jsondata = jsondata.replace("<!--backgrounds-->", backgrounds_string)
    settings.add_json_panel('Ensikello',
        config, None, jsondata)
