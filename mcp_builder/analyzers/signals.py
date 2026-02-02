"""Signal extraction engine."""

import logging
from datetime import datetime, timedelta
from typing import List

from .models import TechnicalSignals
from ..ingestion.models import FileContent, GitCommit
from ..mcp.schemas import ProjectStatus, ProjectType

logger = logging.getLogger(__name__)

# Language mapping from file extensions
LANGUAGE_EXTENSIONS = {
    '.py': 'Python',
    '.js': 'JavaScript',
    '.ts': 'TypeScript',
    '.java': 'Java',
    '.cpp': 'C++',
    '.c': 'C',
    '.h': 'C',
    '.go': 'Go',
    '.rs': 'Rust',
    '.rb': 'Ruby',
    '.php': 'PHP',
    '.cs': 'C#',
    '.scala': 'Scala',
    '.kt': 'Kotlin',
    '.swift': 'Swift',
    '.dart': 'Dart',
}

# Framework keywords in dependencies or imports
FRAMEWORK_KEYWORDS = {
    'flask': 'Flask',
    'django': 'Django',
    'fastapi': 'FastAPI',
    'typer': 'Typer',
    'click': 'Click',
    'streamlit': 'Streamlit',
    'react': 'React',
    'vue': 'Vue',
    'angular': 'Angular',
    'express': 'Express',
    'spring': 'Spring',
    'tensorflow': 'TensorFlow',
    'pytorch': 'PyTorch',
    'pandas': 'Pandas',
    'numpy': 'NumPy',
}


def extract_languages(files: List[FileContent]) -> List[str]:
    """Extract programming languages from file extensions."""
    languages = set()
    for file in files:
        ext = file.path.suffix.lower()
        if ext in LANGUAGE_EXTENSIONS:
            languages.add(LANGUAGE_EXTENSIONS[ext])
    return sorted(list(languages))


def extract_frameworks(files: List[FileContent]) -> List[str]:
    """Extract frameworks from dependencies and imports."""
    frameworks = set()
    for file in files:
        content_lower = file.content.lower()
        # Check config files
        if file.path.name.lower() in ['requirements.txt', 'pyproject.toml', 'package.json']:
            for keyword, name in FRAMEWORK_KEYWORDS.items():
                if keyword in content_lower:
                    frameworks.add(name)
        # Check code files for imports
        elif file.path.suffix.lower() in ['.py', '.js', '.ts']:
            for keyword, name in FRAMEWORK_KEYWORDS.items():
                if f'import {keyword}' in content_lower or f'from {keyword}' in content_lower:
                    frameworks.add(name)
    return sorted(list(frameworks))


def infer_project_type(files: List[FileContent]) -> ProjectType:
    """Infer project type from file structure and content."""
    paths = [str(f.path).lower() for f in files]
    file_names = [f.path.name.lower() for f in files]

    # CLI indicators
    if any('cli' in p or 'main.py' in n or 'main.js' in n for p, n in zip(paths, file_names)):
        return ProjectType.CLI

    # API indicators
    if any('api' in p or 'app.py' in n or 'server.js' in n for p, n in zip(paths, file_names)):
        return ProjectType.API

    # Web app indicators
    if any('web' in p or 'index.html' in n for p, n in zip(paths, file_names)):
        return ProjectType.WEB_APP

    # ML indicators
    if any('ml' in p or 'model' in p for p in paths):
        return ProjectType.ML

    # Automation indicators
    if any('script' in p or 'automation' in p for p in paths):
        return ProjectType.AUTOMATION

    # Library indicators
    if any('lib' in p or 'library' in p for p in paths):
        return ProjectType.LIBRARY

    return ProjectType.OTHER


def infer_maturity(files: List[FileContent], commits: List[GitCommit]) -> ProjectStatus:
    """Infer project maturity from structure and activity."""
    has_tests = any('test' in str(f.path).lower() for f in files)
    has_ci = any('ci' in str(f.path).lower() or '.github' in str(f.path).lower() for f in files)
    has_docs = any('doc' in str(f.path).lower() or 'readme' in str(f.path).lower() for f in files)
    has_version = any('version' in f.path.name.lower() for f in files)

    # Production: tests, CI, docs, version
    if has_tests and has_ci and has_docs and has_version:
        return ProjectStatus.PRODUCTION

    # MVP: tests and docs
    if has_tests and has_docs:
        return ProjectStatus.MVP

    # Prototype: default
    return ProjectStatus.PROTOTYPE


def infer_activity_level(commits: List[GitCommit]) -> str:
    """Infer activity level from commit recency."""
    if not commits:
        return 'low'

    try:
        last_commit_date = datetime.fromisoformat(commits[0].date)
        
        # Ensure both datetimes are timezone-aware for comparison
        from datetime import timezone
        now = datetime.now(timezone.utc)
        
        # If last_commit_date is naive, assume UTC
        if last_commit_date.tzinfo is None:
            last_commit_date = last_commit_date.replace(tzinfo=timezone.utc)
        
        days_since = (now - last_commit_date).days

        if days_since < 30:
            return 'high'
        elif days_since < 90:
            return 'medium'
        else:
            return 'low'
    except ValueError:
        logger.warning("Could not parse commit date")
        return 'unknown'


def extract_tech_stack(languages: List[str], frameworks: List[str]) -> List[str]:
    """Combine languages and frameworks into tech stack."""
    return sorted(set(languages + frameworks))


def extract_signals(snapshot) -> TechnicalSignals:
    """Extract all technical signals from repository snapshot."""
    from ..ingestion.models import RepositorySnapshot  # to avoid circular

    languages = extract_languages(snapshot.files)
    frameworks = extract_frameworks(snapshot.files)
    project_type = infer_project_type(snapshot.files)
    maturity = infer_maturity(snapshot.files, snapshot.recent_commits)
    activity_level = infer_activity_level(snapshot.recent_commits)
    tech_stack = extract_tech_stack(languages, frameworks)

    return TechnicalSignals(
        languages=languages,
        frameworks=frameworks,
        project_type=project_type,
        maturity=maturity,
        activity_level=activity_level,
        tech_stack=tech_stack,
    )