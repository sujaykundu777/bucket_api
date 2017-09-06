from flask import jsonify, make_response, request, url_for
from app import app
from functools import wraps
from app.models import User


def bucket_required(f):
    """
    Decorator to ensure that a valid bucket id is sent in the url path parameters
    :param f:
    :return:
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.view_args:
            return response('failed', 'Request is missing required parameters', 401)

        bucket_id_ = request.view_args['bucket_id']
        if not bucket_id_:
            return response('failed', 'Request is missing the Bucket Id parameter', 401)
        try:
            int(bucket_id_)
        except ValueError:
            return response('failed', 'Provide a valid Bucket Id', 401)
        return f(*args, **kwargs)

    return decorated_function


def response(status, message, status_code):
    """
    Make an http response helper
    :param status: Status message
    :param message: Response Message
    :param status_code: Http response code
    :return:
    """
    return make_response(jsonify({
        'status': status,
        'message': message
    })), status_code


def response_with_bucket_item(status, item, status_code):
    """
    Http response for response with a bucket item.
    :param status: Status Message
    :param item: BucketItem
    :param status_code: Http Status Code
    :return:
    """
    return make_response(jsonify({
        'status': status,
        'item': item.json()
    })), status_code


def response_with_pagination(items, previous, nex, count):
    """
    Get the Bucket items with the result paginated
    :param items: Items within the Bucket
    :param previous: Url to previous page if it exists
    :param nex: Url to next page if it exists
    :param count: Pagination total
    :return: Http Json response
    """
    return make_response(jsonify({
        'status': 'success',
        'previous': previous,
        'next': nex,
        'count': count,
        'items': items
    })), 200


def get_user_bucket(current_user, bucket_id):
    """
    Query the user to find and return the bucket specified by the bucket Id
    :param bucket_id: Bucket Id
    :param current_user: User
    :return:
    """
    user = User.query.filter_by(id=current_user.id).first()
    user_bucket = user.buckets.filter_by(id=bucket_id).first()
    return user_bucket


def get_paginated_items(bucket, bucket_id, page):
    """
    Get the items from the bucket and then paginate the results.
    Construct the previous and next urls.
    :param bucket: Bucket
    :param bucket_id: Bucket Id
    :param page: Page number
    :return:
    """
    pagination = bucket.items.paginate(page=page, per_page=app.config['BUCKET_AND_ITEMS_PER_PAGE'],
                                       error_out=False)
    previous = None
    if pagination.has_prev:
        previous = url_for('items.get_items', bucket_id=bucket_id, page=page - 1, _external=True)
    nex = None
    if pagination.has_next:
        nex = url_for('items.get_items', bucket_id=bucket_id, page=page + 1, _external=True)
    return pagination.items, nex, pagination, previous
