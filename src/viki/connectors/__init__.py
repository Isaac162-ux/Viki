"""Data source connectors for Deep Research."""

from viki.connectors._stubs import (
    Attachment,
    BaseConnector,
    Document,
    SyncStatus,
)
from viki.connectors.store import KnowledgeStore

__all__ = ["Attachment", "BaseConnector", "Document", "KnowledgeStore", "SyncStatus"]

# Auto-register built-in connectors
import viki.connectors.obsidian  # noqa: F401

try:
    import viki.connectors.gmail  # noqa: F401
except ImportError:
    pass

try:
    import viki.connectors.gmail_imap  # noqa: F401
except ImportError:
    pass

try:
    import viki.connectors.gdrive  # noqa: F401
except ImportError:
    pass  # httpx may not be installed

try:
    import viki.connectors.notion  # noqa: F401
except ImportError:
    pass

try:
    import viki.connectors.granola  # noqa: F401
except ImportError:
    pass

try:
    import viki.connectors.gcontacts  # noqa: F401
except ImportError:
    pass

try:
    import viki.connectors.imessage  # noqa: F401
except ImportError:
    pass

try:
    import viki.connectors.apple_notes  # noqa: F401
except ImportError:
    pass

try:
    import viki.connectors.apple_music  # noqa: F401
except ImportError:
    pass

try:
    import viki.connectors.apple_contacts  # noqa: F401
except ImportError:
    pass

try:
    import viki.connectors.apple_calendar  # noqa: F401
except ImportError:
    pass

try:
    import viki.connectors.slack_connector  # noqa: F401
except ImportError:
    pass

try:
    import viki.connectors.outlook  # noqa: F401
except ImportError:
    pass

try:
    import viki.connectors.imap  # noqa: F401
except ImportError:
    pass

try:
    import viki.connectors.gcalendar  # noqa: F401
except ImportError:
    pass

try:
    import viki.connectors.dropbox  # noqa: F401
except ImportError:
    pass  # httpx may not be installed

try:
    import viki.connectors.whatsapp  # noqa: F401
except ImportError:
    pass

try:
    import viki.connectors.oura  # noqa: F401
except ImportError:
    pass

try:
    import viki.connectors.apple_health  # noqa: F401
except ImportError:
    pass

try:
    import viki.connectors.strava  # noqa: F401
except ImportError:
    pass

try:
    import viki.connectors.spotify  # noqa: F401
except ImportError:
    pass

try:
    import viki.connectors.google_tasks  # noqa: F401
except ImportError:
    pass

try:
    import viki.connectors.weather  # noqa: F401
except ImportError:
    pass

try:
    import viki.connectors.github_notifications  # noqa: F401
except ImportError:
    pass

try:
    import viki.connectors.hackernews  # noqa: F401
except ImportError:
    pass

try:
    import viki.connectors.news_rss  # noqa: F401
except ImportError:
    pass
