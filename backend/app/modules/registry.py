"""集中导入所有模块的表模型, 确保 SQLModel.metadata 完整收集, 以便建表。"""
from app.modules.admin import models as _admin_models  # noqa: F401
from app.modules.apikeys import models as _apikeys_models  # noqa: F401
from app.modules.auth import models as _auth_models  # noqa: F401
from app.modules.images import models as _images_models  # noqa: F401
