from kanban_app import create_app
from flask_cors import CORS

app, api = create_app()

CORS(app)

from kanban_app.api import UserAPI, ListAPI, CardAPI, summaryAPI;

api.add_resource(UserAPI, "/api/user")

api.add_resource(ListAPI, "/api/list")

api.add_resource(CardAPI, "/api/card")

api.add_resource(summaryAPI, "/api/summary")

if __name__ == '__main__':
    app.run(port=8080)

