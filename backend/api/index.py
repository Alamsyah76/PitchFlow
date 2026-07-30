try:
    from mangum import Mangum
    from app.main import app
    handler = Mangum(app)
except ImportError:
    from app.main import app
    handler = app
