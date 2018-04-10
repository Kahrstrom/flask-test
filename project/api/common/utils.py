from flask import jsonify
from sqlalchemy import and_
from ..models import Tag


def make_response(status_code, status, message=None, data=None):
    response_content = dict(message=message, data=data, status=status)
    response = jsonify(
        {k: v for k, v in response_content.items() if v is not None})
    response.status_code = status_code
    return response


def set_tags(session, parent, args, relation):
    existing_ids = [tag.id for tag in Tag.query.filter(
        getattr(Tag, relation).__eq__(parent.id)).all()]

    request_ids = [tag.get(
        'id', None) for tag in args['tags'] if tag.get('id', None)]

    delete_ids = list(set(existing_ids) - set(request_ids))
    print(args)
    for t in args['tags']:
        print(t)
        if not t.get('id', None):
            t[relation] = id
            print("!!!!!!!!!!")
            parent.tags.append(Tag(**t))
            continue
        filter_group = [
            getattr(Tag, relation).__eq__(parent.id),
            getattr(Tag, 'id').__eq__(t['id'])]
        tag = Tag.query.filter(and_(*filter_group)).first()
        print(filter_group)
        print(tag)
        if not tag:
            return False
        tag.title = t['title']

    for tag_id in delete_ids:
        tag = Tag.query.get(tag_id)
        session.delete(tag)

    session.commit()
    return True
