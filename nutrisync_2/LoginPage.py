import flet as ft
from nutrisync_2.Page import Page
import bcrypt

class LoginPage(Page):
    def __init__(self, app, name, route):
        super().__init__(app, name, route)
        self.show_signup = False

    def build(self):
        # Email input
        self.email_input = ft.TextField(
            label="Email",
            width=300,
            autofocus=True,
        )

        # Password input
        self.password_input = ft.TextField(
            label="Password",
            password=True,
            can_reveal_password=True,
            width=300,
        )

        # Login button
        login_button = ft.ElevatedButton(
            text="Login",
            width=300,
            on_click=self.login,
        )

        # Sign up link
        signup_link = ft.TextButton(
            text="Sign up",
            on_click=self.toggle_signup,
        )

        # Forgot password link
        forgot_password_link = ft.TextButton(
            text="Forgot password?",
            on_click=self.forgot_password,
        )

        # Sign Up form
        self.signup_email = ft.TextField(label="Email", width=300)
        self.signup_password = ft.TextField(label="Password", password=True, can_reveal_password=True, width=300)
        self.signup_confirm_password = ft.TextField(label="Confirm Password", password=True, can_reveal_password=True, width=300)
        signup_button = ft.ElevatedButton(text="Sign Up", width=300, on_click=self.signup)

        self.signup_form = ft.Column([
            ft.Text("Sign Up", size=24, weight=ft.FontWeight.BOLD),
            self.signup_email,
            self.signup_password,
            self.signup_confirm_password,
            signup_button,
            ft.TextButton(text="Back to Login", on_click=self.toggle_signup),
        ], visible=False)

        self.login_form = ft.Column([
            ft.Text("Welcome to NutriSync", size=24, weight=ft.FontWeight.BOLD),
            self.email_input,
            self.password_input,
            login_button,
            ft.Row([
                signup_link,
                forgot_password_link,
            ]),
        ])

        return ft.Container(
            content=ft.Column([
                self.login_form,
                self.signup_form,
            ], 
            spacing=20,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            alignment=ft.alignment.center,
            padding=50,
        )

    def toggle_signup(self, _):
        self.show_signup = not self.show_signup
        self.login_form.visible = not self.show_signup
        self.signup_form.visible = self.show_signup
        self.app.page.update()

    async def login(self, _):
        email = self.email_input.value
        password = self.password_input.value
        # Implement login logic here
        print(f"Attempting to log in with email: {email}")
        
        if email == None:
            self.app.page.show_snack_bar(ft.SnackBar(content=ft.Text("Email cannot be empty")))
            return
        
        if password == None:
            self.app.page.show_snack_bar(ft.SnackBar(content=ft.Text("Password cannot be empty")))
            return

        await self.app.login(email, password)

    async def signup(self, _):
        email = self.signup_email.value
        password = self.signup_password.value
        confirm_password = self.signup_confirm_password.value
        
        if email == "":
            self.app.page.show_snack_bar(ft.SnackBar(content=ft.Text("Email cannot be empty")))
            return
        
        if password == "":
            self.app.page.show_snack_bar(ft.SnackBar(content=ft.Text("Password cannot be empty")))
            return

        if password != confirm_password:
            self.app.page.show_snack_bar(ft.SnackBar(content=ft.Text("Passwords do not match")))
            return


        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Add user to the database
        if not self.app.db.is_connected():
            await self.app.db.connect()
        try:
            new_user = await self.app.db.user.create(
                data={
                    'email': email,
                    'password': hashed_password.decode('utf-8'),  # Store the hashed password as a string
                }
            )
            self.app.page.show_snack_bar(ft.SnackBar(content=ft.Text("Sign up successful! Please log in.")))
            self.toggle_signup(None)  # Switch back to login form
        except Exception as e:
            self.app.page.show_snack_bar(ft.SnackBar(content=ft.Text(f"Error during sign up: {str(e)}")))

    def forgot_password(self, _):
        print("Handling forgot password")
        pass
        # Handle forgot password
        