from . import gather


@gather.route('/')
def index():
    return "It's gather"
