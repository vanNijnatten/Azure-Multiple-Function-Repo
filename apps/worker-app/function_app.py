"""Entry point that the Azure Functions host indexes (Python v2 programming model).

Keep this file thin: create the app and register the blueprints of this app.
"""

import azure.functions as func

from worker_app.jobs import bp as jobs_bp

app = func.FunctionApp()
app.register_functions(jobs_bp)
