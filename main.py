import requests, clipboard, time, json
import flet as ft

headers = {
    'referer': 'https://arizona-rp.com/'
}

response = requests.get('https://backend.arizona-rp.com/server/get-all', headers=headers)

buttonstyle = ft.ButtonStyle(
    shape={ft.MaterialState.DEFAULT: ft.RoundedRectangleBorder(radius=3)},
    color={ft.MaterialState.DEFAULT: "white"}
)
def main(page: ft.Page):
    page.title = 'ArizonaPasswords'
    page.window_width, page.window_height = [400, 500]
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.padding = 30
    page.theme = ft.Theme(color_scheme=ft.ColorScheme(
        primary='white',
        secondary='white'
    ), scrollbar_theme=ft.ScrollbarTheme(thickness=0))
    page.scroll = ft.ScrollMode.ADAPTIVE
    if page.client_storage.get('Accounts') == None:
        page.client_storage.set('Accounts', [])

    class Account(ft.Container):
        def __init__(self, name, password, server):
            super().__init__()

            self.nameText = ft.TextButton(name, lambda _: clipboard.copy(name), expand=True, style=buttonstyle)
            self.passwordText = ft.TextButton(password, on_click=lambda _: clipboard.copy(password), expand=True, style=buttonstyle)
            self.serverText = ft.TextButton(server, on_click=lambda _: clipboard.copy(server), expand=True, style=buttonstyle)
            
            def delete(e):
                save_data = page.client_storage.get('Accounts')
                for i in save_data:
                    if i["name"] == name:
                        save_data.remove(i)
                page.controls.remove(self)
                page.client_storage.set('Accounts', save_data)
                page.update()

            def hover(e):
                self.border = ft.border.all(6, 'white') if self.border == ft.border.all(1, 'black') else ft.border.all(1, 'black')
                self.update()

            self.delete = ft.IconButton(ft.icons.DELETE_ROUNDED, on_click=delete, style=buttonstyle)
            self.content = ft.Column([
                ft.Row([self.nameText, self.passwordText, self.delete]),
                ft.Row([self.serverText])
            ])
            self.padding = 20
            self.border_radius = 10
            self.bgcolor = '#121212'
            self.animate = ft.Animation(700, ft.AnimationCurve.LINEAR_TO_EASE_OUT)
            self.border = ft.border.all(1, 'black')
            self.on_hover = hover
    
    createName = ft.TextField(label='Ник', expand=True, border_radius=10, height=50, border_color='white')
    createPassword = ft.TextField(label='Пароль', expand=True, border_radius=10, height=50, border_color='white')
    createServer = ft.TextField(label='Сервер', expand=True, border_radius=10, height=50, border_color='white')
    def ChangeServerSelector(e):
        createServer.value = "".join([f'{i["ip"]}:{i["port"]}' for i in response.json() if i["name"] == createServerSelector.value])
        createServer.update()
    createServerSelector = ft.Dropdown(options=[
        ft.dropdown.Option(text=i['name']) for i in response.json()
    ], height=35, expand=True, border_radius=10, border_color='white', content_padding=0, alignment=ft.alignment.center, on_change=ChangeServerSelector, label='Выбор сервера')
    def AddAccount(e):
        save_data = page.client_storage.get('Accounts')
        save_data.append({
            'name': createName.value,
            'password': createPassword.value, 
            'server': createServer.value
        })
        page.client_storage.set('Accounts', save_data)
        page.add(
            Account(createName.value, createPassword.value, createServer.value)
        )
        page.auto_scroll = True
        page.update()
        time.sleep(2)
        page.auto_scroll = False
        page.update()
    createButton = ft.TextButton('Добавить', expand=True, style=buttonstyle, on_click=AddAccount)

    def hover(e):
        createContainer.border = ft.border.all(5, 'white') if createContainer.border == ft.border.all(1, 'black') else ft.border.all(1, 'black')
        createContainer.update()

    createContainer = ft.Container(
        ft.Column([
            ft.Row([createName, createPassword]),
            ft.Column([
                ft.Row([createServer]),
                ft.Row([createServerSelector])
            ]),
            ft.Row([createButton])
        ]),
        bgcolor='#141414',
        border_radius=10,
        padding=15,
        border=ft.border.all(1, 'black'),
        on_hover=hover,
        animate=ft.Animation(700, ft.AnimationCurve.FAST_LINEAR_TO_SLOW_EASE_IN)
    )

    def export_json(e: ft.FilePickerResultEvent):
        if e.path != None:
            with open(e.path, 'w') as f:
                f.write(json.dumps(page.client_storage.get('Accounts'), indent=4))
    def open_json(e: ft.FilePickerResultEvent):
        if e.files != None:
            with open(e.files[0].path, 'r') as f:
                page.client_storage.set('Accounts', json.loads(f.read()))
                for i in page.client_storage.get('Accounts'):
                    page.add(Account(i["name"], i["password"], i["server"]))
    pick_json = ft.FilePicker(on_result=open_json)
    page.overlay.append(pick_json)

    pick_save_json = ft.FilePicker(on_result=export_json)
    page.overlay.append(pick_save_json)

    page.add(
        ft.Row([
            ft.TextButton('Экспорт .json', expand=True, style=buttonstyle, on_click=lambda _: pick_save_json.save_file('Выберите путь', file_name='passwords.json', allowed_extensions=['json'])),
            ft.TextButton('Импорт .json', expand=True, style=buttonstyle, on_click=lambda _: pick_json.pick_files('Выберите файл', allowed_extensions=["json"])),
        ]),
        createContainer
    )

    for i in page.client_storage.get('Accounts'):
        page.add(Account(i["name"], i["password"], i["server"]))

ft.app(main)