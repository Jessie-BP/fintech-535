import reflex as rx

config = rx.Config(
    app_name="options_surface_app",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ]
)