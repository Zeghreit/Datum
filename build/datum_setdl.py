"""Give the AssetForge Chrome profile a download folder.

That profile is launched with a bare --user-data-dir and has never had a
download directory set, so Chrome's own download path goes nowhere. Point it
straight at the project's sfx/ folder and turn off the save-as prompt, and
every file the site hands us lands where the build already looks for it.

Chrome rewrites Preferences on exit, so it must be CLOSED when this runs.
"""
import json, os, shutil, sys

PROF = os.path.join(os.path.expanduser('~'), '.assetforge', 'chrome-profile')
PREF = os.path.join(PROF, 'Default', 'Preferences')
SFX  = os.path.join('E:' + os.sep, 'ClaudeFiles', 'Datum', 'sfx')

if not os.path.exists(PREF):
    sys.exit('Preferences not found: ' + PREF)

# refuse to run while Chrome holds the profile
lock = os.path.join(PROF, 'lockfile')
singleton = os.path.join(PROF, 'SingletonLock')
if os.path.exists(singleton) or os.path.exists(lock):
    print('WARNING: the profile looks locked — close that Chrome window first.')

os.makedirs(SFX, exist_ok=True)
shutil.copy2(PREF, PREF + '.bak')

d = json.load(open(PREF, encoding='utf-8'))
dl = d.setdefault('download', {})
dl['default_directory'] = SFX
dl['prompt_for_download'] = False
dl['directory_upgrade'] = True
d.setdefault('savefile', {})['default_directory'] = SFX

json.dump(d, open(PREF, 'w', encoding='utf-8'), ensure_ascii=False)
print('download.default_directory =', SFX)
print('prompt_for_download        = False')
print('backup at', PREF + '.bak')
print('\nNow relaunch that Chrome:  C:\\Users\\a.bodrov\\Projects\\assetforge\\start_browser.bat')
