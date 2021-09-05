import flask

import wp1.logic.builder as logic_builder
from wp1.web import authenticate
from wp1.web.db import get_db

builders = flask.Blueprint('builders', __name__)


@builders.route('/<builder_id>')
@authenticate
def get_builder(builder_id):
  wp10db = get_db('wp10db')
  builder = logic_builder.get_builder(wp10db, builder_id)
  if not builder:
    flask.abort(404)

  # Don't return the builder unless it belongs to this user.
  user = flask.session.get('user')
  if builder.b_user_id != user['identity']['sub']:
    flask.abort(404)

  return flask.jsonify(builder.to_web_dict())


@builders.route('/<builder_id>', methods=['POST'])
@authenticate
def update_builder(builder_id):
  # TODO: actually update the builder
  pass
