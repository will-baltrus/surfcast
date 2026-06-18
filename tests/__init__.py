import os
import tempfile

# Run the whole test suite against a throwaway database in the temp folder, so
# tests never touch the real instance/surf.sqlite3. This is set here, in the
# tests package, so it takes effect before any test imports the app or models.
_test_db = os.path.join(tempfile.gettempdir(), "surfcast_test.sqlite3")
os.environ["SURFCAST_DATABASE_URI"] = "sqlite:///" + _test_db
