import importlib

SERVICES = [
    "core.services.server_info",    # server info html page
    "app.services.default_tools_messages",
]

ACCESS_KEYS_FILE_PATH = "storage/access_keys.json" 

MIDDLEWARE = {
    "mcp": [
        {
            "middleware": "app.middleware.CheckAccessMiddleware",
            "priority": 1,
            "args": {
                "check_access_func": lambda: getattr(
                    importlib.import_module(
                        "app.middleware.CheckAccessMiddleware.check_access".rsplit(".", 1)[0]
                    ),
                    "app.middleware.CheckAccessMiddleware.check_access".rsplit(".", 1)[-1],
                )
            },
        },
        {
            "middleware": "app.middleware.SetGoogleCredentials",
            "priority": 2
        }
    ]
}