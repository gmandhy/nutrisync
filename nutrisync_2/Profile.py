import flet as ft
from nutrisync_2.Page import Page
from datetime import datetime
import pytz

class Profile(Page):
    def __init__(self, app, name, route):
        super().__init__(app, name, route)
        self.user_data = None
        self.weight_history = []
        self.init_components()

    def init_components(self):
        # Personal Information
        self.name_input = ft.TextField(
            label="Name",
            width=300,
            hint_text="Enter your full name"
        )
        
        self.email_input = ft.TextField(
            label="Email",
            width=300,
            read_only=True  # Email shouldn't be editable
        )

        # Biometric Information
        self.height_input = ft.TextField(
            label="Height (cm)",
            width=150,
            keyboard_type=ft.KeyboardType.NUMBER,
            hint_text="Enter height"
        )

        self.weight_input = ft.TextField(
            label="Weight (kg)",
            width=150,
            keyboard_type=ft.KeyboardType.NUMBER,
            hint_text="Enter weight"
        )

        self.age_input = ft.TextField(
            label="Age",
            width=150,
            keyboard_type=ft.KeyboardType.NUMBER,
            hint_text="Enter age"
        )

        self.gender_dropdown = ft.Dropdown(
            label="Gender",
            width=150,
            options=[
                ft.dropdown.Option("Male"),
                ft.dropdown.Option("Female"),
                ft.dropdown.Option("Other")
            ]
        )

        self.goal_dropdown = ft.Dropdown(
            label="Fitness Goal",
            width=300,
            options=[
                ft.dropdown.Option("Weight Loss"),
                ft.dropdown.Option("Muscle Gain"),
                ft.dropdown.Option("Maintenance"),
                ft.dropdown.Option("General Fitness"),
                ft.dropdown.Option("Athletic Performance")
            ]
        )

        # BMI Display
        self.bmi_text = ft.Text(
            size=16,
            weight=ft.FontWeight.BOLD
        )
        
        self.bmi_category = ft.Text(
            size=14
        )

        # Weight History Chart (simplified version using text)
        self.weight_history_text = ft.Text(
            size=14
        )

    async def load_user_data(self):
        if not self.app.db.is_connected():
            await self.app.db.connect()
        
        try:
            self.user_data = await self.app.db.user.find_unique(
                where={'id': self.app.current_user_id}
            )

            self.weight_history = await self.app.db.weighthistory.find_many(
                where={'userId': self.app.current_user_id},
                order={'date': 'desc'},
                take=5  # Get last 5 weight entries
            )

            # Populate form fields
            self.name_input.value = self.user_data.name or ""
            self.email_input.value = self.user_data.email
            self.height_input.value = str(self.user_data.height) if self.user_data.height else ""
            self.weight_input.value = str(self.user_data.weight) if self.user_data.weight else ""
            self.age_input.value = str(self.user_data.age) if self.user_data.age else ""
            self.gender_dropdown.value = self.user_data.gender
            self.goal_dropdown.value = self.user_data.goal

            # Update BMI
            self.calculate_bmi(None)

            # Update weight history display
            if self.weight_history:
                history_text = "Recent Weight History:\n"
                for entry in self.weight_history:
                    date_str = entry.date.strftime("%Y-%m-%d")
                    history_text += f"• {date_str}: {entry.weight} kg\n"
                self.weight_history_text.value = history_text
            else:
                self.weight_history_text.value = "No weight history available"

        finally:
            await self.app.db.disconnect()

    def calculate_bmi(self, _):
        try:
            if self.height_input.value and self.weight_input.value:
                height_m = float(self.height_input.value) / 100  # convert cm to m
                weight_kg = float(self.weight_input.value)
                bmi = weight_kg / (height_m * height_m)
                
                self.bmi_text.value = f"BMI: {bmi:.1f}"
                
                # Determine BMI category
                if bmi < 18.5:
                    category = "Underweight"
                    color = ft.colors.ORANGE
                elif bmi < 25:
                    category = "Normal weight"
                    color = ft.colors.GREEN
                elif bmi < 30:
                    category = "Overweight"
                    color = ft.colors.ORANGE
                else:
                    category = "Obese"
                    color = ft.colors.RED
                
                self.bmi_category.value = category
                self.bmi_category.color = color
                self.app.page.update()
        except ValueError:
            self.bmi_text.value = "BMI: --"
            self.bmi_category.value = "Enter height and weight to calculate BMI"
            self.bmi_category.color = ft.colors.BLACK
            self.app.page.update()

    async def save_profile(self, _):
        if not self.app.db.is_connected():
            await self.app.db.connect()
        
        try:
            # Prepare update data
            update_data = {
                'name': self.name_input.value,
                'height': float(self.height_input.value) if self.height_input.value else None,
                'weight': float(self.weight_input.value) if self.weight_input.value else None,
                'age': int(self.age_input.value) if self.age_input.value else None,
                'gender': self.gender_dropdown.value,
                'goal': self.goal_dropdown.value
            }

            # Update user profile
            await self.app.db.user.update(
                where={'id': self.app.current_user_id},
                data=update_data
            )

            # Add weight history entry if weight changed
            if (self.weight_input.value and 
                (not self.user_data.weight or 
                 float(self.weight_input.value) != self.user_data.weight)):
                await self.app.db.weighthistory.create(
                    data={
                        'userId': self.app.current_user_id,
                        'weight': float(self.weight_input.value),
                        'date': datetime.now(pytz.utc)
                    }
                )

            self.app.page.show_snack_bar(
                ft.SnackBar(content=ft.Text("Profile updated successfully!"))
            )
            await self.load_user_data()  # Reload data to refresh display

        except ValueError as e:
            self.app.page.show_snack_bar(
                ft.SnackBar(content=ft.Text("Please enter valid numbers for height, weight, and age"))
            )
        except Exception as e:
            self.app.page.show_snack_bar(
                ft.SnackBar(content=ft.Text(f"Error updating profile: {str(e)}"))
            )
        finally:
            await self.app.db.disconnect()

    async def before_build(self):
        await self.load_user_data()

    def build(self):
        # Add callbacks for BMI calculation
        self.height_input.on_change = self.calculate_bmi
        self.weight_input.on_change = self.calculate_bmi

        return ft.Column([
            ft.Text("Profile", size=24, weight=ft.FontWeight.BOLD),
            
            # Personal Information Section
            ft.Container(
                content=ft.Column([
                    ft.Text("Personal Information", size=18, weight=ft.FontWeight.BOLD),
                    self.name_input,
                    self.email_input,
                    ft.Row([
                        self.age_input,
                        self.gender_dropdown,
                    ]),
                    self.goal_dropdown,
                ]),
                padding=20,
                border=ft.border.all(1, ft.colors.GREY_300),
                border_radius=10,
            ),

            # Biometric Information Section
            ft.Container(
                content=ft.Column([
                    ft.Text("Biometric Information", size=18, weight=ft.FontWeight.BOLD),
                    ft.Row([
                        self.height_input,
                        self.weight_input,
                    ]),
                    ft.Column([
                        self.bmi_text,
                        self.bmi_category,
                    ]),
                    self.weight_history_text,
                ]),
                padding=20,
                border=ft.border.all(1, ft.colors.GREY_300),
                border_radius=10,
            ),

            # Save Button
            ft.ElevatedButton(
                "Save Changes",
                on_click=self.save_profile,
                width=300,
            ),

        ], spacing=20, scroll=ft.ScrollMode.AUTO)