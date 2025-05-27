import keyboard 
import json
import os
import time
import djitellopy as djit


class Setting:

    def __init__(self):
        self.settings_path = os.path.join(os.path.dirname(__file__), 'data\setting\settings.json')
        self.defaulth_settings_path = os.path.join(os.path.dirname(__file__), 'data\setting\defaulth_settings.json')
        # Impostazioni di default per il controller
        self.x_cm = 30 # x -> cm percorsi in avanti/indietro    
        self.y_cm = 20 # y -> cm percorsi a sinistra/destra
        self.z_cm = 30 # z -> cm percorsi in alto/in basso
        self.degree = 20 # gradi di rotazione in senso orario/antiorario

        #struttura section setting 1 nome,2 valore di default (che prende il valore modificato dall'utente),3 tipo di widget,4 lista paremtri da inviare alla funzione ,5 lista opzioni visibili all'utente 6 commando 

        self.setting_section_controller = [

            ["connessione", "backslash", "button", None],   
            ["stream on/off", "tab", "button", None],
                
            ["alza in volo", "1", "button", None],
            ["atterra", "2", "button", None],

            ["muoviti in avanti", "w", "button", self.x_cm],
            ["muoviti a dietro", "s", "button",self.x_cm],
            ["muoviti a sinistra", "a", "button",self.y_cm],
            ["muoviti a destra", "d", "button",self.y_cm],

            ["vai su", "e", "button",self.z_cm],
            ["vai giù", "q", "button",self.z_cm],

            ["ruota in senso orario", "r", "button",self.degree],
            ["ruota in senso antiorario", "t", "button",self.degree],

            ["cm di spostemento in avanti/indietro", self.x_cm , "slider", None],
            ["cm di spostemento a sinistra/destra", self.y_cm , "slider", None],
            ["cm di spostemento in alto/in basso", self.z_cm , "slider", None],
            ["gradi di rotazione in senso orario/antiorario", self.degree , "slider", None],
                 
        ]

        self.drone = djit.Tello()

        self.bitrate_video = [self.drone.BITRATE_1MBPS,self.drone.BITRATE_2MBPS,self.drone.BITRATE_3MBPS,self.drone.BITRATE_4MBPS,self.drone.BITRATE_5MBPS]
        self.video_resolution =[self.drone.RESOLUTION_480P ,self.drone.RESOLUTION_720P] 
        self.stream_fps = [self.drone.FPS_15,self.drone.FPS_30]


        self.setting_section_stream = [

            ["bitrate video",4,"optionmenu",self.bitrate_video,[1,2,3,4,5]],
            ["risoluzione video","720p","optionmenu",self.video_resolution, ["480p","720p"]],
            ["fps video","30","optionmenu",self.stream_fps,[15,30]],

        ]

        self.settings = {
            "controller": self.setting_section_controller,
            "stream": self.setting_section_stream,
        }

        self.load_settings_from_json()

        self.x_cm = self.setting_section_controller[10][1]  # cm di spostamento in avanti/indietro
        self.y_cm = self.setting_section_controller[11][1]  # cm di spostamento a sinistra/destra
        self.z_cm = self.setting_section_controller[12][1] # cm di spostamento in alto/in basso

#------------------------------------------------------------------

    def get_key_name(self, event):
        return event.name

    def verify_key(self, key, field_name):
        for row in self.setting_section_controller:
            if row[0] == field_name:
                continue
            if row[1] == key or row[1] is None:
                return None
        return key
    
#------------------------------------------------------------------
    
    def save_settings_to_json(self):
        file_path = os.path.join(self.settings_path)
        with open(file_path, "w") as f:
            json.dump(self.settings,f)
    
    def get_setting_data(self):
        try:
            with open(self.settings_path, 'r') as json_file:
                data = json.load(json_file)  
                return data  
        except FileNotFoundError:
            print("File settings.json non trovato!") 
        except json.JSONDecodeError:
            print("Errore nel file settings.json!") 
                        
    def load_settings_from_json(self):
        data = self.get_setting_data()
        if data is not None:
            self.settings = data
            self.setting_section_controller = self.settings["controller"]
            self.setting_section_stream = self.settings["stream"]
        
    def restore_default_settings(self, section):
        try:
            with open(self.defaulth_settings_path, 'r') as json_file:
                data = json.load(json_file)
                self.settings[section] = data[section]
                self.save_settings_to_json()
                if section == "controller":
                    self.setting_section_controller = self.settings[section]
                elif section == "stream":
                    self.setting_section_stream = self.settings[section]
        except FileNotFoundError:
            print("File defaulth_settings.json non trovato!")
        except json.JSONDecodeError:
            print("Errore nel file defaulth_settings.json!")
            