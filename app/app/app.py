import customtkinter as ctk
from PhotogrammetryPage import PhotogrammetryPage
import webbrowser

class Sylva3DApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sylva3D PHOTOGRAMMETRY")
        self._center_window(1600, 900)
        self.minsize(1600, 900)

        ctk.set_appearance_mode("dark")

        self.create_navigation_bar()

        self.current_page = None

        self.show_home_page()

    def _center_window(self, width, height):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def create_navigation_bar(self):
        nav_bar = ctk.CTkFrame(self, fg_color="transparent")
        nav_bar.pack(side="top", fill="x")

        center_frame = ctk.CTkFrame(nav_bar, fg_color="transparent")
        center_frame.pack(side="top")

        self._add_nav_button(center_frame, "Home", self.show_home_page)
        self._add_nav_button(center_frame, "Photogrammetry", self.show_photogrammetry_page)

    def _add_nav_button(self, parent, text, command):
        button = ctk.CTkButton(parent, text=text, command=command, font=("Arial", 14), width=100, height=35)
        button.pack(side="left", padx=10, pady=10)

    def show_home_page(self):
        self._switch_page(HomePage)

    def show_photogrammetry_page(self):
        self._switch_page(PhotogrammetryPage)

    def _switch_page(self, page_class):
        if self.current_page is not None:
            self.current_page.pack_forget()
        self.current_page = page_class(self)
        self.current_page.pack(fill="both", expand=True)


class HomePage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self.scrollable_frame = ctk.CTkScrollableFrame(self, width=1600, height=900)
        self.scrollable_frame.pack(fill="both", expand=True)

        # Title
        title = ctk.CTkLabel(self.scrollable_frame, text="Welcome to Sylva3D Photogrammetry Application", font=("Helvetica", 24, "bold"))
        title.pack(pady=20)

        # Application Overview
        overview = ctk.CTkLabel(self.scrollable_frame, text="Sylva3D Photogrammetry is a powerful tool for generating 3D models from 2D images. "
                                           "It offers features such as image loading, background removal, and 3D model generation.",
                                font=("Helvetica", 16), wraplength=1000, justify="left")
        overview.pack(pady=10)

        # Instructions for Use
        instructions = ctk.CTkLabel(self.scrollable_frame, text="Instructions for Use:\n"
                                               "1. Load your images or video frames.\n"
                                               "2. Use the background removal tools to clean up your images if needed but not really recommended.\n"
                                               "3. Generate 3D models using the photogrammetry tools.\n"
                                               "4. View your 3D models in the 3D View section.",
                                    font=("Helvetica", 16), wraplength=1000, justify="left")
        instructions.pack(pady=10)

        # Project Information
        project_info = ctk.CTkLabel(self.scrollable_frame, text="Project Information:\n"
                                               "Sylva3D Photogrammetry is developed to provide an easy-to-use platform for "
                                               "photogrammetry enthusiasts and professionals. Utilizing advanced algorithms "
                                               "and robust processing techniques, it aims to deliver high-quality 3D models.",
                                     font=("Helvetica", 16), wraplength=1000, justify="left")
        project_info.pack(pady=10)

        # License Information
        license_info = ctk.CTkLabel(self.scrollable_frame, text="License Information:\n"
                                               "This software is licensed under the MIT License.",
                                    font=("Helvetica", 16), wraplength=1000, justify="left")
        license_info.pack(pady=10)

        # Contact Information
        contact_info = ctk.CTkLabel(self.scrollable_frame, text="Contact Information:\n"
                                               "For support or feedback, please contact us at projectsengineer6@gmail.com.",
                                    font=("Helvetica", 16), wraplength=1000, justify="left")
        contact_info.pack(pady=10)

        # Email in Blue
        email_link = ctk.CTkLabel(self.scrollable_frame, text="projectsengineer6@gmail.com", font=("Helvetica", 16), fg_color="blue", cursor="hand2")
        email_link.pack(pady=10)
        email_link.bind("<Button-1>", lambda e: webbrowser.open("mailto:projectsengineer6@gmail.com"))

        # Recent Updates or News
        updates = ctk.CTkLabel(self.scrollable_frame, text="Recent Updates:\n"
                                          "Version 1.0 released with new background removal features and improved 3D model rendering.",
                                font=("Helvetica", 16), wraplength=1000, justify="left")
        updates.pack(pady=10)

        # Author Information
        author_info = ctk.CTkLabel(self.scrollable_frame, text="Author Information:\n"
                                              "This application was developed by Stéphane KPOVIESSI as part of his internship at Groupe Sylvagreg, Lille France.\n"
                                              "Stéphane is an M2 Big Data & AI student at Junia ISEN Lille, with a strong background in data science and machine learning.\n"
                                              "Contact: oastephaneamiche@gmail.com\n"
                                              "LinkedIn: ",
                                   font=("Helvetica", 16), wraplength=1000, justify="left")
        author_info.pack(pady=10)

        # LinkedIn Link
        linkedin_link = ctk.CTkLabel(self.scrollable_frame, text="linkedin.com/in/stephanekpoviessi/", font=("Helvetica", 16), fg_color="blue", cursor="hand2")
        linkedin_link.pack(pady=10)
        linkedin_link.bind("<Button-1>", lambda e: webbrowser.open("https://linkedin.com/in/stephanekpoviessi/"))

if __name__ == "__main__":
    window = Sylva3DApp()
    window.mainloop()
