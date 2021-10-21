import datetime as dt


def year(request):
    """Adds current year"""
    return {'year': int(dt.datetime.now().strftime('%Y')), }
