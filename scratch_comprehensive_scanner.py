import os
import re
import sys
import importlib.util
from distutils.sysconfig import get_python_lib

# A set of standard library modules in Python 3.10
STD_LIBS = {
    'abc', 'argparse', 'ast', 'asynchat', 'asyncio', 'asyncore', 'base64', 'bdb', 'binascii',
    'bisect', 'calendar', 'cgi', 'cgitb', 'chunk', 'cmd', 'code', 'codecs', 'codeop',
    'collections', 'colorsys', 'compileall', 'configparser', 'contextlib', 'contextvars',
    'copy', 'copyreg', 'crypt', 'csv', 'ctypes', 'curses', 'dataclasses', 'datetime',
    'dbm', 'decimal', 'difflib', 'dis', 'distutils', 'doctest', 'email', 'encodings',
    'ensurepip', 'enum', 'errno', 'faulthandler', 'filecmp', 'fileinput', 'fnmatch',
    'fractions', 'ftplib', 'functools', 'gc', 'getopt', 'getpass', 'gettext', 'glob',
    'graphlib', 'grp', 'gzip', 'hashlib', 'heapq', 'hmac', 'html', 'http', 'imaplib',
    'imghdr', 'imp', 'importlib', 'inspect', 'io', 'ipaddress', 'itertools', 'json',
    'keyword', 'lib2to3', 'linecache', 'locale', 'logging', 'lzma', 'mailbox', 'mailcap',
    'marshal', 'math', 'mimetypes', 'mmap', 'modulefinder', 'multiprocessing', 'netrc',
    'nis', 'nntplib', 'ntpath', 'numbers', 'operator', 'optparse', 'os', 'ossaudiodev',
    'pathlib', 'pdb', 'pickle', 'pickletools', 'pipes', 'pkgutil', 'platform', 'plistlib',
    'poplib', 'posix', 'posixpath', 'pprint', 'profile', 'pstats', 'pty', 'pwd', 'py_compile',
    'pyclbr', 'pydoc', 'queue', 'quopri', 'random', 're', 'readline', 'reprlib', 'resource',
    'rlcompleter', 'runpy', 'sched', 'secrets', 'select', 'selectors', 'shelve', 'shutil',
    'signal', 'site', 'smtpd', 'smtplib', 'sndhdr', 'socket', 'socketserver', 'spwd',
    'sqlite3', 'ssl', 'stat', 'statistics', 'string', 'stringprep', 'struct', 'subprocess',
    'sunau', 'symtable', 'sys', 'sysconfig', 'syslog', 'tabnanny', 'tarfile', 'telnetlib',
    'tempfile', 'termios', 'test', 'textwrap', 'threading', 'time', 'timeit', 'tkinter',
    'token', 'tokenize', 'trace', 'traceback', 'tracemalloc', 'tty', 'types', 'typing',
    'unicodedata', 'unittest', 'urllib', 'uu', 'uuid', 'warnings', 'wave', 'weakref',
    'webbrowser', 'wsgiref', 'xdg', 'xml', 'xmlrpc', 'zipapp', 'zipfile', 'zlib', 'zoneinfo'
}

def parse_imports(filepath):
    imports = set()
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        # Match 'import abc, def'
        for match in re.finditer(r'^\s*import\s+([a-zA-Z0-9_\s,]+)', content, re.MULTILINE):
            for name in match.group(1).split(','):
                parts = name.strip().split('.')
                if parts[0]:
                    imports.add(parts[0])
                    
        # Match 'from abc import def'
        for match in re.finditer(r'^\s*from\s+([a-zA-Z0-9_.]+)\s+import', content, re.MULTILINE):
            parts = match.group(1).strip().split('.')
            if parts[0]:
                imports.add(parts[0])
    except Exception as e:
        print(f"Error parsing {filepath}: {e}")
    return imports

def get_requirements(req_path):
    reqs = set()
    if not os.path.exists(req_path):
        return reqs
    
    with open(req_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            # Handle git urls
            if 'github.com' in line:
                # E.g. git+https://github.com/python-telegram-bot/ptbcontrib.git
                name = line.split('/')[-1].replace('.git', '').lower()
                reqs.add(name)
                # Hardcode common aliases for custom packages
                if 'downloader' in name:
                    reqs.add('downloader')
                if 'ptbcontrib' in name:
                    reqs.add('ptbcontrib')
                continue
            
            # Extract package name before any ==, >=, <=, etc.
            name = re.split(r'[=<>~!]', line)[0].strip().lower()
            name = name.replace('-', '_') # python package folders often use underscores
            reqs.add(name)
    return reqs

def scan_project(directory, req_path):
    all_imports = set()
    python_files = []
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                path = os.path.join(root, file)
                python_files.append(path)
                all_imports.update(parse_imports(path))
                
    # Normalize imports
    external_imports = set()
    for imp in all_imports:
        imp_lower = imp.lower().replace('-', '_')
        if imp in STD_LIBS:
            continue
        if imp == 'DestinyBot': # local package
            continue
        external_imports.add(imp_lower)
        
    reqs = get_requirements(req_path)
    
    # Additional map for commonly differently-named package imports
    pkg_map = {
        'telegram': 'python_telegram_bot',
        'sqlalchemy': 'sqlalchemy',
        'psycopg2': 'psycopg2_binary',
        'bs4': 'beautifulsoup4',
        'googletrans': 'googletrans',
        'gtts': 'gtts',
        'jikanpy': 'jikanpy',
        'pretty_errors': 'pretty_errors',
        'github': 'pygithub',
        'tgcrypto': 'tgcrypto',
        'pyrogram': 'pyrogram',
        'youtube_search': 'youtube_search',
        'lyrics_extractor': 'lyrics_extractor',
        'cloudscraper': 'cloudscraper',
        'dateparser': 'dateparser',
        'dns': 'dnspython',
        'apscheduler': 'apscheduler',
        'countryinfo': 'countryinfo',
        'html2text': 'html2text',
        'redis': 'redis',
        'better_profanity': 'better_profanity',
        'textblob': 'textblob',
        'nekos': 'nekos.py',
        'gpytranslate': 'gpytranslate',
        'fonttools': 'fonttools',
        'cv2': 'opencv_python_headless',
        'tzlocal': 'tzlocal',
        'pendulum': 'pendulum',
        'fuzzysearch': 'fuzzysearch',
        'img2pdf': 'img2pdf',
        'yaml': 'pyyaml',
        'shazamapi': 'shazamapi',
        'hachoir': 'hachoir',
        'faker': 'faker',
        'feedparser': 'feedparser',
        'wget': 'wget',
        'emoji': 'emoji',
        'lxml': 'lxml',
        'PIL': 'pillow',
        'currencyconverter': 'currencyconverter',
        'google_trans_new': 'google_trans_new',
        'speedtest': 'speedtest_cli',
        'telegraph': 'telegraph',
        'heroku3': 'heroku3',
        'spamwatch': 'spamwatch',
        'alphabet_detector': 'alphabet_detector',
        'pyrate_limiter': 'pyrate_limiter',
        'cachetools': 'cachetools',
        'ujson': 'ujson',
        'pydictionary': 'pydictionary',
        'downloader': 'downloader',
        'ptbcontrib': 'ptbcontrib'
    }
    
    missing = []
    for imp in external_imports:
        mapped_name = pkg_map.get(imp, imp)
        if mapped_name not in reqs and imp not in reqs:
            # Check if it's a sub-directory in DestinyBot modules (local relative imports)
            local_module_path = os.path.join(directory, 'modules', imp)
            if os.path.exists(local_module_path) or os.path.exists(local_module_path + '.py'):
                continue
            local_utils_path = os.path.join(directory, 'utils', imp)
            if os.path.exists(local_utils_path) or os.path.exists(local_utils_path + '.py'):
                continue
            missing.append((imp, mapped_name))
            
    print(f"Total Python Files Scanned: {len(python_files)}")
    print(f"Total External Imports Detected: {len(external_imports)}")
    
    if missing:
        print("\n[WARNING] Potential Missing Requirements:")
        for imp, pkg in missing:
            print(f"  - Import '{imp}' used in code but package '{pkg}' might be missing from requirements.txt")
    else:
        print("\n[SUCCESS] All external imports successfully match requirements.txt!")

if __name__ == '__main__':
    bot_dir = 'c:\\Users\\SHREE\\OneDrive\\Desktop\\DestinyBot-main\\DestinyBot-main\\DestinyBot'
    req_file = 'c:\\Users\\SHREE\\OneDrive\Desktop\\DestinyBot-main\\DestinyBot-main\\requirements.txt'
    scan_project(bot_dir, req_file)
