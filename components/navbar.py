import dash
import dash_bootstrap_components as dbc

def create_navbar():
    navbar = dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink(page['name'], href=page['path']))
            for page in dash.page_registry.values()
        ],
        brand="Stock Dashboard",
        color="dark",
        dark=True,
    )
    return navbar
