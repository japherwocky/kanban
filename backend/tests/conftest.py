import warnings
import os

warnings.filterwarnings("ignore", message=".*trapped.*error reading bcrypt version")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="passlib")
