import flet as ft
from datetime import datetime
from nutrisync_2.Page import Page
from nutrisync_2.GoalSystem import GoalSystem, GoalType
import pytz

class GoalTracker(Page):
    def __init__(self, app, name, route):
        super().__init__(app, name, route)
        self.goals = []
        self.goal_system = GoalSystem(app.db, app.current_user_id)
        self.exercise_options = []
        self.init_components()

    def init_components(self):
        # Goal type selector
        self.goal_type_dropdown = ft.Dropdown(
            label="Goal Type",
            width=300,
            options=[
                ft.dropdown.Option(str(GoalType.TARGET_WEIGHT), "Target Weight"),
                ft.dropdown.Option(str(GoalType.WORKOUT_COUNT), "Number of Workouts"),
                ft.dropdown.Option(str(GoalType.EXERCISE_WEIGHT), "Exercise Weight")
            ],
            on_change=self.on_goal_type_change
        )

        # Common inputs
        self.title_input = ft.TextField(
            label="Goal Title",
            width=300,
        )
        
        self.target_value_input = ft.TextField(
            label="Target Value",
            width=300,
            keyboard_type=ft.KeyboardType.NUMBER,
        )

        self.description_input = ft.TextField(
            label="Description (optional)",
            multiline=True,
            min_lines=2,
            max_lines=4,
            width=300,
        )

        # Target date components
        self.target_date_text = ft.TextField(
            label="Target Date",
            value=datetime.now().strftime("%Y-%m-%d"),
            read_only=True,
            width=200,
        )
        self.target_date_button = ft.IconButton(
            icon=ft.icons.CALENDAR_TODAY,
            on_click=self.show_date_picker
        )

        # Exercise selection (initially hidden)
        self.exercise_dropdown = ft.Dropdown(
            label="Exercise",
            width=300,
            visible=False
        )

        # Current weight input (initially hidden)
        self.current_weight_input = ft.TextField(
            label="Current Weight (Kg)",
            width=300,
            keyboard_type=ft.KeyboardType.NUMBER,
            visible=False
        )

    def on_goal_type_change(self, e):
        goal_type = int(e.control.value)
        
        # Show/hide relevant inputs based on goal type
        self.exercise_dropdown.visible = (goal_type == GoalType.EXERCISE_WEIGHT)
        self.current_weight_input.visible = (goal_type == GoalType.TARGET_WEIGHT)
        
        # Update labels based on goal type
        if goal_type == GoalType.TARGET_WEIGHT:
            self.target_value_input.label = "Target Weight (Kg)"
        elif goal_type == GoalType.WORKOUT_COUNT:
            self.target_value_input.label = "Target Number of Workouts"
        elif goal_type == GoalType.EXERCISE_WEIGHT:
            self.target_value_input.label = "Target Weight (Kg)"
        
        self.app.page.update()

    async def before_build(self):
        # Create date picker
        self.date_picker = ft.DatePicker(
            first_date=datetime.now(),
            last_date=datetime(2025, 12, 31),
            on_change=self.on_date_changed
        )
        self.app.page.overlay.append(self.date_picker)
        
        # Load exercise options for exercise weight goals
        if not self.app.db.is_connected():
            await self.app.db.connect()
        
        self.exercise_options = await self.app.db.exerciseoption.find_many(
            order={'name': 'asc'}
        )
        self.exercise_dropdown.options = [
            ft.dropdown.Option(ex.name) for ex in self.exercise_options
        ]
        
        await self.app.db.disconnect()
        
        # Load existing goals
        await self.load_goals()
        await self.app.page.update_async()

    def show_date_picker(self, _):
        self.date_picker.pick_date()

    def on_date_changed(self, e):
        if e.control.value:
            self.target_date_text.value = e.control.value.strftime("%Y-%m-%d")
            self.app.page.update()

    async def load_goals(self):
        if not self.app.db.is_connected():
            await self.app.db.connect()
        
        self.goals = await self.app.db.goal.find_many(
            where={'userId': self.app.current_user_id},
            order={'targetDate': 'asc'}
        )
        
        await self.app.db.disconnect()

    def create_goal_card(self, goal):
        # Calculate progress
        progress = self.goal_system.calculate_progress_percentage(goal)
        
        # Format progress display based on goal type
        if goal.goalType == "TARGET_WEIGHT":
            progress_text = f"Current: {goal.currentValue}Kg / Target: {goal.targetValue}Kg"
        elif goal.goalType == "WORKOUT_COUNT":
            progress_text = f"Completed: {int(goal.currentValue)} / Target: {int(goal.targetValue)} workouts"
        else:  # EXERCISE_WEIGHT
            progress_text = f"Current: {goal.currentValue}Kg / Target: {goal.targetValue}Kg"

        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text(
                            goal.title,
                            size=16,
                            weight=ft.FontWeight.BOLD
                        ),
                        ft.Container(
                            content=ft.Text(
                                "Completed" if goal.completed else "In Progress",
                                color=ft.colors.WHITE
                            ),
                            bgcolor=ft.colors.GREEN if goal.completed else ft.colors.BLUE,
                            padding=5,
                            border_radius=5
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Text(goal.description or ""),
                    ft.Text(
                        f"Type: {GoalType.to_string(goal.goalType)}",
                        size=12,
                        color=ft.colors.GREY_700
                    ),

                    ft.Text(
                        progress_text,
                        size=14,
                    ),
                    ft.ProgressBar(
                        value=progress / 100,
                        color=ft.colors.GREEN if goal.completed else ft.colors.BLUE,
                        bgcolor=ft.colors.GREY_300,
                    ),
                    ft.Text(
                        f"Target Date: {goal.targetDate.strftime('%Y-%m-%d') if goal.targetDate else 'No date set'}",
                        size=12,
                        color=ft.colors.GREY_700
                    ),
                ]),
                padding=20,
            )
        )

    async def add_goal(self, _):
        if not self.title_input.value or not self.target_value_input.value:
            self.app.page.show_snack_bar(
                ft.SnackBar(content=ft.Text("Please fill in all required fields"))
            )
            return

        if not self.app.db.is_connected():
            await self.app.db.connect()
        
        try:
            goal_type = self.goal_type_dropdown.value
            target_date = datetime.strptime(
                self.target_date_text.value,
                "%Y-%m-%d"
            ).replace(tzinfo=pytz.utc)

            # Prepare goal data
            goal_data = {
                'userId': self.app.current_user_id,
                'title': self.title_input.value,
                'description': self.description_input.value,
                'goalType': int(self.goal_type_dropdown.value),  # Convert string to int
                'targetValue': float(self.target_value_input.value),
                'targetDate': target_date,
                'completed': False
            }

            # Add type-specific fields
            if goal_type == "TARGET_WEIGHT":
                goal_data['currentValue'] = float(self.current_weight_input.value)
            elif goal_type == "EXERCISE_WEIGHT":
                goal_data['exerciseName'] = self.exercise_dropdown.value
                goal_data['currentValue'] = 0  # Will be updated when exercise is performed
            else:  # WORKOUT_COUNT
                goal_data['currentValue'] = 0  # Will be updated by goal system

            await self.app.db.goal.create(data=goal_data)

            # Clear inputs
            self.title_input.value = ""
            self.description_input.value = ""
            self.target_value_input.value = ""
            self.current_weight_input.value = ""
            self.exercise_dropdown.value = None

            await self.load_goals()
            self.app.page.update()
            
            self.app.page.show_snack_bar(
                ft.SnackBar(content=ft.Text("New goal added successfully!"))
            )
            
        finally:
            await self.app.db.disconnect()

    def build(self):
        # Create the goals list
        goals_list = ft.Column(spacing=10)
        
        # Separate goals into active and completed
        active_goals = [g for g in self.goals if not g.completed]
        completed_goals = [g for g in self.goals if g.completed]
        
        # Add active goals
        if active_goals:
            goals_list.controls.extend([
                ft.Text("Active Goals", size=18, weight=ft.FontWeight.BOLD),
                *[self.create_goal_card(goal) for goal in active_goals]
            ])
        
        # Add completed goals (collapsed by default)
        if completed_goals:
            completed_goals_expansion = ft.ExpansionTile(
                title=ft.Text("Completed Goals"),
                subtitle=ft.Text(f"{len(completed_goals)} goals"),
                controls=[self.create_goal_card(goal) for goal in completed_goals]
            )
            goals_list.controls.append(completed_goals_expansion)

        return ft.Column([
            ft.Text("Goal Tracker", size=24, weight=ft.FontWeight.BOLD),
            
            # Add new goal section
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Add New Goal", size=18, weight=ft.FontWeight.BOLD),
                        self.goal_type_dropdown,
                        self.title_input,
                        self.target_value_input,
                        self.current_weight_input,
                        self.exercise_dropdown,
                        self.description_input,
                        ft.Row([
                            self.target_date_text,
                            self.target_date_button,
                        ]),
                        ft.ElevatedButton(
                            "Add Goal",
                            icon=ft.icons.ADD,
                            on_click=self.add_goal
                        ),
                    ], spacing=10),
                    padding=20,
                )
            ),
            
            # Goals list
            goals_list,
            
        ], spacing=20, scroll=ft.ScrollMode.AUTO)
