import flet as ft
from nutrisync_2.Page import Page
from typing import List, Dict

class WorkoutPlans(Page):
    def __init__(self, app, name, route):
        super().__init__(app, name, route)
        self.plans_list = ft.Column(spacing=10)
        self.plan_name_input = ft.TextField(label="Plan Name", width=300)
        self.plan_description_input = ft.TextField(label="Plan Description", multiline=True, width=300)
        self.exercise_inputs: List[Dict[str, ft.Control]] = []
        self.exercise_options: List[str] = []
        self.exercise_list_column = ft.Column(spacing=10)
        self.is_creating_plan = False

    async def load_exercise_options(self):
        if not self.app.db.is_connected():
            await self.app.db.connect()
        
        options = await self.app.db.exerciseoption.find_many(
            order={"name": "asc"}
        )
        self.exercise_options = [option.name for option in options]
        self.exercise_options.append("Other")
        await self.app.db.disconnect()

    async def load_plans(self):
        if not self.app.db.is_connected():
            await self.app.db.connect()
        
        plans = await self.app.db.workoutplan.find_many(
            where={"userId": self.app.current_user_id},
            include={"exercises": True}
        )
        
        self.plans_list.controls.clear()
        for plan in plans:
            plan_card = self.create_plan_card(plan.name, plan.description, plan.id)
            self.plans_list.controls.append(plan_card)
        
        await self.app.db.disconnect()
        self.app.page.update()

    def build(self):
        if self.is_creating_plan:
            return self.build_plan_creation_page()
        
        create_plan_button = ft.ElevatedButton(
            "Create New Plan",
            icon=ft.icons.ADD,
            on_click=self.show_plan_creation_page
        )

        return ft.Column([
            ft.Text("Workout Plans", size=24, weight=ft.FontWeight.BOLD),
            create_plan_button,
            ft.Text("Your Plans", size=18, weight=ft.FontWeight.BOLD),
            self.plans_list,
        ], spacing=20, scroll=ft.ScrollMode.AUTO, expand=True)

    def build_plan_creation_page(self):
        add_exercise_button = ft.ElevatedButton(
            "Add Exercise",
            icon=ft.icons.ADD,
            on_click=self.add_exercise_input
        )

        save_plan_button = ft.ElevatedButton(
            "Save Plan",
            icon=ft.icons.SAVE,
            on_click=self.create_new_plan
        )

        return ft.Column([
            ft.Row([
                ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=self.return_to_plans_list),
                ft.Text("Create New Workout Plan", size=24, weight=ft.FontWeight.BOLD),
            ]),
            self.plan_name_input,
            self.plan_description_input,
            add_exercise_button,
            self.exercise_list_column,
            save_plan_button,
        ], spacing=20, scroll=ft.ScrollMode.AUTO, expand=True)

    async def show_plan_creation_page(self, _):
        self.is_creating_plan = True
        self.exercise_inputs.clear()
        self.exercise_list_column.controls.clear()
        self.plan_name_input.value = ""
        self.plan_description_input.value = ""
        await self.app.navigate("/workout-plans")
        self.app.page.update()

    async def return_to_plans_list(self, _):
        self.is_creating_plan = False
        await self.app.navigate("/workout-plans")
        self.app.page.update()

    def add_exercise_input(self, _):
        exercise_input = {
            "name": ft.Dropdown(
                label="Exercise",
                options=[ft.dropdown.Option(ex) for ex in self.exercise_options],
                width=300,
                on_change=self.toggle_custom_exercise
            ),
            "custom_name": ft.TextField(label="Custom Exercise", visible=False, width=300),
            "sets": ft.TextField(label="Sets", width=300),
            "reps": ft.TextField(label="Reps", width=300),
            "weight": ft.TextField(label="Weight (optional)", width=300),
        }
        self.exercise_inputs.append(exercise_input)
        
        exercise_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    exercise_input["name"],
                    exercise_input["custom_name"],
                    exercise_input["sets"],
                    exercise_input["reps"],
                    exercise_input["weight"],
                    ft.ElevatedButton(
                        "Remove Exercise",
                        on_click=lambda _: self.remove_exercise_input(exercise_card),
                        width=300
                    )
                ], spacing=10),
                padding=10,
            )
        )
        
        self.exercise_list_column.controls.append(exercise_card)
        self.app.page.update()

    def toggle_custom_exercise(self, e):
        for exercise_input in self.exercise_inputs:
            if exercise_input["name"] == e.control:
                exercise_input["custom_name"].visible = e.control.value == "Other"
                break
        self.app.page.update()

    def remove_exercise_input(self, exercise_card):
        self.exercise_list_column.controls.remove(exercise_card)
        self.exercise_inputs = [
            exercise for exercise in self.exercise_inputs
            if exercise["name"] in exercise_card.content.content.controls
        ]
        self.app.page.update()

    async def create_new_plan(self, _):
        if not self.plan_name_input.value:
            self.app.page.show_snack_bar(ft.SnackBar(content=ft.Text("Please enter a plan name")))
            return

        if not self.exercise_inputs:
            self.app.page.show_snack_bar(ft.SnackBar(content=ft.Text("Please add at least one exercise")))
            return

        if not self.app.db.is_connected():
            await self.app.db.connect()

        try:
            new_plan = await self.app.db.workoutplan.create(
                data={
                    "name": self.plan_name_input.value,
                    "description": self.plan_description_input.value,
                    "userId": self.app.current_user_id,
                    "exercises": {
                        "create": [
                            {
                                "name": exercise["custom_name"].value if exercise["name"].value == "Other" else exercise["name"].value,
                                "sets": int(exercise["sets"].value),
                                "reps": int(exercise["reps"].value),
                                "weight": float(exercise["weight"].value) if exercise["weight"].value else None
                            }
                            for exercise in self.exercise_inputs
                            if (exercise["name"].value == "Other" and exercise["custom_name"].value) or (exercise["name"].value != "Other" and exercise["name"].value)
                            and exercise["sets"].value and exercise["reps"].value
                        ]
                    }
                }
            )
            print(f"Workout plan created with ID: {new_plan.id}")
            await self.load_plans()
            self.return_to_plans_list(None)
            self.app.page.show_snack_bar(ft.SnackBar(content=ft.Text("Workout plan created successfully")))
        except Exception as e:
            print(f"Error creating workout plan: {str(e)}")
            self.app.page.show_snack_bar(ft.SnackBar(content=ft.Text("Error creating workout plan")))
        finally:
            await self.app.db.disconnect()

    def create_plan_card(self, name, description, plan_id):
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text(name, size=16, weight=ft.FontWeight.BOLD),
                    ft.Text(description, size=14),
                    ft.ResponsiveRow([
                        ft.TextButton("Edit", on_click=lambda _: self.edit_plan(plan_id), col={"sm": 4}),
                        ft.TextButton("Delete", on_click=lambda _: self.delete_plan(plan_id), col={"sm": 4}),
                        ft.TextButton("Use Plan", on_click=lambda _: self.use_plan(plan_id), col={"sm": 4}),
                    ]),
                ]),
                padding=10,
            )
        )

    async def edit_plan(self, plan_id):
        # Implement edit functionality
        pass

    async def delete_plan(self, plan_id):
        if not self.app.db.is_connected():
            await self.app.db.connect()

        try:
            await self.app.db.workoutplan.delete(where={"id": plan_id})
            print(f"Workout plan deleted with ID: {plan_id}")
            await self.load_plans()
        except Exception as e:
            print(f"Error deleting workout plan: {str(e)}")
        finally:
            await self.app.db.disconnect()

    async def use_plan(self, plan_id):
        if not self.app.db.is_connected():
            await self.app.db.connect()

        try:
            plan = await self.app.db.workoutplan.find_first(
                where={"id": plan_id},
                include={"exercises": True}
            )
            if plan:
                # Navigate to WorkoutLogger and pass the plan data
                await self.app.navigate("/log-workout", plan_data=plan)
            else:
                print(f"Workout plan not found with ID: {plan_id}")
        except Exception as e:
            print(f"Error loading workout plan: {str(e)}")
        finally:
            await self.app.db.disconnect()

    async def before_build(self):
        await self.load_exercise_options()
        await self.load_plans()