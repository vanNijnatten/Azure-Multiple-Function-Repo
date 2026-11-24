"""Entry point that the Azure Functions host indexes (Python v2 programming model).

Keep this file thin: create the app and register the blueprints of this app.
"""

import azure.functions as func

from api_app.routes import bp as routes_bp

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)
app.register_functions(routes_bp)
