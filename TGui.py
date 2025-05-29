import PIL
from TController import Controller

import customtkinter as ctk
import os
import threading

import cv2
from PIL import Image, ImageTk
import time
import keyboard

class GUI(Controller):

    def __init__(self):
        Controller.__init__(self)

        self.root = ctk.CTk()

        self.root_height = self.root.winfo_screenheight() - 80
        self.root_width = self.root.winfo_screenwidth()

        self.root.geometry(f"{self.root_width}x{self.root_height}+0+0")
        self.root.resizable(False, False)
        self.root.title("dji tello dalla chiesa")

        self.color = ["#e3e6e0", "#0c4160","#011e31","#c0c0c0"]

        self.top_frame = self.create_frame(self.root, self.root_width, self.root_height / 8, corner_radius=0, fg_color=self.color[1], bg_color=self.color[1])
        self.top_frame.place(relx=0, rely=0)

        self.bg_frame = self.create_frame(self.root, self.root_width, self.root_height - self.root_height / 8, corner_radius=0, fg_color=self.color[0], bg_color=self.color[0])
        self.bg_frame.place(relx=0, rely=0.125, anchor="nw")

        self.video_label = ctk.CTkLabel(self.bg_frame, text="")
        self.video_label.place(relx=0.5, rely=0.5, anchor="center")

        self.title_label = self.create_label(self.top_frame,text='dji tello',font=("impact",50),fg_color=self.color[1]) 
        self.title_label.place(relx=0.005, rely=0.2)

        self.setting_state = False #aperta o chiusa la finestra delle impostazioni
        self.setting_button = self.create_button(self.top_frame, text="impostazioni", command=self.OpenClose_setting_frame, width=self.root_width / 30, height=self.root_height / 12, corner_radius=10, fg_color=self.color[2], bg_color=self.color[1], text_color=self.color[3], font=("impact", 15))
        self.setting_button.place(relx=0.32, rely=0.5, anchor="center")

        self.follow_me_button = self.create_button(self.top_frame, text="follow me off", command=lambda: self.follow_me_switch(self.follow_me_button), width=self.root_width / 30, height=self.root_height / 12, corner_radius=10, fg_color=self.color[2], bg_color=self.color[1], text_color=self.color[3], font=("impact", 15))
        self.follow_me_button.place(relx=0.39, rely=0.5, anchor="center")

        self.controller_switch()

        self.root.mainloop()

        if self.controller_state:  self.controller_switch()
        if self.stream_state: self.stream_switch()
        if self.follow_me_state: self.follow_me_switch(self.follow_me_button)

#------------------------------------------------------------------

    def create_frame(self,master,frame_width,frame_height,corner_radius=0, fg_color='#0c4160',bg_color='#e3e6e0'):
        return ctk.CTkFrame(master, width=frame_width, height=frame_height, corner_radius=corner_radius, fg_color=fg_color,bg_color=bg_color)
     
    def create_label(self,master,text,corner_radius=0, fg_color='#011e31',bg_color='#011e31',text_color='#c0c0c0', font=("impact", 20)):
        return ctk.CTkLabel(master, text=text, corner_radius=corner_radius, fg_color=fg_color, bg_color=bg_color, text_color=text_color, font=font)

    def create_button(self,master,text,command,width,height,corner_radius=0,fg_color='#011e31',bg_color='#e3e6e0' ,text_color='#c0c0c0', font=("impact", 20)):
        return ctk.CTkButton(master, text=text, command=command, width=width, height=height, corner_radius=corner_radius, fg_color=fg_color, bg_color=bg_color,hover_color=fg_color, text_color=text_color, font=font)

    def create_slider(self, master, variable, command, width, height, min=20, max=500, number_of_steps=480, corner_radius=0, fg_color='#011e31', bg_color='#e3e6e0', progress_color='#c0c0c0'):
        return  ctk.CTkSlider(master, variable=variable, command=command, width=width, height=height, from_=min, to=max, number_of_steps=number_of_steps, corner_radius=corner_radius, fg_color=fg_color, bg_color=bg_color, progress_color=progress_color)

    def create_option_menu(self,master,options, deafault_value, command, width, height, corner_radius=0, fg_color='#011e31',dropdown_fg_color='#011e31', bg_color='#e3e6e0', text_color='#c0c0c0',dropdown_text_color='#c0c0c0', font=("impact", 20)):      
        return ctk.CTkOptionMenu(master, values=options,variable=deafault_value,command=command, width=width, height=height, corner_radius=corner_radius, fg_color=fg_color, dropdown_fg_color=dropdown_fg_color, bg_color=bg_color, text_color=text_color, dropdown_text_color=dropdown_text_color, font=font,dropdown_font=font)


#------------------------------------------------------------------

    def clear_section(self, master):
        for widget in master.winfo_children():
            widget.destroy()
          
    def show_section(self, master, section):
        section = self.settings[section]
        self.clear_section(master)  
        buttons = []
        for i in range(len(section)):
            row = self.create_frame(master, frame_width=self.root_width/4, frame_height=100, corner_radius=10, fg_color=self.color[2], bg_color=self.color[1])
            row.pack()
            label = self.create_label(row, text=section[i][0], corner_radius=10, fg_color=self.color[2], bg_color=self.color[2], text_color=self.color[3], font=("impact", 15))
            label.configure(width=100, height=85, wraplength=100)
            label.place(relx=0.2, rely=0.05)
            if section[i][2] == "button":
                btn = self.create_button(row,text=section[i][1],command=lambda index=i: self.change_key(buttons[index], index),width=100,height=60,corner_radius=10,fg_color=self.color[1],bg_color=self.color[2],text_color=self.color[3],font=("arial", 15))
                btn.place(relx=0.6, rely=0.135)
                buttons.append(btn)

            elif section[i][2] == "slider":
                var = ctk.IntVar(value=section[i][1])

                def slider_command(val, index=i, var=var):
                    self.settings["controller"][index][1] = int(float(val))
                    var.set(int(float(val)))

                slider = self.create_slider(row,variable=var,command= slider_command,width=150,height=20,min=20,max=100,number_of_steps=90,corner_radius=10,fg_color=self.color[1],bg_color=self.color[2],progress_color=self.color[3])
                slider.place(relx=0.75, rely=0.5, anchor="center")

            elif section[i][2] == "optionmenu":
                var = ctk.StringVar(value=str(section[i][1]))

                def option_command(value, idx=i):
                    self.settings["stream"][idx][1] = value

                option_menu = self.create_option_menu(row,options=[str(opt) for opt in section[i][4]],deafault_value=var,command=option_command,width=120,height=30,corner_radius=10,fg_color=self.color[1],dropdown_fg_color=self.color[2],bg_color=self.color[2],text_color=self.color[3],dropdown_text_color=self.color[3],font=("arial", 15))
                option_menu.place(relx=0.75, rely=0.5, anchor="center")

#-------------------------------------------------------------------


    def change_key(self, button, key_number):
        button.configure(text="Premi un tasto...")

        def on_key(event):
            key = event.keysym.lower()
            key =   self.verify_key(key, self.setting_section_controller[key_number][0])
            if key is not None:
                self.settings["controller"][key_number][1] = key
                button.configure(text=key)
                self.root.unbind("<Key>")
            else:
                button.configure(text="Tasto già usato!")
                time.sleep(1)
                button.configure(text=self.settings["controller"][key_number][1])
                self.root.unbind("<Key>")

        self.root.bind("<Key>", on_key)

#-------------------------------------------------------------------

    def OpenClose_setting_frame(self):
        setting_frame_width = self.root_width / 4
        top_frame_height = self.root_height / 8

        if not self.setting_state:
            self.setting_state = True

            self.controller_switch()
            self.controller_state = False

            self.setting_frame = self.create_frame(self.root, setting_frame_width, self.root_height,corner_radius=0, fg_color=self.color[3], bg_color=self.color[2])
            self.setting_frame.place(relx=0.75, rely=0)

            top_frame = self.create_frame(self.setting_frame, setting_frame_width, top_frame_height , corner_radius=0, fg_color=self.color[1], bg_color=self.color[1])
            top_frame.place(relx=0, rely=0, anchor="nw")

            title_label = self.create_label(top_frame,text='Impostazioni',font=("impact", 25), fg_color=self.color[1])
            title_label.place(relx=0.05, rely=0.15)

            widget_width = setting_frame_width / 6
            widget_height = self.root_height / 20

            bg_scrollable_frame = ctk.CTkScrollableFrame(self.setting_frame,orientation='vertical', width=setting_frame_width, height=self.root_height - top_frame.winfo_height(), corner_radius=0, fg_color=self.color[2],scrollbar_button_color=self.color[1])
            bg_scrollable_frame.place(relx=0, rely=0.125, anchor="nw")

            section_label = self.create_label(top_frame,text='Sezione ⭢',font=("impact", 18), fg_color=self.color[1])
            section_label.place(relx=0.05, rely=0.60)

            section = ctk.StringVar(value="controller")
            section_button_menu = ctk.CTkOptionMenu(top_frame,values=list(self.settings.keys()), variable=section, command=lambda section: self.show_section(bg_scrollable_frame, section), width=widget_height, height=widget_height, corner_radius=10, fg_color=self.color[2], bg_color=self.color[1], text_color=self.color[3], font=("impact", 15))
            section_button_menu.place(relx=0.26, rely=0.55, anchor="nw")

            restore_section_button = self.create_button(top_frame, text="ripristina", command= lambda: self.restore_default_settings(section.get()), width=widget_width, height=widget_height, corner_radius=10, fg_color=self.color[2], bg_color=self.color[1], text_color=self.color[3], font=("impact", 15))
            restore_section_button.place(relx=0.58, rely=0.55)

            save_button = self.create_button(top_frame, text="salva", command=self.save_settings_to_json, width=widget_width, height=widget_height, corner_radius=10, fg_color=self.color[2], bg_color=self.color[1], text_color=self.color[3], font=("impact", 15))
            save_button.place(relx=0.8, rely=0.55)

            self.show_section(bg_scrollable_frame, "controller")

        else:
            self.setting_state = False
            if hasattr(self, "setting_frame") and self.setting_frame is not None:
                self.setting_frame.place_forget()
                self.setting_frame = None
                self.controller_switch()
    
    def restore_default_settings(self, section,master):
        super().restore_default_settings(section)
        self.OpenClose_setting_frame()
        self.OpenClose_setting_frame()

#-------------------------------------------------------------------

    def follow_me_switch(self, button):
        if self.follow_me_state:
            self.follow_me_state = False
            if self.follow_me_thread is not None and self.follow_me_thread.is_alive():
                self.follow_me_thread = threading.Thread(self.follow_me_thread)
            button.configure(text="follow me on")
        else:
            if self.follow_me_thread is not None and self.follow_me_thread.is_alive():
                self.follow_me_thread.join()
                self.follow_me_thread = None
            self.follow_me_state = True
            button.configure(text="follow me off")


    def stream_switch(self):
        super().stream_switch()  
        if self.stream_state:
            self.show_stream() 
    
    def show_stream(self):  
        if self.stream_state:
            frame = self.drone.get_frame_read().frame
            if frame is not None:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                img = img.resize((self.bg_frame.winfo_width(), self.bg_frame.winfo_height()))
                imgtk = ImageTk.PhotoImage(image=img)
                if self.follow_me_frame is not None:
                    self.video_label.configure(self.follow_me_frame)
                else:
                    self.video_label.configure(image=imgtk)
                self.video_label.image = imgtk 
            self.root.after(30, self.show_stream)
        else:
            return     


if __name__ == "__main__":
    gui = GUI()
    gui.root.mainloop()
