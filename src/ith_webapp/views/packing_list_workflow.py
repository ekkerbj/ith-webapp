from flask import Blueprint, Response

bp = Blueprint('packing_list_workflow', __name__)

@bp.route('/packing-lists/ready-to-produce')
def ready_to_produce():
    return Response('Not Implemented', status=501)

@bp.route('/packing-lists/ready-to-ship')
def ready_to_ship():
    return Response('Not Implemented', status=501)
