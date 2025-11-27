import flet as ft
from datetime import datetime
from nutrisync_2.Page import Page
from nutrisync_2.AchievementSystem import AchievementSystem
import pytz

class FocusedTextField(ft.TextField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.on_change = self.maintain_focus

    def maintain_focus(self, e):
        self.focus()

class WorkoutLogger(Page):
    def __init__(self, app, name, route):
        super().__init__(app, name, route)
        self.exercise_options = []
        self.exercise_list = ft.Column(spacing=10)
        self.init_components()
    
    async def load_exercise_options(self):
        if not self.exercise_options:
            if not self.app.db.is_connected():
                await self.app.db.connect()
            
            options = await self.app.db.exerciseoption.find_many(
                order={"name": "asc"}
            )
            self.exercise_options = [option.name for option in options]
            self.exercise_options.append("Other")
            await self.app.db.disconnect()
            self.exercise_dropdown.options = [ft.dropdown.Option(ex) for ex in self.exercise_options]
        self.app.page.update()



    def init_components(self):
        # Create date text field and button first
        self.date_text = ft.TextField(
            label="Date",
            value=datetime.now().strftime("%Y-%m-%d"),
            read_only=True,
            width=200,
        )
        
        self.date_button = ft.IconButton(
            icon=ft.icons.CALENDAR_TODAY,
            on_click=self.show_date_picker
        )

        self.date_row = ft.Row([
            self.date_text,
            self.date_button
        ])

        # Rest of your existing init_components code
        workout_types = ["Strength", "Cardio", "Flexibility", "HIIT", "Other"]
        self.workout_type_dropdown = ft.Dropdown(
            label="Workout Type",
            options=[ft.dropdown.Option(t) for t in workout_types],
            width=200,
        )

        self.duration_input = ft.TextField(
            label="Duration (minutes)",
            value="60",
            keyboard_type=ft.KeyboardType.NUMBER,
        )

        self.exercise_dropdown = ft.Dropdown(
            label="Exercise",
            options=[],  # Will be populated in load_exercise_options
            width=200,
            on_change=self.toggle_custom_exercise,
        )
        self.custom_exercise_input = ft.TextField(label="Custom Exercise", visible=False)
        self.sets_input = ft.TextField(label="Sets", width=100)
        self.reps_input = ft.TextField(label="Reps", width=100)
        self.weight_input = ft.TextField(label="Weight (Kg)", width=100)

        self.notes = ft.TextField(
            label="Notes",
            multiline=True,
            min_lines=3,
            max_lines=5,
        )

    def on_date_changed(self, e):
        if e.control.value:
            self.date_text.value = e.control.value.strftime("%Y-%m-%d")
            self.app.page.update()

    async def before_build(self):
        # Create and add date picker to the page
        self.date_picker = ft.DatePicker(
            first_date=datetime(2024, 1, 1),
            last_date=datetime(2025, 12, 31),
            on_change=self.on_date_changed
        )
        self.app.page.overlay.append(self.date_picker)
        await self.app.page.update_async()
        
        # Load exercise options
        await self.load_exercise_options()


    def build(self):
        add_exercise_button = ft.ElevatedButton(
            "Add Exercise",
            icon=ft.icons.ADD,
            on_click=self.add_exercise,
        )

        save_workout_button = ft.ElevatedButton(
            "Save Workout",
            icon=ft.icons.SAVE,
            on_click=self.save_workout,
        )

        return ft.Column([
            ft.Text("Log Workout", size=24, weight=ft.FontWeight.BOLD),
            self.date_row,
            self.workout_type_dropdown,
            self.duration_input,
            ft.Text("Add Exercises", size=18, weight=ft.FontWeight.BOLD),
            ft.Row([
                self.exercise_dropdown,
                add_exercise_button,
            ]),
            ft.Row([
                self.custom_exercise_input,
                self.sets_input,
                self.reps_input,
                self.weight_input,
            ]),
            ft.Text("Exercise List", size=18, weight=ft.FontWeight.BOLD),
            self.exercise_list,
            self.notes,
            save_workout_button,
        ], spacing=20, scroll=ft.ScrollMode.AUTO)

    def add_exercise(self, _):
        exercise_name = self.exercise_dropdown.value
        if exercise_name == "Other":
            exercise_name = self.custom_exercise_input.value
        
        if not exercise_name or not self.sets_input.value or not self.reps_input.value:
            self.app.page.show_snack_bar(ft.SnackBar(content=ft.Text("Please fill in all required fields")))
            return

        exercise_item = ft.Text(
            f"{exercise_name} - Sets: {self.sets_input.value}, Reps: {self.reps_input.value}, Weight: {self.weight_input.value or 'N/A'} Kg"
        )
        self.exercise_list.controls.append(exercise_item)
        
        # Clear inputs
        self.exercise_dropdown.value = None
        self.custom_exercise_input.value = ""
        self.sets_input.value = ""
        self.reps_input.value = ""
        self.weight_input.value = ""
        
        self.app.page.update()


    def to_rfc3339(self, dt):
        """Convert a datetime object to RFC 3339 format."""
        return dt.astimezone(pytz.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    
    def from_rfc3339(self, dt_str):
        """Convert an RFC 3339 formatted string to a datetime object."""
        return datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=pytz.utc)

    def create_exercise_card(self):
        exercise_dropdown = ft.Dropdown(
            label="Exercise",
            options=[ft.dropdown.Option(ex) for ex in self.exercise_options],
            width=200,
            on_change=self.toggle_custom_exercise,
        )
        custom_exercise_input = ft.TextField(label="Custom Exercise", visible=False)

        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    
                    ft.Row([
                        exercise_dropdown,
                        custom_exercise_input,
                        ft.TextField(label="Sets", width=100, key="sets"),
                        ft.TextField(label="Reps", width=100, key="reps"),
                        ft.TextField(label="Weight (Kg)", width=100, key="weight"),
                    ]),
                ]),
                padding=10,
            ),
        )
    
    def toggle_custom_exercise(self, e):
        self.custom_exercise_input.visible = e.control.value == "Other"
        self.app.page.update()

    def show_date_picker(self, _):
        self.date_picker.pick_date()

    async def save_workout(self, _):
        if not self.app.db.is_connected(): await self.app.db.connect()
        workout_data = self.get_workout_data()
        if not all([self.workout_type_dropdown.value]):
            print("Invalid Exercise Type")
            return
        try:
            workout_date = datetime.strptime(workout_data["date"], "%Y-%m-%d")
            rfc3339_date = self.to_rfc3339(workout_date)

            new_workout = await self.app.db.workout.create(
                data={
                    "date": rfc3339_date,
                    "duration": int(workout_data["duration"]),
                    "type": workout_data["workout_type"],
                    "notes": workout_data["notes"],
                    "userId": self.app.current_user_id,
                }
            )

            for exercise in workout_data["exercises"]:
                existing_exercise = await self.app.db.exerciseoption.find_first(
                    where={"name": exercise["exercise_name"]}
                )
                if not existing_exercise:
                    await self.app.db.exerciseoption.create(
                        data={"name": exercise["exercise_name"]}
                    )

                await self.app.db.exercise.create(
                    data={
                        "name": exercise["exercise_name"],
                        "sets": int(exercise["sets"]),
                        "reps": int(exercise["reps"]),
                        "weight": float(exercise["weight"]) if exercise["weight"] else None,
                        "workoutId": new_workout.id,
                    }
                )

            print(f"Workout saved successfully with ID: {new_workout.id}")
            await self.update_user_streak()
            
            # Check for achievements
            achievement_system = AchievementSystem(self.app.db, self.app.current_user_id)
            new_achievements = await achievement_system.check_achievements()
            
            # Show achievement notifications
            if new_achievements:
                achievements_text = "\n".join([f"🏆 {a.title}" for a in new_achievements])
                self.app.page.show_snack_bar(
                    ft.SnackBar(
                        content=ft.Text(f"New achievements earned!\n{achievements_text}"),
                        duration=5000
                    )
                )
            
            self.clear_form()
            self.app.page.update()
        except Exception as e:
            print(f"Error saving workout: {str(e)}")
        finally:
            await self.app.db.disconnect()

    def parse_exercise_item(self, item_text):
        parts = item_text.split(" - ")
        exercise_name = parts[0]
        details = parts[1].split(", ")
        sets = details[0].split(": ")[1]
        reps = details[1].split(": ")[1]
        weight = details[2].split(": ")[1].replace(" Kg", "")
        return {
            "exercise_name": exercise_name,
            "sets": sets,
            "reps": reps,
            "weight": weight if weight != "N/A" else None
        }



    async def update_user_streak(self):
        STREAK_INTERVAL_DAYS = 2  # Configure workout interval here
        # Streak will be reset if no new workout is logged within above set limit
        
        today = datetime.now(pytz.utc)
        user_id = self.app.current_user_id

        current_streak = await self.app.db.streak.find_first(
            where={"userId": user_id},
            order={"endDate": "desc"}
        )

        if current_streak:
            current_end_date = current_streak.endDate.date() if isinstance(current_streak.endDate, datetime) else current_streak.endDate
            days_since_last = (today.date() - current_end_date).days

            # Continue streak if within acceptable interval (1-2 days)
            if 1 <= days_since_last <= STREAK_INTERVAL_DAYS:
                await self.app.db.streak.update(
                    where={"id": current_streak.id},
                    data={
                        "endDate": today,
                        "currentStreak": current_streak.currentStreak + 1
                    }
                )
                
                # Update longest streak if applicable
                if current_streak.currentStreak + 1 > current_streak.longestStreak:
                    await self.app.db.streak.update(
                        where={"id": current_streak.id},
                        data={"longestStreak": current_streak.currentStreak + 1}
                    )
            
            # Start new streak if too much time has passed
            elif days_since_last > STREAK_INTERVAL_DAYS:
                await self.app.db.streak.create(
                    data={
                        "startDate": today,
                        "endDate": today,
                        "currentStreak": 1,
                        "longestStreak": max(current_streak.longestStreak, 1),
                        "userId": user_id
                    }
                )
        else:
            # First streak for the user
            await self.app.db.streak.create(
                data={
                    "startDate": today,
                    "endDate": today,
                    "currentStreak": 1,
                    "longestStreak": 1,
                    "userId": user_id
                }
            )

    def get_workout_data(self):
        exercises = []
        for exercise_item in self.exercise_list.controls:
            if isinstance(exercise_item, ft.Text):
                exercise_data = self.parse_exercise_item(exercise_item.value)
                exercises.append(exercise_data)

        return {
            "date": self.date_text.value,  # Updated to use date_text instead of date_picker
            "workout_type": self.workout_type_dropdown.value,
            "duration": self.duration_input.value,
            "exercises": exercises,
            "notes": self.notes.value,
        }


    def clear_form(self):
        self.date_text.value = datetime.now().strftime("%Y-%m-%d")  # Updated to use date_text
        self.workout_type_dropdown.value = None
        self.duration_input.value = "60"
        self.exercise_dropdown.value = None
        self.custom_exercise_input.value = ""
        self.sets_input.value = ""
        self.reps_input.value = ""
        self.weight_input.value = ""
        self.exercise_list.controls.clear()
        self.notes.value = ""
        self.app.page.update()